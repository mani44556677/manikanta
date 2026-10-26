# Security scope

Never commit credentials, kubeconfigs, Terraform state, or real secret examples.
Report sensitive findings privately through GitHub private vulnerability reporting if enabled;
otherwise contact the repository owner privately without posting exploit details in an issue.

CI blocks HIGH/CRITICAL Trivy findings for the container and configuration and scans current
files for secrets. It does not replace full-history secret scanning, application SAST,
or a penetration test. The API has no third-party Python dependencies.
Enable GitHub secret scanning and push protection where available. Require CI on main.

Containers run as a numeric non-root user with no capabilities and a read-only filesystem.
Kubernetes disables service account token mounting and enforces restricted pod security.
NetworkPolicy enforcement requires a compatible CNI; a manifest alone does not enforce it.
Trivy uses versioned scanner images; pin image digests and refresh scanner versions before
using this as a production baseline. The Python base tag floats to receive patches; record
and pin its tested digest for a reproducible release. Review Dependabot updates.

ACR Basic has a public endpoint with authenticated access and admin credentials disabled.
Private endpoints/network isolation, AKS, OIDC federation, remote state and production
RBAC are follow-up work, not implemented security claims. No exceptions suppress findings.
