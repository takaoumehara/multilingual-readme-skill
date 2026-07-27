# Localization rules

Read before writing any non-English file, and again during the self-review pass.

## Contents
- [The principle](#the-principle)
- [Shared glossary](#shared-glossary)
- [日本語](#日本語)
- [简体中文](#简体中文)
- [한국어](#한국어)
- [Español](#español)
- [Self-review rubric](#self-review-rubric)

---

## The principle

You are not translating; you are rewriting the same argument for a different reader.
The facts, the structure, and the three features stay identical. The sentences are
built fresh in the target language.

The tell of a translated README is that every sentence maps 1:1 to an English one. Real
documentation in each language has its own rhythm — Japanese docs use shorter clauses
and more カタカナ, Chinese docs keep English technical terms in Latin script, Spanish
docs prefer the impersonal or the informal "tú" depending on register but never the
stiff "usted debe" of a legal notice.

**One thing that never varies: technical identifiers.** Command names, flags, file
paths, environment variables, package names, and code inside backticks stay byte-identical
across all five files. A reader who copies `npm install foo` from the Korean README must
get the same string as the English one.

---

## Shared glossary

Latin-script terms that stay untranslated in **every** language (translating them makes
the text harder to read, not easier): CLI, API, MCP, IDE, SDK, LLM, AI, JSON, YAML,
Markdown, Git, GitHub, npm, Node.js, Python, React, Next.js, Firebase, Docker, QR,
URL, UI, UX, Claude Code, Cursor, VS Code, Gemini CLI, Codex.

---

## 日本語

### Katakana is the default for technical vocabulary

Japanese developers read katakana loanwords faster than the "correct" kanji compounds,
which read like a 1990s government translation. Forcing kanji is the single most common
way an AI-written Japanese README announces itself.

| Use this | Not this |
|---|---|
| インストール | 導入設置 / 据置 |
| ツール | 道具 |
| ブラウザ | 閲覧器 |
| エンジニア / 開発者 | 技術者（文脈次第で可、ただし堅い） |
| ダイアグラム / 図 | 図表化 |
| システム | 体系 |
| ターミナル | 端末（可だが硬い。CLI 文脈ではターミナル） |
| コマンド | 命令 |
| ファイル / フォルダ | 書類 / 書類入れ |
| セットアップ | 初期設定（可。ただしセットアップの方が自然） |
| リポジトリ | 保管庫 |
| プロンプト | 指示文 |
| ワークフロー | 作業手順（可。長い説明ではワークフロー） |

### Register

Plain 敬体 (です・ます) for prose; 体言止め or 常体 for table cells and bullet fragments —
mixing them inside one sentence is what feels off. Second person is usually dropped
entirely: 「あなたのプロジェクトをスキャンします」→「プロジェクトをスキャンします」.

### Never let Chinese leak in

The failure looks like this — text that is "Japanese-shaped" but built from Chinese
vocabulary or simplified characters:

| ✗ Wrong | ✓ Natural Japanese |
|---|---|
| 我来整理します | 整理します |
| 首先、インストールします | まず、インストールします |
| 你的プロジェクト | プロジェクト |
| 可以実行できます | 実行できます |
| 这は何ですか | これは何ですか |
| 設定を完了后 | 設定が完了したら |

Simplified-only characters — 这么们说见关开为应电网页无让该样单选设输运项简语实库图级组络试验记认识请题闭编辑复务处备术态结构传载执获权释键 — must never appear
in the Japanese file. The checker script fails the build on these.

---

## 简体中文

### Keep English technical terms in Latin script

Chinese developer docs do not translate CLI, API, MCP, IDE, React, Firebase, or product
names. Writing 命令行界面 instead of CLI reads like a textbook, not like a repo.

| Use this | Not this |
|---|---|
| 安装 | インストール（kana must never appear） |
| 浏览器 | 网页浏览工具 |
| 终端 | 终端机 |
| 运行 / 执行 | 跑 (too colloquial for a README) |
| 配置 | 设定 (acceptable, 配置 is more common in docs) |
| 仓库 / repo | 存储库 (works, 仓库 is what developers say) |
| 依赖 | 依赖项 (both fine) |
| 开箱即用 | 立即可用 |

### Register

Concise declaratives. 无需配置、一条命令即可完成 reads well; long subordinate chains do
not. Avoid 您 in a developer README — it is over-formal; drop the pronoun or use 你.

No hiragana, no katakana, no hangul anywhere in the file.

---

## 한국어

### Loanword vs native word — pick by convention, not by rule

Korean developer docs mix Sino-Korean and English loanwords in a settled pattern. Use
the settled form; do not "purify".

| Use this | Not this |
|---|---|
| 설치 | 인스톨 |
| 실행 | 런 |
| 터미널 | 단말기 |
| 엔지니어 / 개발자 | 기술자 |
| 브라우저 | 웹 열람기 |
| 저장소 / 리포지토리 | 보관소 |
| 명령어 | 커맨드 (허용되나 명령어가 표준) |
| 설정 | 세팅 (구어체) |

### Register

해요체 is too casual for docs and 하십시오체 too stiff; use **합니다체** (…합니다 / …입니다)
for prose and noun-ending fragments for table cells and bullets. Spacing (띄어쓰기) errors
are the loudest sign of machine translation — `설치 방법`, `한 번에`, `할 수 있습니다` are
each spaced as shown.

No kana anywhere. Hanja only in the rare fixed term.

---

## Español

### Write like a developer, not like a manual

| Use this | Not this |
|---|---|
| instalación / instalar | procedimiento de instalación |
| navegador | explorador de internet |
| consola / terminal | símbolo del sistema |
| ejecutar | correr (calque of "run") |
| archivo / carpeta | fichero (Spain-only; archivo travels better) |
| repositorio | almacén |
| entorno | ambiente (acceptable in LatAm, entorno is neutral) |
| requisitos previos | prerrequisitos |

### Register

Neutral, non-regional Spanish. Imperative for steps (`Ejecuta este comando`), impersonal
for description (`Se genera un archivo…`). Avoid "usted" — modern developer docs use
tú or drop the subject entirely. Keep the inverted opening marks: ¿ and ¡.

No CJK characters anywhere except in the language nav line.

---

## Self-review rubric

Run this per language after the checker script passes. Score honestly; anything below
"yes" is rework, and rework here is cheap compared to a reader bouncing.

1. **Terminology** — Is every technical term in the form that language's developers
   actually type? Scan specifically for words from the tables above.
2. **Register** — Read three consecutive sentences aloud. Do they sound like a colleague
   explaining a tool, or like a form letter?
3. **Comprehension** — Could this reader install and run the tool using only this file,
   without opening the English one?
4. **Identifier integrity** — Are all commands, paths, and flags byte-identical to the
   English file?
5. **Diagram** — Are the Mermaid labels in this language, and does the diagram still
   make sense with the translated labels (no overflow, no broken syntax)?
6. **The 10-second test** — Cover everything below the tagline. Does a reader now know
   what this is and whether they want it?
