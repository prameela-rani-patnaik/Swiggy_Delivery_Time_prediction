# Webinar: What Happens After the Model Is Trained

A 105-minute, live-demo webinar for a **technical audience that does not yet know these
pipeline stages exist**. The narrative arc: testing → model registry → CI → image build →
image push → manual deploy → it breaks under load → scaling concepts → horizontal scaling →
load balancer → autoscaling (told, not shown) → monitoring & alerts → close.

This folder has three files:

- **README.md** (this file) — the run-of-show, vocabulary plan, and wow-moment list.
- **SLIDE_PROMPTS.md** — paste-into-Gamma prompts for every concept slide.
- **DEMO_RUNBOOK.md** — exact commands, expected output, and pre-staging steps for every live
  demo moment (🎬).

## Format rules this deck follows

1. **Never assume a term is known.** Each piece of vocabulary is defined in one plain sentence
   the first time it's used (see table below), then reused as-is for the rest of the talk.
2. **Live demo, not screenshots**, for every 🎬 moment in the run-of-show — code and infra must
   be pre-staged and tested end-to-end before the room fills up (see DEMO_RUNBOOK.md's prep
   checklist).
3. **Node-level (ASG) and pod-level (HPA) autoscaling are told, not shown** — explained in plain
   language with a contrast, no live console/cluster demo.
4. **Never put real secrets on a slide or in a terminal the audience can see** — every command in
   this folder uses placeholders (`<AWS_ACCOUNT_ID>`, `<DAGSHUB_USER_TOKEN>`, `<INSTANCE_1_IP>`,
   etc.). Export real values into shell variables off-screen before presenting.

---

## Run-of-show (105 minutes)

| Time | Block | Live? |
|---|---|---|
| 0–5 | Hook: "You trained a model that beats baseline. Are you done?" | — |
| 5–10 | First principles: a model is just a file | — |
| 10–20 | **Testing** — smoke test + performance gate | 🎬 WOW #1: the gatekeeper |
| 20–28 | **Model registry** — Staging vs. Production | 🎬 live register + MLflow UI |
| 28–38 | **CI** — the checklist that runs itself | 🎬 WOW #2: trigger early, reveal result |
| 38–45 | **Image build** — kitchen vs. the special | 🎬 WOW #3: the invisible model |
| 45–49 | **Image push** — a warehouse for containers | 🎬 live push to ECR |
| 49–55 | **Manual deploy** — one EC2, prove it serves traffic | 🎬 live SSH/run/curl |
| 55–62 | **Break it** — load test | 🎬 WOW #4: real timeouts on screen |
| 62–66 | Scaling pause: vertical vs. horizontal | — |
| 66–72 | **Horizontal scaling** — second EC2, the coordination gap | 🎬 live second instance |
| 72–80 | **Load balancer** — solves both problems at once | 🎬 WOW #5: before/after re-test |
| 80–83 | Autoscaling need | — |
| 83–86 | Node-level autoscaling (AWS Auto Scaling Groups) | told only |
| 86–89 | Pod-level autoscaling (Kubernetes HPA), contrast with node-level | told only |
| 89–99 | **Monitoring & alerts** | 🎬 WOW #6: the alarm that never sleeps |
| 99–105 | Close: redraw the pipeline as a loop, not a line + Q&A | — |

---

## Vocabulary-at-point-of-use

| Introduced in | Terms defined on the spot |
|---|---|
| Testing | "model registry" (teased, defined fully in next block) |
| Model registry | "artifact," "stage" (Staging/Production) |
| CI | "pipeline," "CI/CD," "workflow" |
| Image build | "image," "container," "Dockerfile" |
| Image push | "container registry" (same idea as a model registry, one layer down) |
| Break-it demo | "load testing," "concurrency," "latency," "timeout" |
| Scaling pause | "vertical scaling," "horizontal scaling" |
| Load balancer | "load balancer," "target group," "health check" |
| Autoscaling | "autoscaling," "node" vs. "pod," "cluster," "orchestration" |
| Monitoring | "observability," "leading indicator" (vs. "drift" — named but explicitly distinguished: this demo detects unusual inputs *right now*, not a tracked change over time), "alerting" |

---

## The six wow moments

1. **The gatekeeper** (Testing, min 10–20) — a deliberately bad model version is sitting in
   Staging before the talk starts. Run the performance test live against it and watch it
   **fail**. "This is the safety net. It just stopped a bad model before a single user saw it."
2. **The robot checklist** (CI, min 28–38) — push a real commit at the top of this block, keep
   teaching, cut back to a completed pipeline run. The whole test → register → promote → build →
   push chain ran untouched by human hands.
3. **The invisible model** (Image build, min 38–45) — search the built image's filesystem for the
   model file. It isn't there. Then show the running container's startup logs pulling the model
   over the network from the registry. "The kitchen doesn't know today's special until it opens
   the fridge in production."
4. **Breaking it live** (Load test, min 55–62) — real timeouts and climbing latency on screen,
   no simulation.
5. **The fix, proven** (Load balancer, min 72–80) — the *exact same* load-test command, same
   output format, before vs. after: timeouts flip to ~100% success.
6. **The alarm that never sleeps** (Monitoring, min 89–99) — feed the live model an
   out-of-distribution payload and show an alert/log fire in real time: no crash, no exception, an
   answer that looks normal but nobody can yet confirm is correct. Closing line: "The performance
   test from the start of this talk needed the right answers to check against. Live traffic
   doesn't come with those attached — so this watches the inputs instead, as an early warning,
   running continuously, with none of the luxury of already knowing the answer."

---

## Known gaps to be upfront about on stage

- Monitoring & alerting is **not implemented** in this codebase today — WOW #6 is a from-scratch
  demonstration built for this talk, presented honestly as "here's what this should look like,"
  not as an existing production system.
- The manual deploy step (stop-then-start on one box) has a real downtime gap — worth naming
  explicitly rather than glossing over it, in the same spirit as flagging the monitoring gap.
