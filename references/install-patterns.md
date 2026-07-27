# Install & usage patterns

Read when writing section 🚀. This is the section readers actually act on, so it is the
one where a wrong line does the most damage.

## Contents
- [Rules](#rules)
- [Pattern A — CLI / terminal](#pattern-a--cli--terminal)
- [Pattern B — AI-integrated IDE](#pattern-b--ai-integrated-ide)
- [Pattern C — Web](#pattern-c--web)
- [Pattern D — From source](#pattern-d--from-source)
- [Choosing which patterns to include](#choosing-which-patterns-to-include)
- [Layout](#layout)

---

## Rules

1. **Every command must be derivable from the target's files.** Package name from
   `package.json`, marketplace slug from `.claude-plugin/marketplace.json`, skill
   directory name from the folder on disk, clone URL from `git remote -v`.
2. **If you cannot verify how a tool installs third-party extensions, do not write the
   steps.** Either omit that environment or write one line pointing at the vendor's
   official docs. Readers forgive a gap; they do not forgive a command that fails.
3. **Show the result, not just the command.** One line of "what you should see" turns a
   command into a checkpoint the reader can pass or fail.
4. **Copy-paste safety.** One command per fence line, no `$` prompt prefixes, no
   placeholder the reader might paste literally without noticing — mark them clearly as
   `<your-repo>` and say so.

---

## Pattern A — CLI / terminal

For Claude Code, Gemini CLI, Codex, and anything installed with a package manager.

**Claude Code — personal skill** (available in every project):

```bash
git clone <repo-url> ~/.claude/skills/<skill-name>
```

**Claude Code — project skill** (committed with the repo, shared with the team):

```bash
git clone <repo-url> .claude/skills/<skill-name>
```

Then invoke it in a session:

```
/<skill-name>
```

**Claude Code — plugin marketplace** (only when the repo actually ships
`.claude-plugin/marketplace.json`):

```
/plugin marketplace add <owner>/<repo>
/plugin install <plugin-name>@<marketplace-name>
```

**npm-distributed CLI:**

```bash
npx <package-name>          # try it without installing
npm install -g <package-name>   # or install globally
```

**Python-distributed CLI:**

```bash
pipx install <package-name>
# or: uv tool install <package-name>
```

**Other agent CLIs** (Gemini CLI, Codex, and similar): these tools each have their own
extension mechanism and it changes frequently. Include steps only if the repo itself
documents them or you verified them; otherwise write a single line such as
"Works with any agent that reads `AGENTS.md` — see <vendor docs link>."

---

## Pattern B — AI-integrated IDE

Cursor, VS Code with an AI extension, Antigravity, Windsurf, and similar.

The portable, always-true statement for these environments is the file-based one: most
of them read a project instruction file from the repository root. If the target ships
one (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/*.mdc`, `.github/copilot-instructions.md`),
say which file and where it goes:

```bash
# from the repository root
cp <path>/AGENTS.md ./AGENTS.md
```

Then describe the trigger in prose: "Ask the assistant in the IDE chat, e.g. *Generate
the multilingual README for this repo*."

Do not enumerate per-IDE menu paths from memory. UI navigation is the fastest-rotting
content in any README, and a stale menu path is indistinguishable to the reader from a
broken product.

---

## Pattern C — Web

claude.ai and other browser-based assistants.

Skills are uploaded through the product's settings UI, and the exact menu labels change.
Write the durable parts — how to produce the uploadable artifact — and link to the
vendor's documentation for the upload step itself:

```bash
cd <skill-directory>
zip -r <skill-name>.zip .
```

Then: "Upload `<skill-name>.zip` in your assistant's skill/capability settings — see
<official docs link>."

If the target is a web app rather than a skill, this pattern is instead just the URL and
whatever sign-in the reader needs.

---

## Pattern D — From source

For contributors and for anyone who wants to read the code before trusting it.

```bash
git clone <repo-url>
cd <repo-name>
npm install        # or: pip install -r requirements.txt / uv sync
npm run dev        # or the project's actual entry command
```

List prerequisites explicitly with versions (Node ≥ 18, Python ≥ 3.10, an API key and
where to get it). A prerequisite discovered halfway through an install is a reader lost.

---

## Choosing which patterns to include

| Distribution type | A | B | C | D |
|---|---|---|---|---|
| Claude Code skill (folder) | ✅ | ✅ if it ships AGENTS.md/CLAUDE.md | ✅ zip upload | ✅ |
| Claude Code plugin (marketplace) | ✅ | — | — | ✅ |
| npm / PyPI package | ✅ | — | — | ✅ |
| Library (imported, not run) | — | — | — | ✅ |
| Web app / hosted service | — | — | ✅ URL | ✅ if open source |

An omitted pattern needs no apology in the README, but do tell the user which ones you
left out and why when you report back.

---

## Layout

Use one `###` subsection per environment so the checker can count them and the reader
can jump straight to their own setup. Label each with an emoji and the environment name
in the file's language — for example:

```markdown
### 🖥️ Claude Code (CLI)
### 🧩 Cursor / VS Code
### 🌐 claude.ai (browser)
### 🛠️ From source
```

Keep the reader's own environment findable in under two seconds of scrolling; that is
the whole point of splitting the section.
