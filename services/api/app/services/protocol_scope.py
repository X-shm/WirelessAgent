"""Recognize explicit 3GPP source restrictions without a model call."""

import re


_SPEC = re.compile(r"(?<![A-Za-z0-9])(?:3GPP\s*)?TS\s*(\d{2}[.．]\d{3})(?!\d|[.．]\d)", re.I)
_EDITION = re.compile(
    r"\s*(?:(?:的|[,，])\s*)?(?:[\[(（]\s*)?(?:(?:release|rel|r)\s*[-‐‑–—]?\s*(?P<release>\d{1,2})(?!\d|\.\d)"
    r"|(?P<version_label>v(?:ersion)?\s*|版本\s*)?(?<![\d.])(?P<version>\d{1,2}\.\d{1,2}\.\d{1,2})(?!\d|\.\d))"
    r"\s*[\])）]?",
    re.I,
)
_JOIN = re.compile(r"\s*(?:,|，|、|/|\band\b|\bor\b|\bwith\b|\bvs\.?|\bversus\b|和|与|及|或)\s*", re.I)
_ONLY_BEFORE = re.compile(
    r"(?:\b(?:only|solely|exclusively)(?:\s+(?:use|using|search|consult|from|based on))?"
    r"|\b(?:restrict|limit)\s+(?:the\s+)?(?:sources?|search|answer)\s+to"
    r"|(?:只|仅)(?:使用|用|查|检索|参考|依据|基于|限(?:于)?)|限定(?:在|于))"
    r'\s*["“《]?\s*$',
    re.I,
)
_ONLY_AFTER = re.compile(r'\s*[”》"]?\s*\bonly\b(?=\s*(?:[,.;!?，。；！？]|$))', re.I)
_EXCLUDE_BEFORE = re.compile(
    r"(?:\b(?:do\s+not|don['’]t|never|not)(?:\s+(?:use|search|consult|include|cite|from))?\b"
    r"|\b(?:exclude|excluding|except)\b|(?:不要|不)(?:使用|用|查|检索|参考|引用)|排除)"
    r'\s*["“《]?\s*$',
    re.I,
)
_COMPARE = re.compile(r"\bcompar(?:e|ing|ison)\b|对比|比较", re.I)
_EDITION_OF = re.compile(r"\s*(?:\bof\b|\bfor\b|的)\s*", re.I)


class ProtocolScopeUnavailable(ValueError):
    """The index cannot satisfy the requested document scope."""


def _has_edition_label(match):
    return match["release"] is not None or match["version_label"] is not None


def _editions(query, start, spec, *, allow_bare=False):
    """Collect adjacent release/version qualifiers and explicit alternatives."""
    cursor = start
    first = _EDITION.match(query, cursor)
    if not first or not (allow_bare or _has_edition_label(first) or _ONLY_AFTER.match(query, first.end())):
        return [{"spec": spec, "release": None, "version": None}], cursor
    editions = []
    while first:
        release_value, version_value = first["release"], first["version"]
        cursor = first.end()
        second = _EDITION.match(query, cursor)
        if second and second.lastgroup != first.lastgroup:
            release_value = release_value or second["release"]
            version_value = version_value or second["version"]
            cursor = second.end()
        release = int(release_value) if release_value else None
        version = ".".join(str(int(part)) for part in version_value.split(".")) if version_value else None
        editions.append({"spec": spec, "release": release, "version": version})
        separator = _JOIN.match(query, cursor)
        first = _EDITION.match(query, separator.end()) if separator else None
    return editions, cursor


def requested_protocol_scope(query):
    """Return explicit source selectors. A plain mention of a TS stays unrestricted."""
    groups = []
    editions_in_query = list(_EDITION.finditer(query))
    for match in _SPEC.finditer(query):
        spec = "3GPP TS " + match[1].replace("．", ".")
        start = match.start()
        joined = groups and _JOIN.fullmatch(query[groups[-1][1]:start])
        prefix = query[:groups[-1][0] if joined else start]
        allow_bare = bool(_ONLY_BEFORE.search(prefix) or _EXCLUDE_BEFORE.search(prefix) or _COMPARE.search(prefix))
        editions, end = _editions(query, match.end(), spec, allow_bare=allow_bare)
        if end == match.end():
            for qualifier in editions_in_query:
                if qualifier.start() >= start:
                    break
                preceding, edition_end = _editions(query, qualifier.start(), spec)
                if edition_end < start and _EDITION_OF.fullmatch(query[edition_end:start]):
                    start, editions = qualifier.start(), preceding
                    break
        if groups and _JOIN.fullmatch(query[groups[-1][1]:start]):
            group_start, _, previous = groups[-1]
            groups[-1] = (group_start, end, previous + editions)
        else:
            groups.append((start, end, editions))

    limited, versioned, excluded = [], [], []
    for start, end, items in groups:
        prefix = query[:start]
        if _EXCLUDE_BEFORE.search(prefix):
            excluded.extend({**item, "exclude": True} for item in items)
        elif _ONLY_BEFORE.search(prefix) or _ONLY_AFTER.match(query, end):
            limited.extend(items)
        elif any(item["release"] is not None or item["version"] for item in items):
            versioned.extend(items)
    if limited or versioned:
        return (limited or versioned) + excluded
    for match in editions_in_query:
        if any(start <= match.start() < end for start, end, _ in groups):
            continue
        if _ONLY_BEFORE.search(query[:match.start()]):
            return _editions(query, match.start(), None, allow_bare=True)[0] + excluded
        if _EXCLUDE_BEFORE.search(query[:match.start()]):
            editions, _ = _editions(query, match.start(), None, allow_bare=True)
            excluded.extend({**item, "exclude": True} for item in editions)
    return excluded
