# Manikanta | DevOps release showcase

A practical portfolio lab: take a small **Release Status API** from tests to a hardened
Docker container, validate it in GitHub Actions, run it in Kubernetes, and prepare an
Azure registry with Terraform. The `/` response reports the image's build commit so
an operator can prove which release is running and demonstrate rollback.

**Status:** starter implementation. Local Python tests are runnable now. CI performs
container, schema, Terraform and security checks. No Azure resources or hosted service
are created automatically. This is a learning lab, not a production platform.

## Architecture and scope

Git commit → API tests → Terraform/schema validation → secret/config scans → Docker
build → vulnerability scan → container smoke test. Local Kubernetes deployment is manual.
Azure ACR infrastructure is optional. GitHub Actions is the primary CI; `Jenkinsfile`
provides an optional alternative on a dedicated Docker-capable agent.

| Path | Purpose |
| --- | --- |
| `app/server.py`, `app/test_server.py` | Dependency-free JSON API and HTTP integration tests |
| `Dockerfile`, `.dockerignore`, `compose.yaml` | Non-root container and local startup |
| `.github/workflows/ci.yml` | Validation, build, security gates and smoke test |
| `.github/dependabot.yml` | Action, base-image and provider update proposals |
| `k8s/` | Namespace, Deployment, ClusterIP Service, NetworkPolicy |
| `infra/terraform/` | Azure resource group and Basic ACR starter |
| `Jenkinsfile` | Optional test/build/scan pipeline |
| `docs/runbook.md` | Deploy, verify, break, roll back and clean up |
| `SECURITY.md` | Implemented controls, limitations and next hardening steps |

## Start here: first implementation milestone

Use Python 3.12, Docker with Compose, Git, and curl. Run from the repository root:

```bash
python3 -m unittest discover -s app -p 'test_*.py' -v
python3 -m app.server
# In a second terminal:
curl --fail http://localhost:8080/healthz
curl --fail http://localhost:8080/
```

Stop the Python process, then try the same API in Docker:

```bash
docker compose up --build -d
curl --fail http://localhost:8080/healthz
curl --fail http://localhost:8080/
docker compose down
```

The container serves port 8080, uses UID 10001, drops capabilities, and works with a
read-only root filesystem. The Python standard-library server keeps this demo small;
replace it with a maintained application framework/server before production use.

## Implement in this order

1. **API + container:** run the tests and both startup paths above. Save actual output
   and explain how `/healthz` differs from `/` (health versus release identity).
2. **CI:** merge the starter after reviewing its CI result. Require the `verify` check
   on `main`. Resolve scanner findings rather than disabling the gates. A failing scan
   is an actionable result; scanner databases and base-image findings change over time.
3. **Local Kubernetes:** follow [the runbook](docs/runbook.md). Show two replicas,
   readiness, version verification, a failed rollout and recovery. Keep screenshots
   or sanitized logs from your own run, with dates and commit IDs.
4. **Azure infrastructure:** authenticate locally, inspect a Terraform plan, then
   create the resource group and ACR only if you want the paid cloud milestone.
5. **CD extension:** add AKS, least-privilege Azure federated OIDC identity, ACR pull
   permission for the kubelet identity, a protected GitHub environment, image publishing
   and digest-based deployment. Verify `/` matches the expected commit after rollout.
   This is future work; the current workflow builds and tests without publishing.
6. **Operations extension:** add metrics/alerts, an ingress with TLS and a controlled
   smoke-test failure/rollback exercise. Compare the optional Jenkins pipeline with
   Actions once the primary path works; avoid maintaining two pipelines initially.

## Terraform: optional Azure starter

Requires Azure CLI login, Terraform 1.9.x, a subscription and permission to create
resource groups and registries. **ACR is billed even without AKS.** Set a budget and
remove the demo when finished. Never use a shared production subscription for this lab.

```bash
az login
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit subscription_id and choose a globally unique registry_name.
terraform init
terraform fmt -check
terraform validate
terraform plan -out=demo.tfplan
# Review the complete plan before running:
terraform apply demo.tfplan
terraform output registry_login_server
# When finished, review and confirm removal of this demo:
terraform destroy
```

Commit the generated `.terraform.lock.hcl` after reviewing it; it is intentionally not
fabricated in this starter. Local state is for a single-user lab and is ignored by Git.
Before team/CI applies, bootstrap an Azure Storage backend, migrate state, restrict
access and use locking. Do not pass Azure secrets into pull-request workflows.

## Evidence to show in an interview or LinkedIn post

- Successful CI run URL and an example security finding you fixed.
- The exact commit returned by a running container and a Kubernetes deployment.
- A failed rollout, diagnosis using events/logs, and verified recovery.
- A sanitized Terraform plan and proof that demo resources were removed.

Describe only the stages you actually ran. Do not claim production deployment, zero
vulnerabilities, automatic rollback or AKS delivery until those are implemented and tested.

## Reference documentation

- [GitHub Actions security](https://docs.github.com/en/actions/security-for-github-actions)
- [Kubernetes deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [AzureRM provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Trivy](https://trivy.dev/)
