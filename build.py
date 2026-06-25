#!/usr/bin/env python3
"""
build.py  --  generate index.html for the RADIUS Lab site from data files.

You edit the CONTENT in two plain data files:

    content.en.json   (English)
    content.zh.json   (Chinese)

…then run this script:

    python build.py

It reads both files, checks that they line up (same number of publications,
news items, people, links, etc.), fills in the page skeleton (template.html),
and writes a finished index.html. That index.html is what you deploy.

Rules of thumb
--------------
* Edit the JSON files, never index.html (index.html is regenerated every time).
* The two JSON files must have the SAME SHAPE — same keys, same list lengths.
  If you add a publication to one language, add it to the other too. This
  script will stop and tell you exactly where they differ.
* No installation needed: standard library only.
"""

import json
import sys
from html import escape as _escape


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def esc(text):
    """Escape &, <, > so text is safe inside HTML (keeps quotes as-is)."""
    return _escape(str(text), quote=False)


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"ERROR: cannot find {path} (run build.py from the site folder).")
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: {path} is not valid JSON.\n  -> {e}\n"
                 f"  (A stray comma or missing quote is the usual cause; "
                 f"line {e.lineno}, column {e.colno}.)")


def check_shape(en, zh, path="content"):
    """Make sure the two language files have identical structure.
    Stops the build with a clear message if they don't."""
    if type(en) is not type(zh):
        sys.exit(f"ERROR: structure mismatch at '{path}': "
                 f"English is {type(en).__name__}, Chinese is {type(zh).__name__}.")
    if isinstance(en, dict):
        only_en = set(en) - set(zh)
        only_zh = set(zh) - set(en)
        if only_en:
            sys.exit(f"ERROR: key(s) {sorted(only_en)} exist at '{path}' in "
                     f"content.en.json but are missing from content.zh.json.")
        if only_zh:
            sys.exit(f"ERROR: key(s) {sorted(only_zh)} exist at '{path}' in "
                     f"content.zh.json but are missing from content.en.json.")
        for k in en:
            check_shape(en[k], zh[k], f"{path}.{k}")
    elif isinstance(en, list):
        if len(en) != len(zh):
            sys.exit(f"ERROR: '{path}' has {len(en)} item(s) in English but "
                     f"{len(zh)} in Chinese. Add or remove items so they match.")
        for i, (a, b) in enumerate(zip(en, zh)):
            check_shape(a, b, f"{path}[{i}]")
    # leaf values (strings) may differ freely — that's the whole point.


def pair(tag, cls, en_text, zh_text):
    """One bilingual element pair: an English version and a Chinese version."""
    return (f'<{tag} class="{cls}" data-en>{esc(en_text)}</{tag}>\n'
            f'      <{tag} class="{cls}" data-zh>{esc(zh_text)}</{tag}>')


def spanpair(en_text, zh_text):
    """Bilingual pair as two spans inside another element (links, buttons)."""
    return (f'<span data-en>{esc(en_text)}</span>'
            f'<span data-zh>{esc(zh_text)}</span>')


# ---------------------------------------------------------------------------
# section builders  (en / zh are the two loaded dictionaries)
# ---------------------------------------------------------------------------

def build_nav(en, zh):
    n_en, n_zh = en["nav"], zh["nav"]
    links = [("#research", "research"), ("#publications", "publications"),
             ("#people", "people"), ("#news", "news")]
    nav_links = "\n        ".join(
        f'<a class="nav-link" href="{href}">{spanpair(n_en[key], n_zh[key])}</a>'
        for href, key in links)
    return f'''  <header class="site-nav">
    <div class="nav-inner">
      <a class="brand" href="#top">
        <span class="brand-name">RADIUS</span>
        <span class="brand-sub">NCKU</span>
      </a>
      <nav class="nav-links">
        {nav_links}
        <button class="lang-toggle" type="button" data-lang-toggle aria-label="Switch language">
          {spanpair(n_en["lang_button"], n_zh["lang_button"])}
        </button>
        <a class="btn-join" href="#join">{spanpair(n_en["join"], n_zh["join"])}</a>
      </nav>
    </div>
  </header>'''


def build_hero(en, zh):
    h_en, h_zh = en["hero"], zh["hero"]
    title_en = (f'{esc(h_en["title_before"])}'
                f'<span class="accent">{esc(h_en["title_accent"])}</span>'
                f'{esc(h_en["title_after"])}')
    title_zh = (f'{esc(h_zh["title_before"])}'
                f'<span class="accent">{esc(h_zh["title_accent"])}</span>'
                f'{esc(h_zh["title_after"])}')
    return f'''  <section class="hero" id="top">
    <div class="container">
      {pair("p", "eyebrow", h_en["eyebrow"], h_zh["eyebrow"])}
      <h1 class="hero-title" data-en>{title_en}</h1>
      <h1 class="hero-title" data-zh>{title_zh}</h1>
      {pair("p", "hero-sub", h_en["subtitle"], h_zh["subtitle"])}
      <div class="hero-actions">
        <a class="btn btn-primary" href="#research">{spanpair(h_en["btn_primary"], h_zh["btn_primary"])}</a>
        <a class="btn btn-ghost" href="#publications">{spanpair(h_en["btn_secondary"], h_zh["btn_secondary"])}</a>
      </div>
    </div>
  </section>'''


def build_research(en, zh):
    r_en, r_zh = en["research"], zh["research"]
    items = []
    for a, b in zip(r_en["items"], r_zh["items"]):
        items.append(f'''      <div class="research-item">
        <span class="research-num">{esc(a["num"])}</span>
        <div class="research-body">
          <div>
            {pair("h3", "ri-title", a["title"], b["title"])}
          </div>
          <div>
            {pair("p", "ri-desc", a["desc"], b["desc"])}
          </div>
        </div>
      </div>''')
    return f'''  <section class="research" id="research">
    <div class="container">
      {pair("p", "eyebrow", r_en["eyebrow"], r_zh["eyebrow"])}

{chr(10).join(items)}
    </div>
  </section>'''


def build_pubs(en, zh):
    p_en, p_zh = en["publications"], zh["publications"]
    items = []
    for a, b in zip(p_en["items"], p_zh["items"]):
        link_html = "".join(
            f'<a href="{esc(lk["href"])}">[ {esc(lk["label"])} ]</a>'
            for lk in a["links"])
        items.append(f'''      <div class="pub">
        <span class="pub-year">{esc(a["year"])}</span>
        <div>
          {pair("h3", "pub-title", a["title"], b["title"])}
          <p class="pub-meta">{esc(a["authors"])} · <em>{esc(a["journal"])}</em></p>
          <div class="pub-links">{link_html}</div>
        </div>
      </div>''')
    return f'''  <section class="pubs" id="publications">
    <div class="container">
      {pair("p", "eyebrow", p_en["eyebrow"], p_zh["eyebrow"])}
      {pair("h2", "section-title", p_en["title"], p_zh["title"])}

{chr(10).join(items)}

      <a class="more-link" href="#">{spanpair(p_en["more"], p_zh["more"])}</a>
    </div>
  </section>'''


def build_people(en, zh):
    pe_en, pe_zh = en["people"], zh["people"]
    pi_en, pi_zh = pe_en["pi"], pe_zh["pi"]

    def photo(cls, src, alt):
        if src:
            return f'<img class="photo {cls}" src="{esc(src)}" alt="{esc(alt)}" />'
        return f'<div class="photo {cls}"><span>[ photo ]</span></div>'

    pi_links = "".join(f'<a href="{esc(lk["href"])}">{esc(lk["label"])}</a>'
                       for lk in pi_en["links"])

    members = []
    for a, b in zip(pe_en["members"], pe_zh["members"]):
        members.append(f'''        <div class="member">
          {photo("member-photo", a["photo"], a["name"])}
          <h4>{esc(a["name"])}</h4>
          <p class="member-role">{spanpair(a["role"], b["role"])}</p>
        </div>''')

    return f'''  <section class="people" id="people">
    <div class="container">
      {pair("p", "eyebrow", pe_en["eyebrow"], pe_zh["eyebrow"])}
      {pair("h2", "section-title", pe_en["title"], pe_zh["title"])}

      <div class="pi">
        {photo("pi-photo", pi_en["photo"], pi_en["name"])}
        <div>
          {pair("h3", "pi-name", pi_en["name"], pi_zh["name"])}
          {pair("p", "pi-role", pi_en["role"], pi_zh["role"])}
          {pair("p", "pi-bio", pi_en["bio"], pi_zh["bio"])}
          <div class="pi-links">{pi_links}</div>
        </div>
      </div>

      <div class="members">
{chr(10).join(members)}
      </div>
    </div>
  </section>'''


def build_news(en, zh):
    n_en, n_zh = en["news"], zh["news"]
    items = []
    for a, b in zip(n_en["items"], n_zh["items"]):
        items.append(f'''        <div class="news-item">
          <span class="news-date">{esc(a["date"])}</span>
          {pair("p", "news-text", a["text"], b["text"])}
        </div>''')
    return f'''  <section class="news" id="news">
    <div class="container">
      {pair("p", "eyebrow", n_en["eyebrow"], n_zh["eyebrow"])}
      {pair("h2", "section-title", n_en["title"], n_zh["title"])}
      <div class="news-list">
{chr(10).join(items)}
      </div>
    </div>
  </section>'''


def build_join(en, zh):
    j_en, j_zh = en["join"], zh["join"]
    email = esc(j_en["email"])
    return f'''  <section class="join" id="join">
    <div class="container">
      <div>
        {pair("p", "eyebrow", j_en["eyebrow"], j_zh["eyebrow"])}
        {pair("h2", "join-title", j_en["title"], j_zh["title"])}
      </div>
      <div>
        {pair("p", "join-text", j_en["text"], j_zh["text"])}
        <div class="join-actions">
          <a class="btn-email" href="mailto:{email}">{email}</a>
          <a class="btn-positions" href="#">{spanpair(j_en["positions"], j_zh["positions"])}</a>
        </div>
      </div>
    </div>
  </section>'''


def build_footer(en, zh):
    f_en, f_zh = en["footer"], zh["footer"]
    addr_en = "<br />".join(esc(line) for line in f_en["address"].split("\n"))
    addr_zh = "<br />".join(esc(line) for line in f_zh["address"].split("\n"))
    explore = "\n          ".join(
        f'<a href="{esc(a["href"])}">{spanpair(a["label"], b["label"])}</a>'
        for a, b in zip(f_en["explore_links"], f_zh["explore_links"]))
    elsewhere = "\n          ".join(
        f'<a href="{esc(lk["href"])}">{esc(lk["label"])}</a>'
        for lk in f_en["elsewhere_links"])
    return f'''  <footer class="site-footer">
    <div class="footer-grid">
      <div>
        <span class="footer-brand">{esc(f_en["brand"])}</span>
        <p class="footer-addr" data-en>{addr_en}</p>
        <p class="footer-addr" data-zh>{addr_zh}</p>
      </div>
      <div>
        <p class="footer-col-title">{spanpair(f_en["explore_title"], f_zh["explore_title"])}</p>
        <div class="footer-links">
          {explore}
        </div>
      </div>
      <div>
        <p class="footer-col-title">{spanpair(f_en["elsewhere_title"], f_zh["elsewhere_title"])}</p>
        <div class="footer-links">
          {elsewhere}
        </div>
      </div>
    </div>
    <div class="footer-copy">
      <p>{esc(f_en["copyright"])}</p>
    </div>
  </footer>'''


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    en = load("content.en.json")
    zh = load("content.zh.json")

    # Verify the two languages line up before building anything.
    check_shape(en, zh)

    body = "\n\n".join([
        build_nav(en, zh),
        build_hero(en, zh),
        build_research(en, zh),
        build_pubs(en, zh),
        build_people(en, zh),
        build_news(en, zh),
        build_join(en, zh),
        build_footer(en, zh),
    ])

    try:
        with open("template.html", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        sys.exit("ERROR: cannot find template.html (the page skeleton).")

    html = (template
            .replace("{{TITLE}}", esc(en["meta"]["title"]))
            .replace("{{DESCRIPTION}}", esc(en["meta"]["description"]))
            .replace("{{BODY}}", body))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    n_pubs = len(en["publications"]["items"])
    n_news = len(en["news"]["items"])
    n_people = 1 + len(en["people"]["members"])
    print("Built index.html")
    print(f"  {n_pubs} publications | {n_news} news items | {n_people} people")

    # Automatically double-check the result, so one click does everything:
    # build the page AND confirm the English / Chinese lines all line up.
    ok = True
    try:
        from check_bilingual import check_file
        print()
        ok = check_file("index.html")
    except Exception as e:
        print(f"  (auto-check skipped: {e})")

    print()
    if ok:
        print("=" * 52)
        print("  DONE. index.html is ready.")
        print("  Next: preview it, then Commit + Sync in VS Code.")
        print("=" * 52)
    else:
        print("=" * 52)
        print("  PROBLEM found above. Fix the JSON, then Run again.")
        print("=" * 52)
        sys.exit(1)


if __name__ == "__main__":
    main()
