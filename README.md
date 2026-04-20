# AccuSleePy Collaboration Station™ Demo

## Introduction

The following is a demo of [Collaboration Station™](https://github.com/Dandelion-Engineering/Collaboration-Station)
running an AccuSleePy sleep staging pipeline. All the finished work is in the `AccuSleePy_Demo/` folder. `AccuSleePy_Demo/README.md` explains how to reproduce the full pipeline from scratch on your own machine. `AccuSleePy_Demo/report/report.pdf` is the written analytical report covering the dataset, methods, validation results, and sleep architecture findings.

This demo has one major implication worth naming upfront: researchers should no longer feel limited by not knowing how to code certain data pipelines. The agents will do the coding. Moreover, the code they create will be well-commented and reproducible and come with documentation for others to understand and run it. What is required of researchers now is simply knowing what sort of data pipelines are available and what they can do. This presents an opportunity to explore data in ways that might've been too time consuming or difficult in the past. To reinforce this point, I first learned about AccuSleePy three weeks prior to starting this demo. To this day, I have still not written even one line of AccuSleePy code. This project took a total of 6 hours to complete from first agent launch. I only participated for 2 of those 6 hours, steering the agents and checking the work. The rest of the time I was working on other things. 

I should point out that this is a very clean project of a relatively straightforward data pipeline. The project ran very smoothly, for the most part. This is largely due to a very well structured Project Details.md. I had previously ran an AccuSleePy project for a grad student and from that experience I learned what a well structured Project Details.md for this type of pipeline looks like. But projects can definitely get a lot messier than this, especially with first attempts. Luckily, the agents can handle the messiness. And if you are running similar data pipelines consistently, you will learn what a well structured Project Details.md looks like and your projects will run more smoothly over time. In that case, you would eventually have a template Project Details.md that you can copy and paste with minor editing for each project that runs the same data pipeline.

The guided tour below will walk you through the project in the order it was run.

---

## Guided Tour (Section written by Claude)

### Reading Path

Work through the project in the order it ran:

1. `Project Details/Project Details.md` — the spec that drove everything
2. `chats/Claude-Codex-Antigravity-Human/Phase 1/Summary.md` through `Phase 7/Summary.md` — read the phase summaries in order for the high-level story; dip into the full transcripts for any phase that interests you
3. `agents/Claude/Session Summaries/`, `agents/Codex/Session Summaries/`, `agents/Antigravity/Session Summaries/` — first-person accounts of each session from each agent's perspective
4. `AccuSleePy_Demo/` — the deliverable itself

*If you only have a few minutes: read `Project Details/Project Details.md`, skim the seven phase summaries, then open `AccuSleePy_Demo/README.md` and `AccuSleePy_Demo/report/report.pdf`.*


### Things to Notice Along the Way

A few things worth looking for as you go through it.

**1. A precise project brief that let agents work without asking for clarification**

The agents' work is only as focused as what you give them to work with. Before a single line of code was written, the Project Details file named the exact dataset with its download URL, the exact pre-trained model, the exact calibration approach, and the expected output folder structure down to the file names. That level of specificity means the agents could resolve most judgment calls on their own without asking. It's the same dynamic you'd expect with any collaborator: a vague ask produces vague results, a precise one produces precise results. `Project Details/Project Details.md` is a good reference for what a well-structured brief looks like in practice.

**2. A requirement all three agents missed that Randy caught**

By the end of Phase 2, three agents had each reviewed the data inspection script and signed off. Randy looked at it and noticed it didn't save its output to a file. The requirement hadn't been specified in Project Details.md, and none of the agents had raised it. The point isn't that the agents failed — it's that the human coordinator's role isn't just setting direction at the start. It includes genuine quality checking, and domain familiarity is what makes that effective. See `chats/Claude-Codex-Antigravity-Human/Phase 2/Phase 2 - Concluded.md`.

**3. An agent re-ran the full pipeline independently to verify all outputs**

Phase 3 asked agents to verify that the output files were complete. One agent re-ran the full pipeline independently on all 50 recordings and confirmed every output matched exactly. That wasn't required. Sometimes agents do more than the minimum asked of them — useful to keep in mind when you're deciding how much detail to specify. See `chats/Claude-Codex-Antigravity-Human/Phase 3/Phase 3 - Concluded.md`.

**4. Two agents running separate workstreams simultaneously**

Phase 4 had two workstreams running simultaneously: one agent handling quality control, another handling validation, each working independently. They then cross-checked each other's outputs. In any project where the work can be cleanly divided, agents can run different analyses at the same time rather than sequentially, and the cross-check step tends to catch things that a single reviewer would miss. See `chats/Claude-Codex-Antigravity-Human/Phase 4/Phase 4 - Concluded.md`.

**5. A figure that needed human correction after two agent fixes**

Phase 6 produced 11 figures. Ten went through without issue. The eleventh had a layout problem. An agent applied a fix, then a second fix, and both were still off. The issue: agents still struggle with some visual tasks. Randy made the final correction manually. Anything requiring visual judgment — a figure, a layout, a chart — still needs a human to confirm the outcome. See `chats/Claude-Codex-Antigravity-Human/Phase 6/Phase 6 - Concluded.md`.

**6. The review structure Codex designed when asked to create a checklist**

Randy asked for a review of the final report and asked Codex to design an appropriate review checklist to go with it. Codex defined five categories — spec compliance, quantitative consistency, method fidelity, scientific communication, reproducibility — and required that every finding cite specific line numbers. A second agent used the same checklist independently. What was asked for was a checklist; what Codex decided was what to put in it, how detailed to make the criteria, and how to make findings actionable. See `chats/Claude-Codex-Antigravity-Human/Phase 7/Phase 7 - Concluded.md`.

**7. A statistic that was plausible but computed at the wrong level of aggregation**

The report described certain statistics as animal-level summaries but computed the values from the full recording dataset — a different level of aggregation than what the figures were showing. The numbers weren't obviously off; they just didn't match the framing. Subtle inconsistencies like this are easy to miss. An independent reviewer reading it fresh is more likely to notice. See `chats/Claude-Codex-Antigravity-Human/Phase 7/Phase 7 - Concluded.md`.

**8. Two README command bugs caught before any user ran them**

In a second pass through the deliverable README, a reviewer caught two command bugs: one command would have written output to the wrong location without any warning, and another used the wrong argument name and would have thrown an error on first run. Both were fixed before the deliverable was packaged. Catching bugs like these before users do is one of the less obvious places where review adds real value. See `chats/Claude-Codex-Antigravity-Human/Phase 7/Phase 7 - Concluded.md`.

*Questions or consulting inquiries: randy@dandelionengineering.com*

---

## References

Barger, Z., Frye, C. G., Liu, D., Dan, Y., & Bouchard, K. E. (2019). Robust, automated sleep scoring by a compact neural network with distributional shift correction. PLOS ONE, 14(12), 1–18. [https://doi.org/10.1371/journal.pone.0224642]

Barger, Z., & Frye, C. (2025, June 6). AccuSleep. https://doi.org/10.17605/OSF.IO/PY5EB


