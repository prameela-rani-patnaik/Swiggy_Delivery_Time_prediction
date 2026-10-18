# EC2 Setup Commands (Amazon Linux 2023)

Exact commands used to get a fresh EC2 instance ready for this webinar's demo — Docker, AWS CLI
check, and Docker Compose (needed later for the monitoring stack). Run this on **every** instance
you provision (both EC2s for the load balancer section; if you're using the monitoring stack on
instance 1 specifically it needs Compose too).

Confirmed working against Amazon Linux 2023, `ec2-user`.

**Instance 1** used below: IP `3.110.114.41`, key `/Users/nikithmajeti/Downloads/swiggy-ec2-login.pem`.
When you provision instance 2, repeat every step with its own IP (the key may be the same or
different depending on what you chose at launch).

## 1. Fix key permissions and confirm SSH access

```bash
chmod 400 /Users/nikithmajeti/Downloads/swiggy-ec2-login.pem
ssh -i /Users/nikithmajeti/Downloads/swiggy-ec2-login.pem -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 ec2-user@3.110.114.41 \
  "echo connected: \$(whoami) on \$(hostname); cat /etc/os-release | head -3; docker --version 2>&1 || echo 'docker not installed'"
```

## 2. Install and start Docker

```bash
ssh -i /Users/nikithmajeti/Downloads/swiggy-ec2-login.pem -o ConnectTimeout=10 ec2-user@3.110.114.41 "
sudo yum update -y -q
sudo yum install -y docker -q
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
echo '--- versions ---'
docker --version
aws --version 2>&1 || echo 'aws cli not found'
"
```
`usermod -aG docker ec2-user` lets you run `docker` without `sudo` — log out and back in (new SSH
session) for the group change to take effect. AWS CLI came pre-installed on this AMI
(`aws-cli/2.33.15`) — nothing to do there.

## 3. Install Docker Compose (manual — AL2023's yum repo doesn't have `docker-compose-plugin`)

`sudo yum install -y docker-compose-plugin` fails on this AMI with
`Error: Unable to find a match: docker-compose-plugin`. Install the plugin binary directly
instead:

```bash
ssh -i /Users/nikithmajeti/Downloads/swiggy-ec2-login.pem -o ConnectTimeout=10 ec2-user@3.110.114.41 "
mkdir -p ~/.docker/cli-plugins
curl -sSL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
docker compose version
"
```
Result on this instance: `Docker Compose version v5.3.1`. (Use `docker-compose-linux-aarch64`
instead if the instance is Graviton/ARM — check with `uname -m`.)

## 4. Copy the monitoring folder over and start it

Prometheus + Grafana are a separate stack from the app — not baked into the app image, not part
of the CI/CD pipeline. Copy the folder over once and start it:

```bash
scp -i /Users/nikithmajeti/Downloads/swiggy-ec2-login.pem -r monitoring ec2-user@3.110.114.41:~/monitoring
```

```bash
ssh -i /Users/nikithmajeti/Downloads/swiggy-ec2-login.pem -o ConnectTimeout=10 ec2-user@3.110.114.41 "
cd monitoring
docker compose up -d
docker compose ps
"
```

Then verify (see `monitoring/README.md` steps 4–7 for the full dry run):

- Prometheus targets: `http://3.110.114.41:9090/targets` — `swiggy-time-api` job should show `UP`
- Grafana: `http://3.110.114.41:3000` — login `admin` / `admin`, then Dashboards → "Swiggy
  Monitoring" folder → "Swiggy Delivery Time API"
- Alerting → Alert rules → "Out-of-distribution prediction requests spiking" should show `Normal`

Make sure the instance's security group has inbound rules open for ports **3000** (Grafana) and
**9090** (Prometheus), same as you opened 8000 for the app.

## What this looked like end to end on instance 1

```
$ chmod 400 /Users/nikithmajeti/Downloads/swiggy-ec2-login.pem
$ ssh -i /Users/nikithmajeti/Downloads/swiggy-ec2-login.pem -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 ec2-user@3.110.114.41 "echo connected..."
Warning: Permanently added '3.110.114.41' (ED25519) to the list of known hosts.
connected: ec2-user on ip-172-31-7-181.ap-south-1.compute.internal
NAME="Amazon Linux"
VERSION="2023"
ID="amzn"
bash: line 1: docker: command not found
docker not installed

$ ssh ... "sudo yum install -y docker ..."
Docker version 25.0.14, build 0bab007
aws-cli/2.33.15 Python/3.9.25 Linux/6.18.38-73.137.amzn2023.x86_64 source/x86_64.amzn.2023

$ ssh ... "mkdir -p ~/.docker/cli-plugins && curl ... && docker compose version"
Docker Compose version v5.3.1
```

## Notes

- After this, ECR login + pulling the app image works the same way documented in
  `DEMO_RUNBOOK.md` § Manual Deploy.
- If you're setting up the monitoring stack on this instance too, `docker compose` from step 3 is
  what `monitoring/README.md` needs.
- Don't commit real instance IPs/paths like this file has if you ever make this repo public
  beyond the webinar — they're ephemeral (this EC2 instance won't outlive the demo) but still
  worth a mental note.
