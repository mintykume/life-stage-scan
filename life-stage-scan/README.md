# life-stage-scan

A skill for Claude that reads where someone is in life, in layers, and turns the reading into their smartest next move, a way to contribute from where they stand, ideas to romanticize everyday life, a personal style direction, and a plan.

It follows the open [Agent Skills format](https://agentskills.io/specification), so it works in claude.ai, the Claude desktop app, Claude Code, and other agents that support skills.

## What's in this repo

```
life-stage-scan/              ← this repository
├── life-stage-scan/          ← the skill itself: this folder is what gets installed
│   ├── SKILL.md              ← the instructions Claude follows
│   ├── references/           ← detail Claude opens only when a step needs it
│   └── evals/                ← test cases (left out of the download)
├── docs/DESIGN.md            ← why it's built this way, prior work, limitations
├── tools/                    ← validate.py and package.sh
├── README.md, LICENSE, CHANGELOG.md
└── .github/workflows/        ← checks every push, builds the download on each release
```

The inner `life-stage-scan/` folder has the same name as the repo on purpose: Claude requires the skill's folder name to match its `name`.

## Install

**claude.ai or the Claude desktop app**

1. Open this repo's **Releases** page and download **`life-stage-scan.zip`**.
2. In Claude, go to **Customize → Skills → + → Create skill → Upload a skill** and choose the ZIP.
3. Make sure code execution and file creation is turned on in **Settings → Capabilities**.

Don't use GitHub's green **Code → Download ZIP** button for this. That ZIP wraps everything in a `life-stage-scan-main/` folder, which Claude won't recognize as a skill.

**Claude Code**

Clone this repository, then copy the skill folder into your skills directory:

```bash
cp -r life-stage-scan ~/.claude/skills/
```

Or unzip the release ZIP into `~/.claude/skills/`. Then ask naturally ("where am I in life?") or type `/life-stage-scan`.

## What it does

You ask something like *"scan me: where am I in life and what should I do next?"* The skill then works in three stages.

**1. It asks questions in rounds.** About five at a time, not a 30-item form:

- **Snapshot:** your situation and constraints.
- **Deep scan:** role models, the stories you love, envy, where your free time and money really go, whose voice decides.
- **Threads:** the contradictions it noticed in your answers.

**2. It reads six layers.**

| Layer | Question it answers | Lens |
|---|---|---|
| Season & situation | What roles and transition are you in? | Super's life-span, life-space theory; Bridges' transitions |
| Build | How are you wired for energy and pace? | McAdams level 1 (traits), read from behavior |
| Strivings | What are you reaching for, and how ready are you? | McAdams level 2; stages of change; career capital |
| Meaning-making | Whose standards run the show? | Kegan's orders of mind (light-touch hypothesis) |
| Story | What story do you tell, and whose script is it? | McAdams level 3 (narrative identity); Savickas's life themes |
| Tensions | Where do the layers disagree? | Where the real stage usually shows |

**3. It turns the reading into action.**

- A chapter name and one core tension.
- Three paths, scored on fit, compounding, reversibility, contribution, aliveness and cost.
- One best next move, with everything else kept at a minimum.
- How you can contribute from your current stage.
- Life texture: romanticize (grounded in savoring research), personal style, things to explore.
- A plan: today, this week, 30 days, 90 days, this year.

Every claim is labeled **[said]** (you told it), **[shown]** (behavior you described) or **[read]** (its inference), with a confidence level. Each reading ends with *what would change this reading*, so you can correct it.

A full example with an invented person: [`life-stage-scan/references/example-reading.md`](life-stage-scan/references/example-reading.md).

## Try it

- "Do a deep scan of me — where am I in life and what's my smartest next move?"
- "I feel stuck between chapters. Quick read, please."
- "I just started my first real job and still dress like a student. Style me for who I'm becoming."
- "Re-read me — here's what happened since last month."

## Why it exists

Most AI "life audit" prompts take self-description at face value and return a generic 90-day plan. This skill treats what you say, what you do and the story you tell as separate evidence, and pays most attention to where they disagree. Prior work, design decisions and limitations are in [`docs/DESIGN.md`](docs/DESIGN.md).

## Limitations and safety

- **Not therapy, diagnosis or a validated assessment.** The frameworks are lenses for noticing, not instruments. Kegan's stages in particular need a trained interviewer; here they're a low-confidence hypothesis.
- **Self-report.** Every reading depends on what you share. The skill asks about behavior, not just opinions, but it can't verify either.
- **Cultural bias.** Most of the frameworks come from Western, largely US research. The skill treats family, faith and community obligations as possibly chosen values, not as immaturity, but it can still misread.
- **Uneven evidence.** Some ideas are well supported (savoring, stages of change, narrative identity); some are popular with weak evidence (seasonal color analysis), and the skill says so. See [`references/sources.md`](life-stage-scan/references/sources.md).
- **Distress.** If someone is in crisis, the skill drops the framework, responds to the person and points to real support.
- **Privacy.** Readings contain personal details. Don't commit your own readings to a public repo; a `readings/` folder is git-ignored for that reason.

## Tests

Five test cases live in [`life-stage-scan/evals/`](life-stage-scan/evals). Each has a realistic prompt and statements describing a good result:

- asks before reading
- produces the full reading structure with evidence labels
- gives no body-change styling advice
- steps back during distress
- searches before naming real programs

To run them with Claude Code (v2.1.269 or later):

```bash
cd life-stage-scan
claude plugin eval . --allow-tools WebFetch
```

These are real, paid model runs. Each case runs with and without the skill so you can compare.

## Maintaining

Before each commit:

```bash
python3 tools/validate.py     # frontmatter, file references, test cases
bash tools/package.sh         # builds dist/life-stage-scan.zip, the upload file
```

To release a new version:

1. Bump `metadata.version` in `life-stage-scan/SKILL.md`.
2. Add a `CHANGELOG.md` entry.
3. Tag and push:

   ```bash
   git tag v1.1.0 && git push --tags
   ```

The workflow then creates a GitHub Release with `life-stage-scan.zip` attached. If you use the skill on claude.ai, delete the old upload before adding the new one, so you don't end up with two.

## License

[MIT](LICENSE). The skill references published research and books; full citations are in [`references/sources.md`](life-stage-scan/references/sources.md). Not affiliated with Anthropic.
