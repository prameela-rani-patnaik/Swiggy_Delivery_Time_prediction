# Teaching Plan: Deploying an ML API and Discovering Why Load Balancers Exist

A first-principles walkthrough for teaching AWS deployment, containers, and horizontal scaling —
not by explaining the "correct" architecture upfront, but by making the audience feel the problem
before showing the solution. Each slide prompt below can be pasted into Gamma AI one at a time (or
as a batch) to generate the deck. Commands are real, taken from `docs/DEPLOYMENT_DEMO_PLAN.md`.

**How to use this file**: copy each "Slide N prompt" block into Gamma. The narrative arc is:
*what is a deployment → what is a container and why → single server → it breaks under load →
naive fix (bigger box) vs real fix (more boxes) → the coordination problem that creates →
load balancer solves it → prove it with numbers.*

---

## Slide 1 — Title
**Prompt:**
> Create a title slide for a technical talk called "From One Server to Many: Deploying a Machine
> Learning API and Discovering Why Load Balancers Exist". Subtitle: "A first-principles, hands-on
> walkthrough — Swiggy delivery time prediction API on AWS". Clean, minimal, engineering-conference style.

---

## Slide 2 — The question we're answering
**Prompt:**
> Create a slide posing the core question the talk answers: "We built a machine learning model.
> It works on my laptop. How does it become something the whole internet can send requests to —
> and what happens when too many people show up at once?" Keep it as a single bold question with
> a simple supporting illustration of a laptop connecting to a cloud icon.

---

## Slide 3 — First principles: what does "deploying" actually mean?
**Prompt:**
> Create a slide explaining deployment from first principles: a trained model is just a file
> (weights/parameters) sitting on a disk. To let others use it, something has to (1) load that
> file into memory, (2) accept requests over the network, (3) run the model's logic on each
> request, and (4) send back a response. That "something" is a running program on a machine
> reachable over the internet. Show this as a simple 4-step flow diagram: Model file → Loaded
> into a running process → Listens on a network port → Responds to requests.

---

## Slide 4 — Why not just run it on my laptop?
**Prompt:**
> Create a slide listing why a personal laptop can't serve as public infrastructure: no fixed
> public IP address, gets turned off, home network isn't built for many simultaneous connections,
> no one manages it if it crashes at 3am. Conclude with: "We need a machine that's always on and
> reachable — that's what a cloud server (like AWS EC2) gives us." Use a simple contrast layout:
> laptop (bad) vs cloud server (good).

---

## Slide 5 — First principles: what is a container, and why Docker?
**Prompt:**
> Create a slide explaining containers from first principles. Problem: "it works on my machine but
> not on the server" happens because the server is missing exact library versions, OS packages, or
> Python packages the code depends on. A container solves this by packaging the application code
> AND all its dependencies (OS libraries, Python packages, model files) into one portable unit that
> runs identically anywhere. Show a simple diagram: [Code + Dependencies + Runtime] all bundled
> into one box labeled "Docker Image", which runs the same on a laptop, a teammate's machine, or
> a cloud server.

---

## Slide 6 — Anatomy of our Dockerfile
**Prompt:**
> Create a slide walking through a real Dockerfile line by line as a "recipe" analogy: each
> instruction is one step in preparing a meal. Show this code block and annotate each block in
> plain English (base image = "start with a clean kitchen", RUN pip install = "buy and prepare
> ingredients", COPY = "bring in your own dish", CMD = "serve the dish"):
> ```
> FROM python:3.12-slim
> RUN apt-get update && apt-get install -y libgomp1
> WORKDIR /app
> COPY requirements-docker.txt ./
> RUN pip install -r requirements-docker.txt
> COPY app.py ./
> COPY ./models/preprocessor.joblib ./models/preprocessor.joblib
> COPY ./scripts/data_clean_utils.py ./scripts/data_clean_utils.py
> COPY ./run_information.json ./
> EXPOSE 8000
> CMD [ "python","./app.py" ]
> ```

---

## Slide 7 — Building and shipping the image
**Prompt:**
> Create a slide titled "Getting our container to AWS" explaining the build → tag → push flow as
> a shipping analogy: build the image (pack the box), tag it (write the shipping label/address),
> push it (ship it to the warehouse — AWS ECR, Elastic Container Registry). Show these real
> commands as a numbered sequence:
> ```
> # 1. Authenticate Docker to AWS's registry
> aws ecr get-login-password --region ap-south-1 \
>   | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com
>
> # 2. Build the image from the Dockerfile
> docker build -t swiggy/time-prediction .
>
> # 3. Tag it with the destination address
> docker tag swiggy/time-prediction:latest \
>   <account-id>.dkr.ecr.ap-south-1.amazonaws.com/swiggy/time-prediction:latest
>
> # 4. Push it to ECR
> docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/swiggy/time-prediction:latest
> ```

---

## Slide 8 — Phase 1: Launching our first server
**Prompt:**
> Create a slide describing launching a single AWS EC2 instance as "renting one computer in
> Amazon's data center". List the choices made and why: small instance type (t3.micro) chosen
> deliberately small so we can later demonstrate it struggling under load; a security group as
> "a firewall — a list of who's allowed to knock on which door (port)"; opening port 22 for SSH
> (remote login) and port 8000 for the app itself.

---

## Slide 9 — Pulling and running the container on the server
**Prompt:**
> Create a slide showing the commands run after SSHing into the new EC2 instance, framed as
> "now the server fetches the same packaged box we shipped to ECR, and runs it":
> ```
> # Log in to the server
> ssh -i my-key.pem ec2-user@<INSTANCE_PUBLIC_IP>
>
> # Authenticate to ECR and pull the image
> aws ecr get-login-password --region ap-south-1 \
>   | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com
> docker pull <account-id>.dkr.ecr.ap-south-1.amazonaws.com/swiggy/time-prediction:latest
>
> # Run it, exposing port 8000, passing in the secret token it needs
> docker run -d --name swiggy-app -p 8000:8000 \
>   -e DAGSHUB_USER_TOKEN="<token>" \
>   <account-id>.dkr.ecr.ap-south-1.amazonaws.com/swiggy/time-prediction:latest
> ```
> Emphasize: the container is now a running process on this specific machine, listening on port 8000.

---

## Slide 10 — Proof it works
**Prompt:**
> Create a slide titled "Proof of life" showing these commands hitting the live server from a
> local machine, with example expected output:
> ```
> curl http://<INSTANCE_PUBLIC_IP>:8000/
> → "Welcome to the Swiggy Food Delivery Time Prediction App"
>
> curl -X POST http://<INSTANCE_PUBLIC_IP>:8000/predict \
>   -H "Content-Type: application/json" \
>   -d '{ ... order details ... }'
> → 17.38   (predicted delivery time in minutes)
> ```
> Add a checkmark icon and the caption: "One model. One server. One request at a time — for now."

---

## Slide 11 — The question that breaks the illusion
**Prompt:**
> Create a slide with a single provocative question, minimal design, big text: "This works great
> for ONE request. What happens when 500 people order food from Swiggy in the same second?"

---

## Slide 12 — First principles: what actually happens under load
**Prompt:**
> Create a slide explaining, from first principles, why a single server has a ceiling. A server
> has a fixed number of CPU cores and a fixed amount of memory. Each incoming request needs CPU
> time to run the model and produce a prediction. If requests arrive faster than the server can
> finish processing them, they queue up. If the queue grows long enough, some requests wait so
> long that the client gives up — a timeout. Show a simple diagram: a funnel with many arrows
> (requests) going in, one narrow pipe (single CPU/process) in the middle, and some arrows falling
> off the side labeled "TIMEOUT".

---

## Slide 13 — Load testing: the tool that proves it
**Prompt:**
> Create a slide introducing load testing as "deliberately sending a flood of requests to see
> where the system breaks — like a stress test at the gym, but for servers". Introduce the `hey`
> command-line tool and show the exact command used:
> ```
> hey -z 30s -c 200 http://<INSTANCE_PUBLIC_IP>:8000/
> ```
> Explain: `-z 30s` = run for 30 seconds, `-c 200` = 200 requests fired concurrently, simulating
> 200 users hitting the API at once.

---

## Slide 14 — The results: it breaks
**Prompt:**
> Create a slide showing example load test output/summary stats from `hey`, highlighting non-200
> status codes and timeout errors, and a latency histogram showing response times climbing sharply
> as concurrency increases. Caption: "Some requests succeed. Some time out entirely. The single
> t3.micro instance has a ceiling — and we just hit it."

---

## Slide 15 — Two paths forward
**Prompt:**
> Create a slide presenting the two classic scaling strategies as a fork in the road:
> "Vertical Scaling" (make the one server bigger — more CPU, more RAM) vs "Horizontal Scaling"
> (add more servers and share the load). For vertical scaling, note the tradeoff: there's always
> a bigger-instance ceiling eventually, and it's still a single point of failure — if that one
> server goes down, everything goes down. For horizontal scaling, note: no hard ceiling (keep
> adding servers), and if one server dies, others keep serving. Visually: one big box vs three
> smaller connected boxes.

---

## Slide 16 — Phase 3: adding a second server
**Prompt:**
> Create a slide showing that we repeated the exact same deployment steps (launch EC2, pull image,
> run container) on a second instance. Show two server icons, each independently running the same
> Docker image, each with its own public IP address. Caption: "Same container. Same code. Two
> independent front doors."

---

## Slide 17 — The new problem this creates
**Prompt:**
> Create a slide posing the coordination problem that having two servers introduces: "Now there
> are two addresses. Which one does a user's request go to? What if we add a third? A tenth? What
> happens if one server crashes — does the user's app know to try the other one?" Show two IP
> addresses with a confused question mark between them and a single incoming request arrow unsure
> which way to go. This is the moment that "intuitively creates the need" for something that sits
> in front of both servers and makes that decision automatically.

---

## Slide 18 — First principles: what a load balancer actually is
**Prompt:**
> Create a slide explaining a load balancer from first principles: it's a program/service that
> sits in front of a group of servers, gets one single public address itself, and for every
> incoming request, decides which backend server should handle it — spreading requests roughly
> evenly, and automatically skipping any server that's unhealthy. Show a diagram: many incoming
> request arrows → one box labeled "Load Balancer" → arrows fanning out evenly to two server
> icons behind it.

---

## Slide 19 — Building it: target group + load balancer
**Prompt:**
> Create a slide describing the two AWS building blocks used, in plain English: a "Target Group"
> is simply the list of servers eligible to receive traffic, plus a health check ("periodically
> ask each server 'are you okay?' and stop sending it traffic if it stops answering"). An
> "Application Load Balancer" is the actual traffic director that uses that target group. List the
> concrete configuration used: Target group → HTTP port 8000, health check path `/`, both EC2
> instances registered. Load balancer → Internet-facing, listens on port 80, forwards to that
> target group.

---

## Slide 20 — Hitting the load balancer instead
**Prompt:**
> Create a slide showing the shift in how the app is now accessed — no longer a specific
> instance's IP, but the load balancer's own DNS name:
> ```
> curl http://<load-balancer-dns-name>/
> → "Welcome to the Swiggy Food Delivery Time Prediction App"
> ```
> Caption: "Same request. Different front door. Now something intelligent is behind it."

---

## Slide 21 — Repeating the exact same load test
**Prompt:**
> Create a slide emphasizing that we run the identical stress test as before, changing only the
> target address, to make it a fair comparison:
> ```
> hey -z 30s -c 200 http://<load-balancer-dns-name>/
> ```
> Caption: "Same 200 concurrent users. Same 30 seconds. This time, there are two servers sharing
> the work instead of one."

---

## Slide 22 — The results: it holds
**Prompt:**
> Create a before/after comparison slide: left side shows the single-instance load test results
> (many timeouts, high latency), right side shows the load-balanced results (near 100% success
> rate, stable latency). Add a simple bar or line chart illustrating success rate: ~60-70% (single
> instance) vs ~99-100% (load balanced). Caption: "Same traffic. Same total demand. The difference
> is entirely architectural."

---

## Slide 23 — Proving the traffic actually split
**Prompt:**
> Create a slide showing how to visually confirm requests are landing on both servers: tail the
> logs on both EC2 instances simultaneously while the load test runs (`docker logs -f swiggy-app`
> on each), and observe hits appearing on both in real time. Optionally show each instance
> returning its own identity (e.g. an environment variable like INSTANCE_NAME=app-1 / app-2
> reflected in the home endpoint's response) as concrete evidence of distribution.

---

## Slide 24 — Recap: the full arc
**Prompt:**
> Create a summary slide recapping the entire journey as a simple numbered arc: 1) Package the
> model as a container. 2) Ship it to AWS (ECR). 3) Run it on one server (EC2) — it works for one
> user. 4) Stress-test it — it breaks under real traffic. 5) Adding a second server alone creates
> a coordination problem. 6) A load balancer solves both problems at once: distributes load AND
> removes any single point of failure. 7) Proven with the same load test, before and after.

---

## Slide 25 — Why this pattern is universal
**Prompt:**
> Create a closing slide generalizing the lesson beyond this one project: this exact pattern —
> container → registry → compute → scale horizontally → load balancer — is how the vast majority
> of production web services and APIs are built, at any company, at any scale. What changes as you
> grow (more instances, auto-scaling, multiple regions) is the SIZE of this pattern, not its shape.
> End with: "You just built, broke, and fixed the same architecture real companies run in production."

---

## Slide 26 — Q&A / Thank you
**Prompt:**
> Create a closing slide: "Questions?" with a subtle footer referencing the repository name
> "swiggy-time" and the key AWS services used (EC2, ECR, Application Load Balancer, Docker).

---

## Notes for the presenter

- Never paste real secrets (AWS keys, DagsHub tokens) into slides shown to an audience — every
  command above uses `<placeholder>` values for exactly this reason. Substitute your own values
  live or keep them off-screen.
- If presenting live rather than from screenshots, run Phase 1–4 from
  `docs/DEPLOYMENT_DEMO_PLAN.md` shortly before the talk so the IPs/DNS names in your terminal
  history match what you show on slides.
- The single most important visual moment is Slide 22 (the before/after load test comparison) —
  spend the most rehearsal time making sure that result is real and captured, not simulated.
