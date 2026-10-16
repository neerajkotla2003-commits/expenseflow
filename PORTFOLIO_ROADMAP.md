# Five enterprise-style portfolio projects

These are bounded demonstrations of enterprise problems, not claims of
enterprise readiness. Complete them in order. Only phase 1 of project 1 is
implemented in this starter. Later infrastructure and workflow configurations
will be supplied when their prerequisites exist.

| Order | Project and business problem | Users | Distinctive scope | Stack and data | GCP platform/services | Difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ExpenseFlow: slow, inconsistent employee expense approvals | Employees, managers, finance | Policy checks, approval transitions, no self-approval, receipts, audit timeline | FastAPI, Jinja/JS, SQLAlchemy, Alembic, MySQL | Cloud Run; Cloud SQL, Cloud Storage | Beginner to intermediate |
| 2 | SupportDesk: tickets missed or escalated too late | Customers, agents, supervisors | Assignment, SLA deadlines, authenticated delayed tasks, safe retries, escalation dashboard | FastAPI, Jinja/JS, Firestore | Cloud Run; Firestore, Cloud Tasks | Intermediate |
| 3 | ReconcileOps: invoice and payment spreadsheets do not match | Finance operations | CSV validation, deterministic matching, duplicate detection, retry-safe runs, exception reports | FastAPI, Pandas, MySQL | Cloud Run service + Cloud Run Job; Cloud Storage, Cloud SQL | Intermediate |
| 4 | StockGuard: concurrent orders oversell limited inventory | Buyers, warehouse operators | Atomic stock reservations, reservation expiry, transactional outbox, idempotent fulfillment worker | FastAPI, MySQL, Pub/Sub consumer | GKE; Cloud SQL, Pub/Sub | Intermediate to advanced |
| 5 | WatchTower: slow detection of service outages and duplicate incidents | Support teams, service owners | Allowlisted synthetic checks, consecutive-failure thresholds, incident deduplication, recovery timeline | FastAPI, Python checker/worker, Firestore | GKE; Pub/Sub, Firestore | Intermediate to advanced |

All projects use GitHub, GitHub Actions, Artifact Registry, managed identity,
Secret Manager where secrets are needed, Cloud Logging and Cloud Monitoring.
Begin with a small server-rendered interface; frontend frameworks are optional.
Use fictional users and data. Avoid real reimbursements, payments and customer data.

## Platform choices

ExpenseFlow and SupportDesk are stateless request/response services: managed
HTTP scaling saves operational work. SupportDesk uses authenticated Cloud Tasks
callbacks rather than assuming in-process timers survive Cloud Run scale-down.
Each callback rechecks the ticket state and ignores obsolete task versions.

ReconcileOps separates short API requests from finite batch work. A Cloud Run
Job processes each uploaded batch and exits; job status and progress live in the
database. Begin with strict CSV size and row limits, exact invoice-ID matching,
and a fake payments CSV. No bank integration or fuzzy matching is required.

StockGuard introduces separately scaled API and continuously polling consumer
deployments, Kubernetes probes, resource requests, rolling updates and HPA.
One database transaction reserves stock and writes an outbox event; publishing
and processing are retry-safe. Never assume Pub/Sub delivery is exactly once.

WatchTower introduces an independently scheduled checker (Kubernetes CronJob),
an API and a long-running incident consumer. Start with a fixed allowlist of
your own demo endpoints and bounded timeouts/concurrency. A demo endpoint can
intentionally return errors. Avoid an arbitrary public URL-fetching service.

GKE is useful here to learn workload operations. Cloud Run plus managed services
could also implement projects 4 and 5. Kubernetes is an explicit learning choice,
not a claim that small applications inherently require it.

## Repeatable phases

1. Define one demo scenario, business invariants and a tested local vertical slice.
2. Add persistence, migrations, constraints and integration tests.
3. Add managed sign-in, verified tokens, stored roles/ownership checks and a minimal UI.
4. Package a non-root container; test/build on GitHub without cloud credentials on PRs.
5. Configure GCP, keyless CI identity and least-privilege runtime identities; deploy.
6. Add operational checks: structured logs, alerts, bounded scaling and rollback drills.
7. Capture evidence, finish README/architecture/demo/resume bullets, then clean up.

Each checkpoint has commands, expected results and a troubleshooting decision.
Proceed only after the user verifies the current checkpoint on their machine.

## Deployment pipeline target

PR: tests (including negative auth tests and database integration tests where
relevant) -> container build. No production deployment or cloud secrets on PRs.

Main: tests -> build -> Artifact Registry -> deploy immutable image digest ->
health/synthetic smoke checks -> record commit, image and revision.
Use GitHub OIDC and Workload Identity Federation restricted to the intended
repository/owner and main deployment context. Separate deploy and runtime identities.
Never store a long-lived GCP service-account JSON key in GitHub.

Cloud Run rollback: route traffic to a previously verified revision. GKE rollback:
restore a previous known image/Deployment revision. Database changes require
backward-compatible migrations; application rollback does not undo data changes.
Run migrations once in a controlled deployment job, not in every API replica.

## Practices to implement versus further enterprise work

| Portfolio implementation target | Further enterprise work |
| --- | --- |
| Managed sign-in; server-side role and ownership checks | Corporate federation, account lifecycle, MFA policy and access reviews |
| Migrations, constraints, transactions and a small restore exercise | Tested recovery objectives, HA/DR, retention and regular restore drills |
| Secret Manager and least-privilege workload identities | Organization-wide policy, rotation and formal IAM reviews |
| Structured redacted logs, request IDs, basic metrics and alerts | SLOs, paging ownership, distributed tracing and response procedures |
| Bounded retries, idempotency, dead-letter handling for workers | Load/failure testing and capacity planning at measured traffic |
| Immutable images, dependency scanning, health checks and rollback drill | Artifact provenance, release governance and independent security review |

None of the target column is implemented merely by describing it here.

## Cost and cleanup plan

- Work locally first. Use one active cloud project application at a time.
- Choose a region deliberately (for example asia-south1 for India); colocate
  application, storage and database where supported. Check regional estimates.
- Cloud Run: request-based billing, minimum instances 0, initial maximum 2,
  modest resource allocation and bounded upload/job sizes. Cold starts are acceptable.
- Cloud SQL has compute/storage/backup charges independent of Cloud Run traffic.
  Use local MySQL through development; provision a small demo instance late.
  Reuse a demo instance sequentially with separate databases and least-privilege
  application users if appropriate. Do not leave five instances running.
- Use one GKE cluster sequentially for the final two projects, with separate
  namespaces if they overlap. Practice on local Kubernetes first. GKE free-tier
  cluster credits do not cover all compute, disks or load-balancer charges.
- Set billing alerts at 50%, 80%, 100% of a personally affordable budget. Alerts
  are notifications, not a spending cap. Limit job retries and worker concurrency.
- After a demo: preserve source, deployment manifests, sanitized screenshots and
  a video. Export required demo data. Delete unused services/jobs, task queues,
  SQL instances/backups as appropriate, buckets, Pub/Sub resources, secrets and
  unused image versions. Review retained data before deleting anything.
- For GKE delete exposed Services/Ingress first; then workloads/cluster. Inspect
  remaining load balancers, disks, reserved IPs, logs retention and SQL backups.
  Deleting a namespace or cluster alone is not proof that billing has stopped.
- Verify resource inventory and billing afterwards; billing reporting may lag.
  Exact scoped cleanup commands will accompany each cloud deployment phase.

No fixed monthly price is promised: region, runtime, traffic, database size and
credits determine actual charges. Keep a deploy-on-demand portfolio with demo
videos rather than maintaining five services continuously.

## Evidence at completion

For each project: README with setup/limitations, diagram matching deployed
resources, one normal demo and one failure demo, CI run link, tested rollback
notes, cleanup instructions, interview Q&A and accurate resume bullets.
Only report measured latency, test counts and other metrics you actually obtained.

## Official references (checked 2026-10-15)

- Cloud Run autoscaling: https://docs.cloud.google.com/run/docs/about-instance-autoscaling
- Cloud Run pricing: https://cloud.google.com/run/pricing
- Cloud SQL pricing: https://cloud.google.com/sql/pricing
- GKE pricing: https://cloud.google.com/kubernetes-engine/pricing
- Budget alerts: https://docs.cloud.google.com/billing/docs/how-to/budgets
- CI identity: https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
