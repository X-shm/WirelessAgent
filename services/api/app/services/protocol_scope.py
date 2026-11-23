"""Recognize explicit 3GPP source restrictions without a model call."""

import re


_SPEC = re.compile(r"(?<![A-Za-z0-9])(?:3GPP\s*)?TS\s*(\d{2}[.．]\d{3})(?!\d|[.．]\d)", re.I)
_EDITION = re.compile(
    r"\s*(?:(?:的|[,，])\s*)?(?:[\[(（]\s*)?(?:(?:release|rel|r)\s*[-‐‑–—]?\s*(?P<release>\d{1,2})(?!\d|\.\d)"
    r"|(?:v(?:ersion)?\s*|版本\s*)(?P<version>\d{1,2}\.\d{1,2}\.\d{1,2})(?!\d|\.\d))"
    r"\s*[\])）]?",
    re.I,
)
_JOIN = re.compile(r"\s*(?:,|，|、|/|\band\b|\bor\b|\bvs\.?|\bversus\b|和|与|及|或)\s*", re.I)
_ONLY_BEFORE = re.compile(
    r"(?:\b(?:only|solely|exclusively)(?:\s+(?:use|using|search|consult|from|based on))?"
    r"|\b(?:restrict|limit)\s+(?:the\s+)?(?:sources?|search|answer)\s+to"
    r"|(?:只|仅)(?:使用|用|查|检索|参考|依据|基于|限(?:于)?)|限定(?:在|于))"
    r'\s*["“《]?\s*$',
    re.I,
)
_ONLY_AFTER = re.compile(r'\s*[”》"]?\s*\bonly\b(?=\s*(?:[,.;!?，。；！？]|$))', re.I)
_EDITION_OF = re.compile(r"\s*(?:\bof\b|的)\s*", re.I)


class ProtocolScopeUnavailable(ValueError):
    """At least one explicitly requested source is missing from the index."""


def _editions(query, start, spec):
    """Collect adjacent release/version qualifiers and explicit alternatives."""
    cursor = start
    first = _EDITION.match(query, cursor)
    if not first:
        return [{"spec": spec, "release": None, "version": None}], cursor
    editions = []
    while first:
        parsed = first.groupdict()
        cursor = first.end()
        second = _EDITION.match(query, cursor)
        if second and second.lastgroup != first.lastgroup:
            parsed[second.lastgroup] = second.group(second.lastgroup)
            cursor = second.end()
        release = int(parsed["release"]) if parsed["release"] else None
        version = ".".join(str(int(part)) for part in parsed["version"].split(".")) if parsed["version"] else None
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
        editions, end = _editions(query, match.end(), spec)
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

    limited = [items for start, end, items in groups
               if _ONLY_BEFORE.search(query[:start]) or _ONLY_AFTER.match(query, end)]
    selected = limited or [items for _, _, items in groups
                           if any(item["release"] is not None or item["version"] for item in items)]
    if selected:
        return [item for items in selected for item in items]
    for match in editions_in_query:
        if _ONLY_BEFORE.search(query[:match.start()]):
            return _editions(query, match.start(), None)[0]
    return []
