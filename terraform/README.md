# Terraform deployment

This configuration deploys the RAG Workbench container to AWS App Runner and creates the ECR
repository used by the service.

## Prerequisites

- Terraform 1.6+
- AWS credentials configured for the target account
- Docker installed

## Deploy

```bash
terraform init
terraform apply
```

Build and push the image using the `ecr_repository_url` output:

```bash
REPOSITORY=$(terraform output -raw ecr_repository_url)
REGION=us-east-1
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$REPOSITORY"
docker build -t "$REPOSITORY:latest" ..
docker push "$REPOSITORY:latest"
```

Because the service uses immutable App Runner deployments, apply again after pushing a new tag:

```bash
terraform apply -var='image_tag=2026-09-14'
```

The service exposes `/health`, `/documents`, `/query`, and the browser UI at `/`. The default
configuration runs without an LLM and returns retrieved evidence. Set `llm_base_url` and
`llm_model` to connect an OpenAI-compatible endpoint.

## Cost and security notes

Review App Runner and ECR pricing before deployment. The Terraform configuration creates an ECR
access role and enables image scanning, but application-level authentication and authorization
must be added before exposing private documents to untrusted users.
