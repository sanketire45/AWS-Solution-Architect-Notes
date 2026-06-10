# 6 — AWS Pricing Reference (single source of truth)

> **Verified:** June 2026 · **Anchor region:** us-east-1 (N. Virginia) · **Dublin region:** eu-west-1 (Ireland) deltas noted.
> **Caveat:** AWS quietly drops prices and adds new instance generations. Treat every figure as *order-of-magnitude correct*,
> and re-verify the exact cents on the AWS pricing page before quoting in a real interview or design doc.
> Standard month = **730 hours**. All EC2/RDS figures are **Linux/MySQL, On-Demand** unless stated.

This file is the **source of truth** for every `💰 COST REALITY` block in the masterclass topic files.
Update a number *here*, then propagate — so EC2, VPC, and combined-architecture examples never contradict each other.

---

## 🧠 How an architect reads a price

Three things matter, in this order:

1. **The billing *dimensions*** — *what* AWS actually meters (per-hour? per-GB stored? per-GB transferred? per-request?).
   Getting the dimension wrong is how bills explode. This is 70% of the value.
2. **The *ratios*** — Spot ≈ 1/5th of On-Demand; Deep Archive ≈ 1/23rd of S3 Standard. You reason in ratios, not cents.
3. **The *hidden* costs** — egress, cross-AZ traffic, NAT Gateway data processing, idle resources. These are the surprises.

> **The #1 AWS bill-shock source is data transfer, not compute.** Storing and computing is cheap; *moving bytes out* is what hurts.

---

## EC2 — compute

**Billed on:** instance-seconds (per-second, 60s min) × instance size · **plus** attached EBS · **plus** data transfer out.
The instance price already includes its share of CPU + RAM + networking; you do **not** pay separately for the OS (Linux).

| Instance | vCPU / RAM | On-Demand $/hr (us-east-1) | ≈ $/month (730h) | eu-west-1 delta |
|---|---|---|---|---|
| t3.micro | 2 / 1 GiB | $0.0104 | ~$7.60 | +~10% |
| t3.medium | 2 / 4 GiB | $0.0416 | ~$30 | +~10% |
| m5.large | 2 / 8 GiB | $0.096 | ~$70 | +~11% ($0.107/hr) |
| m6i.large | 2 / 8 GiB | $0.096 | ~$70 | +~11% |
| c6i.large (compute) | 2 / 4 GiB | $0.085 | ~$62 | +~10% |
| r6i.large (memory) | 2 / 16 GiB | $0.126 | ~$92 | +~10% |
| m7g.large (Graviton) | 2 / 8 GiB | ~$0.0816 | ~$60 | +~10% |

**Pricing models (same hardware, different commitment):**

| Model | Discount vs On-Demand | When |
|---|---|---|
| On-Demand | baseline | spiky / short / unknown duration |
| Savings Plans / Reserved (1-yr, no upfront) | ~30–40% off | steady 24/7 baseline |
| Savings Plans / Reserved (3-yr, all upfront) | up to ~60–72% off | locked-in long-term baseline |
| Spot | up to **90% off** | fault-tolerant, interruptible (batch, CI, stateless workers) |
| Graviton (ARM) | ~10–20% cheaper + better perf/watt | anything with an ARM-compatible build |

- **Cost lever:** match the *commitment* to the *workload shape*. 100% On-Demand = beginner; 100% Spot = reckless; real fleets mix On-Demand baseline + Spot for elastic + Savings Plans for the steady core.

---

## Containers — ECS, Fargate, EKS, ECR

**Billed on:** the **compute underneath** (EC2 or Fargate) · **plus** the EKS control-plane fee · **plus** ECR image storage. The *orchestrators* ECS itself is free.

| Service | Billed on | Headline price | Feel / gotcha |
|---|---|---|---|
| **ECS (orchestrator)** | nothing | **$0** | you pay only for the EC2 or Fargate it runs |
| **Fargate** | per **vCPU-hour + GB-hour** (per second, 1-min min) | ~**$0.04048/vCPU-hr + $0.004445/GB-hr** | 1 vCPU + 2 GB 24/7 ≈ **$36/mo**; **Fargate Spot ~70% off** |
| **EKS control plane** | per **cluster-hour** | **$0.10/hr ≈ $73/month per cluster** | flat fee *before* any nodes — the EKS "tax" |
| **EKS nodes** | EC2 or Fargate underneath | (see EC2 / Fargate) | EKS = control-plane fee + node compute |
| **ECR** | per GB-month stored + data transfer out | **$0.10/GB-month** | image storage; cross-region replication adds transfer |

- **The key cost contrast:** **ECS adds no fee** (run it on Fargate or EC2 and pay only for that). **EKS charges $73/mo per cluster** *just for the managed control plane* — so for a small workload with no Kubernetes requirement, ECS on Fargate is cheaper *and* simpler. Pick EKS for the K8s ecosystem/portability, not to save money.
- **Fargate vs EC2 launch type:** Fargate = zero node management, pay-per-task (great for spiky/low-density). At **steady high utilization**, self-managed **EC2 (esp. Spot + Graviton + Karpenter)** is usually cheaper per unit — which is why Coinbase/Flutter run huge EKS-on-EC2 fleets.
- **Fargate Spot** (~70% off) for interruptible tasks; **Graviton (ARM) Fargate** ~20% cheaper.
- eu-west-1 ≈ +~10% on Fargate/EKS hourly rates.

---

## Serverless — Lambda, DynamoDB, API Gateway, Cognito

**Billed on:** pure **pay-per-use** — per request/invocation + resource-time. The defining trait: **scale to zero, pay $0 when idle.**

| Service | Billed on | Headline price | Free tier (monthly) |
|---|---|---|---|
| **Lambda** | per request + **GB-second** of run time | **$0.20/M requests** + **$0.0000166667/GB-s** | **1M requests + 400,000 GB-s** |
| **DynamoDB (on-demand)** | per **read/write request unit** + storage | ~$0.625/M writes · ~$0.125/M reads · **$0.25/GB-mo** | 25 GB storage |
| **DynamoDB (provisioned)** | per **RCU/WCU-hour** + storage | ~$0.00013/WCU-hr · ~$0.000025/RCU-hr | 25 WCU + 25 RCU |
| **API Gateway — REST** | per million calls | **$3.50/M** (+ optional cache $/hr) | 1M calls (first 12 mo) |
| **API Gateway — HTTP** | per million calls | **$1.00/M** (~70% cheaper than REST) | — |
| **API Gateway — WebSocket** | per million messages + connection-minutes | ~$1.00/M + $0.25/M conn-min | — |
| **Cognito User Pools** | per **monthly active user (MAU)** | **first 50,000 MAU free**, then ~$0.0055/MAU (tiers down) | 50,000 MAU |

- **The serverless cost story:** a low-traffic API (Lambda + DynamoDB on-demand + HTTP API + Cognito under 50k users) can run **$0–a few dollars/month** and scale automatically — no idle servers. That "$0 at rest" is *why* serverless wins for spiky/unpredictable/new workloads.
- **Lambda cost lever:** cost = requests × (memory × duration). More memory also = more CPU, so a function can run *faster and cheaper* at higher memory — tune with Lambda Power Tuning. **Provisioned Concurrency** removes cold starts but adds an always-on charge (don't leave it on needlessly).
- **DynamoDB lever:** **on-demand** for spiky/unknown traffic (pay per request, no capacity planning); **provisioned + auto-scaling** for steady, predictable, high volume (cheaper per unit). **DAX** (microsecond cache) and **Global Tables** (multi-region) add cost.
- **API Gateway lever:** **HTTP API** is ~⅓ the price of REST — use it unless you need REST-only features (API keys/usage plans, request validation, per-method caching, WAF).
- eu-west-1 ≈ +~10% on Lambda GB-s and DynamoDB; API Gateway/Cognito ~uniform.

---

## EBS — block storage

**Billed on:** GB **provisioned** per month (not used — provision 100 GB, use 1 GB, pay for 100) · plus IOPS/throughput on some types · plus snapshots.

| Type | $/GB-month | Baseline included | Extra |
|---|---|---|---|
| gp3 (default SSD) | $0.08 | 3,000 IOPS + 125 MB/s **free** | +$0.005/IOPS over 3k · +$0.04/MB/s over 125 |
| gp2 (legacy SSD) | $0.10 | IOPS scales with size (3/GB) | — |
| io2 / io2 Block Express | $0.125 | — | +$0.065 per provisioned IOPS (tiered) |
| Snapshots (to S3) | $0.05 | incremental (changed blocks only) | archive tier $0.0125 (90-day min) |

- **Trap:** EBS keeps billing after the EC2 instance is **stopped or terminated** if the volume isn't deleted. Orphaned volumes + snapshots are a classic silent cost.
- **Cost lever:** default to **gp3** — it's ~20% cheaper than gp2 *and* lets you buy IOPS/throughput independently of size.
- eu-west-1 ≈ +~10% (gp3 ≈ $0.088/GB-mo).

---

## S3 — object storage

**Billed on:** GB stored/month (per class) · **plus requests** (PUT/GET) · **plus retrieval fees** (cold classes) · **plus data transfer out**.

| Class | $/GB-month | Retrieval fee | Min duration | Use |
|---|---|---|---|---|
| Standard | $0.023 | — | — | hot, frequent |
| Intelligent-Tiering | $0.023 + $0.0025/1k obj monitor | — (auto-moves) | — | unknown/changing access |
| Standard-IA | $0.0125 | $0.01/GB | 30 days | infrequent, fast when needed |
| One Zone-IA | $0.010 | $0.01/GB | 30 days | re-creatable, single-AZ ok |
| Glacier Instant Retrieval | $0.004 | $0.03/GB | 90 days | archive, ms access |
| Glacier Flexible Retrieval | $0.0036 | mins–12h tiers | 90 days | archive, occasional |
| Glacier Deep Archive | **$0.00099** (~$1/TB) | 12–48h | 180 days | compliance, "never" access |
| Express One Zone | $0.11 (storage) | cheap requests | — | ultra-low-latency, single-AZ |

**Requests:** PUT/COPY/POST/LIST $0.005/1,000 · GET/SELECT $0.0004/1,000.
**Data transfer OUT to internet:** first 100 GB/month **free**, then ~$0.09/GB (tiers down past 10 TB). **IN is free.**

- **23× ratio:** Deep Archive is ~1/23rd the price of Standard — lifecycle policies that age data down the classes are the biggest S3 saving.
- **Trap:** cold classes charge **per-object overhead + retrieval fees + minimum durations**. Storing millions of tiny objects in Glacier can cost *more* than Standard.
- eu-west-1 ≈ same for Standard ($0.023); Deep Archive same (~$0.00099).

---

## Storage Extras — FSx, Storage Gateway, DataSync, Transfer Family, Snow, Backup

**Billed on:** mostly **GB provisioned/stored per month** (FSx, Gateway) · **per-GB moved** (DataSync) · **per-endpoint-hour + per-GB** (Transfer) · **per-job + per-day** (Snow).

| Service | Billed on | Headline price | Gotcha / feel |
|---|---|---|---|
| **FSx for Windows** | GB-month (SSD) + throughput | ~$0.13/GB-mo SSD (HDD ~$0.013) | 1 TB SSD ≈ $130/mo; Multi-AZ ~doubles |
| **FSx for Lustre** | GB-month, by deployment | Scratch ~$0.14/GB-mo · Persistent by throughput tier | HPC scratch is cheap-ish but ephemeral |
| **FSx ONTAP / OpenZFS** | GB-month + throughput/IOPS | ~$0.13–0.14/GB-mo (+ capacity pool tiering) | ONTAP auto-tiers cold data cheaply |
| **Storage Gateway** | per-GB written to AWS + underlying S3/Glacier | ~$0.01/GB written + S3/Glacier storage | gateway VM is free; you also pay the S3 it lands in |
| **DataSync** | per-GB copied | **$0.0125/GB** moved | 100 TB migration ≈ $1,250 (one-off); ~10× faster than DIY |
| **Transfer Family** | per-protocol-endpoint-hour + per-GB | **$0.30/endpoint-hr ≈ $216/mo** + $0.04/GB | the always-on endpoint fee is the surprise — idle still bills |
| **Snowball Edge** | per-job fee + days + shipping | ~$300 Storage-Optimized job (incl. ~10 days), +~$30/day | **data transfer INTO AWS is free**; you pay for the box/time |
| **Snowcone** | per-job fee + days | ~$60–$70 job + per-day | small edge/8 TB jobs |
| **AWS Backup** | GB-month of backup + restore/cross-region | EBS-snapshot backup ~$0.05/GB-mo (varies by resource) | cross-region copy adds transfer; Vault Lock = WORM |

- **Snow billing model is different:** you don't pay per-GB to import — you pay a **job/service fee + per-day retention + shipping**. Inbound data transfer to AWS is free. That's *why* Snow wins over the network for huge datasets: no egress, no bandwidth bottleneck.
- **Transfer Family trap:** that **$0.30/hour-per-protocol endpoint (~$216/mo)** bills whether or not anyone connects — like an idle ALB. Don't leave SFTP endpoints running in dev.
- **DataSync vs Snowball cost lever:** DataSync ($0.0125/GB) is great for ≤ tens of TB with decent bandwidth; past that, network time/cost loses to a Snowball job (free inbound transfer, fixed box fee).
- eu-west-1 ≈ +~10% on the GB-month figures.

---

## RDS / Aurora / ElastiCache — databases

**RDS billed on:** instance-hours × size · **×2 for Multi-AZ** · plus storage (gp2 $0.115/GB-mo) · plus backups (free up to DB size, then $0.095/GB-mo) · plus data transfer.

| RDS MySQL instance | $/hr single-AZ | ≈ $/mo single-AZ | Multi-AZ |
|---|---|---|---|
| db.t3.micro | ~$0.017 | ~$12.40 | ~$25 |
| db.t3.medium | ~$0.068 | ~$50 | ~$100 |
| db.m5.large | ~$0.171 | ~$125 | ~$250 |
| db.r5.large (memory) | ~$0.24 | ~$175 | ~$350 |

**Aurora:**
- Provisioned: db.r6g.large ~$0.26/hr · storage $0.10/GB-mo · **I/O $0.20 per million requests** (Aurora Standard).
- **Aurora I/O-Optimized:** no per-I/O charge, but ~30% higher instance + higher storage — wins when I/O is > ~25% of the bill.
- **Aurora Serverless v2:** **$0.12 per ACU-hour** (1 ACU ≈ 2 GiB RAM). Scales 0.5→256 ACU (or to **0** with auto-pause). Pay only for capacity used.
- **RDS Proxy:** $0.015 per vCPU-hour of the underlying instance (connection pooling).

**ElastiCache:** cache.t3.micro ~$0.017/hr · cache.r6g.large ~$0.226/hr · Redis Serverless $0.125/GB-hr stored + ECPU.

- **Trap:** Multi-AZ **doubles** the compute bill — it buys availability, not read scaling. Read **Replicas** scale reads; don't confuse them.
- **Cost lever:** Serverless v2 for spiky/dev workloads (scales to near-zero); provisioned + Reserved for steady 24/7 production.
- eu-west-1 ≈ +~10%.

**Purpose-built databases (order-of-magnitude):**
- **Redshift** (data warehouse): from ~$0.25/hr (dc2.large) to large clusters; **Redshift Serverless** ~$0.36/RPU-hr — petabyte analytics, columnar/OLAP.
- **Neptune** (graph): ~$0.10–$0.35/hr per instance (+ storage/IO) — Serverless available.
- **DocumentDB** (MongoDB-compatible): ~$0.28/hr (t3.medium) up — instance-based like RDS.
- **Keyspaces** (Cassandra): serverless, on-demand per read/write request unit.
- **Timestream** (time-series): pay per ingest + per query (TB scanned) + storage tiers (memory vs magnetic).
- **MemoryDB** (durable Redis): ~$0.20/hr (r6g.large) — primary DB, not just cache.
- **Teaching point:** these are *purpose-built* — you pick by data shape (graph, ledger, time-series, document, wide-column), not cost. The exam tests "which purpose-built DB," rarely their price.

**Data & Analytics (order-of-magnitude):**
- **Athena** (serverless SQL on S3): **$5 per TB scanned** — partition + columnar (Parquet) + compression slash cost (scan less data). Pay only per query.
- **Glue** (serverless ETL + Data Catalog): ETL jobs ~$0.44/DPU-hour; Data Catalog first 1M objects free; crawlers per DPU-hour.
- **EMR** (managed Hadoop/Spark): EC2 cost + small EMR per-instance surcharge (~$0.01–0.27/hr/instance); use Spot for task nodes.
- **OpenSearch**: instance-hours (~$0.10–$1/hr) + EBS — or **Serverless** (per OCU-hour).
- **QuickSight** (BI): **Author ~$24/user/mo** (or $18 annual); **Reader ~$0.30/session (capped $5/mo)**; SPICE in-memory included tier.
- **MSK** (managed Kafka): per broker-hour (like Amazon MQ) + storage — always-on; **MSK Serverless** per-partition + throughput.
- **Cost lever (Athena):** "scan less" — partitioning by date and converting to Parquet can cut a query from $5 to cents. The classic least-ops/cheap S3 analytics answer is **Athena + Glue Catalog**, not a running Redshift/EMR cluster.

---

## ELB & ASG — load balancing + scaling

**Billed on:** fixed hourly rate · **plus capacity units** (LCU/NLCU) metering new connections, active connections, processed bytes, rule evals.

| Resource | $/hr | ≈ $/mo base | + capacity |
|---|---|---|---|
| ALB | $0.0225 | ~$16.20 | $0.008 / LCU-hr |
| NLB | $0.0225 | ~$16.20 | $0.006 / NLCU-hr |
| Gateway LB | $0.0125 | ~$9.10 | $0.004 / GLCU-hr |
| Classic LB (legacy) | $0.025 | ~$18.25 | $0.008 / GB |
| **Auto Scaling Group** | **$0** | **free** | you pay only for the EC2 it launches |

- **KEY:** **ASG is free.** It's a control loop, not a billed resource — you pay for the instances it adds. This is why "scale to zero at night" is pure saving.
- **Trap:** an ALB costs ~$16/mo **even with zero traffic** (the fixed hour charge). Idle ALBs in dev accounts are a classic waste.
- eu-west-1 ALB ≈ $0.0252/hr (~$18.40/mo, +~12%).

---

## Decoupling / Messaging — SQS, SNS, Kinesis, Amazon MQ

**Billed on:** per-request/per-message (SQS, SNS) · per-shard-hour + payload (Kinesis Streams) · per-GB (Firehose) · **per-broker-hour** (Amazon MQ — always-on, the odd one out).

| Service | Billed on | Headline price | Feel / gotcha |
|---|---|---|---|
| **SQS Standard** | per request (64 KB = 1 req) | **$0.40 / million** (first 1M free) | dirt cheap; serverless, scales to zero |
| **SQS FIFO** | per request | **$0.50 / million** | slight premium for exactly-once + ordering |
| **SNS** | per million publishes + delivery | **$0.50 / million** publishes (first 1M free) | SQS/Lambda deliveries cheap; **SMS/email cost extra** |
| **Kinesis Data Streams (provisioned)** | per **shard-hour** + payload units | **$0.015/shard-hr (~$11/shard/mo)** + $0.014/M PUT (25 KB units) | you pay for shards 24/7 even when idle |
| **Kinesis Streams (on-demand)** | per-GB in/out + stream-hour | ~$0.040/GB in + stream-hour | no shard management; pricier per-GB, simpler |
| **Kinesis Data Firehose** | per GB ingested | ~**$0.029/GB** (tiers down) | fully serverless; no shards; near-real-time buffering |
| **Amazon MQ** | per **broker-instance-hour** + storage | mq.m5.large ~**$0.30/hr (~$220/mo)** + storage | **always-on like an EC2/RDS box** — not pay-per-message |

- **The shape difference (key teaching point):** SQS & SNS are **serverless / pay-per-use** (scale to zero, pennies per million). Kinesis Streams (provisioned) and **Amazon MQ** are **provisioned / always-on** (you pay for shards/brokers by the hour whether or not traffic flows). That's *why* "new cloud-native, least cost at low/spiky volume" → SQS/SNS, while MQ is chosen for *compatibility*, not cost.
- **SQS cost trap:** billing is per **request**, and each request carries up to 64 KB — a 256 KB message = 4 requests. Long polling cuts empty-receive requests (and cost).
- **Kinesis vs SQS at scale:** very high *steady* throughput can make per-shard Kinesis or per-broker MQ cheaper than per-message SQS — but for spiky/low volume SQS wins.
- eu-west-1 ≈ +~10% (MQ/Kinesis hourly rates); SQS/SNS per-request prices are ~uniform.

---

## Route 53 — DNS (global, no per-region pricing)

**Billed on:** hosted zones/month · DNS queries answered · health checks.

| Item | Price |
|---|---|
| Hosted zone | $0.50/mo (first 25), $0.10/mo after |
| Standard queries | $0.40 / million (first 1B), $0.20 after |
| Latency-based queries | $0.60 / million |
| Geolocation / geoproximity | $0.70 / million |
| Health check (AWS endpoint) | $0.50/mo (first 50 free) |
| Health check (external endpoint) | $0.75/mo + optional features |
| **Alias query → ALB / CloudFront / S3 / API GW** | **FREE** |
| Domain registration (.com) | ~$9–15 / year |

- **Cost lever:** use **Alias records** to AWS resources, not CNAMEs — Alias queries to AWS targets are **free**, CNAME queries are billed.
- Route 53 is **global** — the same price worldwide. No eu-west-1 delta.

---

## CloudFront — CDN / edge caching

**Billed on:** GB **transferred out** to viewers (per edge region) · **plus HTTP/HTTPS requests** · plus invalidations, edge-compute, Origin Shield.
There is **no hourly/fixed fee** — a CloudFront distribution with zero traffic costs **$0**. You pay only when bytes/requests flow.

| Dimension | Price (US / Europe edges) | Notes |
|---|---|---|
| Data transfer out to internet | ~**$0.085/GB** first 10 TB → tiers down (~$0.080 / $0.060 / $0.040 at higher volume) | Asia/India/S.America/Oceania edges are pricier (~$0.10–$0.17/GB) |
| **Origin fetch (S3/EC2/ALB → CloudFront)** | **FREE** | AWS does **not** charge data-transfer-out from an AWS origin into CloudFront |
| HTTPS requests | ~**$0.01 per 10,000** | HTTP slightly cheaper |
| Invalidation paths | first **1,000 paths/month free**, then **$0.005/path** | use versioned object names instead of invalidating |
| CloudFront Functions | **$0.10 per 1M** invocations | sub-ms, JS only, viewer events |
| Lambda@Edge | **$0.60 per 1M** + $0.00000625 / 128MB-s | ~6× CloudFront Functions; us-east-1 authored |
| Origin Shield | ~$0.0075–$0.01 per 10,000 requests | extra caching layer |

- **Always-Free Tier (perpetual, not 12-month):** **1 TB** data transfer out + **10M** requests + **2M** CloudFront Functions invocations per month.
- **Price Classes** (cost lever): **All** (every edge) · **200** (drops the priciest — S.America, Australia, NZ) · **100** (US, Canada, Europe, Israel only = cheapest). Fewer edges = lower bill, slightly higher latency for excluded regions.
- **The big lever / gotcha:** serving via CloudFront is usually **cheaper than serving directly from S3/EC2**, because (a) origin→edge transfer is free and (b) CloudFront egress rates undercut raw S3 egress at volume. The classic mistake is paying S3 egress to the world instead of fronting it with CloudFront.
- eu-west-1 (Ireland) viewers are served from **Europe edges** → same ~$0.085/GB tier as US.

---

## Global Accelerator — static-IP anycast networking

**Billed on:** a **fixed hourly fee per accelerator** · **plus a per-GB Data-Transfer-Premium (DT-Premium)** on top of normal AWS data transfer.

| Dimension | Price | Notes |
|---|---|---|
| Accelerator fixed fee | **$0.025 / accelerator / hour ≈ $18/month** | charged even at zero traffic; per accelerator you run |
| DT-Premium (out) | ~**$0.015/GB** (US/Europe) up to ~$0.10+/GB (Asia/S.America) | premium *added to* standard data-transfer-out, based on the dominant edge→region path |

- **Unlike CloudFront, GA has a fixed monthly floor (~$18)** whether or not anyone connects — because you're reserving 2 static anycast IPs + backbone routing, not caching.
- **No caching, no free tier.** GA never reduces bytes (it has nothing to cache) — it only makes them travel faster on the AWS backbone, so the DT-Premium is a *pure performance/availability tax* you pay on every GB.
- **Cost framing vs CloudFront:** CloudFront *lowers* effective egress (caching + free origin fetch); GA *raises* it (premium per GB). Choose GA for non-HTTP / static-IP / fast-failover needs — never to "save money on transfer."
- eu-west-1 endpoints: DT-Premium from Europe edges ≈ the $0.015/GB low tier.

---

## IAM — identity (the free one)

**Billed on:** *nothing for the core service.*

- IAM **users, groups, roles, policies** = **free**. Unlimited. You pay only for what the identities *consume*.
- **IAM Identity Center** (SSO) = free.
- **IAM Access Analyzer:** external-access analyzers free; **unused-access analyzers** ~$0.20 per IAM role/user analyzed per month.

- **Teaching point:** IAM being free is *why* "least privilege via more granular roles" never costs more — there's no penalty for creating 50 tightly-scoped roles instead of 5 broad ones.

---

## NAT Gateway — the famous bill-shock

**Billed on:** $0.045/hr (~$32.85/mo) **+ $0.045 per GB processed** (us-east-1). eu-west-1: $0.048/hr (~$35.04/mo) + $0.048/GB.

- **The trap:** the per-GB *processing* charge stacks **on top of** normal data-transfer-out. A chatty private subnet pulling packages/updates through NAT can quietly cost **$1,000s/month**.
- **Cost lever:** **VPC Gateway Endpoints for S3 and DynamoDB are FREE** and bypass NAT entirely — route that traffic around the NAT Gateway.

---

## 🧮 Combined reference architecture — small production web app (us-east-1)

A realistic 3-tier app: ALB → 2× EC2 (ASG) → Multi-AZ RDS, with S3 assets and a NAT Gateway.

| Component | Spec | ≈ $/month |
|---|---|---|
| EC2 | 2 × t3.medium (On-Demand) | $60 |
| ALB | base + light LCU | $24 |
| RDS MySQL | db.t3.medium **Multi-AZ** + 100 GB | $111 |
| S3 | 100 GB Standard + light requests | $3 |
| NAT Gateway | base + modest data | $33+ |
| Route 53 | 1 hosted zone (Alias → ALB, free queries) | $0.50 |
| Data transfer out | ~200 GB (100 free) | $9 |
| **Total** | | **≈ $240/month (~$2,900/yr)** |

- In **eu-west-1 (Dublin)** the same stack is **≈ +10% ≈ $265/month**.
- **Biggest levers, in order:** (1) Reserved/Savings Plans on the EC2 + RDS baseline → cut ~30–40%; (2) Spot for any elastic ASG capacity → cut up to 90% on that slice; (3) drop RDS to single-AZ in non-prod → halve the DB line.

---

## 🏭 Industry-scale ballparks (clearly labelled *estimates*)

Real spend depends on contracts, EDPs (Enterprise Discount Programs, often 10–30% off list), and Savings Plans — these are **order-of-magnitude** only.

- **Ryanair-scale S3 data lake** (petabytes, mixed classes + lifecycle to Glacier): storage alone easily **$10k–$50k+/month**, dominated by Standard for hot data; lifecycle to Deep Archive is what keeps it from being 5–10× higher.
- **Intercom-scale relational tier** (high-connection SaaS, many large Aurora/RDS instances + replicas + Proxy): the database tier alone runs **tens of thousands $/month** — which is exactly why connection pooling (RDS Proxy) and right-sizing matter at their scale.
- **Coinbase-scale EKS on Graviton** (thousands of services): the published Graviton move ("scales 50% faster, cuts costs 62%") shows the lever — **ARM + Spot + Karpenter** turns a multi-million-dollar annual compute bill into a fraction of it.
- **Rule of thumb at scale:** the bill is almost always **compute + data transfer first**, storage second, managed-service premiums third. Cut egress and right-size compute before anything else.

---

## Sources (verified June 2026)
- EC2 On-Demand — https://aws.amazon.com/ec2/pricing/on-demand/
- EBS — https://aws.amazon.com/ebs/pricing/
- S3 — https://aws.amazon.com/s3/pricing/
- RDS — https://aws.amazon.com/rds/pricing/ · Aurora — https://aws.amazon.com/rds/aurora/pricing/
- ELB — https://aws.amazon.com/elasticloadbalancing/pricing/
- Route 53 — https://aws.amazon.com/route53/pricing/
- VPC / NAT Gateway — https://aws.amazon.com/vpc/pricing/
- CloudFront — https://aws.amazon.com/cloudfront/pricing/
- Global Accelerator — https://aws.amazon.com/global-accelerator/pricing/
