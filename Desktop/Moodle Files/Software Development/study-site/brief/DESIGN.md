# Design system

The user's words: "clean development, no mistakes, a full-on learning platform, no AI crappy site defaults or clichés,
actually well designed and easy to use". This is a tool a student will use for hours a day for eight days, on a laptop
and on a phone. It must feel calm, fast and exact, like good engineering documentation, not like a marketing page.

## Concept
A lab manual with a check runner. The subject's own world supplies the visual language:
- CI checks: module and section status shown as check rows (pending ○, passing ✓, failing ✗), the way GitHub Actions lists
  ruff / mypy / pytest. Status = the student's recent accuracy on that section's questions.
- pytest's summary line: exam results read `14 passed, 3 failed, 2 to mark in 52m10s` with the pass/fail words coloured.
- Diffs: added/removed lines tinted, `@@` hunk headers muted, commit hashes in mono.
- Terminal transcripts: `$ ` prompt muted, output plain, exit code chips (`exit 0`, `exit 1`).
- The real exam is pen and paper; exam mode looks like a clean answer paper: question numbers in the margin (Q7), parts
  1. 2. 3., a lined area that grows, the number of handwritten lines estimated as you type.

## Tokens (write exactly this shape at the top of app/styles.css; you may tune values for contrast, keep the roles)
```css
/* Layout: left rail of modules as a check list, one reading column (~68ch), margin notes at ≥1200px, bottom tab bar on phones */
:root {
  --paper:   #F2F4F6;   /* page ground: cool steel-tinted neutral */
  --sheet:   #FFFFFF;   /* reading surfaces, question sheets */
  --ink:     #15202B;   /* text */
  --ink-2:   #4A5664;   /* secondary text */
  --ink-3:   #7A8592;   /* captions, muted */
  --rule:    #D9DEE4;   /* hairlines */
  --signal:  #C8410E;   /* the one accent: git-orange; links, focus, current item, primary action */
  --signal-ink: #FFFFFF;
  --pass:    #1E7A3C;   --pass-bg: #E6F4EA;   /* semantic, never decorative */
  --fail:    #C2272D;   --fail-bg: #FBE9EA;
  --warn:    #8A5A00;   --warn-bg: #FFF4D6;
  --code-bg: #F6F7F9;   --code-ink: #1B2733;
  --add-bg:  #E8F6EC;   --del-bg:  #FBECEC;
  --font-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-head: "IBM Plex Sans Condensed", "IBM Plex Sans", system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { /* dark values */ color-scheme: dark } }
:root[data-theme="dark"] { /* the same dark values */ color-scheme: dark }
```
Dark palette: ground `#11161C`, sheet `#171E26`, ink `#E6EBF0`, ink-2 `#A9B4C0`, ink-3 `#7D8894`, rule `#2A333D`,
signal `#FF7A45` (with dark `--signal-ink`), pass `#4CC274`, fail `#FF6B6B`, warn `#E3B341`, tinted backgrounds at low alpha,
code-bg `#0F141A`. Check contrast (WCAG AA 4.5:1 for text) in both themes; adjust values if a pair fails.

Fonts from Google Fonts (one `<link>`): IBM Plex Sans 400/500/600 (+ italic 400), IBM Plex Sans Condensed 500/600,
IBM Plex Mono 400/500. Always with the fallback stacks above.

## Type scale
Body 17px / 1.6 on desktop, 16px on phones. Scale: 13 (mono labels, uppercase, letter-spacing .06em) · 15 (secondary) ·
17 (body) · 20 (h3) · 24 (h2) · 32 (h1, condensed 600). Headings use `text-wrap: balance`. Running text max ~68ch.
`font-variant-numeric: tabular-nums` on timers, scores, counts, tables.

## Components (look)
- Rail item: module code in mono (`M2`), title, a compact row of section dots coloured by status. Current item marked with
  the signal colour as a 2px left rule on the rail item only (not on cards).
- Buttons: primary = signal fill; secondary = ink outline; quiet = text button. 40px min height, 44px on touch.
  Radius 6px everywhere; no pill buttons except status chips.
- MCQ options: full-width rows with the teacher's letters `a)` `b)` `c)` `d)` in mono. Selected = signal outline.
  After checking: correct row gets pass tint + ✓, your wrong choice fail tint + ✗, and every option shows its `why` text
  beneath it. Do not hide the reasoning behind more clicks.
- Open answers: a sheet with ruled lines (repeating-linear-gradient using --rule), textarea per part, a live
  "≈ N lines" estimate (handwriting ≈ 60 characters per line) against the 5–8 target.
- Code blocks: --code-bg, 15px mono, horizontal scroll inside the block, language label top-right in mono 12px,
  syntax colours from a small token palette defined for both themes (keywords, strings, numbers, comments, functions,
  diff add/del/hunk). No third-party theme.
- Status chips: `✓ passing`, `✗ failing`, `○ not tried`, `predicted` (warn tint, for session 10 content).
- Cards are used sparingly: question sheets and the exam paper are sheets; lists are lists with hairlines.

## Never
- Gradients, glassmorphism, drop-shadow stacks, glowing borders, emoji, decorative icons, stock illustrations, confetti,
  "streak" gamification, mascots, a big centred hero, numbered 01/02/03 markers that encode nothing, accent bars on cards,
  rounded-xl on everything, Inter or Space Grotesk, purple/blue gradient, cream + serif + terracotta, black + acid green.
- Toasts for everything. Modals for anything that could be inline.
- Motion beyond 150ms ease-out state transitions. Respect `prefers-reduced-motion` (no motion at all).

## Interaction rules
- Everything is keyboard-operable: a–d / 1–4 pick an option, Enter checks/next, F flips a flashcard, ←/→ navigate,
  `?` shows shortcuts. Visible focus ring (2px signal outline, 2px offset).
- Touch targets ≥ 44px. No hover-only affordances.
- Copy is plain and specific: "Check answer", "Next question", "Start Paper B (60 min)", "Mark my answer".
- Empty and error states say what to do next.
- Works at 360px wide with 16px gutters and no horizontal page scroll (code/diff/table blocks scroll inside themselves).
