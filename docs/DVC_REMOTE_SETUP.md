# Connecting DVC to the S3 Remote

This project uses an S3 bucket as the DVC remote for storing data and model artifacts tracked by the pipeline (`dvc.yaml`).

- **Bucket**: `my-swiggydvc `
- **Region**: `eu-north-1`
- **Remote name**: `s3remote`

## 1. Prerequisites

- `dvc` and `dvc-s3` installed (already in `requirements.txt`).
- AWS credentials with access to the bucket. Set them as environment variables — never hardcode them in `.dvc/config` or any tracked file:

```bash
export AWS_ACCESS_KEY_ID="<your-access-key-id>"
export AWS_SECRET_ACCESS_KEY="<your-secret-access-key>"
export AWS_DEFAULT_REGION="eu-north-1"
```

## 2. Add the remote (already done in this repo)

This is the command that configured `.dvc/config`. You only need to re-run it if setting up a fresh clone/remote from scratch:

```bash
dvc remote add -d s3remote s3://my-swiggydvc
```

This writes to `.dvc/config`:

```ini
[core]
    remote = s3remote
['remote "s3remote"']
    url = s3://my-swiggy-dvc
```

## 3. Push tracked data/artifacts to the remote

After running the pipeline (`dvc repro`) or pulling new data, push the tracked outputs to S3:

```bash
dvc push
```

## 4. Pull tracked data/artifacts from the remote

On a fresh clone, or to sync local data/model files with what's in the remote:

```bash
dvc pull
```

## 5. Verify the remote configuration

```bash
dvc remote list
```

## Notes

- AWS credentials are never committed to the repo. Locally, export them as environment variables (or configure the standard `~/.aws/credentials` file via `aws configure`). In CI, they are injected via GitHub Actions secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) as configured in `.github/workflows/ci_cd.yaml`.
- If an AWS key is ever exposed (e.g. pasted into a chat, log, or committed by mistake), rotate it immediately in IAM before continuing to use it.
