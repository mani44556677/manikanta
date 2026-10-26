# Local deployment and recovery runbook

Prerequisites: Docker, kind, kubectl, curl. Use an isolated kind cluster and verify
`kubectl config current-context` is `kind-showcase` before changing anything.

## Build and deploy

```bash
kind create cluster --name showcase
kubectl config current-context
docker build --build-arg APP_VERSION=v1-demo -t release-status:local .
kind load docker-image release-status:local --name showcase
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
kubectl -n showcase rollout status deployment/release-status --timeout=120s
kubectl -n showcase get pods
kubectl -n showcase port-forward service/release-status 8080:80
# In a second terminal:
curl --fail http://localhost:8080/healthz
curl --fail http://localhost:8080/
```

Expect `v1-demo` from `/`. Port forwarding is for operator access and does not prove
NetworkPolicy enforcement. The policy permits only pods in the same namespace with
label `access: release-status` on port 8080; app egress is denied because it has no
external dependencies. Default kind networking does not enforce NetworkPolicy; install
a supporting CNI in a separate exercise before claiming network isolation. Kubelet
health probes are node traffic. There is no ingress, public load balancer or DNS need.

## Deploy a second release

Use a new immutable tag rather than overwriting the running tag:

```bash
docker build --build-arg APP_VERSION=v2-demo -t release-status:v2-demo .
kind load docker-image release-status:v2-demo --name showcase
kubectl -n showcase set image deployment/release-status api=release-status:v2-demo
kubectl -n showcase rollout status deployment/release-status --timeout=120s
```

Restart the port-forward if it disconnects; verify `/` reports `v2-demo`. In a registry
release, tag with the Git commit and deploy by image digest. The checked-in image is a
local starter; reapplying the Deployment resets its image to `release-status:local`.

## Failure drill and rollback

```bash
kubectl -n showcase set image deployment/release-status api=release-status:does-not-exist
kubectl -n showcase rollout status deployment/release-status --timeout=120s
# The previous command is expected to fail. Investigate:
kubectl -n showcase get pods
kubectl -n showcase get events --sort-by=.lastTimestamp
kubectl -n showcase describe deployment release-status
kubectl -n showcase rollout history deployment/release-status
kubectl -n showcase rollout undo deployment/release-status
kubectl -n showcase rollout status deployment/release-status --timeout=120s
```

Reconnect port-forward and verify `/` returns `v2-demo` and `/healthz` is healthy.
This is a **manual** recovery exercise. A Deployment reports failure but does not
roll back automatically. A future CD job must capture the previous image digest,
check rollout plus expected-version HTTP response, restore the previous digest on
failure, and fail the job even if recovery succeeds. Serialize deployments and account
for database compatibility before implementing automatic rollback.

## Azure registry milestone

After Terraform creates ACR, use its output as `REGISTRY` (for example
`yourname.azurecr.io`) and the current commit as `TAG`:

```bash
export REGISTRY=REPLACE_WITH_ACR_LOGIN_SERVER
export TAG=$(git rev-parse HEAD)
az acr login --name "${REGISTRY%%.*}"
docker build --build-arg APP_VERSION="$TAG" -t "$REGISTRY/release-status:$TAG" .
docker push "$REGISTRY/release-status:$TAG"
```

The signed-in principal needs ACR push permissions. ACR is private by authentication;
AKS kubelet pull access and OIDC are not provisioned here. Do not put registry passwords
in Kubernetes YAML. Add AKS and identity wiring as a reviewed infrastructure milestone.

## Cleanup and evidence

Record sanitized CI output, app version, rollout history and lessons learned. Never
capture tokens or state in screenshots. Delete the local cluster:

```bash
kind delete cluster --name showcase
```

Separately run `terraform destroy` from `infra/terraform` if you created Azure resources.
Deleting the kind cluster does not remove ACR. Verify deletion in Azure.
