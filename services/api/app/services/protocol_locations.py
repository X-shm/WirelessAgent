"""Locate citation fragments in the same PDF used to build the protocol index."""

from bisect import bisect_right
import json
import re
import unicodedata


_QUOTES = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "\u00ad": None})
_WHITESPACE = re.compile(r"\s+")
_GENERATED_STEP = re.compile(r"^Step\s+\d+\.\s+", re.I)


def _normalized(text):
    return unicodedata.normalize("NFKC", text).translate(_QUOTES).casefold()


def _compact(text):
    return _WHITESPACE.sub("", _normalized(text))


class ProtocolPdfLocations:
    def __init__(self, pdf, sha256):
        self.pdf = pdf
        self.sha256 = sha256
        self.page_offsets = None
        self.declared_pages = {}

    def _valid_page(self, page):
        return type(page) is int and 1 <= page <= len(self.pdf)

    def _declared_page(self, page):
        if page not in self.declared_pages:
            # These are offsets into the cleaned, sorted page text from the evidence builder.
            lines = self.pdf[page - 1].get_text("text", sort=True).splitlines(keepends=True)
            self.declared_pages[page] = "".join(
                line for index, line in enumerate(lines)
                if not (index < 8 and "3GPP TS" in line and "ETSI TS" in line and "Release" in line)
                and not (index >= len(lines) - 5 and line.strip() == "ETSI")
            ).strip()
        return self.declared_pages[page]

    def _declared_spans(self, text, metadata):
        spans = metadata.get("source_spans")
        if not isinstance(spans, list) or not spans:
            return []
        fragments = []
        offset = 0
        previous = 0
        for span in spans:
            if not isinstance(span, dict):
                return []
            page, left, right = (span.get(field) for field in ("pdf_page", "char_start", "char_end"))
            if (not self._valid_page(page) or page <= previous
                    or type(left) is not int or type(right) is not int or not 0 <= left < right):
                return []
            if previous:
                separator = "\n\n" * (page - previous)
                if not text.startswith(separator, offset):
                    return []
                offset += len(separator)
                fragments[-1][1] = offset
            page_text = self._declared_page(page)
            end = offset + right - left
            if right > len(page_text) or text[offset:end] != page_text[left:right]:
                return []
            offset = end
            fragments.append([page, offset])
            previous = page
        if (offset != len(text) or fragments[0][0] != metadata.get("pdf_page_start")
                or fragments[-1][0] != metadata.get("pdf_page_end")):
            return []
        return fragments

    def _read_pages(self):
        offsets, parts = [0], []
        self.legacy_pages = []
        for page in self.pdf:
            lines = page.get_text().splitlines()
            start = next((index + 1 for index, line in enumerate(lines[:12])
                          if line.strip().startswith("3GPP TS") and "Release" in line), 0)
            normalized = _normalized("\n".join(lines[start:]))
            self.legacy_pages.append(normalized)
            part = _WHITESPACE.sub("", normalized)
            offsets.append(offsets[-1] + len(part))
            parts.append(part)
        self.page_offsets = offsets
        self.page_text = "".join(parts)

    def _legacy_spans(self, text, first, last):
        if self.page_offsets is None:
            self._read_pages()
        lower, upper = self.page_offsets[first - 1], self.page_offsets[last]
        # Legacy procedure splitting may prepend a synthetic "Step N." label.
        step = _GENERATED_STEP.match(text)
        for prefix in (0, step.end()) if step else (0,):
            needle = _compact(text[prefix:])
            if not needle:
                continue
            start = self.page_text.find(needle, lower, upper)
            if start < 0:
                continue
            if self.page_text.find(needle, start + 1, upper) >= 0:
                return []
            first_page = bisect_right(self.page_offsets, start)
            last_page = bisect_right(self.page_offsets, start + len(needle) - 1)
            if len(needle) < 100:
                # Confirm that a short match is complete, including its word boundaries.
                words = _normalized(text[prefix:]).split()
                pattern = r"(?<!\w)" + r"\s+".join(map(re.escape, words)) + r"(?!\w)"
                pages = "\n".join(self.legacy_pages[first_page - 1:last_page])
                if not re.search(pattern, pages):
                    continue
            if first_page == last_page:
                return [[first_page, len(text)]]
            # Recover original offsets to split the existing chunk without altering its text.
            letters = [_compact(char) for char in text[prefix:]]
            if "".join(letters) != needle:
                return []
            original_offsets = [index for index, part in enumerate(letters, prefix + 1) for _ in part]
            fragments = [[page, original_offsets[self.page_offsets[page] - start - 1]]
                         for page in range(first_page, last_page)
                         if self.page_offsets[page] > self.page_offsets[page - 1]]
            return [*fragments, [last_page, len(text)]]
        return []

    def metadata_for(self, row):
        text, source = row["text"], row["metadata"]
        first, last = source.get("pdf_page_start"), source.get("pdf_page_end")
        digest = source.get("source_sha256")
        if digest == self.sha256:
            spans = self._declared_spans(text, source)
            if spans:
                return {"citation_location": "evidence", "citation_spans": json.dumps(spans)}
            if (row["content_type"] == "figure_description"
                    and source.get("authority") == "derived_visual_description"
                    and self._valid_page(first) and first == last):
                return {"citation_location": "figure", "citation_spans": json.dumps([[first, len(text)]])}
        elif digest is None and source.get("clause") and self._valid_page(first):
            if self._valid_page(last) and first <= last and source.get("authority") == "authoritative_pdf":
                spans = self._legacy_spans(text, first, last)
                if spans:
                    return {"citation_location": "evidence", "citation_spans": json.dumps(spans)}
            return {"citation_location": "clause", "citation_spans": json.dumps([[first, len(text)]])}
        return {"citation_location": "document"}
