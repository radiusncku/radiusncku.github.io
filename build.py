#!/usr/bin/env python3
"""
build.py  --  multi-page site generator for the RADIUS Lab.

You edit CONTENT in two data files (content.en.json / content.zh.json) and run:

    python build.py

It generates several HTML pages that share one navigation bar and footer:

    index.html         Home  (hero + about + research + join)
    pi.html            Principal Investigator
    people.html        The team (students, grouped)
    publications.html  Full publication list
    teaching.html      Teaching & invited talks
    resources.html     Resources
    news.html          News

You still only ever edit the two JSON files -- this script rebuilds every page
from them. The English / Chinese toggle and the chosen language carry across all
pages automatically. Standard library only; nothing to install.
"""

import json
import sys
from html import escape as _escape


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def esc(text):
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
    if type(en) is not type(zh):
        sys.exit(f"ERROR: structure mismatch at '{path}': "
                 f"English is {type(en).__name__}, Chinese is {type(zh).__name__}.")
    if isinstance(en, dict):
        only_en = set(en) - set(zh)
        only_zh = set(zh) - set(en)
        if only_en:
            sys.exit(f"ERROR: key(s) {sorted(only_en)} at '{path}' exist in "
                     f"content.en.json but not content.zh.json.")
        if only_zh:
            sys.exit(f"ERROR: key(s) {sorted(only_zh)} at '{path}' exist in "
                     f"content.zh.json but not content.en.json.")
        for k in en:
            check_shape(en[k], zh[k], f"{path}.{k}")
    elif isinstance(en, list):
        if len(en) != len(zh):
            sys.exit(f"ERROR: '{path}' has {len(en)} item(s) in English but "
                     f"{len(zh)} in Chinese. Add or remove items so they match.")
        for i, (a, b) in enumerate(zip(en, zh)):
            check_shape(a, b, f"{path}[{i}]")


def pair(tag, cls, en_text, zh_text):
    return (f'<{tag} class="{cls}" data-en>{esc(en_text)}</{tag}>\n'
            f'      <{tag} class="{cls}" data-zh>{esc(zh_text)}</{tag}>')


def spanpair(en_text, zh_text):
    return (f'<span data-en>{esc(en_text)}</span>'
            f'<span data-zh>{esc(zh_text)}</span>')


# ---------------------------------------------------------------------------
# shared chrome: nav + footer
# ---------------------------------------------------------------------------

NAV_LINKS = [
    ("index.html#about", "about"),
    ("index.html#research", "research"),
    ("pi.html", "pi"),
    ("people.html", "people"),
    ("publications.html", "publications"),
    ("teaching.html", "teaching"),
    ("resources.html", "resources"),
    ("news.html", "news"),
]


def build_nav(en, zh, active):
    n_en, n_zh = en["nav"], zh["nav"]
    items = []
    for href, key in NAV_LINKS:
        cls = "nav-link active" if key == active else "nav-link"
        items.append(f'<a class="{cls}" href="{href}">'
                     f'{spanpair(n_en[key], n_zh[key])}</a>')
    nav_links = "\n        ".join(items)
    return f'''  <header class="site-nav">
    <div class="nav-inner">
      <a class="brand" href="index.html">
        <span class="brand-name">RADIUS</span>
        <span class="brand-sub">NCKU</span>
      </a>
      <button class="nav-toggle" type="button" data-nav-toggle aria-label="Menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <nav class="nav-links">
        {nav_links}
        <button class="lang-toggle" type="button" data-lang-toggle aria-label="Switch language">
          {spanpair(n_en["lang_button"], n_zh["lang_button"])}
        </button>
        <a class="btn-join" href="index.html#join">{spanpair(n_en["join"], n_zh["join"])}</a>
      </nav>
    </div>
  </header>'''


def build_footer(en, zh):
    f_en, f_zh = en["footer"], zh["footer"]
    addr_en = "<br />".join(esc(l) for l in f_en["address"].split("\n"))
    addr_zh = "<br />".join(esc(l) for l in f_zh["address"].split("\n"))
    explore = "\n          ".join(
        f'<a href="{esc(a["href"])}">{spanpair(a["label"], b["label"])}</a>'
        for a, b in zip(f_en["explore_links"], f_zh["explore_links"]))
    elsewhere = "\n          ".join(
        f'<a href="{esc(a["href"])}">{spanpair(a["label"], b["label"])}</a>'
        for a, b in zip(f_en["elsewhere_links"], f_zh["elsewhere_links"]))
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
# section builders
# ---------------------------------------------------------------------------

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
        <a class="btn btn-primary" href="index.html#research">{spanpair(h_en["btn_primary"], h_zh["btn_primary"])}</a>
        <a class="btn btn-ghost" href="index.html#about">{spanpair(h_en["btn_secondary"], h_zh["btn_secondary"])}</a>
      </div>
    </div>
  </section>'''


def build_about(en, zh):
    a_en, a_zh = en["about"], zh["about"]
    return f'''  <section class="about" id="about">
    <div class="container">
      {pair("p", "eyebrow", a_en["eyebrow"], a_zh["eyebrow"])}
      {pair("h2", "section-title", a_en["title"], a_zh["title"])}
      <div class="about-body">
        {pair("p", "about-text", a_en["p1"], a_zh["p1"])}
        {pair("p", "about-text", a_en["p2"], a_zh["p2"])}
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
    groups_html = []
    for g_en, g_zh in zip(p_en["groups"], p_zh["groups"]):
        items = []
        for a in g_en["items"]:
            link_html = "".join(
                f'<a href="{esc(lk["href"])}">[ {esc(lk["label"])} ]</a>'
                for lk in a["links"])
            links_div = f'\n            <div class="pub-links">{link_html}</div>' if link_html else ""
            items.append(f'''        <div class="pub">
          <span class="pub-year">{esc(a["year"])}</span>
          <div>
            <h3 class="pub-title">{esc(a["title"])}</h3>
            <p class="pub-meta">{esc(a["authors"])} · <em>{esc(a["journal"])}</em></p>{links_div}
          </div>
        </div>''')
        groups_html.append(f'''      <div class="pub-group">
        {pair("h3", "pub-group-title", g_en["title"], g_zh["title"])}
{chr(10).join(items)}
      </div>''')
    return f'''  <section class="pubs" id="publications">
    <div class="container">
      {pair("p", "eyebrow", p_en["eyebrow"], p_zh["eyebrow"])}
      {pair("h2", "section-title", p_en["title"], p_zh["title"])}

{chr(10).join(groups_html)}

      <a class="more-link" href="{esc(p_en["more_href"])}">{spanpair(p_en["more"], p_zh["more"])}</a>
    </div>
  </section>'''


def build_pi(en, zh):
    pi_en, pi_zh = en["pi"], zh["pi"]
    if pi_en["photo"]:
        photo = f'<img class="photo pi-photo" src="{esc(pi_en["photo"])}" alt="{esc(pi_en["name"])}" />'
    else:
        photo = '<div class="photo pi-photo"><span>[ photo ]</span></div>'
    links = "".join(f'<a href="{esc(lk["href"])}">{esc(lk["label"])}</a>'
                    for lk in pi_en["links"])
    return f'''  <section class="people pi-page" id="pi">
    <div class="container">
      {pair("p", "eyebrow", pi_en["eyebrow"], pi_zh["eyebrow"])}
      <div class="pi">
        {photo}
        <div>
          {pair("h3", "pi-name", pi_en["name"], pi_zh["name"])}
          {pair("p", "pi-role", pi_en["role"], pi_zh["role"])}
          {pair("p", "pi-bio", pi_en["bio"], pi_zh["bio"])}
          <div class="pi-links">{links}</div>
        </div>
      </div>
    </div>
  </section>'''


def build_people(en, zh):
    pe_en, pe_zh = en["people"], zh["people"]

    def photo(src, alt):
        if src:
            return f'<img class="photo member-photo" src="{esc(src)}" alt="{esc(alt)}" />'
        return '<div class="photo member-photo"><span>[ photo ]</span></div>'

    def name_html(name_en, name_zh):
        e, z = name_en.strip(), name_zh.strip()
        if e and z and e != z:
            return f'<span data-en>{esc(e)}</span><span data-zh>{esc(z)}</span>'
        return esc(e or z)

    groups = []
    for g_en, g_zh in zip(pe_en["groups"], pe_zh["groups"]):
        if not g_en["members"]:
            continue
        cards = []
        for a, b in zip(g_en["members"], g_zh["members"]):
            cohort = f'\n          <p class="member-class">{esc(a["cohort"])}</p>' if a.get("cohort") else ""
            note = ""
            if a.get("note"):
                note = "\n          " + pair("p", "member-note", a["note"], b["note"])
            alt = a["name"] or b["name"]
            cards.append(f'''        <div class="member">
          {photo(a["photo"], alt)}
          <h4>{name_html(a["name"], b["name"])}</h4>{cohort}{note}
        </div>''')
        groups.append(f'''      <div class="member-group">
        {pair("h3", "member-group-title", g_en["title"], g_zh["title"])}
        <div class="members">
{chr(10).join(cards)}
        </div>
      </div>''')
    return f'''  <section class="people" id="people">
    <div class="container">
      {pair("p", "eyebrow", pe_en["eyebrow"], pe_zh["eyebrow"])}
      {pair("h2", "section-title", pe_en["title"], pe_zh["title"])}

{chr(10).join(groups)}
    </div>
  </section>'''


def build_teaching(en, zh):
    t_en, t_zh = en["teaching"], zh["teaching"]

    def block(title_en, title_zh, rows_en, rows_zh, kind):
        if not rows_en:
            body = "        " + pair("p", "empty-state", t_en["empty"], t_zh["empty"])
        else:
            lines = []
            for a, b in zip(rows_en, rows_zh):
                if kind == "course":
                    lead = esc(a.get("term", ""))
                else:
                    lead = esc(a.get("year", ""))
                venue = ""
                if a.get("venue"):
                    venue = f' · <em>{esc(a["venue"])}</em>'
                main = (f'<p class="tt-title" data-en>{esc(a["title"])}{venue}</p>\n'
                        f'            <p class="tt-title" data-zh>{esc(b["title"])}{venue}</p>')
                lines.append(f'''        <div class="tt-item">
          <span class="tt-lead">{lead}</span>
          <div>{main}</div>
        </div>''')
            body = "\n".join(lines)
        return f'''      <div class="tt-block">
        {pair("h3", "tt-block-title", title_en, title_zh)}
{body}
      </div>'''

    courses = block(t_en["courses_title"], t_zh["courses_title"],
                    t_en["courses"], t_zh["courses"], "course")
    talks = block(t_en["talks_title"], t_zh["talks_title"],
                  t_en["talks"], t_zh["talks"], "talk")
    return f'''  <section class="pubs" id="teaching">
    <div class="container">
      {pair("p", "eyebrow", t_en["eyebrow"], t_zh["eyebrow"])}
      {pair("h2", "section-title", t_en["title"], t_zh["title"])}

{courses}

{talks}
    </div>
  </section>'''


def build_resources(en, zh):
    r_en, r_zh = en["resources"], zh["resources"]
    intro = ""
    if r_en.get("intro"):
        intro = "\n      " + pair("p", "about-text", r_en["intro"], r_zh["intro"])
    if not r_en["items"]:
        body = "      " + pair("p", "empty-state", r_en["empty"], r_zh["empty"])
    else:
        rows = []
        for a, b in zip(r_en["items"], r_zh["items"]):
            href = a.get("href", "")
            title = (f'<a href="{esc(href)}">{spanpair(a["title"], b["title"])}</a>'
                     if href else spanpair(a["title"], b["title"]))
            desc = ""
            if a.get("desc"):
                desc = "\n        " + pair("p", "res-desc", a["desc"], b["desc"])
            rows.append(f'''      <div class="res-item">
        <h3 class="res-title">{title}</h3>{desc}
      </div>''')
        body = "\n".join(rows)
    return f'''  <section class="pubs" id="resources">
    <div class="container">
      {pair("p", "eyebrow", r_en["eyebrow"], r_zh["eyebrow"])}
      {pair("h2", "section-title", r_en["title"], r_zh["title"])}{intro}

{body}
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
        </div>
        {pair("p", "join-note", j_en["note"], j_zh["note"])}
      </div>
    </div>
  </section>'''


# ---------------------------------------------------------------------------
# page assembly
# ---------------------------------------------------------------------------

def page_body(en, zh, active, sections):
    parts = [build_nav(en, zh, active)]
    parts += sections
    parts.append(build_footer(en, zh))
    return "\n\n".join(parts)


def main():
    en = load("content.en.json")
    zh = load("content.zh.json")
    check_shape(en, zh)

    try:
        with open("template.html", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        sys.exit("ERROR: cannot find template.html (the page skeleton).")

    site_title = en["meta"]["title"]
    desc = en["meta"]["description"]

    pages = [
        ("index.html", "about", None,
         [build_hero(en, zh), build_about(en, zh), build_research(en, zh), build_join(en, zh)]),
        ("pi.html", "pi", en["nav"]["pi"], [build_pi(en, zh)]),
        ("people.html", "people", en["nav"]["people"], [build_people(en, zh)]),
        ("publications.html", "publications", en["nav"]["publications"], [build_pubs(en, zh)]),
        ("teaching.html", "teaching", en["nav"]["teaching"], [build_teaching(en, zh)]),
        ("resources.html", "resources", en["nav"]["resources"], [build_resources(en, zh)]),
        ("news.html", "news", en["nav"]["news"], [build_news(en, zh)]),
    ]

    for filename, active, label, sections in pages:
        title = site_title if label is None else f"{label} · {site_title}"
        body = page_body(en, zh, active, sections)
        html = (template
                .replace("{{TITLE}}", esc(title))
                .replace("{{DESCRIPTION}}", esc(desc))
                .replace("{{BODY}}", body))
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

    n_pubs = sum(len(g["items"]) for g in en["publications"]["groups"])
    n_people = 1 + sum(len(g["members"]) for g in en["people"]["groups"])
    print("Built " + ", ".join(p[0] for p in pages))
    print(f"  {len(pages)} pages | {n_pubs} publications | {n_people} people")

    try:
        from check_bilingual import check_file
        print()
        ok = all(check_file(p[0]) for p in pages)
    except Exception as e:
        print(f"  (auto-check skipped: {e})")
        ok = True

    print()
    if ok:
        print("=" * 52)
        print("  DONE. All pages built.")
        print("  Next: preview index.html, then Commit + Sync in VS Code.")
        print("=" * 52)
    else:
        print("=" * 52)
        print("  PROBLEM found above. Fix the JSON, then Run again.")
        print("=" * 52)
        sys.exit(1)


if __name__ == "__main__":
    main()
