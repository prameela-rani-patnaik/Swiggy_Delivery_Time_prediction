# Slide Prompts: What Happens After the Model Is Trained

Paste each block below into Gamma AI, one at a time. These cover the **concept beats only** —
the 🎬 live-demo moments are not slides, they're screen-shares; see `DEMO_RUNBOOK.md` for those.
Where a slide sits right before or after a live demo, it says so, so you know when to flip away
from Gamma to a terminal/browser and back.

---

## Slide 1 — Title

**Prompt:**
> Create a title slide for a technical webinar called "What Happens After the Model Is Trained:
> Testing, Shipping, Scaling, and Watching a Machine Learning System in Production". Subtitle:
> "A live, first-principles walkthrough — Swiggy delivery time prediction system". Clean,
> minimal, engineering-conference style.

---

## Slide 2 — The hook

**Prompt:**
> Create a slide with one bold question, minimal design: "You trained a model. It beats your
> baseline. Are you done?" Below it, smaller: "No — and this next part is where most real machine
> learning work actually happens." Simple supporting visual: a trophy icon next to a much longer,
> mostly-empty road labeled "???"

---

## Slide 3 — The roadmap

**Prompt:**
> Create an agenda/roadmap slide listing everything this talk covers, as a single numbered
> journey rather than a bullet list of disconnected topics: 1) Testing — does it work, is it good
> enough. 2) Model Registry — Staging vs. Production. 3) CI/CD — the checklist that runs itself.
> 4) Containers — packaging the app, not the model. 5) Image Registry — shipping the container.
> 6) Manual Deployment — getting it onto a real server. 7) Load Testing — breaking it on purpose.
> 8) Scaling — vertical vs. horizontal. 9) Load Balancing — fixing the break. 10) Autoscaling —
> node-level and pod-level. 11) Monitoring & Alerting — catching the failure nothing else catches.
> Style it as a single left-to-right or top-to-bottom path with 11 waypoints, not a grid or table,
> to visually foreshadow the "it's a loop" close at the end of the talk. Caption: "Eleven stops.
> One trained model. Watch it become something real."

---

## Slide 4 — First principles: what is a model, once training ends?

**Prompt:**
> Create a slide explaining, from first principles, that a trained model is just a file — a set
> of numbers fit to past data, sitting on a disk. That file has no opinion about whether it's
> good enough to trust, no memory of which version is "the real one" in use, and no way to reach
> a user by itself. State the question the rest of the talk answers: "How does a file become
> something safe enough to bet real decisions on?" Show a simple visual: a single file icon
> labeled "model.joblib" with a large question mark pointing toward a cloud/user icon.

---

## Slide 5 — Testing: two different questions

**Prompt:**
> Create a slide introducing testing a model before it ships as answering two separate
> questions, not one: (1) "Does it even exist and load correctly?" — a smoke test — and
> (2) "Is it actually good enough?" — a performance test, e.g. average prediction error must stay
> under a threshold. Use a factory quality-control analogy: first check the part exists and fits,
> then check it meets spec, before it's allowed on the truck. Show two simple checklist icons
> side by side: "Does it load?" and "Is it good enough?"

*(Flip to terminal here for 🎬 WOW #1 — the gatekeeper. See DEMO_RUNBOOK.md § Testing.)*

---

## Slide 6 — First principles: the model registry

**Prompt:**
> Create a slide explaining why a trained model needs a "registry" instead of just being a file
> someone remembers the path to. Analogy: a librarian who tracks every version of every book and
> which shelf it's currently allowed to be borrowed from, versus a pile of loose papers on a
> desk. Introduce two shelves/stages: "Staging" (a draft shelf — for models that passed initial
> checks but aren't yet trusted with real traffic) and "Production" (the public shelf — what
> actually serves users right now). Show a simple diagram: a model file moving from a "Staging"
> shelf icon to a "Production" shelf icon, gated by a checkmark labeled "tests passed."

*(Flip to terminal/MLflow UI here for the live registry demo. See DEMO_RUNBOOK.md § Model Registry.)*

---

## Slide 7 — The trust boundary

**Prompt:**
> Create a slide making one point clearly: promotion from Staging to Production should only ever
> happen automatically if the tests from the previous section passed. This is the trust boundary
> of the whole system — no human has to remember to "double check" a model before it goes live,
> because the gate is structural, not a habit. Show a simple gate/turnstile icon between the two
> shelves from the previous slide, labeled "only opens if tests passed."

---

## Slide 8 — First principles: why automate any of this? (CI)

**Prompt:**
> Create a slide posing the problem CI solves: if testing and promoting a model is a manual
> checklist a person has to remember to run every single time code changes, it will eventually be
> skipped under deadline pressure — that's how bad models reach production. Introduce "CI/CD"
> (Continuous Integration / Continuous Deployment) and "pipeline" as: an automated checklist that
> runs itself, in the same order, every single time, with no human able to accidentally skip a
> step. Show a simple visual: a human standing next to a robot; the robot is holding the same
> checklist, but never gets tired or forgets a line.

---

## Slide 9 — Anatomy of the pipeline

**Prompt:**
> Create a slide showing a real CI/CD workflow as a numbered sequence of stages, each annotated
> in plain English: "Pull the data and code," "Run the smoke test," "Run the performance test,"
> "If both pass, promote the model to Production," "Build the container image," "Push it to the
> image registry." Frame it as: this entire sequence fires automatically on every code push, in
> this exact order, and stops early if any test fails.

*(Flip to GitHub/terminal here — trigger the CI push at the START of this block, per
DEMO_RUNBOOK.md § CI, then return to slides while it runs in the background, and cut back to the
completed run for 🎬 WOW #2.)*

---

## Slide 10 — First principles: what is a container, and why package the app this way?

**Prompt:**
> Create a slide explaining containers from first principles: the classic failure mode is "it
> works on my machine but not on the server," caused by missing library versions, OS packages, or
> Python packages on the target machine. A container solves this by packaging the application
> code and all its dependencies into one portable unit that runs identically anywhere. Show a
> simple diagram: [Code + Dependencies + Runtime] bundled into one box labeled "image," which runs
> the same on a laptop, a teammate's machine, or a cloud server.

---

## Slide 11 — The kitchen vs. the special

**Prompt:**
> Create a slide making one subtle, important point: this container image does NOT contain the
> model's weights/parameters. It only contains the serving code and the data-preprocessing logic.
> The actual model is fetched live from the model registry when the container starts. Use a
> restaurant analogy: the kitchen (the image) is built identically every time, but "today's
> special" (which model version is being served) is decided at serving time by asking the
> registry what's currently in Production. Show a simple diagram: a "Kitchen" box (fixed) with an
> arrow reaching out to a "Registry" box labeled "today's special," rather than the special being
> baked into the kitchen itself.

*(Flip to terminal here for 🎬 WOW #3 — the invisible model. See DEMO_RUNBOOK.md § Image Build.)*

---

## Slide 12 — First principles: why does an image need its own registry?

**Prompt:**
> Create a slide explaining container registries (e.g. AWS ECR) as the same idea as the model
> registry, one layer down: a single source of truth for "the sealed box," so any server anywhere
> can pull an identical copy on demand, instead of someone manually copying files machine to
> machine. Analogy: a warehouse that holds the shipping container so any truck can pick up an
> identical one, rather than one specific truck being the only place the box exists.

*(Flip to terminal here for the live push to ECR. See DEMO_RUNBOOK.md § Image Push.)*

---

## Slide 13 — Getting it onto a real machine

**Prompt:**
> Create a slide describing the manual deploy step in plain language: log into one cloud server
> (AWS EC2 — "renting one computer in Amazon's data center"), pull the image from the registry,
> and run it as a container. State plainly this is being done by hand in this demo specifically so
> the audience can see every step, not because this is the recommended way to deploy at scale
> (that gap gets addressed later in the talk).

*(Flip to terminal here for the live SSH/pull/run/curl. See DEMO_RUNBOOK.md § Manual Deploy.)*

---

## Slide 14 — The question that breaks the illusion

**Prompt:**
> Create a slide with a single provocative question, minimal design, big text: "This works
> great for one request. What happens when hundreds of people ask for a delivery-time prediction
> in the same second?"

---

## Slide 15 — First principles: why a single server has a ceiling

**Prompt:**
> Create a slide explaining, from first principles, why one server can't serve unlimited traffic:
> it has a fixed number of CPU cores and a fixed amount of memory. Each incoming request needs CPU
> time to run the model and produce a prediction. If requests arrive faster than the server can
> finish processing them, they queue up; if the queue grows long enough, the client gives up —
> that's a "timeout." Define "load testing" as deliberately sending a flood of requests to find
> where a system breaks, "concurrency" as how many requests are in flight at once, and "latency"
> as how long one request takes to come back. Show a funnel diagram: many arrows going in, one
> narrow pipe in the middle, some arrows falling off the side labeled "TIMEOUT."

*(Flip to terminal here for 🎬 WOW #4 — breaking it live. See DEMO_RUNBOOK.md § Break It.)*

---

## Slide 16 — Two paths forward

**Prompt:**
> Create a slide presenting the two classic scaling strategies as a fork in the road: "vertical
> scaling" (make the one server bigger — more CPU, more RAM) versus "horizontal scaling" (add more
> servers and share the load). For vertical scaling, note the tradeoff: there's always a
> bigger-instance ceiling eventually, and it's still a single point of failure — if that one
> server goes down, everything goes down. For horizontal scaling, note: no hard ceiling (keep
> adding servers), and if one server dies, others keep serving. Visually: one big box vs. three
> smaller connected boxes.

---

## Slide 17 — A second server, and the new problem it creates

**Prompt:**
> Create a slide showing a second server now running the exact same container image, independent
> of the first. Then pose the coordination problem this creates: "Now there are two addresses.
> Which one does a user's request go to? What if we add a third? A tenth? What happens if one
> server crashes — does the client know to try the other one?" Show two server icons with two IP
> addresses, a confused question mark between them, and a single incoming request arrow unsure
> which way to go.

*(Flip to terminal here for the live second-instance deploy. See DEMO_RUNBOOK.md § Horizontal Scaling.)*

---

## Slide 18 — First principles: what a load balancer actually is

**Prompt:**
> Create a slide explaining a load balancer from first principles: a service that sits in front
> of a group of servers, has one single public address itself, and for every incoming request
> decides which backend server should handle it — spreading requests roughly evenly, and
> automatically skipping any server that's unhealthy. Define "target group" as the list of
> servers eligible to receive traffic, and "health check" as periodically asking each server "are
> you okay?" and pulling it out of rotation if it stops answering. Show a diagram: many incoming
> arrows → one box labeled "Load Balancer" → arrows fanning out evenly to two server icons behind
> it.

*(Flip to terminal/console here for the live ALB creation + re-test. See DEMO_RUNBOOK.md § Load Balancer, for 🎬 WOW #5.)*

---

## Slide 19 — Recap: what you just watched

**Prompt:**
> Create a recap slide explicitly referencing the live result the audience just saw, not a fresh
> generic graphic: "What we just watched — same load-test command, same 200 concurrent users,
> pointed at the load balancer instead of one server. Timeouts became successes." Show the actual
> shape of the result as a simple two-column layout labeled "Before (one server)" and "After (load
> balancer)," framed as a recap of the live output rather than an illustration, so it doesn't read
> as a canned graphic contradicting what was just demonstrated. Caption: "Same traffic. Same total
> demand. The difference is entirely architectural."

---

## Slide 20 — The question that comes after the load balancer

**Prompt:**
> Create a slide posing the next gap: "We manually decided to run exactly two servers. What if
> traffic is unpredictable — quiet at 3am, ten times higher at lunch? Do we guess and leave
> capacity idle, or guess wrong and get overwhelmed again?" Introduce "autoscaling" as: a system
> that automatically adds or removes serving capacity based on real-time demand, instead of a
> human guessing a fixed number in advance.

---

## Slide 21 — Node-level autoscaling (told, not shown)

**Prompt:**
> Create a slide explaining node-level autoscaling in plain language, no live demo implied: a
> service like AWS Auto Scaling Groups watches metrics (like CPU usage or request count) across a
> group of servers and automatically launches new whole EC2 machines when demand rises, and
> terminates them when demand falls — the same manual "spin up a second EC2" step from earlier in
> the talk, just done automatically by a policy instead of a person. Define "node" as one physical
> or virtual machine.

---

## Slide 22 — Pod-level autoscaling (told, not shown) and the contrast

**Prompt:**
> Create a slide explaining pod-level autoscaling in plain language, no live demo implied:
> introduce "orchestration" as the general job of automatically deciding what runs where across a
> group of machines, and "Kubernetes" as one popular system that does this — it groups machines
> together into a "cluster" and manages many containers across that cluster for you. Define "pod"
> as the smallest unit Kubernetes runs (roughly: one or a few containers working together).
> "Horizontal Pod Autoscaling" (HPA) adds or removes pods *within an already-provisioned cluster*,
> rather than adding or removing whole machines. Make the contrast explicit with a two-column
> diagram: Node-level autoscaling = "change how much hardware exists"; Pod-level autoscaling =
> "change how the existing hardware is divided up." Note that real production systems often
> combine both at once.

---

## Slide 23 — The question that comes after autoscaling

**Prompt:**
> Create a slide with a single question: "The system now scales itself and recovers from a
> crashed server. But what if nothing crashes — and the model is just quietly wrong?"

---

## Slide 24 — First principles: monitoring a model is not the same as monitoring a server

**Prompt:**
> Create a slide contrasting two failure modes: a crashed server announces itself loudly — an
> error, a page, a red dashboard. A model being fed data unlike anything it was trained on
> doesn't — it keeps returning confident, normal-looking answers, with zero exceptions, even
> though nobody can yet confirm whether those answers are actually correct. Use a fire-alarm vs.
> gas-leak-detector analogy: infrastructure monitoring (CPU, latency, error rate) is the fire
> alarm — catches the fire. Watching the inputs a model receives is the gas-leak detector — an
> early warning that something might be wrong, well before you'd otherwise find out. Be precise
> about what this catches: it's a leading indicator (unusual inputs arriving right now), not
> "drift" in the full sense (a tracked change in the input or prediction distribution over time,
> which needs a history of requests to measure) — that's a natural next thing to build on top of
> this. Define "observability" as: having enough signal from a running system to know what it's
> actually doing, not just whether it's turned on.

*(Flip to terminal here for 🎬 WOW #6 — the alarm that never sleeps. See DEMO_RUNBOOK.md § Monitoring.)*

---

## Slide 25 — The full-circle insight

**Prompt:**
> Create a slide making the closing connection of the whole talk explicit, precisely stated: "The
> performance test from the first ten minutes of this talk could only run because we already had
> the right answers (the test set's real delivery times) to check against. Live traffic doesn't
> come with the right answer attached — it arrives before we know if the model was correct. So
> production monitoring has to watch a proxy signal instead: are the *inputs* still what the model
> was trained to handle? That's what just fired. It's an early warning, not the final verdict —
> and it's the same instinct as the performance test, just running continuously and without the
> luxury of already knowing the right answer." Show a simple visual: the "performance test" icon
> from Slide 5, connected by a dotted arrow (labeled "same instinct, no ground truth yet") to a
> live "input monitor" icon with a clock/infinity symbol.

---

## Slide 26 — Recap: the loop, not a line

**Prompt:**
> Create a closing slide that redraws the entire journey not as a line ending at deployment, but
> as a circle: Train → Test → Register (Staging) → Promote (Production) → Build image → Push
> image → Deploy → Scale → Monitor → (arrow back to) Train. Caption: "You didn't just ship a
> model. You built a loop — and monitoring is what tells you when it's time to go around again."

---

## Slide 27 — Q&A / Thank you

**Prompt:**
> Create a closing slide: "Questions?" with a subtle footer listing the key stages covered:
> Testing, Model Registry, CI/CD, Containers, Image Registry, Deployment, Load Balancing,
> Autoscaling, Monitoring.

---

## Notes for the presenter

- Never paste real secrets (AWS keys, DagsHub tokens, account IDs) into any slide shown to an
  audience — every command referenced in `DEMO_RUNBOOK.md` uses placeholders for exactly this
  reason.
- The six 🎬 wow moments are the spine of the talk — rehearse each one standalone, with a
  fallback screen recording ready in case live infra misbehaves in front of the room (see
  `DEMO_RUNBOOK.md`'s prep checklist).
- Slides 21–22 (autoscaling) are deliberately the only "told, not shown" beats — don't open a
  console or cluster during these, or the pacing for the rest of the 105 minutes will slip.
