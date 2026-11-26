# Design notes: life-stage-scan

## Problem

People ask AI assistants "where am I in life?" and "what should I do next?" all the time. The usual answer has three weaknesses:

1. **It believes the self-description.** "I value creativity" gets taken at face value, even when the person's week says otherwise.
2. **It reads one layer.** Situation, temperament, goals and life story get blended into a single summary, so the contradictions, which usually hold the real insight, disappear.
3. **It returns a generic plan.** Gratitude journals, morning routines, 90-day goals: advice that could be pasted into anyone's reading.

## Prior work

| What exists | What it does well | Gap this skill fills |
|---|---|---|
| Copy-paste "life audit" prompts (newsletters, prompt libraries, creator prompt packs) | Fast, structured: themes, patterns, a 90-day plan | Single pass over self-report; no follow-up on contradictions; no evidence labels |
| Human career counseling (e.g. Savickas's Career Construction Interview) | Deep narrative questions; a trained listener | Needs a counselor; not available on demand. This skill borrows the question types, not the clinical method |
| Coaching tools (wheel of life, values card sorts) | Easy snapshot of life areas | Measures satisfaction per area, not stage, story or tensions |
| *Designing Your Life* workshops (odyssey plans, prototyping) | Generating alternative paths; small experiments | Doesn't read the person first; this skill uses odyssey plans after the reading |
| Narrow assistant skills (standing in one field; choosing a project) | Depth on one question | This skill hands off to them for those questions |

## What's different

- **A tension engine.** Six layers are read separately, then compared. The reading centers on the one or two tensions that explain the most.
- **Evidence labels and confidence.** Every claim is marked [said], [shown] or [read], with low, medium or high confidence. Meaning-making claims rarely go above medium.
- **Falsifiers.** Each reading ends with what would change it, which invites correction instead of acceptance.
- **Readiness-matched plans.** A goal still at the "thinking about it" stage gets an information-producing experiment, not a commitment.
- **Contribution at every stage.** It finds a person's rare combination and the people one step behind them, so contributing doesn't wait for being established.
- **Grounded fun.** Romanticizing builds on savoring research and the original, everyday sense of ikigai. Style reasons from contrast, value and undertone, and says plainly when a popular method has weak evidence.
- **The world is checked.** Current programs, prices and rules are searched before they're recommended, and contribution ideas are checked against existing work.

## Design decisions and trade-offs

- **Questions in rounds of about five, not a form.** Long forms get autopilot answers. The cost is more back-and-forth; the quick-read mode exists for people who want speed.
- **No personality-type labels.** The skill describes behavior in plain terms ("you recharge alone after people-heavy days") instead of assigning types. Labels the person brings are respected.
- **One primary move.** "Advance one, maintain the rest." Plans that improve everything at once are abandoned. The trade-off is that some areas deliberately stay at maintenance.
- **Progressive disclosure.** `SKILL.md` holds the workflow and boundaries, which are always loaded. Question bank, layer details, texture modules, templates and sources load only when a step needs them.
- **Document output for full scans.** A full reading is something to return to, so it goes into a document where the environment supports one. Quick reads stay in chat.

## Known limitations

- **Not validated.** There is no study showing these readings are accurate or helpful. The evals check structure and safety behaviors, not life outcomes.
- **Self-report.** The skill can only read what the person shares. It asks for behavior to reduce this bias, but can't verify anything.
- **Western-centric lenses.** Super, Kegan, McAdams and Savickas built their work mostly on Western, largely US samples. The skill mitigates this by treating obligations as possibly chosen values and by naming the risk, but doesn't remove it.
- **Kegan without the interview.** Orders of mind can't be reliably assessed informally. The layer is kept because naming what someone can't yet see is valuable, but it's always low-to-medium confidence.
- **Sycophancy risk.** Language models tend to flatter. The skill includes a flattery check and requires at least one uncomfortable observation, but users should still push back.
- **Subjective modules.** Style and romanticizing ideas are taste. They are tied to the person's own story to stay relevant, but there's no right answer to grade them against.

## Evaluation

Current evals (`life-stage-scan/evals/`) test behaviors that can be checked objectively:

| Case | Checks |
|---|---|
| `thin-context-asks-first` | asks a short numbered round before reading; low-friction framing |
| `rich-context-full-reading` | chapter, evidence labels, a grounded tension, three scored paths, one primary move, horizons, falsifiers, specific romanticize ideas |
| `style-no-body-change` | no weight or body-change advice; style statement; honest color-analysis framing; budget-aware |
| `distress-sets-framework-down` | drops the framework, responds to the person, points to support, no diagnosis |
| `current-facts-checked` | searches before naming programs or funding; contribution from current position |

**Next steps for evaluation:**

1. Run the evals with and without the skill and report the pass-rate difference.
2. Collect blind ratings from five to ten real users. Two questions: "how accurate was the reading?" and "did you act on the next move within a week?"
3. Check consistency: run the same input several times and see whether the core tension and next move stay stable.

## Roadmap

- **Re-read mode improvements:** structured comparison against a previous reading.
- **Optional check-in template:** a monthly prompt for the re-read.
- **Localization notes:** life-phase markers and obligations differ by culture; add guidance per region where users provide it.
