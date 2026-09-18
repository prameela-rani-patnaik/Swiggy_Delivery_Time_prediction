# Demo Runbook: What Happens After the Model Is Trained

Exact commands and expected output for every 🎬 live moment in the run-of-show. Work through the
**pre-webinar setup checklist** completely, end-to-end, at least once before presenting — every
step here has been designed to be re-runnable, but live infra is still live infra.

Placeholders used throughout (never put real values on screen):
`<AWS_ACCOUNT_ID>`, `<ECR_REPO_URI>`, `<DAGSHUB_USER_TOKEN>`, `<INSTANCE_1_IP>`,
`<INSTANCE_2_IP>`, `<ALB_DNS_NAME>`. Export real values into shell variables *before* the
webinar starts, off-screen, e.g.:

```bash
export DAGSHUB_USER_TOKEN="<your real token>"
export ECR_REPO_URI="<your real ECR repo URI>"
```

Then every command below can use `$DAGSHUB_USER_TOKEN` / `$ECR_REPO_URI` and never show a raw
secret on screen.

---

## Pre-webinar setup checklist (do this the day before, not the morning of)

1. **A deliberately bad model staged in "Staging"** (for WOW #1 — the gatekeeper):
   - Run `python scripts/train_bad_model_demo.py`. This trains a deliberately under-fit
     RandomForest (2 trees, depth 2, 5% of the data), registers it, and pushes it to the
     **Staging** stage — without touching `params.yaml` or `dvc.yaml`.
   - The script backs up the previous, good `run_information.json` to
     `run_information_good_backup.json` automatically.
   - Confirm it's bad: `pytest tests/test_model_perf.py -v -s` should **fail** locally right now.
   - During the live Model Registry section, restore the good run info
     (`cp run_information_good_backup.json run_information.json`) and run
     `python src/models/register_model.py` live to push the good model back to Staging in front
     of the audience.
2. **Feature bounds for out-of-distribution detection**: run
   `python scripts/compute_feature_bounds.py` once (regenerate if training data changes) — this
   writes `models/feature_bounds.json`, which `app.py` uses to flag out-of-range prediction
   requests for WOW #6. It's already wired into the Dockerfile.
3. **Monitoring stack**: follow `monitoring/README.md` to bring up Prometheus + Grafana on the
   demo EC2 instance and do one full dry run of an out-of-distribution alert before the room
   fills up.
4. **A second EC2 instance** provisioned and reachable, Docker installed, but with **no
   container running yet** — you'll deploy to it live during Horizontal Scaling (don't
   pre-deploy, that's the live moment).
5. **A target group + Application Load Balancer** — do **not** pre-create; you'll create it live
   during the Load Balancer section. Do confirm in advance that your AWS console navigation to
   "Create target group" → "Create load balancer" takes under 3–4 minutes so it fits the block.
6. **`hey` installed locally**: `brew install hey` (or your platform's equivalent).
7. **A `payload.json`** sample matching the `Data` schema in `app.py`, for the heavier `/predict`
   load test — see § Break It below for the exact fields.
8. **An out-of-distribution payload** for WOW #6 (Monitoring) — see § Monitoring below.
9. **Fallback recordings**: screen-record a full successful run of WOW #1 through WOW #6 at
   least once, in case live infra misbehaves in the room. Never announce which is which — the
   fallback should be indistinguishable from live if you need to cut to it.
10. Confirm your GitHub Actions workflow (`.github/workflows/ci_cd.yaml`) is green on `main`
    right before the talk, so the live push during the CI section has a clean base to diff from.

---

## § Testing (min 10–20) — 🎬 WOW #1: the gatekeeper

Run locally, on screen:

```bash
# 1. Smoke test — does a model even exist in Staging, and does it load?
pytest tests/test_model_registry.py -v -s
```
Expected: **passes** — "The <model_name> model with version N was loaded successfully."

```bash
# 2. Performance test — is it actually good enough?
pytest tests/test_model_perf.py -v -s
```
Expected (because of the pre-staged bad model): **fails**, printing something like
`AssertionError: The model does not pass the performance threshold of 5 minutes`.

Talking point while it fails: "Notice what just happened — nothing crashed, nothing threw an
exception. The model works fine. It's just not *good enough*, and this is the only thing standing
between that and a real user getting a bad prediction."

---

## § Model Registry (min 20–28)

Register the *good*, previously-noted model run to Staging (superseding the bad one):

```bash
python src/models/register_model.py
```
This reads `run_information.json` (make sure it currently points at the good run's `run_id`
before running this live — swap the file back if you overwrote it during setup) and:
- registers a new model version from that run
- transitions it to the **Staging** stage

Then show the DagsHub / MLflow UI (Models tab) live: the model's version history, with the new
version now sitting in "Staging" above the bad one. Point out the bad version is still there,
just no longer the *latest* — nothing gets silently deleted, which is itself worth a sentence
("the registry never forgets, it just tells you what's current").

Optional close-the-loop moment, if time allows: re-run
`pytest tests/test_model_perf.py -v -s` — it now **passes** against the new Staging version.

---

## § CI (min 28–38) — 🎬 WOW #2: the robot checklist

At the **top** of this block (not the middle — it needs the full ~10 minutes to run in the
background while you teach):

```bash
git add .
git commit -m "Retrain and validate delivery-time model"
git push
```

Immediately switch to the GitHub Actions tab and show the workflow has started (`CI-CD` job,
yellow/in-progress). Then switch back to slides and teach through Slide 9 (anatomy of the
pipeline) while it runs unattended.

Return to the Actions tab near the end of the block and show the completed run, expanding these
steps live to narrate what each one did:
- `Test Model Registry` / `Test Model Performance` — green
- `Promote Model` — green (this ran `scripts/promote_model_to_prod.py`)
- `Build, tag, and push docker image to Amazon ECR` — green

Talking point: "I didn't touch any of this after I ran `git push`. Test, register, promote,
build, push — all of it happened because the checklist runs itself."

---

## § Image Build (min 38–45) — 🎬 WOW #3: the invisible model

```bash
docker build -t swiggy/time-prediction .
```

Prove the model isn't baked in:

```bash
docker run --rm --entrypoint find swiggy/time-prediction / -name "*.joblib"
```
Expected output: only `preprocessor.joblib` — no model weights file. Talking point: "The
preprocessor is baked in because it never changes model-to-model. The model itself isn't here at
all."

Then run it for real and show it fetching the model at startup:

```bash
docker run -d --name swiggy-local -p 8000:8000 \
  -e DAGSHUB_USER_TOKEN="$DAGSHUB_USER_TOKEN" \
  swiggy/time-prediction

docker logs -f swiggy-local
```
Point at the startup logs where `mlflow.sklearn.load_model(...)` pulls the model over the network
from the registry — this is the "opening the fridge" moment. Stop the container after:
`docker stop swiggy-local && docker rm swiggy-local`.

---

## § Image Push (min 45–49)

```bash
aws ecr get-login-password --region <YOUR_REGION> \
  | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com

docker tag swiggy/time-prediction:latest $ECR_REPO_URI:latest
docker push $ECR_REPO_URI:latest
```

Show it land in the ECR console, or from CLI:
```bash
aws ecr describe-images --repository-name <your-repo-name> --region <YOUR_REGION>
```

---

## § Manual Deploy (min 49–55)

SSH into the **first** pre-provisioned EC2 instance:

```bash
ssh -i <your-key>.pem ec2-user@<INSTANCE_1_IP>

aws ecr get-login-password --region <YOUR_REGION> \
  | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com

docker pull $ECR_REPO_URI:latest

docker run -d --name swiggy-app -p 8000:8000 \
  -e DAGSHUB_USER_TOKEN="$DAGSHUB_USER_TOKEN" \
  $ECR_REPO_URI:latest
```

From your **local machine**, prove it's live:

```bash
curl http://<INSTANCE_1_IP>:8000/
# expect: "Welcome to the Swiggy Food Delivery Time Prediction App"

curl -X POST http://<INSTANCE_1_IP>:8000/predict \
  -H "Content-Type: application/json" \
  -d @payload.json
# expect: a single number — predicted delivery time in minutes
```

---

## § Break It (min 55–62) — 🎬 WOW #4: breaking it live

```bash
hey -z 30s -c 200 http://<INSTANCE_1_IP>:8000/
```
- `-z 30s`: run for 30 seconds. `-c 200`: 200 concurrent workers.

For the heavier `/predict` endpoint (runs the real model pipeline per request):
```bash
hey -z 30s -c 100 -m POST -T "application/json" -D payload.json \
  http://<INSTANCE_1_IP>:8000/predict
```

Expected: a chunk of non-200 responses / timeouts in the status code distribution, and a latency
histogram climbing sharply. Let this run fully on screen — the scrolling failure is the point.

**`payload.json`** (sample matching the `Data` model in `app.py`):
```json
{
  "ID": "0x1",
  "Delivery_person_ID": "RES1DEL01",
  "Delivery_person_Age": "29",
  "Delivery_person_Ratings": "4.6",
  "Restaurant_latitude": 12.9716,
  "Restaurant_longitude": 77.5946,
  "Delivery_location_latitude": 12.9352,
  "Delivery_location_longitude": 77.6146,
  "Order_Date": "19-03-2022",
  "Time_Orderd": "18:30:00",
  "Time_Order_picked": "18:40:00",
  "Weatherconditions": "conditions Sunny",
  "Road_traffic_density": "Low",
  "Vehicle_condition": 1,
  "Type_of_order": "Snack",
  "Type_of_vehicle": "motorcycle",
  "multiple_deliveries": "1",
  "Festival": "No",
  "City": "Urban"
}
```

---

## § Horizontal Scaling (min 66–72)

Repeat the § Manual Deploy steps on the **second** pre-provisioned instance:

```bash
ssh -i <your-key>.pem ec2-user@<INSTANCE_2_IP>
# ... same login / pull / run as before ...
```

Prove both independently work:
```bash
curl http://<INSTANCE_1_IP>:8000/
curl http://<INSTANCE_2_IP>:8000/
```
Talking point: both work, but there's no single address, no automatic failover, and no traffic
distribution — someone has to manually choose which IP to call.

---

## § Load Balancer (min 72–80) — 🎬 WOW #5: the fix, proven

Create live in the AWS Console (EC2 → Target Groups → Create target group):
- Target type: Instances. Protocol/port: HTTP, 8000. Health check path: `/`.
- Register both instances → Create.

Then EC2 → Load Balancers → Create Application Load Balancer:
- Scheme: Internet-facing. Listener: HTTP 80 → forward to the target group above.
- Wait for both targets to show `healthy` in the target group's Targets tab.

Prove it works:
```bash
curl http://<ALB_DNS_NAME>/
```

Re-run the **identical** load test from § Break It, pointed at the ALB instead:
```bash
hey -z 30s -c 200 http://<ALB_DNS_NAME>/
```
Expected: near-100% success rate this time, since load is now split across two instances.
Put this side by side with the § Break It output still on screen/in a second terminal pane for
the visual before/after.

Optional extra proof: tail logs on both instances during the test —
```bash
docker logs -f swiggy-app   # on each instance, in separate panes
```
— and show hits landing on both.

---

## § Monitoring (min 89–99) — 🎬 WOW #6: the alarm that never sleeps

This section had no existing implementation in the repo before this webinar — it's now real:
`app.py` exposes Prometheus metrics at `/metrics`, including a custom `ood_requests_total`
counter that increments whenever a `/predict` request's numeric features fall outside the
min/max range observed in `data/interim/train.csv` (computed by
`scripts/compute_feature_bounds.py` into `models/feature_bounds.json`). Prometheus scrapes it,
Grafana visualizes it, and a Grafana alert rule fires on it — see `monitoring/README.md` for full
setup. This must be brought up and dry-run **before** the talk, per the pre-webinar checklist.

Have three things on screen/tabs ready before this block starts:
1. The Grafana dashboard ("Swiggy Monitoring" folder → "Swiggy Delivery Time API") — showing the
   `ood_requests_total` panel and the p95 latency panel, currently flat/zero.
2. Grafana's Alerting → Alert rules page — showing "Out-of-distribution prediction requests
   spiking" in state `Normal`.
3. A terminal ready to fire the out-of-distribution payload below.

**Out-of-distribution payload** — same shape as `payload.json`, but with age and ratings the
model never saw in training (age 95 vs. a training max of 39, ratings 1.0 vs. a training min of
2.5 — computed live by `scripts/compute_feature_bounds.py`, not guessed). Keep the
restaurant/delivery coordinates close together like a normal order: an extreme distance (e.g. a
Bangalore→Delhi span) falls outside the `distance_type` bucketing in the cleaning pipeline and
gets silently dropped as a null row, which throws a 500 instead of the intended "quiet wrong
answer" — tested and confirmed locally, so don't reach for a dramatic distance here.
```json
{
  "ID": "0x2",
  "Delivery_person_ID": "RES1DEL02",
  "Delivery_person_Age": "95",
  "Delivery_person_Ratings": "1.0",
  "Restaurant_latitude": 12.9716,
  "Restaurant_longitude": 77.5946,
  "Delivery_location_latitude": 12.9352,
  "Delivery_location_longitude": 77.6146,
  "Order_Date": "19-03-2022",
  "Time_Orderd": "03:15:00",
  "Time_Order_picked": "03:55:00",
  "Weatherconditions": "conditions Stormy",
  "Road_traffic_density": "Jam",
  "Vehicle_condition": 0,
  "Type_of_order": "Buffet",
  "Type_of_vehicle": "bicycle",
  "multiple_deliveries": "3",
  "Festival": "Yes",
  "City": "Semi-Urban"
}
```
Save this as `ood_payload.json` before the talk. Tested end-to-end locally: this payload returns
a normal-looking prediction (~50.7 min) while `ood_requests_total` increments — no 500.

Live:
```bash
curl -X POST http://<INSTANCE_1_IP>:8000/predict \
  -H "Content-Type: application/json" \
  -d @ood_payload.json
# still returns a normal-looking predicted number — no crash, no error
```
Send it a handful of times (`for i in {1..5}; do curl ... ; done` works well on screen), then cut
to the Grafana dashboard: the "Out-of-distribution requests" panels move, and within about a
minute the Alerting page flips the rule from `Normal` → `Pending` → `Firing` (red).

Closing line while the alert is still on screen: "The performance test from the start of this
talk needed the right answers to check against — a held-out test set where we already knew the
real delivery times. Live traffic never comes with that attached; we don't know if a prediction
was right until well after the fact. So this watches the inputs instead, as an early warning,
running continuously, without the luxury of already knowing the answer."

Clean up after the talk: stop all containers, terminate/stop the demo EC2 instances, and delete
the load balancer + target group if they were only created for this demo, to avoid ongoing AWS
cost.
