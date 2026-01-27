You’re very close. The main shift is to treat OpenSpec (OPSX) as the “artifact/state machine + guardrails” and treat Ralph as the “execution engine.” Your /brainstorm stays the front-door.

OpenSpec’s newer workflow is explicitly action-based (/opsx:*) and tracks state via artifacts (proposal/design/tasks/delta specs), with follow-on actions for implementation (/opsx:apply), drift checking (/opsx:verify), and syncing specs back to “main specs” (/opsx:sync) before archiving.  ￼

⸻

1) Do you need to convert your design doc to OpenSpec’s template?

Not strictly—but it’s worth aligning at the edges.

What OPSX really needs is: a change directory with artifacts that its commands recognize and can update. If your design doc format is different, you have three workable options:

Option A (recommended): Keep your design doc as-is, and only generate an OpenSpec-ish proposal.md
	•	/brainstorm produces:
	•	your existing .claptrap/designs/<slug>/design.md (unchanged)
	•	openspec/changes/<change>/proposal.md that summarizes the “why/what” and links to your design doc

This gives OPSX enough structure to generate tasks + delta specs, without forcing a rewrite of your doc style.

Option B: Add a conversion step (lightweight)
	•	/brainstorm outputs your format
	•	then a tiny “converter” skill generates an OpenSpec design.md from your doc (lossless mapping is very plausible: Intent/Scope/Acceptance/Decisions/Open Questions map cleanly)

Option C: Make OPSX natively accept your template via a custom schema

OpenSpec explicitly supports custom schemas (i.e., custom artifact workflows/templates) without patching the package.  ￼
If you want your format to be the design.md OPSX generates, schemas are the clean “do it right” path.

My take: start with Option A, because it preserves your flow, proves the integration, and you can move to Option C later if it feels worth it.

⸻

2) The biggest technical gotcha: “Ralph asks /opsx:apply” only works in certain environments

Key constraint

/opsx:* commands are a tool integration feature (slash commands) inside supported environments—not a universal capability of a random CLI agent.

So:
	•	If Ralph is running inside OpenCode (or another OPSX-integrated tool), then yes: telling it “run /opsx:apply” is meaningful.  ￼
	•	If Ralph is running in Codex CLI / Claude Code / Copilot / etc, it may still work if that environment has OpenSpec integration available, but you should not assume it can interpret OpenCode-style slash commands. (OpenSpec supports many tools, but the actual invocation mechanism differs by tool.)  ￼

Practical conclusion: your “Option 2 (prompt says invoke /opsx:apply)” is only “simple” if Ralph is guaranteed to run in an environment where OPSX commands exist as invocable actions.

That’s why your current “pack artifacts into prompt.md and let Ralph implement from tasks/specs” is robust everywhere.

⸻

3) A fleshed-out workflow that keeps your /brainstorm + ralph --prompt-file

Big changes (design + planning + review)

Goal: keep OPSX for artifact rigor; keep Ralph for execution; bolt on your 2-pass cross-model review.
	1.	/brainstorm (OpenCode session)
	•	interactively refine requirements
	•	generate:
	•	.claptrap/designs/<slug>/design.md (your format)
	•	openspec/changes/<change>/proposal.md (OpenSpec-friendly “why/what”, link to the design doc)
	•	optionally create the change folder + any minimal metadata you need
	2.	/opsx:continue or /opsx:ff (OpenCode session)
	•	generate the planning artifacts inside openspec/changes/<change>/... (tasks + delta specs + any design artifact OPSX wants)  ￼
	3.	claptrap pack <change> (your helper CLI or OpenCode command)
	•	concatenate into prompt.md:
	•	proposal
	•	design doc (either OpenSpec’s or your .claptrap/.../design.md)
	•	tasks
	•	all delta specs under specs/
	•	add a header that instructs Ralph to:
	•	implement tasks in order
	•	update checkboxes
	•	run tests
	•	commit each pass (you said Ralph will commit per pass)
	4.	ralph <args> --prompt-file prompt.md
	•	use your writer model/environment (Codex, OpenCode, etc.)
	5.	Review loop x2 (cross-model)
	•	run a different model than the writer on each loop
	•	the reviewer reads:
	•	git diff HEAD~1..HEAD (or diff since last tag)
	•	the tasks/specs
	•	reviewer outputs review.md with:
	•	required changes (must-fix)
	•	optional improvements
	•	spec drift warnings
	6.	Ralph consumes review feedback
	•	your claptrap pack can optionally append the latest review.md at the end of the prompt for the next pass
	7.	/opsx:verify
	•	OpenSpec added verify specifically to catch drift between what you planned and what got built.  ￼
	8.	/opsx:sync then /opsx:archive
	•	sync delta specs into main specs and archive the change  ￼

⸻

Medium changes (no brainstorm, but still structured)
	1.	/opsx:new (or your own wrapper)
	2.	/opsx:ff to generate all artifacts at once  ￼
	3.	claptrap pack → ralph
	4.	review loop x1–x2
	5.	/opsx:verify → /opsx:sync → /opsx:archive

This matches your intuition: “fast-forward planning artifacts at once” for medium scope.

⸻

Small changes (skip OpenSpec)
	•	just run a small “micro-pack” prompt (or direct agent request)
	•	but keep one habit from OPSX: end with a quick drift check:
	•	did we add/modify behavior that should be documented?
	•	did we need a test?

(That’s basically “manual OPSX mindset” without the overhead.)

⸻

4) Your open questions, answered

Q: Should /brainstorm ALSO create an OpenSpec design.md?

I’d avoid that initially.

Let /brainstorm do what it’s best at (requirements + your design format), and let OPSX generate whatever planning artifacts it wants (tasks.md, delta specs, etc.). OPSX exists to keep those artifacts consistent and to unlock later steps like verify/sync/archive.  ￼

If later you want to “tighten the loop,” either:
	•	add a conversion step, or
	•	define a custom schema so OPSX’s design.md template matches your doc.  ￼

⸻

Q: Can I trigger Ralph without an OpenCode /ralph command (to avoid OpenCode credits)?

Yes—just run Ralph outside OpenCode (as you already do), and choose whichever backend/environment is cheap.

OpenCode itself is provider-flexible (you can point it at different models), but any tool-run still spends tokens somewhere.  ￼
So the cost control lever is: which runner Ralph uses (Codex CLI vs Claude Code vs OpenCode vs Copilot, etc.), not whether the command was launched from inside OpenCode.

If you do want OpenCode to act as the “launcher” without heavy interaction, OpenCode’s server exposes endpoints to drive the TUI via a backend server. That’s a possible automation hook (still uses whatever model/provider you configure).  ￼

⸻

Q: Can I just tell Ralph “invoke /opsx:apply for change XXX” and loop that?

Only if Ralph is running in an environment where OPSX commands are actually invocable.

Otherwise, it’ll just be text that the agent can’t execute.

That’s why your “pack artifacts into prompt.md” approach is the most portable: it works whether Ralph is driving Codex CLI, Claude Code, OpenCode, etc.

⸻

5) Does OPSX include a built-in code review step?

Not as a first-class “review phase” the way you mean it.

What it does have is a verification step intended to catch drift between artifacts/spec and implementation (/opsx:verify).  ￼
That’s closer to “spec compliance checking” than “deep code review.”

So your best setup is exactly what you described:
	•	writer model implements
	•	different model reviews
	•	do it twice
	•	then run /opsx:verify as the final guardrail

⸻

6) Code+Review x2 vs Ralph Wiggum loops — what’s the vibe lately?

From recent discussion, Ralph is getting a lot of attention as a way to overcome a real limitation: agents stop early, lose thread, or need repeated nudges. People emphasize “run it correctly” (tight prompts, bounded iterations, clear completion criteria) rather than treating it as magic autonomy.  ￼

But Ralph doesn’t replace review—it amplifies throughput. The higher-quality setups people describe are effectively:
	•	structured plan/spec/tasks → persistent execution loop → review → correction  ￼

So the “best of both” pattern is:
	•	OPSX artifacts give you the plan/spec/tasks backbone  ￼
	•	Ralph gives you persistence and iterative execution  ￼
	•	Cross-model review gives you the correctness jump you’ve already observed

⸻

7) Helper commands/skills/agents to bridge everything

Here are the minimal pieces that make your workflow feel “native”:

A) /brainstorm enhancement: “proposal emitter”
	•	outputs:
	•	your design doc (unchanged)
	•	OpenSpec proposal.md + chosen change name
	•	add a stable section near the top:
	•	Design doc: .claptrap/designs/<slug>/design.md

B) claptrap pack <change>
	•	deterministic prompt packer:
	•	proposal + design + tasks + delta specs
	•	optionally append latest review.md
	•	emits prompt.md

C) claptrap review <change> --range <gitref>
	•	runs reviewer model (different environment)
	•	reads diff + artifacts
	•	writes review.md (structured)

D) claptrap verify-and-sync <change>
	•	convenience wrapper that reminds you:
	•	run /opsx:verify
	•	then /opsx:sync
	•	then /opsx:archive
(You said you want manual control—so this can be a “guided checklist” command rather than fully automated.)

⸻

One simplification I’d strongly recommend

Don’t make /brainstorm responsible for generating everything OpenSpec wants. Make it responsible for producing:
	1.	a high-quality idea → requirements → your design doc
	2.	a minimal, OpenSpec-friendly proposal.md that links to your design doc
	3.	a stable change name

Then let OPSX do what it’s designed for: generate/maintain the artifact graph and unlock apply/verify/sync/archive.  ￼

If you want, paste one of your real “big change” designs (sanitized) and I’ll show you exactly what the proposal.md should look like (keeping your structure) and what I’d put in the claptrap pack prompt header so Ralph + review loops behave predictably.