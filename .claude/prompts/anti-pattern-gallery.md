# The anti-pattern gallery

Four habits that cost you an outcome — not tokens, not politeness, not elegance. Each entry names
the failure, shows its shape, states the fix in one line, and points back into the kit at the thing
that addresses it.

Politeness padding is deliberately **not** here. It wastes tokens and costs you nothing, and an
entry like that teaches the room to discount the other four.

---

## 1. Asking for an opinion, then arguing with it

**Leads the gallery because it is the one the room least expects, and the only one that destroys
value rather than wasting time.**

**The shape.** You ask for an assessment. You get one. You disagree — or just push back, or restate
your own view more firmly, or ask "are you sure?" — and the assessment moves toward yours. Push once
more and it arrives.

**What it costs you.** You walked in wanting a second view and walked out with your own view,
returned to you with more confidence than you started with. You now believe it has been
independently checked. It has not. Every later decision rests on a confirmation that was
manufactured by the pressure you applied, and nothing in the conversation records that it happened.

This is worse than never asking. Never asking leaves you knowing you have one opinion.

**The fix, in one line.** Before you push back, ask what evidence would change its mind — and when
it concedes, ask what changed.

**Where the kit addresses it.** `demo-cmd-second-opinion`, which argues against its own prior answer
and must report both what it would change and what it would keep — the structure that makes total
capitulation as visible a failure as total agreement.

---

## 2. Stacked questions

**The shape.** One message carrying four questions — often separated by "also" and "and can you
explain". The answer covers the last one thoroughly, the first one briefly, and silently drops the
two in the middle.

**What it costs you.** Not the dropped answers — you would notice those. It costs you the *belief*
that you asked. You move on thinking all four are settled, and the unasked ones surface later as
surprises, usually in front of someone else. The middle questions are also, reliably, the ones you
were least sure about and most needed answered.

**The fix, in one line.** One question per turn, and when you catch yourself typing "also", start a
new message.

**Where the kit addresses it.** `demo-cmd-askme` and `demo-skill-ask-me`, which turn questioning
into a structured exchange with a capped batch, so nothing gets silently dropped in the middle.

---

## 3. "Be comprehensive"

**The shape.** You ask for everything, on the theory that you can cut what you do not need. You get
everything.

**What it costs you.** You asked for a judgement and received an inventory. The recommendation you
needed is in there, at equal weight with eleven things that do not matter, and the work of ranking
them — which is the work you wanted done — has been handed back to you. Worse, comprehensiveness
reads as rigour, so the output looks more trustworthy precisely where it is least useful. You will
either act on whatever you happen to read first, or you will do the analysis yourself.

**The fix, in one line.** Ask for the shortlist and what was excluded from it, rather than for
everything.

**Where the kit addresses it.** Rung 4, the audience rung, where naming what the reader *does* with
the output forces things to be cut rather than listed — and `demo-skill-scorecard`, which ranks
against stated weights instead of enumerating.

---

## 4. Manufactured urgency

**The shape.** "Urgent", "quickly", "I need this in five minutes", "just give me something" — added
to convey pressure rather than to state a real deadline.

**What it costs you.** The model matches the register. It produces something that reads as finished,
skips the qualifications it would otherwise have raised, and stops asking the questions that would
have slowed you down — which are exactly the questions worth being slowed down by when you are under
real time pressure. You get a confident answer at the moment you are least able to check it, and you
send it on.

**The fix, in one line.** State the deadline as a constraint on scope, not as a mood: say what you
need by when, and let the work be sized to it.

**Where the kit addresses it.** Rung 3, the objective rung, and its warning about false precision —
a stated constraint produces a plan you can inspect, where a conveyed mood produces confidence you
cannot.

---

## Using the gallery

These are habits, not mistakes, which is why naming them once does not remove them. The useful
exercise is to look back at your own last ten prompts and count which of the four you did. Most
people find two of them repeatedly, and the same two each time.
