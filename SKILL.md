---
name: multilingual-readme
description: Generate a polished, multilingual README set (English / 日本語 / 简体中文 / Español / 한국어) that explains a tool in 10 seconds — with badges, a language switcher, a non-engineer explanation, a Mermaid architecture diagram, exactly 3 features, a Before/After table, and per-environment install guides (CLI, AI-IDE, web, source). It inspects the target itself (SKILL.md, package.json, scripts, git remote) instead of asking you to paste specs, includes YAML frontmatter instructions if creating a skill README, and self-verifies output with a checker script. Use this skill whenever the user wants a README, docs, front matter, or a "front page" for a skill, plugin, CLI, library, or app — including requests phrased as "READMEを作って", "多言語化して", "translate the README", "i18n the docs", "GitHubに公開したい", "READMEをもっと分かりやすく", "add a Japanese/Chinese/Korean/Spanish README", "front matterも書いて", or "この機能を人に説明するドキュメントが欲しい" — even if they never say the word "multilingual".
---


# Multilingual README

A README is a landing page, not a manual. A reader decides in ~10 seconds whether to
try the thing or close the tab. This skill produces a README set where that 10 seconds
is enough — in five languages, each of which reads like it was written by a native
developer rather than translated.

## The two failure modes to design against

Almost every bad multilingual README fails in one of two ways. Keep both in view the
whole time:

1. **Fabricated install steps.** The single fastest way to destroy trust is an install
   command that errors out. Never invent a path, package name, or command — derive
   every one of them from the target's actual files, or omit that environment.
2. **Translationese.** Text that is grammatically correct but reads foreign — 直訳,
   over-hanzi-fied Japanese, English words force-translated into Chinese, formal
   Spanish nobody uses in a terminal. A developer who hits this assumes the tool is
   sloppy too. See `references/localization.md`.

## Workflow

### 1. Recon — establish facts before writing a word

Read the target yourself. Ask the user only for what genuinely cannot be found on disk.

Sources, in order of usefulness:

| Source | What you extract |
|---|---|
| `SKILL.md` frontmatter | name, description, trigger contexts |
| `SKILL.md` body | what it actually does, workflow steps, bundled scripts |
| `package.json` | package name, bin, scripts, license, deps, repo URL |
| `plugin.json` / `.claude-plugin/marketplace.json` | plugin name, marketplace install path |
| `scripts/`, `commands/`, `src/` | real entry points and CLI flags |
| existing `README*.md` | prior claims, tone, screenshots to reuse |
| `git remote -v`, `LICENSE` | clone URL, badge for the license |

Assemble a fact sheet before drafting:

- **Name** and **distribution type** (Claude Code skill / plugin / npm package / CLI /
  library / web app) — this determines which install patterns are even valid
- **The value in one sentence** — what the user stops having to do
- **Invocation** — the exact command, slash command, or trigger phrase
- **Requirements** — runtime, API keys, accounts, OS
- **Three strengths** and **the pain they replace** (raw material for Features and Before/After)

If two or more of these are still unknown after reading, ask the user once, in a single
batch, up to three questions. Guessing here is what produces the fabricated-install
failure mode.

### 2. Sharpen the value before drafting

- **Tagline**: state the outcome, not the mechanism. "Turn any repo into a
  presentation-ready site" beats "A Markdown-to-HTML converter." A good test: does the
  line survive if you delete every noun that names a technology?
- **Non-engineer section**: use one concrete analogy from ordinary life. If you cannot
  produce an analogy, you do not yet understand the tool well enough to write about it.
- **Exactly three features.** Three is memorable; six is a list nobody reads. When a
  fourth candidate appears, either fold it into an existing one or cut it. The
  discipline of choosing is what makes the section useful.

### 3. Write English first, then transcreate

English is the canonical file (`README.md`) and the source of truth for structure and
facts. Write it completely, then produce each other language **from the English
meaning**, not by mapping words. Section order, diagram shape, and table rows stay
identical across languages so readers can switch mid-scroll; the prose does not.

Read `references/template.md` for the exact section skeleton and the localized headings.
Read `references/localization.md` before writing any non-English file — it has the
per-language terminology rules, the katakana/hanzi/hangul conventions, and worked
examples of the mistakes to avoid.

Read `references/install-patterns.md` when writing the install section. It contains the
canonical snippets per environment (Pattern A: CLI/terminal, B: AI-integrated IDE,
C: web, D: from source). Include only the environments the target genuinely supports —
a plugin that only exists in a marketplace has no `npm install` line, and pretending
otherwise is the failure mode from the top of this file.

### 4. File naming and the language switcher

```
README.md         ← English, canonical
README.ja.md      ← 日本語
README.zh-CN.md   ← 简体中文
README.es.md      ← Español
README.ko.md      ← 한국어
```

Every file carries the same nav line near the top, with the current language shown in
bold plain text and the others as relative links:

```markdown
[English](README.md) · **日本語** · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [한국어](README.ko.md)
```

Languages are adjustable. If the user wants only English + Japanese, or wants French
added, honor that — generate the requested set and make every nav line list exactly the
files that exist. A link to a README you did not write is a 404 on the project's front
page.

### 5. Verify mechanically — always run the checker

```bash
python3 <skill-dir>/scripts/check_readme.py <target-dir> --langs en,ja,zh-CN,es,ko
```

It checks structure (badges, nav line, tagline, the five required sections, a Mermaid
block, exactly three features, a Before/After table, install subsections with runnable
code fences), resolves every relative link, and runs **script purity** checks — hangul
leaking into the Japanese file, kana in the Chinese file, simplified-only characters in
Japanese, CJK in Spanish. Those are the errors that are invisible to you and glaring to
a native reader.

Fix everything it reports and run it again until it exits clean. Treat a warning as a
question you have to answer, not noise.

### 6. Self-review — read as each native developer

The checker cannot judge naturalness, so do this pass deliberately. For each non-English
file, re-read it as a developer who speaks that language and has never seen the tool,
and check the three things from `references/localization.md`:

1. **Terminology** — is every technical term in the form that language's developers
   actually use? (JA: インストール not 導入設置; ZH: keep CLI/API/React in Latin script;
   KO: 설치 / 터미널; ES: instalación / navegador / consola)
2. **Register** — does it sound like a colleague explaining a tool, or like a manual
   translated by committee?
3. **Comprehension** — can this reader run the install command successfully using only
   this file?

Fixing what you find here is the highest-value work in the whole task. If you want a
genuinely fresh perspective and subagents are available, dispatch one per language with
the instruction "you are a native <language> developer seeing this project for the first
time; list what reads unnaturally and what you could not act on" — but only when the
user has not asked you to avoid subagents.

### 7. Report

Tell the user which files were written, which environments the install section covers
and why any were omitted, and the checker's final result. If you had to assume a fact,
say which one — an unflagged assumption in a README propagates to every reader.

## Non-negotiables (and why)

- **Never invent install steps or URLs.** Omit rather than guess; a missing section
  costs a reader ten seconds, a wrong command costs them their trust.
- **Same structure across languages.** Readers switch language mid-page; a different
  skeleton makes them lose their place.
- **Mermaid instead of screenshots.** Diagrams stay correct after a UI change, render
  natively on GitHub, and cost nothing to localize — the labels get translated too, and
  the checker verifies they did.
- **Three features, no more.** Stated again because the pressure to add a fourth is
  relentless and always wrong.
