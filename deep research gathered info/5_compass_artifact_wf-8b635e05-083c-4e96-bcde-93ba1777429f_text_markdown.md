# SAA-C03 FINAL MEGA-RESEARCH DELIVERABLE — Dublin Edition (Pass 3 of 3)
### Prepared for: Sanky, Dublin, Ireland | Current date: 6 June 2026
### Format: Raw, dense research notes — masterclass source material. Verified facts vs. inferences are explicitly labelled.

---

## TL;DR
- **The SAA-C03 exam is 65 questions in 130 minutes, scored 100–1000 with 720 to pass** (50 scored + 15 unscored pilot questions; compensatory scoring — you pass on the overall, not per-domain). Domain weights: **Security 30% / Resilient 26% / High-Performing 24% / Cost-Optimized 20%.** Fee is **150 USD** (note: some 2026 sources list ~300 USD — verify on the official AWS pricing page near your booking date). Fail → **14-day cooling period**, unlimited attempts.
- **Dublin companies are ideal memory anchors:** Ryanair (all-in AWS, Aurora, S3+Kinesis lake, **22M emails/day**), Intercom (Aurora MySQL → Vitess/PlanetScale migration), Coinbase (**3,500 services on EKS+Graviton+Karpenter**, MSK, the May 7 2026 outage), Fenergo (event-sourcing/CQRS on DynamoDB+EventStoreDB), Flutter/PokerStars (EKS+MSK+Cloud WAN, **20% TCO cut, 1,100 apps + 3 PB migrated**).
- **Three critical corrections from this pass:** (1) The May 7 2026 Coinbase MSK control-plane defect hit **both 2-AZ and 3-AZ clusters** — 3-AZ reduces blast radius but did NOT cure the defect; (2) **Revolut and N26 are Google-Cloud-primary, not AWS** — use Starling Bank as the AWS neobank exemplar; (3) **Intercom has migrated off Aurora** to Vitess/PlanetScale — treat Aurora facts as historical.

---

## KEY FINDINGS — VERIFIED FACTS LEDGER

| Company | Verified AWS / Architecture Facts | Source quality |
|---|---|---|
| **Ryanair** | All-in AWS; migrated **Microsoft SQL Server → Amazon Aurora**; **"sending out 22 million emails daily"** (CTO John Hurley, AWS/Ryanair press release, 10 May 2018); S3 data lake + Kinesis real-time analytics; SageMaker (demand forecasting); Lex (support routing); Alexa skill; Storage Gateway Tape Gateway (**65% savings**); S3 Object Lambda (COVID wallet); MSK event-driven gate system with Manchester Airports Group; Bedrock employee app | First-party + AWS case study |
| **Intercom** | Was Aurora MySQL default (**hundreds of TB, 2M reads/sec**, function-sharded then per-customer); ProxySQL writer pooling (2017); ElastiCache memcached; DynamoDB for very-high read/write; Elasticsearch for search. **NOW migrating to Vitess managed by PlanetScale (PlanetScale Metal)** — VTGate eliminates ProxySQL + the **16,000-connection-per-MySQL-host Aurora limit** (Inbox "would routinely require 135,000 active connections"). Ember.js + Rails monolith; 3 regions (US/EU/AU) | First-party eng blog |
| **Coinbase** | **Migrated 3,500 services EC2 → EKS + Graviton** (AWS case study: "Scales 50% Faster, Cuts Costs 62%"); Graviton ~20% lower cost; **Karpenter delivered an additional ~10% compute savings** (NOT 20%); MSK ingests **"billions of events daily"** at **<10ms e2e latency** (vs ~200ms on Kinesis); 30-broker prod cluster with headroom to 90; CCoE for cost optimization; kubetools; CLB→ALB automation | First-party + AWS case study + re:Invent PRO303 (2024) |
| **Coinbase May 7 2026 outage** | AWS us-east-1 thermal/chiller event in **use1-az4**; **MSK control-plane defect prevented automatic partition-leader reelection** → 2 clusters stuck "healing," producers blocked → cascaded to fee service → quoting → broken trades; matching engine lost Raft quorum (3 of 5 nodes in a Cluster Placement Group terminated); **manual partition reassignment at 3:00 AM ET**; **the defect hit 2-AZ AND 3-AZ clusters similarly**; remediation = **migrating 2-AZ Kafka → 3-AZ** + runbooks | First-party postmortem (1 Jun 2026) |
| **HubSpot** | **"As of July 2022, ~4,000 Kafka topics spread across 80 clusters"**; HBase on Graviton (im4gn/is4gen NVMe; **"almost 100 production HBase clusters, over 7000 regionservers across two regions," "over 2.5 PB of low latency traffic per day"**); EKS + historical Mesos; 9,000+ deployable units; "Hublet" multi-region (na1/eu1) | First-party eng blog |
| **Flutter/PokerStars** | **"Migrated 1,100 applications and 3 PB of data... 70% of on-premises footprint"; "reduced its TCO by 20 percent"; "production change rate sped up by 40 percent"; 33 data centers; 850,000 hands/hour; 3.4M players in 140 countries**; EKS, MSK, Cloud WAN + Network Firewall, Systems Manager, multi-account, S3, CloudWatch | AWS case study + OpsGuru |
| **Fenergo** | Event-sourcing + CQRS; DynamoDB state/read DB (TTL, optimistic locking, Streams CDC); EventStoreDB (3 nodes / 3 AZs: leader/follower/readonly); API Gateway WebSockets + 2 Lambdas; MemoryDB for connection store; EventBridge fanout; circuit breaker; Step Functions for cluster updates | First-party eng blog |
| **Stripe** | PCI DSS Level 1; EC2/Lambda/S3/KMS/Shield; **~3,000 engineers, 360 teams, 500M metrics/10s**; Amazon Managed Service for Prometheus + Managed Grafana for observability | AWS case study |
| **Workday** | Born-in-cloud; AWS primary since 2016 (+GCP, +Azure for Adaptive Planning); EKS; **DataSync moved 8+ PB to observability data lake**; Docker/K8s; weekly zero-downtime releases | First-party podcast + APN blog |
| **Revolut / N26** | **Revolut = Google Cloud primary** (Compute Engine, IAM, incremental snapshots; Java/Kotlin event-driven, Postgres event store). **N26 = GCP** (HashiCorp Nomad, Kotlin/Java Spring Boot, 100+ microservices). NOT AWS-primary | Google Cloud case study + InfoQ |
| **AIB** | Hybrid; **IBM z15 mainframe (€65m 3-yr IBM deal, 2021)**; nCino cloud banking on AWS; Accenture. NOT all-in AWS | IBM newsroom + Computer Weekly |

---

## PART 1 — DEEP DUBLIN COMPANY ARCHITECTURES (Expansion)

### 1. RYANAIR — All-In AWS Airline

**(a) Business/regulatory context.** Europe's largest airline (~600 aircraft, 240+ destinations, 40 countries). Regulations: **GDPR** (passenger PII), **PCI DSS** (card payments), **PSD2** (payment initiation/SCA), **EU261** (consumer compensation), **NIS2** (critical transport infra). Drove a 3-year program to **close the majority of its data centers** and standardize on AWS.

**(b) Verified AWS footprint.** Aurora (replaced MS SQL Server); S3 company-wide data lake + Kinesis real-time analytics; SageMaker (forecasts demand for "tea, ham and cheese paninis, and chocolate croissants" per route); Lex (support routing); Alexa MyRyanair skill; **Storage Gateway Tape Gateway** (65% backup savings, per senior systems engineer Paul Walsh); **S3 Object Lambda** (COVID mobile wallet); **MSK** (event-driven live-gate system with Manchester Airports Group); **Bedrock** (employee app); Couchbase (offline reservations). CTO John Hurley; Head of Software Dev Juan Valdés Gayo (Ryanair Labs).

**(c) Inferred architecture across 25 SAA-C03 topics:**
- **EC2/Compute:** ASG of stateless web/API tiers behind ALB for Ryanair.com and Ryanair Rooms; Graviton candidates for cost.
- **Storage:** S3 lake (raw/curated zones), lifecycle → Glacier Deep Archive for old booking records; EBS gp3 for any stateful nodes.
- **Database:** Multi-AZ Aurora MySQL/PostgreSQL writer + reader endpoints; DynamoDB for cart/session; ElastiCache for fare/price caching.
- **Networking:** VPC with public ALB subnets + private app subnets + NAT; Route 53 latency + failover routing; CloudFront for static + image assets.
- **Decoupling:** SQS/SNS/EventBridge for booking-confirmation, schedule-change events; Kinesis for clickstream.
- **Serverless:** Lambda glue + S3 Object Lambda; Step Functions for booking sagas.
- **Security:** WAF on CloudFront+ALB; KMS for PII; Secrets Manager for DB creds; GuardDuty/Security Hub; Cognito for MyRyanair identity.
- **Scaling:** Predictive + scheduled scaling for holiday/Brexit volatility.
- **Cost:** Savings Plans + Spot for batch/ETL; Intelligent-Tiering; Cost Explorer/Budgets.

**(d) Terraform sketch (illustrative, educational):**
```hcl
module "vpc" {
  source             = "terraform-aws-modules/vpc/aws"
  name               = "ryanair-prod"
  cidr               = "10.0.0.0/16"
  azs                = ["eu-west-1a","eu-west-1b","eu-west-1c"]
  private_subnets    = ["10.0.1.0/24","10.0.2.0/24","10.0.3.0/24"]
  public_subnets     = ["10.0.101.0/24","10.0.102.0/24","10.0.103.0/24"]
  enable_nat_gateway = true
  single_nat_gateway = false   # one NAT per AZ for resilience
}

resource "aws_rds_cluster" "aurora" {
  engine                 = "aurora-mysql"
  engine_mode            = "provisioned"
  database_name          = "bookings"
  master_username        = "admin"
  manage_master_user_password = true        # → Secrets Manager
  storage_encrypted      = true
  kms_key_id             = aws_kms_key.db.arn
  db_subnet_group_name   = aws_db_subnet_group.this.name
  backup_retention_period = 14
  preferred_backup_window = "02:00-03:00"
}
resource "aws_rds_cluster_instance" "writer" {
  count              = 1
  cluster_identifier = aws_rds_cluster.aurora.id
  instance_class     = "db.r6g.xlarge"      # Graviton
  engine             = aws_rds_cluster.aurora.engine
}
resource "aws_rds_cluster_instance" "readers" {
  count              = 2
  cluster_identifier = aws_rds_cluster.aurora.id
  instance_class     = "db.r6g.large"
  engine             = aws_rds_cluster.aurora.engine
}

resource "aws_s3_bucket" "lake" { bucket = "ryanair-data-lake-prod" }
resource "aws_s3_bucket_lifecycle_configuration" "lake" {
  bucket = aws_s3_bucket.lake.id
  rule {
    id     = "archive-old"
    status = "Enabled"
    transition { days = 90  storage_class = "INTELLIGENT_TIERING" }
    transition { days = 365 storage_class = "GLACIER" }
  }
}

resource "aws_kinesis_stream" "clickstream" {
  name             = "ryanair-clickstream"
  shard_count      = 10
  retention_period = 24
  stream_mode_details { stream_mode = "ON_DEMAND" }
}
```

**(e) Engineer workflow narratives (representative).**
- *Platform engineer:* owns Terraform modules in a mono-repo, runs `terraform plan` in CI on PRs, manages the landing-zone account structure via Organizations + Control Tower, maintains the golden AMI pipeline (Image Builder), and triages drift. A typical ticket: "Add a NAT gateway per-AZ to the booking VPC and migrate the Aurora cluster to Graviton r6g."
- *SRE:* on-call rotation watching CloudWatch alarms + dashboards for Aurora replica lag, ALB 5xx, Kinesis IteratorAge. Runbooks for Aurora failover (RDS reboots to a reader in <30s), Storage Gateway tape recovery. Practices game-days for AZ failure.
- *Security engineer:* manages WAF rule groups, reviews GuardDuty findings, rotates KMS keys, audits IAM via Access Analyzer, runs Audit Manager for PCI evidence.
- *Backend dev:* ships Lambda + ECS services, uses Secrets Manager for DB creds, instruments with X-Ray, codes idempotent booking handlers backed by SQS.
- *Data engineer:* builds Kinesis → S3 → Glue → Athena/Redshift pipelines; feeds SageMaker demand-forecasting models; manages data-lake partitioning + lifecycle.

**(f) Failure modes (real + plausible).** Brexit-driven traffic volatility → **predictive auto-scaling**. Unreliable physical tape backup → **Storage Gateway Tape Gateway migration (verified, 65% savings)**. Slow feature delivery for COVID wallet → **S3 Object Lambda** to transform on GET.

**(g) Interview talking points.** *"Ryanair runs one of Europe's largest email campaigns — 22 million emails a day — and moved it from SQL Server to Aurora for higher performance at a fraction of the cost; the lesson is that for a managed, MySQL/Postgres-compatible relational engine with read-replica scaling and minimal admin, Aurora is almost always the SAA answer over self-managed RDBMS on EC2."*

**(h) Exam pattern mapping:** "migrate commercial DB with minimal admin → Aurora"; "ingest real-time clickstream → Kinesis to S3"; "replace physical tape backup → Storage Gateway Tape Gateway"; "transform S3 objects per-request without copies → S3 Object Lambda"; "predictable spiky traffic → scheduled + predictive scaling."

---

### 2. INTERCOM — Customer Messaging SaaS

**(a) Business/regulatory.** GDPR, SOC 2, data residency across US/EU/AU; Fin AI bot resolves customer conversations — "when Intercom is down, large parts of [customers'] business is down too."

**(b) Verified footprint (historical Aurora era).** Aurora MySQL default DB (**hundreds of TB, 2M reads/sec, tens of thousands of writes/sec**), sharded first by function then per-customer (complete early 2020); **ProxySQL** writer connection pooling (rolled out 2017); ElastiCache **memcached** caching layer; DynamoDB used **sparingly** for very-high read/write; Elasticsearch (sharded indices) for Inbox Views, Articles, Outbound, Reporting, Resolution Bot. Ember.js teammate app + **Ruby on Rails monolith** on dedicated per-function clusters (web/API/async). Black Friday auto-scales without human intervention.

**(b′) Current migration (KEY UPDATE — verified).** Moving **off Aurora + custom sharding → Vitess managed by PlanetScale (PlanetScale Metal:** semi-synchronous, row-based MySQL replication to ≥3 replicas across 3 AZs). **VTGate eliminates ProxySQL** and Aurora's **16,000-connection-per-MySQL-host limit** — "the database that powers the Inbox would routinely require 135,000 active connections." Zero-downtime maintenance; the Contacts DB (Aurora 1→2 upgrade had taken **6 months**) migrated in a couple of weeks on Metal.

**(c) Inferred 25-topic mapping:** ALB + ASG for Rails clusters; ElastiCache for hot reads; OpenSearch managed for search at scale (or self-managed Elasticsearch as they do); DynamoDB on-demand for high-velocity counters; SQS for async workers; KMS at-rest; Multi-AZ everywhere; CloudFront for static assets; Route 53 geo-routing for regional isolation.

**(d) Terraform sketch (ElastiCache + DynamoDB):**
```hcl
resource "aws_elasticache_replication_group" "memcached_layer" {
  replication_group_id = "intercom-cache"
  description          = "front-of-DB cache"
  engine               = "redis"          # ValKey/Redis for HA; memcached for pure cache
  node_type            = "cache.r7g.large" # Graviton
  num_node_groups      = 3
  replicas_per_node_group = 1
  automatic_failover_enabled = true
  multi_az_enabled     = true
}
resource "aws_dynamodb_table" "high_velocity" {
  name         = "intercom-events"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"
  attribute { name = "pk" type = "S" }
  attribute { name = "sk" type = "S" }
  ttl { attribute_name = "expires_at" enabled = true }
  point_in_time_recovery { enabled = true }
  stream_enabled = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
}
```

**(e) Workflow narratives.** Platform/DB-reliability engineers own the Vitess/PlanetScale migration (the "running less software" philosophy), running per-customer shard cutover playbooks. SREs handle connection-storm incidents (the ProxySQL 2.x instability outages). Backend devs work in the Rails monolith with strict per-function cluster boundaries.

**(f) Failure modes (verified).** ProxySQL 2.x upgrade → instability/outages. Aurora 1→2 Contacts upgrade → 6 months of engineering. Read-replica hang blocking SELECTs → fallback routing to primary (the Pismo/ProxySQL chaos-test pattern).

**(g) Talking points.** *"Intercom's journey is the canonical 'connection-limit' story: a Rails fleet exhausting Aurora's per-host connection cap led to ProxySQL pooling and ultimately Vitess. On the exam, when a fleet of app servers exhausts RDS connections, the answer is RDS Proxy / connection pooling — not bigger instances."*

**(h) Exam patterns:** "RDS connection exhaustion under serverless/large fleets → RDS Proxy"; "scale reads → reader endpoint + replicas"; "DB cache layer → ElastiCache"; "full-text search → OpenSearch"; "horizontal write scaling on MySQL → sharding (Vitess) / Aurora Limitless equivalent."

---

### 3. COINBASE — Crypto Exchange

**(a) Business/regulatory.** NYSE:COIN; MiCA (EU), VASP registration, SOC 1/2; "traffic surges comparable to a massive video game launch — but we never know when launch day is."

**(b) Verified footprint.** **3,500 services on EKS + Graviton** (multi-arch ARM64/AMD64 images, taints/tolerations to pin ARM workloads); migration in 12 months with AWS Professional Services "pods" + kubetools; **Karpenter** replaced Cluster Autoscaler (old: 15-min timeout, single upgrade attempt) for ~10% additional compute savings; **MSK** ingests "billions of events daily" at **<10ms e2e latency** (vs ~200ms Kinesis), 30-broker prod cluster (headroom to 90 via support ticket); Aurora (migrated from RDS singles, auto-scaling, Graviton); **S3 Intelligent-Tiering as the org default** + lifecycle; CCoE aligned to Well-Architected.

**(c) The May 7 2026 outage (verified first-party postmortem, the centrepiece failure-mode case study).**
- Trigger: AWS us-east-1 **thermal event — chiller units failed in data hall use1-az4**, thermal-safety shutdown took EC2/EBS offline at 7:20 PM ET.
- **MSK control-plane defect prevented automatic partition-leader reelection** → two MSK clusters stuck in a "healing" state, producers unable to write → cascaded: **fee service blocked → quoting blocked → customers saw broken trades/quotes** (plus ledger, payments, data pipelines).
- The matching engine lost **Raft quorum** when AWS terminated 3 of 5 nodes in a **Cluster Placement Group**.
- Recovery: **manual partition reassignment at 3:00 AM ET**; P0/P1 topics restored by 9:30 AM ET; full recovery ~2:00 PM ET. ~8 hours disruption.
- **CRITICAL NUANCE:** Coinbase states the control-plane defect "**impacted 2-AZ and 3-AZ Kafka clusters similarly**." The 2-AZ cluster increased blast radius/recovery time, but 3-AZ alone would NOT have prevented the defect. Remediation = **migrating the 2-AZ Kafka cluster to 3-AZ** + building runbooks/tooling + AWS root-causing the defect.
- **DO NOT claim Coinbase uses ValKey/ElastiCache** — that is unverified and likely confused with **MaiCoin** (a Taiwanese exchange in an AWS ValKey case study).

**(d) Terraform sketch (EKS + Karpenter + Graviton + MSK):**
```hcl
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "coinbase-prod"
  cluster_version = "1.30"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
  eks_managed_node_groups = {
    graviton = {
      ami_type       = "AL2_ARM_64"
      instance_types = ["m7g.2xlarge"]
      min_size = 3, max_size = 50, desired_size = 6
      taints = [{ key = "arch", value = "arm64", effect = "NO_SCHEDULE" }]
    }
  }
}
resource "aws_msk_cluster" "events" {
  cluster_name           = "coinbase-events"
  kafka_version          = "3.6.0"
  number_of_broker_nodes = 3          # 3-AZ post-incident remediation
  broker_node_group_info {
    instance_type   = "kafka.m7g.large"
    client_subnets  = module.vpc.private_subnets   # one per AZ
    storage_info { ebs_storage_info { volume_size = 1000 } }
  }
  encryption_info { encryption_in_transit { client_broker = "TLS" } }
}
```

**(e) Workflow narratives.** SREs run on-call across 3,500 services, with the matching engine as the highest-tier P0; the May 7 incident shows the manual-partition-reassignment runbook in action. Platform engineers own kubetools and the Karpenter provisioners (NodePools), fighting **IP exhaustion** (driving dual-stack IPv6 EKS). FinOps/CCoE engineers run the Trusted Advisor + Cost Explorer optimization loops.

**(f) Exam patterns:** "single-AZ increases blast radius → multi-AZ"; "cluster placement group concentrates AZ risk → use spread/partition or multi-AZ for resilience"; "managed Kafka → MSK"; "ARM price-performance → Graviton"; "JIT node provisioning → Karpenter"; "automatic storage cost optimization with unknown access patterns → S3 Intelligent-Tiering."

---

### 4. FENERGO — RegTech (KYC/AML/CLM)

**(a) Business/regulatory.** Client Lifecycle Management SaaS for banks; **GDPR, financial-crime/AML, MiFID II, DORA, SOC 2, data residency.** Availability is existential ("SaaS providers can live or die on availability").

**(b) Verified footprint.** **Event-sourcing + CQRS**; **DynamoDB** as state/read-model store (TTL, optimistic locking via condition expressions, **DynamoDB Streams** for CDC); **EventStoreDB** (3 nodes across 3 AZs — leader/follower/readonly, ≥3 AZs recommended); **API Gateway WebSockets + two Lambdas** (connect/disconnect); **MemoryDB** for WebSocket connection store; **EventBridge** fanout from Streams; circuit-breaker pattern; **Step Functions** orchestrating zero-downtime EventStore cluster upgrades (read-only → follower → leader ordering). 3-AZ active-active.

**(c) CQRS/event-sourcing reference flow:** Commands → events appended to event store (DynamoDB or EventStoreDB) → DynamoDB Streams filtered for INSERT → fanout Lambda → EventBridge → projector Lambda updates read models. Optimistic concurrency via a `version` sort key (two concurrent writers on same version → one fails the conditional write).

**(d) Terraform sketch (WebSocket + Streams projector):**
```hcl
resource "aws_apigatewayv2_api" "ws" {
  name                       = "fenergo-ws"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"
}
resource "aws_dynamodb_table" "event_store" {
  name         = "events"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "streamId"
  range_key    = "version"          # sort key enforces ordering + optimistic lock
  attribute { name = "streamId" type = "S" }
  attribute { name = "version"  type = "N" }
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"
  point_in_time_recovery { enabled = true }
}
resource "aws_lambda_event_source_mapping" "projector" {
  event_source_arn  = aws_dynamodb_table.event_store.stream_arn
  function_name     = aws_lambda_function.projector.arn
  starting_position = "TRIM_HORIZON"
  filter_criteria { filter { pattern = jsonencode({ eventName = ["INSERT"] }) } }
  function_response_types = ["ReportBatchItemFailures"]   # partial batch responses
}
```

**(e) Workflow narratives.** Backend devs implement aggregates/command handlers; data/platform engineers own the EventStore scaling Step Function and DynamoDB capacity. SREs watch Stream IteratorAge, projector DLQs, and WebSocket connection counts in MemoryDB.

**(f) Failure modes.** Indefinite Lambda retries on Stream events (mitigated with Destinations + retry policy). EventStore reader-node overload (mitigated by capacity planning, not dynamic scale-out).

**(g) Talking points.** *"Fenergo's append-only event store on DynamoDB with Streams-driven projections is the textbook CQRS pattern — when the exam wants an immutable audit log of all state changes plus independently scalable read views, that's event sourcing on DynamoDB Streams + EventBridge, not a single CRUD table."*

**(h) Exam patterns:** "separate read/write scaling → CQRS"; "immutable audit trail of changes → event sourcing + DynamoDB Streams"; "real-time push to many clients → API Gateway WebSockets + Lambda"; "prevent lost updates → DynamoDB conditional writes (optimistic locking)"; "auto-expire records → TTL."

---

### 5–10. CONDENSED DEEP PROFILES

**5. HubSpot:** ~4,000 Kafka topics / 80 clusters (Jul 2022); HBase on Graviton (im4gn/is4gen local NVMe; ~100 clusters / 7,000+ regionservers / 2.5 PB/day); EKS + historical Mesos; Hublet multi-region (na1/eu1) with aggregated topics; JVM on ARM with no recompile, Docker CPU emulation for cross-arch builds. **Exam:** Graviton price-performance; local NVMe instance storage for stateful/low-latency workloads; multi-region data isolation; managed Kafka (MSK).

**6. Flutter/PokerStars:** 1,100 apps + 3 PB migrated (70% of footprint); EKS, MSK, **Cloud WAN + Network Firewall**, Systems Manager (fleet patching), multi-account, S3, CloudWatch; OpsGuru partner; 1,200+ engineers trained; **20% TCO cut, 40% production-change-rate boost**; 33 DCs replaced; 3.4M players / 850k hands per hour. **Exam:** "global low-latency network backbone → Cloud WAN"; "managed IDS/IPS → Network Firewall"; "fleet patching at scale → Systems Manager Patch Manager"; "multi-account governance → Organizations/Control Tower."

**7. AIB:** Hybrid — **IBM z15 mainframe (€65m IBM deal, 2021)**, nCino cloud banking on AWS, Accenture integration; Central Bank of Ireland, EBA, PSD2, DORA, MiFID II. **Inferred:** IAM Identity Center + Okta federation (SCIM/SAML), Direct Connect for hybrid, KMS/CloudHSM, GuardDuty/Security Hub/Audit Manager. **Exam:** "hybrid on-prem ↔ AWS → Direct Connect + VPN backup"; "federated workforce SSO → IAM Identity Center + external IdP"; "compliance evidence collection → Audit Manager."

**8. Stripe:** PCI DSS Level 1; EC2/Lambda/S3/KMS/Shield; observability via **Amazon Managed Service for Prometheus + Managed Grafana** (3,000 engineers, 500M metrics/10s). AWS payments reference architecture (FSI Lens): ECS/Fargate app tier, Aurora **or** DynamoDB for transactions, ElastiCache session store, CloudHSM, Secrets Manager, GuardDuty, NAT gateway → card schemes. **Exam:** "managed Prometheus/Grafana at scale → AMP + AMG"; "PCI cardholder data isolation → tokenization + CloudHSM + KMS + dedicated VPC."

**9. Mastercard (inferred):** payments network; multi-region active-active, tokenization, HSM-backed crypto, Route 53 failover, DynamoDB global tables for low-latency global reads. Label as inference.

**10. Wayflyer:** Dublin revenue-based-financing fintech (Ireland's 6th unicorn, $1.6bn valuation); job posts confirm **AWS + Python/Django + REST APIs + microservices**. PSD2/GDPR/financial-services regs. Inferred: ECS/Fargate or EKS, Aurora PostgreSQL, S3 + Athena for analytics models, KMS, Secrets Manager.

---

## PART 2 — ADDITIONAL DUBLIN COMPANIES (best-effort; inference labelled)

| # | Company | Status | Notes |
|---|---|---|---|
| 11 | **Workday** (EMEA HQ) | Verified | AWS primary since 2016 (+GCP, +Azure for Adaptive Planning); EKS; DataSync moved 8+ PB; weekly zero-downtime releases; multi-tenant SaaS on containers |
| 12 | **Workhuman** | Inference | Employee-recognition SaaS, Irish unicorn; processes billions in rewards → likely Aurora/RDS + DynamoDB ledger, ECS/EKS, KMS, PCI for payouts |
| 13 | **Datadog (Dublin eng)** | Verified consumer/partner | Massive AWS user; 1,000+ integrations; monitors EKS/Lambda/Fargate; Cloudcraft auto-diagrams AWS |
| 14 | **Salesforce (Dublin)** | Verified | **Hyperforce** runs Salesforce on AWS/Azure/GCP via Kubernetes + containers; immutable infra via Terraform; multi-AZ; zero-trust; in-country data residency |
| 15 | **LinkedIn EMEA (Dublin)** | Inference | Microsoft-owned → Azure primary; cross-cloud awareness |
| 16 | **Meta (Dublin EMEA HQ)** | Inference | Primarily own data centers; minimal AWS |
| 17 | **Google (Dublin EMEA HQ)** | Inference | GCP-native; cross-cloud awareness only |
| 18 | **Microsoft (Dublin EMEA HQ)** | Inference | Azure-primary; cross-cloud awareness |
| 19 | **Slack EMEA** | Inference (historically AWS-heavy) | Pre-Salesforce: heavy AWS (EC2, S3, ELB, Vitess/MySQL); now under Salesforce/Hyperforce |
| 20 | **Squarespace (Dublin)** | Inference | Website builder; classic web stack — ALB+ASG, RDS/Aurora, CloudFront, ElastiCache, S3 for media |
| 21 | **Riot Games (Dublin)** | Inference | Gaming infra; low-latency global — Global Accelerator, EKS, GameLift-style patterns, DynamoDB for player state |
| 22 | **Zendesk (Dublin)** | Inference | Support SaaS; multi-tenant — RDS/Aurora, Kafka/MSK, Elasticsearch, EKS |
| 23 | **Pinterest (Dublin)** | Partly verified | **Verified S3 Express One Zone + MemQ user (10x data processing speedup)**; 600M MAU; heavy AWS/data-lake |
| 24 | **Etsy (Dublin)** | Inference | E-commerce marketplace; ALB+ASG, Aurora/MySQL, CloudFront, ElastiCache, search via OpenSearch |
| 25 | **Hostelworld (Dublin)** | Inference | Travel booking; spiky seasonal traffic → auto-scaling, CloudFront, RDS read replicas, ElastiCache |
| 26 | **Bank of Ireland** | Inference | Regulated/hybrid like AIB — Direct Connect, KMS/CloudHSM, Audit Manager; mainframe + cloud |
| 27 | **Revolut (Ireland licence)** | Verified | **Google Cloud primary** (Compute Engine, IAM, incremental snapshots); Java/Kotlin event-driven; Postgres event store. NOT AWS |
| 28 | **TransferMate** | Inference | Cross-border payments; PCI DSS + PSD2; tokenization, multi-region, HSM |
| 29 | **CurrencyFair** | Inference | FX (part of Assembly Payments); ledger DB, KMS, PCI |
| 30 | **Fineos** | Inference | Insurance (life/accident/health) software; regulated; RDS/Aurora, EKS, document storage in S3 |
| 31 | **Wise (Dublin)** | Inference | Cross-border money transfer; PSD2/PCI; microservices, Kafka, sharded MySQL, multi-region |
| 32 | **Plaid (Dublin)** | Inference | Financial-data connectivity; PSD2/Open Banking; API Gateway, Lambda, DynamoDB, KMS, tokenization |
| 33 | **AccessPay (Dublin)** | Inference | B2B payments/bank automation; SFTP/Transfer Family, SQS, KMS, PCI |
| 34 | **SumUp (Dublin)** | Inference | SMB card processing; PCI DSS L1; tokenization, HSM, EKS, DynamoDB |
| 35 | **N26 (Dublin presence)** | Verified | **Google Cloud Platform**; HashiCorp Nomad, Kotlin/Java Spring Boot, 100+ microservices, regional config layer. NOT AWS-primary |

> **Comparison anchor:** **Starling Bank (UK)** is the AWS-native neobank exemplar — EC2, VPC, CloudFormation, Lambda, S3, DynamoDB, SQS; microservices with idempotence, "at least once / at most once," no distributed transactions. Use Starling (not Revolut/N26) when you need an AWS-banking story.

---

## PART 3 — DEEP SERVICE COVERAGE (previously-light topics)

### A) WAF Managed Rule Groups
- **Pricing:** Web ACL $5/mo; each rule/rule group $1/mo; **$0.60/million requests.** Default **1,500 WCU** free; **+$0.20/million per extra 500 WCU**; **max 5,000 WCU/web ACL**; body inspection beyond 16 KB **+$0.30/million**.
- **AWS Managed Rule Group WCUs:** Core/Common Rule Set (CRS) **700**, Known Bad Inputs **200**, Admin Protection **100**, Bot Control **50**; also SQLi, Linux/Unix/POSIX, Windows, PHP, WordPress, IP Reputation (no versions, frequently updated), Anonymous IP.
- **Bot Control:** **$10/mo per web ACL**; common bots first **10M free** then **$1/million**; targeted bots first **1M free** then **$10/million**; ML rules prefixed **TGT_ML_**; **CAPTCHA** + **Challenge** actions billed per attempt/response; Web Bot Authentication for AI crawlers (v4.0+).
- **Rate-based rules:** **5-minute trailing window**, tracks up to **10,000 source IPs** per rule, base **2 WCU + 30 WCU per custom aggregation key**; supports scope-down statements; aggregate by IP / forwarded IP / custom keys.
- **Account Takeover Prevention (ATP)** and **Account Creation Fraud Prevention (ACFP)** carry separate fees ($10/mo + per-million by risk).
- **Custom responses/bodies**, **rule ordering** (cheap IP/geo blocks first, expensive ML/Bot Control last), **Count mode** for testing, **scope-down** to cut cost, label-based correction of false positives.
- **Logging** to S3 / CloudWatch Logs / Kinesis Data Firehose.
- **Attaches to:** CloudFront, ALB, API Gateway REST, AppSync GraphQL, Cognito user pools, App Runner, Verified Access.
- **Exam triggers:** "block SQLi/XSS at L7 → WAF managed rules"; "stop scrapers/bots → Bot Control"; "limit requests per IP → rate-based rule"; "block by country → geo-match"; "org-wide WAF → Firewall Manager."

### B) Shield Advanced
- **$3,000/mo base, 1-year commitment**, up to **50 billion requests per payer ID**; **free WAF** (no web ACL/rule/request fees) for protected resources; **Bot Control NOT included**; **SRT (Shield Response Team) requires Business/Enterprise Support**; **DDoS Cost Protection** refunds scaling charges (EC2/ELB/CloudFront/Route 53/Global Accelerator) during attacks; health-check-based detection; Firewall Manager for org-wide rollout.
- **Exam triggers:** "guaranteed DDoS cost protection + SRT → Shield Advanced"; "free L3/L4 DDoS → Shield Standard (default, free)."

### C) Step Functions — full state-type reference
- **Task** (`.sync` waits for completion, `.waitForTaskToken` for human/callback; **200+ optimized integrations**), **Choice** (branching), **Parallel** (concurrent branches), **Map** (Inline ≤**40** concurrency / ≤**25,000** history entries, JSON array only; **Distributed** up to **10,000** concurrent child executions, reads **S3 CSV/JSON/manifest**, for datasets >**256 KiB**), **Wait** (seconds/timestamp/JSONPath), **Pass** (no-op/transform), **Succeed**, **Fail**.
- **Retry/Catch** error handling; data flow: **InputPath → Parameters → (Task) → ResultSelector → ResultPath → OutputPath**.
- **Standard** (exactly-once, up to 1 year, full audit/history) vs **Express** (high-throughput, <5 min, billed per-request + duration, history only in CloudWatch Logs). **Distributed Map** runs only on a Standard parent; children may be Standard or Express.
- **256 KB payload limit → Claim Check pattern** (write to S3, pass the URI). **Activities** for workers running outside AWS.
- **Exam triggers:** "orchestrate microservices with visual state machine → Step Functions"; "process millions of S3 objects in parallel → Distributed Map"; "high-volume short event processing → Express"; "long-running auditable workflow → Standard"; "human approval step → waitForTaskToken."

### D) AppSync — data sources complete
- **Data sources:** DynamoDB (most common), RDS (via Data API), Lambda, OpenSearch, **HTTP** endpoints, **EventBridge** (publish), **None** (local resolvers).
- **Resolvers:** VTL vs JavaScript; **Pipeline resolvers** (multiple functions sequentially); **Subscriptions** (real-time WebSocket); **caching** (full-request or per-resolver); **conflict resolution** (auto-merge, optimistic concurrency, custom Lambda); **DataStore** (offline-first mobile sync); **auth modes** (API key, IAM, Cognito User Pools, OIDC, Lambda); **Merged APIs** (combine multiple AppSync APIs).
- **Exam triggers:** "managed GraphQL with real-time + offline → AppSync"; "single GraphQL endpoint over multiple data sources → AppSync resolvers."

### E) Aurora Limitless Database
- **Two-tier:** **Routers** (accept SQL, route, maintain system-wide consistency, coordinate atomic cross-shard commits) + **Shards** (store data, not directly client-addressable).
- **Table types:** **Sharded** (partitioned by shard key), **Reference** (replicated to all shards, **32 TiB cap**, ideal for catalogs/lookup), **Standard** (on a single system-chosen shard).
- **Requirements:** **Aurora I/O-Optimized only**; **PostgreSQL 16.4+**; each shard ≤**128 TiB**; capacity **16–6144 ACUs** (contact AWS beyond); **one DB shard group per cluster**; max **5 Limitless clusters/region**; **no serializable isolation**; **can't UPDATE shard keys**; available in **Ireland (eu-west-1)** among others. Handles **millions of writes/sec**.
- **Collocation:** tables sharing a shard key can be collocated for single-shard joins.
- **Exam triggers:** "scale PostgreSQL writes beyond a single writer / petabytes → Aurora Limitless"; vs **DSQL** (serverless distributed SQL, multi-region active-active) and standard Aurora (single writer + read replicas).

### F) DynamoDB — advanced
- **Adaptive capacity** (auto-rebalances; **split-for-heat** isolates hot items onto their own partition); **burst capacity** (up to **300 s / 5 min** of unused capacity); **on-demand** vs **provisioned + auto-scaling**; **reserved capacity** for steady provisioned workloads.
- **Streams iterators:** TRIM_HORIZON / LATEST / AT_TIMESTAMP; **Lambda partial batch responses** (`ReportBatchItemFailures`).
- **DAX:** microsecond reads (10x), **write-through / read-through**, multi-AZ; **global tables bypass DAX** → stale-cache risk (refreshes only on TTL).
- **Global Tables:** multi-active, **last-writer-wins**; priced in **rWCU/rWRU**; **MRSC** (multi-Region strong consistency, transactions error) vs **MREC** (eventual, ACID only within origin Region — **no cross-region transactions**).
- **Transactions:** TransactWriteItems/TransactGetItems, **100-item / 4 MB limit**, transactional write = **2 WCU per 1 KB**.
- **PartiQL** (SQL-like); **encryption** (AWS-owned default / AWS-managed / customer-managed KMS); **PITR** (continuous, **1–35 days**, no perf impact); **Export to S3** (no table impact); **TTL** (deletes within **48 h**, free); **conditional writes** (optimistic locking); **hot-partition mitigation** (write sharding/suffixes); **single-table design**.
- **Exam triggers:** "microsecond reads → DAX"; "multi-region active-active → global tables"; "auto-expire → TTL"; "point-in-time restore → PITR"; "all-or-nothing multi-item → transactions"; "analytics export without affecting prod → Export to S3."

### G) EC2 — advanced
- **Placement groups:** **Cluster** (low-latency/HPC, single AZ), **Spread** (max **7 instances/AZ**, distinct hardware, critical small fleets), **Partition** (HDFS/Kafka/Cassandra, up to 7 partitions/AZ).
- **Capacity Reservations** (zonal, no commitment); **Capacity Blocks for ML** (reserve GPU ahead); **Dedicated Hosts** (socket/core visibility, BYOL) vs **Dedicated Instances**; License-Included vs BYOL; **IMDSv2 mandatory**; ENA/SR-IOV + **EFA** (HPC); **Auto Recovery** (replaces impaired hardware, same instance) vs Auto Restart; **EC2 Fleet**; **Image Builder** pipelines; user-data/cloud-init.
- **Exam triggers:** "lowest inter-node latency → cluster placement group"; "max HA for few critical instances → spread"; "compliant licensing/visibility → Dedicated Hosts."

### H) VPC — advanced
- **Transit Gateway** (route tables, attachments, inter-region peering, multicast, Network Manager) vs **Cloud WAN** (global, policy-based, central dashboard — newer); **Network Firewall** (stateless + stateful **Suricata-compatible** rules, domain filtering, IDS/IPS); **Reachability Analyzer**; **Flow Logs** → CloudWatch/S3/Firehose; **Traffic Mirroring**; **PrivateLink** endpoint services (expose your service cross-account); **IPv6** dual-stack + **egress-only IGW**; **IPv4 public address billing** (since Feb 2024, ~$0.005/hr per public IPv4); **VPC sharing via RAM**.
- **Exam triggers:** "connect hundreds of VPCs/accounts → Transit Gateway"; "global multi-region network with central policy → Cloud WAN"; "managed IDS/IPS in VPC → Network Firewall"; "private access to a service across accounts → PrivateLink."

### I) Lambda — advanced
- **SnapStart** (Java 17+, Python 3.12+, .NET 8+; priming + restore costs reduce cold starts); **layers** (max **5**, **250 MB** unzipped total incl. function); **container images** (**10 GB**); **extensions**; **Provisioned Concurrency** (pre-warmed, no cold start) vs **Reserved Concurrency** (cost cap / throttle protection); **VPC via Hyperplane ENI** (no cold-start penalty since 2019); event source mapping; async retries (**2** then **DLQ/Destinations**); **Destinations** (success + failure routing); **Lambda@Edge** (CloudFront, larger compute, regional, no VPC) vs **CloudFront Functions** (sub-ms, JS-only, viewer request/response); **function URLs** (built-in HTTPS); **response streaming** (up to **20 MB**).
- **Exam triggers:** "reduce Java cold starts → SnapStart"; "guarantee no cold start → Provisioned Concurrency"; "protect downstream from Lambda flood / cap cost → Reserved Concurrency"; "lightweight header rewrite at edge → CloudFront Functions"; "edge compute with more logic → Lambda@Edge."

### J) S3 — advanced
- **Express One Zone** (single-AZ **directory buckets**, single-digit ms, up to **2M req/s**, ~80% lower request cost; **April 2025 cuts: storage −31%, PUT −55%, GET −85%**; bucket name `name--azid--x-s3`; SSE-KMS since mid-2025; co-locate with EC2/EKS/ECS); **Object Lambda** (transform on GET); **Access Points** + **Multi-Region Access Points** (single global endpoint, $0.0033/GB routing); cross-account replication; **RTC** (15-min SLA for 99.99%); **Batch Operations** (billions of objects, one request); **Inventory** (CSV/ORC/Parquet); **Storage Lens** (org-wide analytics + recommendations); **Requester Pays**; **Glacier Vault Lock** (WORM compliance); **bucket types** (general-purpose, directory, **table/Iceberg**, **vector**); **Mountpoint**; **Transfer Acceleration** (CloudFront edge for uploads).
- **Exam triggers:** "single-digit-ms object access, latency-critical, co-located compute → Express One Zone"; "single endpoint failover across regions → Multi-Region Access Point"; "operate on billions of objects → Batch Operations"; "org-wide storage analytics → Storage Lens."

### K) Security services decision tree
- **GuardDuty** = ML threat detection (VPC Flow / DNS / CloudTrail / EKS audit / S3 / RDS / Lambda protection + Malware Protection for EC2/volumes).
- **Inspector** = vulnerability assessment (EC2 / ECR / Lambda code + dependencies).
- **Macie** = PII discovery/classification in S3.
- **Security Hub** = aggregator + CIS / PCI-DSS / NIST standards.
- **Detective** = investigation graphs from GuardDuty/CloudTrail/VPC Flow.
- **Audit Manager** = compliance evidence (PCI/HIPAA/GDPR templates).
- **Firewall Manager** = org-wide WAF / Network Firewall / Shield Advanced.
- **Network Firewall** = managed IDS/IPS in VPC. **RAM** = cross-account resource sharing.
- **Decision cue:** "find threats" → GuardDuty; "find vulnerabilities" → Inspector; "find PII" → Macie; "aggregate findings + standards" → Security Hub; "investigate root cause" → Detective; "prove compliance" → Audit Manager.

### L) Monitoring decision tree
- **CloudWatch** (metrics/logs/alarms/dashboards/**Logs Insights**); **Synthetics** (canary uptime); **RUM** (real-user monitoring); **Container/Lambda Insights**; **X-Ray** (distributed tracing, merging into CloudWatch); **Application Signals** (unified APM); **Evidently** (feature flags / A/B); **Internet Monitor**; **Network Monitor**.
- **Decision cue:** "trace a request across microservices → X-Ray / Application Signals"; "simulate user journeys → Synthetics canary"; "real end-user browser metrics → RUM"; "query logs ad hoc → Logs Insights."

### M) Database decision tree
- **RDS** (Postgres/MySQL/MariaDB/Oracle/SQL Server/**IBM Db2**) — managed relational, lift-and-shift commercial DBs.
- **Aurora** (Postgres/MySQL; **Limitless** for horizontal write scaling; **Serverless v2** for variable load; **DSQL** for serverless distributed multi-region).
- **DynamoDB** — key-value/document, single-digit-ms at any scale.
- **DocumentDB** (MongoDB-compatible); **Neptune** (graph); **Keyspaces** (Cassandra); **Timestream** (time-series); **QLDB** (ledger — **deprecated, migrate to Aurora**); **MemoryDB** (durable Redis-compatible, primary DB); **ElastiCache** (Redis/Memcached/**ValKey** — cache, not source of truth).
- **Decision cue:** "relational + minimal admin → Aurora/RDS"; "NoSQL massive scale → DynamoDB"; "relationships/social graph → Neptune"; "time-series/IoT → Timestream"; "durable in-memory → MemoryDB"; "pure cache → ElastiCache."

---

## PART 4 — EXAM-DAY PREPARATION

**(a) Time management.** 65 Q / 130 min = **~2 min/Q**. Plan: ~90 min first pass (answer + flag the hard ones), ~25 min flagged review, ~15 min buffer. Never leave blanks — **no penalty for wrong answers.**

**(b) Two-pass strategy.** Pass 1: commit instantly on confident answers; flag any that take >2 min or have two plausible options. Pass 2: re-read flagged stems slowly, focusing on the qualifier word. Don't change a confident answer without a concrete reason.

**(c) Question-stem dissection.** Read the **last sentence first** (the actual ask + qualifier), then the constraints (cost, latency, RTO/RPO, compliance, "no/least operational overhead"), then eliminate. Watch for distractor keywords that match the scenario but violate a constraint.

**(d) Qualifier hierarchy (decode the superlative):**
- **LEAST operational overhead / fully managed** → serverless/managed: Fargate, Lambda, Aurora Serverless, DynamoDB, SQS, S3.
- **MOST cost-effective** → Spot, Savings Plans/RIs, S3 IA/Glacier + Intelligent-Tiering, Graviton, right-sizing, gateway endpoints (free) vs NAT.
- **MOST resilient / highly available** → Multi-AZ, cross-region, Route 53 failover, decoupling.
- **MOST performant** → caching (CloudFront/ElastiCache/DAX), Global Accelerator, provisioned IOPS, Express One Zone.
- **MOST scalable** → decouple (SQS/SNS/Kinesis) + auto-scaling.

**(e) Top trigger phrases → service (compiled):** "millions of small writes/sec, single-digit ms" → DynamoDB; "microsecond reads" → DAX; "decouple/buffer/smooth spikes" → SQS; "fan-out to many subscribers" → SNS/EventBridge; "real-time streaming/replay" → Kinesis/MSK; "transform on GET" → S3 Object Lambda; "cache static at edge" → CloudFront; "non-HTTP global low-latency" → Global Accelerator; "lift-and-shift Oracle/SQL Server" → RDS; "minimal-admin MySQL/Postgres + read scaling" → Aurora; "session store" → ElastiCache; "scheduled cron in cloud" → EventBridge Scheduler; "human approval in workflow" → Step Functions waitForTaskToken; "process millions of S3 files in parallel" → Step Functions Distributed Map; "hybrid private link to on-prem" → Direct Connect (+ VPN backup); "private access to AWS service no internet" → VPC endpoint/PrivateLink; "central multi-account WAF" → Firewall Manager; "detect threats with ML" → GuardDuty; "find PII in S3" → Macie; "rotate DB creds automatically" → Secrets Manager; "WORM compliance" → S3 Object Lock/Glacier Vault Lock; "DDoS cost protection + SRT" → Shield Advanced; "cross-account temporary access" → IAM role with session duration (NOT IAM user); "MFA + federated workforce SSO" → IAM Identity Center.

**(f) Top common traps:** single-AZ ≠ "highly available"; IAM user ≠ best for cross-account (use a **role**); root account for daily ops = always wrong; storing creds in code/AMI = wrong (Secrets Manager/Parameter Store); gp2 when gp3 is cheaper/faster; manual scaling when target-tracking exists; provisioned DynamoDB when traffic is unpredictable (use on-demand); EBS when shared file access needed (use EFS); NAT gateway when a free gateway endpoint suffices (S3/DynamoDB); CloudFront not used for global static; security group "stateful" vs NACL "stateless"; Multi-AZ (HA) confused with read replicas (scaling).

**(g) Legacy answers to auto-eliminate:** Classic Load Balancer, EC2-Classic, Simple Scaling (prefer target-tracking), storing data only in one AZ for "DR," using EBS for multi-instance shared storage, self-managed NAT instances, hardcoded long-lived access keys, QLDB for new ledgers (deprecated → Aurora).

**(h) Pre-exam checklist (technical/mental/logistics):** valid government ID; clean desk + quiet room (online proctor) or arrive early at Pearson VUE; system/network check 24h before; review trigger-phrase + decision-tree sheets only (no cramming new topics); sleep 7–8h.

**(i) Exam-day morning routine:** light breakfast, hydrate, 10-min review of the qualifier hierarchy, arrive/log in 30 min early, do a 2-min breathing reset before starting.

**(j) Score interpretation.** **720/1000 scaled**, **compensatory** (overall pass — a weak domain can be offset). Domain weights tell you where points concentrate: **Security 30% + Resilient 26% = 56%** of scored content — prioritize these.

**(k) If you fail.** **14-day cooling period**, unlimited attempts, full fee each time (150 USD; verify current price). Use the score report's per-section performance table to target your weakest domain; re-drill mocks until consistently **80–85%+** with no weak domain.

---

## PART 5 — CONSOLIDATED MEGA-REFERENCE

### (a) Service-to-domain mapping
- **Domain 1 — Secure (30%):** IAM (users/groups/roles/policies/permission boundaries), Organizations + SCPs, **IAM Identity Center**, KMS, CloudHSM, Secrets Manager, Parameter Store, WAF, Shield, GuardDuty, Inspector, Macie, Security Hub, Detective, Network Firewall, Firewall Manager, Cognito, ACM, security groups vs NACLs, VPC endpoints/PrivateLink, Audit Manager.
- **Domain 2 — Resilient (26%):** Multi-AZ, ASG, ELB (ALB/NLB/GWLB), Route 53 (failover/latency/geo/weighted), SQS/SNS/EventBridge, Aurora (Multi-AZ + global), DynamoDB global tables, S3 CRR/SRR, AWS Backup, **DR strategies (backup & restore → pilot light → warm standby → active-active)**, Step Functions.
- **Domain 3 — High-Performing (24%):** CloudFront, ElastiCache, DAX, Global Accelerator, RDS/Aurora read replicas, Kinesis/MSK, EKS/ECS/Fargate, placement groups, EBS types + provisioned IOPS, EFS/FSx, S3 Express One Zone, Aurora Limitless.
- **Domain 4 — Cost-Optimized (20%):** Spot, Savings Plans/RIs, S3 storage classes + Intelligent-Tiering + lifecycle, Graviton, right-sizing, Compute Optimizer, Cost Explorer/Budgets, gateway endpoints vs NAT, Fargate vs EC2.

### (b) Cross-topic integration architectures (20 patterns w/ Dublin anchors)
1. **3-tier web app** (ALB → ASG → Aurora Multi-AZ + ElastiCache) — Ryanair.com.
2. **Event-driven CQRS** (DynamoDB + Streams + EventBridge + Lambda projectors) — Fenergo.
3. **Real-time streaming pipeline** (MSK/Kinesis → Lambda/Flink → S3 lake → Athena) — Coinbase / Ryanair.
4. **Container platform** (EKS + Graviton + Karpenter + ALB Ingress) — Coinbase / HubSpot.
5. **Serverless API** (API Gateway → Lambda → DynamoDB, WAF on front) — Stripe webhooks.
6. **WebSocket real-time** (API Gateway WebSocket + Lambda + MemoryDB) — Fenergo.
7. **Global low-latency network** (Cloud WAN + Network Firewall + multi-account) — Flutter/PokerStars.
8. **Data lake + ML** (S3 + Glue + SageMaker + Kinesis) — Ryanair demand forecasting.
9. **Observability at scale** (Managed Prometheus + Managed Grafana) — Stripe.
10. **Hybrid connectivity** (Direct Connect + VPN backup + Transit Gateway) — AIB.
11. **Federated workforce SSO** (IAM Identity Center + Okta SCIM/SAML) — AIB.
12. **Multi-region active-active** (DynamoDB global tables + Route 53 latency) — payments (Mastercard inferred).
13. **DR warm standby** (cross-region Aurora global + pilot infra + Route 53 failover).
14. **PCI payment processing** (ECS/Fargate + Aurora/DynamoDB + CloudHSM + KMS + GuardDuty + NAT to schemes) — Stripe/SumUp.
15. **Massive parallel batch** (Step Functions Distributed Map over S3) — data processing.
16. **Edge personalization** (CloudFront + Lambda@Edge / CloudFront Functions).
17. **Cost-optimized storage tiering** (S3 Intelligent-Tiering org default + lifecycle) — Coinbase.
18. **Bot/DDoS protection** (WAF Bot Control + rate rules + Shield Advanced + CloudFront).
19. **Stateful low-latency datastore on K8s** (local NVMe im4gn + EKS) — HubSpot HBase / Kafka.
20. **Horizontal write scaling** (Aurora Limitless sharded/reference tables, or Vitess) — Intercom.

### (c) The 100 most-tested facts (high-yield extract)
SQS standard = at-least-once/best-effort order; FIFO = exactly-once/ordered (300 TPS or 3,000 batched). SNS = pub/sub fan-out. Kinesis = ordered, replayable, shards. S3 = 11 nines durability, eventually-then-strong read-after-write (now strong). S3 storage classes ordered by cost/retrieval. EBS = single-AZ block, snapshot to S3. EFS = multi-AZ NFS, Linux. FSx = Windows/Lustre/NetApp/OpenZFS. Multi-AZ RDS = sync standby HA (not for reads); read replicas = async, scale reads. Aurora = 6 copies across 3 AZs, 15 read replicas, reader endpoint. DynamoDB = single-digit ms, on-demand vs provisioned, GSI vs LSI (LSI same partition key, created at table creation; GSI any key, anytime). Lambda = 15-min max, 10 GB memory, /tmp up to 10 GB. ALB = L7/HTTP host+path routing; NLB = L4/static IP/millions rps; GWLB = third-party appliances. Route 53 routing policies. CloudFront = edge cache, OAC for S3. Security groups stateful + allow-only; NACL stateless + allow/deny + ordered. IAM policy evaluation: explicit deny > allow > implicit deny. KMS key rotation. VPC: 1 IGW/VPC, NAT for private egress, gateway endpoints free (S3/DynamoDB). Savings Plans vs RIs. Spot = up to 90% off, 2-min interruption notice. Organizations SCPs = guardrails (don't grant). Cognito user pools (auth) vs identity pools (AWS creds). Step Functions Standard vs Express. EventBridge schema/rules vs CloudWatch Events. Storage Gateway types (File/Volume/Tape). DataSync for bulk migration. Transfer Family for SFTP. (Drill the full set against mocks.)

### (d) The 50 most important comparisons (top distinctions)
SQS vs SNS vs Kinesis vs MSK; ALB vs NLB vs GWLB; Multi-AZ vs read replica; EBS vs EFS vs FSx vs Instance Store; S3 Standard vs IA vs One Zone-IA vs Glacier vs Express One Zone; RDS vs Aurora vs DynamoDB; DynamoDB on-demand vs provisioned; DAX vs ElastiCache vs MemoryDB; ElastiCache Redis vs Memcached vs ValKey; security group vs NACL; IAM user vs role; KMS vs CloudHSM vs Secrets Manager; CloudFront vs Global Accelerator; Lambda@Edge vs CloudFront Functions; Step Functions Standard vs Express; Inline vs Distributed Map; GuardDuty vs Inspector vs Macie; Security Hub vs Detective; WAF vs Shield vs Network Firewall; Direct Connect vs VPN vs Transit Gateway vs Cloud WAN; gateway vs interface endpoint; Spot vs Reserved vs On-Demand vs Savings Plan; provisioned vs reserved concurrency; backup&restore vs pilot light vs warm standby vs active-active; QLDB vs Aurora (ledger); Timestream vs DynamoDB; Neptune vs DocumentDB; Cognito user vs identity pool; SCP vs IAM policy; Aurora Serverless v2 vs Limitless vs DSQL; Fargate vs EC2 launch type; EKS vs ECS; ACM vs IAM cert store; CloudTrail vs CloudWatch; Config vs Audit Manager; gp3 vs gp2 vs io2; ASG target-tracking vs step vs simple; Route 53 failover vs latency vs geolocation.

### (e) Well-Architected 6 pillars → question patterns
- **Operational Excellence** → IaC (CloudFormation/CDK), automation, runbooks, observability.
- **Security** → least privilege, encryption everywhere, detective controls (Domain 1).
- **Reliability** → Multi-AZ, auto-recovery, decoupling, DR (Domain 2).
- **Performance Efficiency** → right service selection, caching, serverless (Domain 3).
- **Cost Optimization** → right-size, purchasing options, storage tiering (Domain 4).
- **Sustainability** → Graviton, managed services, right-sizing, region selection.

---

## Recommendations (staged, with thresholds)
1. **Weeks 1–2 — Security + Resilient (56% of exam).** Master IAM (roles vs users, policy evaluation, Identity Center), KMS/Secrets Manager, VPC (SG vs NACL, endpoints), Multi-AZ vs read replicas, ASG/ELB, Route 53 policies, SQS/SNS/EventBridge decoupling, DR strategies. *Threshold to advance:* 80%+ on Domain 1 & 2 topic quizzes.
2. **Weeks 3 — High-Performing + Cost.** Caching trio (CloudFront/ElastiCache/DAX), storage classes + lifecycle, Spot/Savings Plans, Graviton, Express One Zone, Aurora Limitless. Drill the **service decision trees** (database, security, monitoring) until automatic.
3. **Throughout — anchor concepts to Dublin companies** for recall (Coinbase = EKS/Graviton/MSK/Karpenter + AZ blast-radius lesson; Ryanair = Aurora migration + S3/Kinesis lake; Fenergo = CQRS/DynamoDB Streams; Intercom = connection-limit/RDS Proxy; Flutter = Cloud WAN/Network Firewall).
4. **Week 4 — Timed full mocks.** *Booking threshold:* consistently **80–85%+** across all four domains with **no single weak domain**. If any domain lags <70%, do not book — target that domain.
5. **Exam day — qualifier discipline.** For every question, underline the superlative (MOST cost-effective / LEAST operational overhead / MOST resilient/performant/scalable) and let it break ties between the final two options.
6. *If you fail:* use the per-section report, wait the mandatory 14 days, re-drill the weakest domain, rebook only after returning to the 80–85% threshold.

## Caveats
- **Revolut and N26 are Google-Cloud-primary, not AWS.** Use **Starling Bank** as the AWS neobank example. AIB is **hybrid IBM-mainframe-heavy**, not all-in AWS.
- **Intercom has migrated off Aurora to Vitess/PlanetScale** — Aurora/ProxySQL details are historical context, not current state.
- **Coinbase ValKey/ElastiCache is unverified** (most likely confused with **MaiCoin**, a Taiwanese exchange in an AWS ValKey case study). The **May 7 2026 MSK control-plane defect hit both 2-AZ and 3-AZ clusters** — the 3-AZ migration reduces blast radius but did not by itself cure the defect; the cure requires AWS's root-cause fix.
- **Karpenter savings at Coinbase were ~10% additional compute** (the draft's earlier "20%" is corrected; Graviton itself was the ~20% lever).
- **Most Part 2 architectures are reasoned inferences** from domain patterns (banking/payments/gaming/SaaS/e-commerce), not verified — clearly flagged inline.
- **Pricing and service limits change frequently** (WAF WCU thresholds, S3 Express One Zone cuts, exam fee 150 vs ~300 USD in some 2026 sources, IPv4 billing). Verify on official AWS pricing/exam pages near your exam date.
- The exam tests **architectural trade-off judgment**, not memorization — the company anchors and decision trees are scaffolding for reasoning, not answer keys.

---

## How to Use This Document for Your Final Exam Push
1. **Daily warm-up (10 min):** read the **Qualifier hierarchy** (Part 4d) and **trigger phrases** (Part 4e) aloud. These are the single highest-leverage pages.
2. **Decision-tree drills (Part 3 K/L/M + Part 5d):** cover the right column and reproduce the "when to use" from memory. Repeat until you never hesitate between, e.g., DAX vs ElastiCache vs MemoryDB.
3. **Company-anchored recall:** for each of the 10 Part-1 companies, recite (a) what they run, (b) why, (c) the failure mode, (d) the exam pattern. Coinbase's May 7 2026 incident is your go-to "AZ blast radius / managed-service control-plane risk" story.
4. **Mock-exam loop:** after each timed mock, map every miss back to a Part-3 service section or a Part-4f trap, and re-read that section. Track per-domain scores; do not book until all four domains clear the 80–85% threshold.
5. **Final 48 hours:** stop new topics. Re-read only Parts 4 and 5 (qualifiers, traps, legacy eliminations, the 100 facts, the 50 comparisons). Sleep. On exam morning, do the Part-4i routine.
6. **Treat inferences as inferences:** in interviews you may cite the verified facts confidently (Ryanair 22M emails/day, Coinbase 3,500 services, Flutter 20% TCO/1,100 apps/3 PB, HubSpot 4,000 topics/80 clusters); label the Part-2 inferences as "industry-standard pattern for this domain."