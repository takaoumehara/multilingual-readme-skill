#!/usr/bin/env python3
"""Structural and script-purity checker for a multilingual README set.

Usage:
    python3 check_readme.py <dir> [--langs en,ja,zh-CN,es,ko] [--quiet]

Exit code 0 when every check passes (warnings allowed), 1 when anything fails.

The checks fall into three groups:
  structure  - badges, language nav, tagline, the five required sections,
               a Mermaid diagram, exactly three features, a Before/After
               table, install subsections with runnable code
  links      - every relative link resolves to a file that exists
  purity     - characters from the wrong writing system (hangul in the
               Japanese file, kana in the Chinese file, simplified-only
               characters in Japanese, CJK in Spanish), plus untranslated
               bodies and commands that drifted between languages

Purity checks are the point of this script: they catch the errors that are
invisible to the author and glaring to a native reader.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

# --------------------------------------------------------------------------
# language table
# --------------------------------------------------------------------------

LANG_LABELS = {
    "en": "English",
    "ja": "日本語",
    "zh-CN": "简体中文",
    "zh-TW": "繁體中文",
    "es": "Español",
    "ko": "한국어",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "it": "Italiano",
    "ru": "Русский",
    "hi": "हिन्दी",
    "ar": "العربية",
}

# writing-system ranges
RE_KANA = re.compile(r"[ぁ-ゖゝ-ゟァ-ヺー-ヿ]")
RE_HANGUL = re.compile(r"[가-힣ᄀ-ᇿ㄰-㆏]")
RE_CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿]")

# characters whose simplified form differs from the Japanese form, so their
# presence in a Japanese file means Chinese vocabulary leaked in
SIMPLIFIED_ONLY = set(
    "这么们说见关开为应电网页无让该样单选设输运项简语实库图级组络试验记认识请题闭编辑复"
    "务处备术态结构传载执获权释键"
)

REQUIRED_SECTIONS = [
    ("🔰", "non-engineer explanation"),
    ("📐", "architecture diagram"),
    ("✨", "features"),
    ("🔄", "before / after"),
    ("🚀", "install & usage"),
]

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
MARK = {PASS: "✓", WARN: "⚠", FAIL: "✗"}


# --------------------------------------------------------------------------
# parsing helpers
# --------------------------------------------------------------------------

def filename_for(lang: str) -> str:
    return "README.md" if lang == "en" else f"README.{lang}.md"


def split_fences(text: str):
    """Return (text_without_fences, [(info_string, fence_body), ...])."""
    lines = text.split("\n")
    out, fences = [], []
    info, buf, fence_char, fence_len = None, [], "", 0
    for line in lines:
        m = re.match(r"^(\s*)(`{3,}|~{3,})(.*)$", line)
        if m and info is None:
            fence_char, fence_len = m.group(2)[0], len(m.group(2))
            info, buf = m.group(3).strip(), []
            continue
        if info is not None:
            m2 = re.match(r"^\s*(`{3,}|~{3,})\s*$", line)
            if m2 and m2.group(1)[0] == fence_char and len(m2.group(1)) >= fence_len:
                fences.append((info, "\n".join(buf)))
                info = None
                continue
            buf.append(line)
            continue
        out.append(line)
    if info is not None:  # unterminated fence
        fences.append((info, "\n".join(buf)))
    return "\n".join(out), fences


def strip_noise(text: str) -> str:
    """Remove inline code, URLs and link targets — the parts that are
    legitimately Latin-script (or legitimately foreign) in every language."""
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"\]\([^)\s]*\)", "]( )", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    return text


def headings(text: str):
    """[(level, title, line_index)] for ATX headings outside fences."""
    result = []
    for i, line in enumerate(text.split("\n")):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            result.append((len(m.group(1)), m.group(2).strip(), i))
    return result


def section_body(text: str, anchor: str) -> str | None:
    """Body of the section whose heading contains `anchor`, up to the next
    heading of the same or higher level."""
    lines = text.split("\n")
    hs = headings(text)
    for idx, (level, title, line_no) in enumerate(hs):
        if anchor in title:
            end = len(lines)
            for level2, _t, line_no2 in hs[idx + 1:]:
                if level2 <= level:
                    end = line_no2
                    break
            return "\n".join(lines[line_no + 1:end])
    return None


def command_lines(fences) -> set:
    """Runnable-looking lines from non-mermaid fences."""
    cmds = set()
    for info, body in fences:
        if info.lower().startswith("mermaid"):
            continue
        for line in body.split("\n"):
            s = line.strip()
            if not s or s.startswith("#") or s.startswith("//") or s.startswith("<!--"):
                continue
            if s.startswith("|") or s.startswith(">"):
                continue
            cmds.add(s)
    return cmds


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

class Report:
    def __init__(self, name: str):
        self.name = name
        self.rows = []

    def add(self, level, check, message=""):
        self.rows.append((level, check, message))

    @property
    def failed(self):
        return any(r[0] == FAIL for r in self.rows)

    @property
    def warned(self):
        return sum(1 for r in self.rows if r[0] == WARN)


def check_file(directory, lang, langs, en_data, quiet):
    path = os.path.join(directory, filename_for(lang))
    rep = Report(filename_for(lang))

    if not os.path.isfile(path):
        rep.add(FAIL, "file exists", f"{path} not found")
        return rep, None

    with open(path, encoding="utf-8") as fh:
        raw = fh.read()

    nofence, fences = split_fences(raw)
    lines = raw.split("\n")
    head = lines[:25]

    # --- title -------------------------------------------------------------
    first = next((l for l in lines if l.strip()), "")
    if first.startswith("# "):
        rep.add(PASS, "title", first.strip()[:60])
    else:
        rep.add(FAIL, "title", "first non-empty line is not an H1")

    # --- badges ------------------------------------------------------------
    badges = sum(l.count("img.shields.io") for l in lines[:20])
    if badges >= 2:
        rep.add(PASS, "badges", f"{badges} found")
    elif badges == 1:
        rep.add(WARN, "badges", "only 1 badge; 2-4 reads as more established")
    else:
        rep.add(FAIL, "badges", "no shields.io badge in the first 20 lines")

    # --- language nav ------------------------------------------------------
    nav_idx, nav_line = None, ""
    for i, line in enumerate(head):
        if sum(1 for l2 in langs if l2 != lang and filename_for(l2) in line) >= 1:
            nav_idx, nav_line = i, line
            break
    if nav_idx is None and len(langs) > 1:
        rep.add(FAIL, "language nav", "no line linking to the other languages")
    elif len(langs) > 1:
        missing = [l2 for l2 in langs if l2 != lang and filename_for(l2) not in nav_line]
        label = LANG_LABELS.get(lang, lang)
        if missing:
            rep.add(FAIL, "language nav", "missing links: " + ", ".join(missing))
        elif re.search(r"\[[^\]]*" + re.escape(label) + r"[^\]]*\]\(", nav_line):
            rep.add(FAIL, "language nav",
                    f"current language ({label}) is a link; it should be bold plain text")
        elif label not in nav_line:
            rep.add(WARN, "language nav", f"current language label ({label}) not shown")
        else:
            rep.add(PASS, "language nav", f"{len(langs)} languages listed")
    else:
        rep.add(PASS, "language nav", "single-language set")

    # --- tagline -----------------------------------------------------------
    if any(l.strip().startswith(">") for l in lines[:30]):
        rep.add(PASS, "tagline", "blockquote present near the top")
    else:
        rep.add(FAIL, "tagline", "no `> ...` value statement in the first 30 lines")

    # --- required sections -------------------------------------------------
    titles = " | ".join(t for _l, t, _i in headings(nofence))
    missing = [f"{a} ({name})" for a, name in REQUIRED_SECTIONS if a not in titles]
    if missing:
        rep.add(FAIL, "sections", "missing: " + ", ".join(missing))
    else:
        rep.add(PASS, "sections", "all 5 anchors present")

    # --- mermaid -----------------------------------------------------------
    mermaid = [b for info, b in fences if info.lower().startswith("mermaid")]
    if not mermaid:
        rep.add(FAIL, "mermaid diagram", "no ```mermaid block")
    else:
        rep.add(PASS, "mermaid diagram", f"{len(mermaid)} block(s)")
        pattern = {"ja": RE_KANA, "ko": RE_HANGUL, "zh-CN": RE_CJK, "zh-TW": RE_CJK}.get(lang)
        if pattern and not any(pattern.search(b) for b in mermaid):
            rep.add(WARN, "mermaid localized",
                    "diagram labels appear untranslated for this language")

    # --- features: exactly three -------------------------------------------
    feat = section_body(nofence, "✨")
    if feat is None:
        rep.add(FAIL, "3 features", "no ✨ section")
    else:
        n = len(re.findall(r"^#{3,4}\s+\S", feat, re.M))
        if n == 0:
            n = len(re.findall(r"^\s*[-*]\s+\S", feat, re.M))
        if n == 0:
            n = len(re.findall(r"^\*\*\S", feat, re.M))
        if n == 3:
            rep.add(PASS, "3 features", "exactly 3")
        else:
            rep.add(FAIL, "3 features", f"found {n}; the section must hold exactly 3")

    # --- before / after table ----------------------------------------------
    ba = section_body(nofence, "🔄")
    if ba is None:
        rep.add(FAIL, "before/after", "no 🔄 section")
    else:
        rows = [l for l in ba.split("\n")
                if l.strip().startswith("|") and not re.match(r"^\s*\|[\s|:-]+\|\s*$", l)]
        if len(rows) >= 4:
            rep.add(PASS, "before/after", f"{len(rows) - 1} comparison rows")
        elif len(rows) >= 2:
            rep.add(WARN, "before/after", f"only {len(rows) - 1} rows; 3+ makes the case")
        else:
            rep.add(FAIL, "before/after", "no comparison table")

    # --- install section ---------------------------------------------------
    inst = section_body(raw, "🚀")
    if inst is None:
        rep.add(FAIL, "install section", "no 🚀 section")
    else:
        subs = len(re.findall(r"^#{3,4}\s+\S", inst, re.M))
        code = len(re.findall(r"^\s*(?:`{3,}|~{3,})", inst, re.M)) // 2
        if subs == 0:
            rep.add(FAIL, "install section", "no per-environment subsections")
        elif subs == 1:
            rep.add(WARN, "install section", "only 1 environment covered")
        else:
            rep.add(PASS, "install section", f"{subs} environments")
        if code == 0:
            rep.add(FAIL, "install commands", "no code block a reader can copy")
        else:
            rep.add(PASS, "install commands", f"{code} code block(s)")

    # --- relative links ----------------------------------------------------
    broken = []
    for target in re.findall(r"\]\(([^)\s]+)\)", nofence):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        rel = target.split("#")[0]
        if rel and not os.path.exists(os.path.join(directory, rel)):
            broken.append(target)
    if broken:
        rep.add(FAIL, "relative links", "broken: " + ", ".join(sorted(set(broken))[:5]))
    else:
        rep.add(PASS, "relative links", "all resolve")

    # --- script purity -----------------------------------------------------
    nav_files = tuple(filename_for(l2) for l2 in langs)
    body = "\n".join(l for i, l in enumerate(lines)
                     if i != nav_idx and not any(f"]({f})" in l for f in nav_files))
    body, _ = split_fences(body)
    body = strip_noise(body)

    kana = RE_KANA.findall(body)
    hangul = RE_HANGUL.findall(body)
    cjk = RE_CJK.findall(body)
    simplified = [c for c in body if c in SIMPLIFIED_ONLY]

    def purity(level, condition, message):
        if condition:
            rep.add(level, "script purity", message)
            return True
        return False

    dirty = False
    if lang in ("en", "es"):
        dirty |= purity(FAIL, kana, f"kana in a {lang} file: {''.join(sorted(set(kana))[:8])}")
        dirty |= purity(FAIL, hangul, f"hangul in a {lang} file: {''.join(sorted(set(hangul))[:8])}")
        dirty |= purity(FAIL, cjk, f"CJK in a {lang} file: {''.join(sorted(set(cjk))[:8])}")
    elif lang == "ja":
        dirty |= purity(FAIL, hangul, f"hangul in the Japanese file: {''.join(sorted(set(hangul))[:8])}")
        dirty |= purity(FAIL, simplified,
                        "simplified-Chinese characters in Japanese: "
                        + "".join(sorted(set(simplified))[:8]))
        dirty |= purity(WARN, len(kana) < 20, f"only {len(kana)} kana; likely untranslated")
    elif lang in ("zh-CN", "zh-TW"):
        dirty |= purity(FAIL, kana, f"kana in the Chinese file: {''.join(sorted(set(kana))[:8])}")
        dirty |= purity(FAIL, hangul, f"hangul in the Chinese file: {''.join(sorted(set(hangul))[:8])}")
        dirty |= purity(WARN, len(cjk) < 60, f"only {len(cjk)} hanzi; likely untranslated")
    elif lang == "ko":
        dirty |= purity(FAIL, kana, f"kana in the Korean file: {''.join(sorted(set(kana))[:8])}")
        dirty |= purity(WARN, len(hangul) < 40, f"only {len(hangul)} hangul; likely untranslated")
    else:
        dirty |= purity(WARN, kana or hangul,
                        "kana or hangul in a file that should not contain them")
    if not dirty:
        rep.add(PASS, "script purity", "no characters from the wrong writing system")

    # `body` already has the nav line, fences and URLs removed, so two files
    # that differ only by their language switcher still count as untranslated
    data = {"body": re.sub(r"\s+", " ", body).strip(), "cmds": command_lines(fences)}

    # --- cross-file checks against English ---------------------------------
    if lang != "en" and en_data:
        if data["body"] and data["body"] == en_data["body"]:
            rep.add(FAIL, "translated", "body is identical to the English file")
        else:
            rep.add(PASS, "translated", "differs from the English file")
        missing_cmds = sorted(en_data["cmds"] - data["cmds"])
        if missing_cmds:
            rep.add(WARN, "identifier integrity",
                    f"{len(missing_cmds)} command line(s) differ from English, e.g. "
                    + " / ".join(missing_cmds[:3]))
        else:
            rep.add(PASS, "identifier integrity", "commands match English byte-for-byte")

    return rep, data


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Check a multilingual README set.")
    ap.add_argument("directory", help="directory holding the README files")
    ap.add_argument("--langs", default="en,ja,zh-CN,es,ko",
                    help="comma-separated language codes (default: en,ja,zh-CN,es,ko)")
    ap.add_argument("--quiet", action="store_true", help="show only warnings and failures")
    args = ap.parse_args()

    directory = os.path.abspath(args.directory)
    langs = [l.strip() for l in args.langs.split(",") if l.strip()]
    if "en" in langs:
        langs = ["en"] + [l for l in langs if l != "en"]

    reports, en_data = [], None
    for lang in langs:
        rep, data = check_file(directory, lang, langs, en_data, args.quiet)
        if lang == "en":
            en_data = data
        reports.append(rep)

    fails = warns = 0
    for rep in reports:
        print(f"\n── {rep.name} " + "─" * max(0, 56 - len(rep.name)))
        for level, check, message in rep.rows:
            if args.quiet and level == PASS:
                continue
            print(f"  {MARK[level]} {check:<22} {message}")
        fails += sum(1 for r in rep.rows if r[0] == FAIL)
        warns += rep.warned

    print("\n" + "─" * 60)
    if fails:
        print(f"FAIL — {fails} failure(s), {warns} warning(s). Fix and re-run.")
        return 1
    if warns:
        print(f"PASS with {warns} warning(s). Answer each one before shipping.")
        return 0
    print("PASS — all checks clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
