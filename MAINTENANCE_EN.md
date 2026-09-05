# RADIUS Lab Website — Maintenance Guide

This guide tells you **where to change what**, how to update, and how to publish.
You barely touch HTML/CSS — day-to-day maintenance is just editing **two data
files** and pressing one button to rebuild.

---

## Contents
1. [30-second quick start](#1-30-second-quick-start)
2. [File overview: what each file does](#2-file-overview)
3. [Core idea: data → rebuild → pages](#3-core-idea)
4. [The daily loop (in VS Code)](#4-the-daily-loop)
5. [Content map: where to edit each section](#5-content-map)
6. [Cookbook: common tasks](#6-cookbook)
7. [Adding photos](#7-adding-photos)
8. [Changing colours & fonts](#8-changing-colours--fonts)
9. [Publishing to GitHub](#9-publishing-to-github)
10. [Golden rules & don'ts](#10-golden-rules--donts)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. 30-second quick start

To change any content, you **only ever do this**:

```
① Open content_en.json (English) and content_zh.json (Chinese); edit the text
② Press ▶ to run build.py        → regenerates all pages
③ Open index.html in a browser    → check it looks right
④ Commit + Sync in VS Code        → site updates in about a minute
```

Live site: **https://radiusncku.github.io/**

---

## 2. File overview

| File | What it does | Do you edit it? |
|------|--------------|-----------------|
| **`content_en.json`** | All **English** content | ✏️ Often |
| **`content_zh.json`** | All **Chinese** content | ✏️ Often |
| `build.py` | Reads the two data files → generates every page | ▶ Run it, don't edit |
| `check_bilingual.py` | Checks that English/Chinese line up | ▶ Run it |
| `template.html` | Page shell (`<head>`, fonts) | Rarely |
| `styles.css` | Colours, fonts, layout | Occasionally (§8) |
| `script.js` | Language toggle, mobile menu, animations | Rarely |
| The 7 `.html` files | **Generated output** | ⚠️ **Never edit by hand** — a rebuild overwrites them |
| `使用手冊.md` / this file | The manual | Reference |

The 7 generated pages: `index.html` (home), `pi.html` (Principal Investigator),
`people.html` (team), `publications.html`, `teaching.html`, `resources.html`,
`news.html`.

> ⚠️ **Never edit those 7 `.html` files directly.** They are machine-generated
> and get overwritten every time you build. Always edit
> `content_en.json` / `content_zh.json` instead.

---

## 3. Core idea

The site keeps **content** and **appearance** separate:

```
content_en.json ┐
content_zh.json ┤─→ (python build.py) ─→ index.html / pi.html / … 7 pages
template.html   ┘
                       ↑ appearance is controlled by styles.css
```

- You maintain the **content** (JSON — like a Python dictionary).
- `build.py` pours the content into the layout and produces the pages.
- **The two JSON files must "look the same"** (same keys, same list lengths).
  For any given field, just put English in one file and Chinese in the other.
- If you add an item to one file but forget the other, `build.py` **stops and
  tells you exactly where they disagree** — it won't produce a broken site.
  That's your safety net.

**Which fields must be identical in both files, and which differ by language?**

- **Identical in both** (language-neutral): `year`, `date`, `term`, link `href`,
  `email`, `photo` path, `cohort` (years enrolled), and **paper title / authors /
  journal** (academic names are not translated).
- **Different in each** (per language): any `title` / `desc` / `text` / `bio` /
  `note`, a person's `name`, and `role`.

---

## 4. The daily loop

All in VS Code, mostly by clicking.

**① Edit** — open `content_en.json` / `content_zh.json` on the left and change text.

**② Rebuild** — open `build.py`, click **▶ Run** (top-right).
When you see `DONE. All pages built.` it worked. If a translation is missing it
tells you in plain words (e.g. "English has 5 items but Chinese has 4"); fix and
run again.

**③ Preview** — right-click `index.html` → **Show Preview** (or open it in a
browser), click through the pages and the **中文/EN** toggle.

**④ Publish** — open the **Source Control** panel (branch icon, or
`Ctrl/Cmd+Shift+G`): type a short message (e.g. "Update June news") → click
**✓ Commit** → click **Sync Changes**. About a minute later
https://radiusncku.github.io/ updates.

> ⚠️ When you Commit, if you **added new pages or photos**, make sure those
> **new files are also staged** before syncing, or they won't go live.

---

## 5. Content map

Below is where each section lives in the JSON. A **path** uses dots for levels;
e.g. `people.groups[1].members` means: the `people` object → the 2nd item of the
`groups` list → its `members`. (Lists start at 0: `[0]` is the first item.)

### 5.1 Site basics — `meta`
Browser-tab title and search description: `meta.title`, `meta.description`.

### 5.2 Navigation labels — `nav`
Button text: `about / research / pi / people / publications / teaching /
resources / news / join`, plus the language button `lang_button`. **Text only** —
where each links to is fixed.

### 5.3 Home hero — `hero`
- `hero.eyebrow`: the small top line (the RADIUS acronym).
- The big title is three parts: `title_before` + `title_accent` (red) +
  `title_after`. e.g. `"Engineering "` + `"Resilience"` + `"."`.
- `hero.subtitle`: the line under the title.
- `hero.btn_primary` / `hero.btn_secondary`: the two button labels.

### 5.4 About — `about`
`about.eyebrow`, `about.title`, `about.p1` (first paragraph), `about.p2`.

### 5.5 Research areas — `research.items` (list)
Each item: `{ "num": "01", "title": "…", "desc": "…" }`.
`num` is identical in both files; `title`/`desc` differ by language. To add or
remove an area, add/delete the whole item (**in both files**).

### 5.6 Principal Investigator — `pi`
- `pi.name` (English in the EN file / Chinese in the ZH file), `pi.role`, `pi.bio`.
- `pi.photo`: photo path (see §7); leave `""` for the grey placeholder.
- `pi.links`: list of `{ "label": "Google Scholar", "href": "https://…" }`.
- `pi.interests`: a **list of strings** (research-interest tags),
  e.g. `["Urban resilience", …]`.
- `pi.education`: list of `{ "years": "", "degree": "…", "place": "…" }`.
- `pi.experience`: list of `{ "years": "", "role": "…", "place": "…" }`.
- Matching headings: `interests_title` / `education_title` / `experience_title`.

### 5.7 Team — `people.groups` (4 groups)
Fixed groups: `groups[0]` = PhD, `groups[1]` = Master's, `groups[2]` =
Undergraduate, `groups[3]` = Alumni. Each group's `members` is a list; each member:

```json
{ "photo": "", "name": "…", "cohort": "202X–202X", "note": "…" }
```

- `name`: **English name in the EN file, Chinese name in the ZH file.** If only
  one exists, leave the other `""` — the site shows whichever is present (so a
  student with only a Chinese name shows it in the English view too).
- `cohort`: years enrolled (identical in both), e.g. `"2024–2026"`.
- `note`: a one-line bio (per language); for alumni, put their current position
  and affiliation here.
- Empty groups (Undergraduate/Alumni) **don't show**; they appear automatically
  once you add someone.

### 5.8 Publications — `publications.groups` (3 groups)
`groups[0]` = journal papers, `groups[1]` = conference papers & posters,
`groups[2]` = technical reports. Each `items` entry:

```json
{
  "year": "2025",
  "title": "Paper title (English, identical in both files, not translated)",
  "authors": "C.-W. Hsu, … & A. Mostafavi",
  "journal": "Journal name",
  "links": [ { "label": "DOI", "href": "https://doi.org/…" } ]
}
```

`links` can hold several (PDF / Code / DOI); use `"links": []` for none.
The "View all" link at the bottom points to `publications.more_href`
(your Google Scholar).

### 5.9 Teaching & invited talks — `teaching`
- `teaching.courses`: each `{ "term": "Fall 2025", "title": "Course name" }`.
- `teaching.talks`: each `{ "date": "2026/06/18", "title": "Talk title",
  "venue": "Host" }`. `title`/`venue` differ by language; `date` is identical.

### 5.10 Resources — `resources.items` (currently empty)
Each `{ "title": "…", "desc": "…", "href": "https://…" }`.
When the list is empty the page shows "coming soon".

### 5.11 News — `news.items`
Each `{ "date": "2026.06", "text": "one line" }`. Newest at the top.

### 5.12 Join us — `join`
`join.title`, `join.text`, `join.email`, `join.note` (recruiting line).

### 5.13 Footer — `footer`
`footer.address` (use `\n` for line breaks), `explore_links`, `elsewhere_links`
(affiliation links), `copyright`.

---

## 6. Cookbook

> Rule of thumb: **copy an existing entry, paste it, change the text — and edit
> BOTH JSON files.**

### Add a Master's student
In `content_en.json` → `people.groups[1].members`, copy an entry and make it:
```json
{ "photo": "", "name": "Wang Xiaoming", "cohort": "2025–2027", "note": "Graduate researcher at the RADIUS Lab." }
```
In `content_zh.json`, the same position:
```json
{ "photo": "", "name": "王小明", "cohort": "2025–2027", "note": "RADIUS 實驗室研究生。" }
```

### Add a journal paper
In both files, add an entry at the top of `publications.groups[0].items`
(title/authors/journal identical, in English):
```json
{ "year": "2026", "title": "…", "authors": "C.-W. Hsu et al.", "journal": "…",
  "links": [ { "label": "DOI", "href": "https://doi.org/…" } ] }
```

### Add a news item
In both files, add to the top of `news.items`; `date` identical, `text` per language.

### Change the email
Search for `chiaweihsu@gs.ncku.edu.tw` and change it in both files (it appears in
`join.email` and in `pi.links` under Email).

### Add a resource link
In both files, add to `resources.items`:
`{ "title": "…", "desc": "…", "href": "https://…" }`.

### Fill in a student's English name / years enrolled
In `content_en.json`, set that member's `name` from `""` to their English
spelling; set `cohort` to the real years (in both files).

Then always: **▶ build → preview → Commit + Sync.**

---

## 7. Adding photos

This is a static site — there's no "upload button". You drop image files into the
folder and reference them by filename.

1. Make an `images/` subfolder in the site folder and put images there
   (e.g. `images/joe.jpg`). Use lowercase names, no spaces; format `.jpg`/`.png`/
   `.webp`; before adding, shrink to ~800–1200px on the long side and under ~200KB.
2. In the JSON, change `photo` from `""` to the path, e.g. for the PI:
   ```json
   "photo": "images/joe.jpg"
   ```
   Members work the same way — set that member's `photo` (put the same path in
   both files).
3. ▶ build. Photos are auto-cropped to fill the frame without distortion.
4. **When you Commit, make sure the `images/` folder is included**, or the site
   can't find the pictures.

---

## 8. Changing colours & fonts

Open `styles.css`; the `:root` block at the very top is the site-wide palette.
Change one value and it updates everywhere:

```css
--phoenix: #E8442F;   /* orange-red accent */
--maroon:  #6E1E2E;   /* NCKU maroon (secondary) */
--cream:   #FAF7F4;   /* light background */
--ink:     #1A1416;   /* dark sections (nav, hero) */
```

`#E8442F` is a hex colour code — pick a new one from any online colour picker and
paste it in. Fonts are the `--font-*` variables just below (best left alone).
Just save the file — no build needed, since `styles.css` isn't generated.

---

## 9. Publishing to GitHub

For routine updates, just **Commit → Sync** in the VS Code Source Control panel
(§4 step ④). About a minute later https://radiusncku.github.io/ updates on its own.

First-time setup (done once) is already complete: the repository
`radiusncku/radiusncku.github.io` exists and Settings → Pages is enabled. You
never need to set that up again.

> Reminder: **new files (new pages, images in `images/`)** must be staged in the
> Commit, or they won't go live.

---

## 10. Golden rules & don'ts

1. **Only edit `content_en.json` / `content_zh.json`**; never hand-edit the 7 `.html` files.
2. **Keep both language files in sync**: add an entry to one, add it to the other.
   `build.py` enforces this for you.
3. **Always ▶ build and preview before publishing**; publish only after you see
   `DONE` and the page looks right.
4. **Valid JSON matters**: commas and quotes must be paired; no trailing comma
   after the last item in a list.
5. Version control is your backup: every version you commit is kept and can be
   restored (see §11).
6. The data files use **underscore** names: `content_en.json` / `content_zh.json`.
   `build.py` finds them automatically — it looks for the underscore names first
   and falls back to the dotted names (`content.en.json`), so either naming works
   and you never have to worry about the filename matching.

---

## 11. Troubleshooting

**`build.py` errors with `not valid JSON`**
→ A typo in one JSON file (extra/missing comma, unpaired quote). The error gives
you the **line number** — fix that line.

**`build.py` says English N vs Chinese M don't match**
→ You added/removed an item in one file but not the other. Make both sides equal.

**In the English view, a student shows their Chinese name**
→ That person's English `name` is still `""`. Fill in the English spelling in
`content_en.json`.

**Text disappears when switching language**
→ The two files are out of sync. Run `python check_bilingual.py *.html`; it points
to the page and line.

**Changed data but the site didn't update**
→ ① Did you ▶ build? ② Did you Commit + Sync? ③ Wait 1–2 min, then hard-refresh
the browser with `Ctrl/Cmd+Shift+R`.

**A photo doesn't appear**
→ ① The `photo` path must exactly match the real filename (including case);
② was the `images/` folder committed?

**A new page gives a 404**
→ That `.html` wasn't committed. Check it exists in the GitHub repo.

**Roll back to an earlier version**
→ GitHub keeps every commit. In the repo, open the file → History, and restore a
working version.

---

## Quick commands (optional)

From the site folder's terminal (or VS Code's integrated terminal):

```bash
python build.py                    # rebuild all pages (same as pressing ▶)
python check_bilingual.py *.html   # check every page's English/Chinese alignment
```

---

*One-line mantra: **copy an existing entry → edit both language files → ▶ build →
preview → publish.***
