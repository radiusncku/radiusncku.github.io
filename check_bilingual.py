#!/usr/bin/env python3
"""
check_bilingual.py  --  sanity-check the English / 中文 pairs on a RADIUS Lab page.

Every visible piece of text on the site exists twice: once in an element marked
data-en (English) and once in an element marked data-zh (Chinese). If one half
is missing, left blank, or accidentally left untranslated, the language toggle
breaks -- text vanishes or shows the wrong language. This script finds those
problems before your visitors do.

USAGE (run it from the folder that contains your .html files):

    python check_bilingual.py                 # checks index.html
    python check_bilingual.py people.html      # checks another page
    python check_bilingual.py *.html           # checks several pages

It prints a short report. It exits with status 1 if it finds a real problem
(a missing or empty half), and 0 if everything looks healthy -- so you can wire
it into automated checks later if you ever want to.

No installation needed: it uses only Python's standard library.
"""

import sys
import glob
from html.parser import HTMLParser


class BilingualParser(HTMLParser):
    """Walks the HTML and records the text of every data-en / data-zh element,
    in the order they appear, together with the line number where each starts."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []      # list of (lang, text, line_number)
        self._stack = []     # currently-open elements

    def handle_starttag(self, tag, attrs):
        keys = [k for k, _ in attrs]
        lang = "en" if "data-en" in keys else "zh" if "data-zh" in keys else None
        self._stack.append({"tag": tag, "lang": lang,
                             "line": self.getpos()[0], "text": []})

    def handle_data(self, data):
        # Append text to every open element that is language-tagged
        # (so text inside a nested <span> still counts toward its parent).
        for frame in self._stack:
            if frame["lang"]:
                frame["text"].append(data)

    def handle_endtag(self, tag):
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i]["tag"] == tag:
                frame = self._stack.pop(i)
                if frame["lang"]:
                    text = " ".join("".join(frame["text"]).split())
                    self.items.append((frame["lang"], text, frame["line"]))
                break


def check_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            html = f.read()
    except OSError as e:
        print(f"  !! could not open {path}: {e}")
        return False

    parser = BilingualParser()
    parser.feed(html)
    items = parser.items

    n_en = sum(1 for lang, _, _ in items if lang == "en")
    n_zh = sum(1 for lang, _, _ in items if lang == "zh")

    problems = []   # serious: stop the presses
    warnings = []   # worth a human glance

    # Pair them up in document order. The site always writes English first,
    # then its Chinese partner immediately after.
    i = 0
    while i < len(items):
        lang, text, line = items[i]
        if lang == "en":
            if i + 1 < len(items) and items[i + 1][0] == "zh":
                en_text, en_line = text, line
                zh_text, zh_line = items[i + 1][1], items[i + 1][2]
                if not en_text:
                    problems.append(f"line {en_line}: English text is EMPTY")
                if not zh_text:
                    problems.append(f"line {zh_line}: Chinese text is EMPTY")
                if en_text and zh_text and en_text == zh_text:
                    warnings.append(
                        f"line {zh_line}: English and Chinese are identical "
                        f"-- looks untranslated  ->  \"{en_text[:50]}\"")
                i += 2
            else:
                problems.append(
                    f"line {line}: English has NO Chinese partner  "
                    f"->  \"{text[:50]}\"")
                i += 1
        else:  # a Chinese element with no English in front of it
            problems.append(
                f"line {line}: Chinese has NO English partner  "
                f"->  \"{text[:50]}\"")
            i += 1

    # ---- report ----
    print(f"\n{path}")
    print(f"  English elements : {n_en}")
    print(f"  Chinese elements : {n_zh}")

    if n_en != n_zh:
        print(f"  !! COUNT MISMATCH: {n_en} English vs {n_zh} Chinese "
              f"-- one or more translations is missing.")

    if problems:
        print(f"  !! {len(problems)} problem(s):")
        for p in problems:
            print(f"       - {p}")
    if warnings:
        print(f"  ~  {len(warnings)} thing(s) to double-check:")
        for w in warnings:
            print(f"       - {w}")
    if not problems and not warnings and n_en == n_zh:
        print("  OK -- every English line has a matching Chinese line. ")

    return not problems and n_en == n_zh


def main():
    args = sys.argv[1:] or ["index.html"]
    paths = []
    for a in args:
        paths.extend(glob.glob(a))
    if not paths:
        print("No matching .html files found.")
        sys.exit(1)

    all_ok = True
    for path in paths:
        ok = check_file(path)
        all_ok = all_ok and ok

    print()
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
