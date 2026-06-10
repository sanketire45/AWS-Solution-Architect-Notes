# SAA-C03 Gap-Fill Research Pass — Raw Notes
### Dublin Company Architectures · Missing Services · Distractor Maps · Pricing Math · Cross-Topic Integrations · Meta-Patterns

> These are dense raw research notes intended as source material for a later masterclass/exam-cracker doc. They **extend** the prior 25-topic deliverable — they do not restate it. Facts are tagged **VERIFIED** (with named source) or **INFERRED** (industry-pattern reasoning). Pricing is region/time-sensitive (us-east-1/eu-west-1 examples); the exam tests *relative ordering*, not exact dollars.

## TL;DR
- **Dublin architectures verified from primary sources:** Fenergo (single-cloud AWS, Lambda + DynamoDB + EventStoreDB event-sourcing across 3 AZs, "Always On – Active-Active-Active"); Coinbase Ireland (EKS + Graviton + MSK); Stripe (isolated AWS Card Data Vault, AES-256, SAML+SCIM+JIT); Ryanair (all-in AWS — Aurora, S3 data lake + Kinesis, MSK, Tape Gateway, Shield Advanced); Intercom (13 Aurora MySQL clusters + DynamoDB + ElastiCache memcached); Flutter/PokerStars (EKS-style containers, MSK, Cloud WAN, MWAA).
- **Missing services now covered with exam triggers + numbers:** WAF/Shield Advanced, VPC Lattice, Step Functions, AppSync, MSK, Amazon MQ, DMS/SCT, Resilience Hub/FIS/MGN/DRS, hybrid AD, Mountpoint for S3, ECS Service Connect, DynamoDB adaptive capacity/split-for-heat, warm pools, hibernation, EBS Multi-Attach/Snapshot Archive, Aurora Backtrack/Clone/PITR/Limitless, Lambda event-source-mapping batching, Organizations/Control Tower, cost categories.
- **Pricing-math crossovers quantified:** S3 storage class break-even, NAT-GW-vs-interface-endpoint crossover, Aurora I/O-Optimized 25% rule, RI break-even, Step Functions Standard-vs-Express.

---

# TOPIC 1 — IAM

**Dublin deep-dives**
- **AIB (Allied Irish Banks)** — *VERIFIED hybrid posture:* AIB signed a €65m three-year agreement with IBM (Dec 2021) for an IBM z15 + Cloud Pak hybrid-cloud platform, and uses partner Version 1's "Journey to Cloud" methodology for AWS finance workloads. *INFERRED IAM pattern:* IAM Identity Center federated to an external IdP (Okta/Entra), permission sets mapped to job roles; developers obtain just-in-time access via a ServiceNow request that triggers a Lambda to provision a temporary role; PCI-DSS auditors get a cross-account read-only `SecurityAudit` role assumed via STS.
- **Fenergo (RegTech KYC/AML SaaS)** — *VERIFIED single-cloud AWS, serverless-first.* IAM driver: multi-tenant SaaS for regulated banks needs hard tenant isolation → IAM policies with per-tenant condition keys, least-privilege Lambda execution roles per microservice.
- **Stripe** — *VERIFIED:* isolated AWS Card Data Vault with separate credentials; access "restricted to a small number of specially trained engineers and access is reviewed quarterly"; dashboard supports SAML 2.0 SSO + SCIM + just-in-time provisioning.

**Section-2 services mapped here**
- **Organizations + Control Tower:** SCPs are *deny-based guardrails* (they cap, never grant). Tag policies, Backup policies, AI-services opt-out policies. Control Tower = landing zone + Account Factory + delegated administration (e.g., delegate GuardDuty/Config admin to a security account). Data-residency SCP example: `Deny` when `aws:RequestedRegion` ∉ {eu-west-1, eu-west-2} for Irish-regulated workloads.
- **Hybrid AD:** **AD Connector** = proxy/redirect to on-prem AD, no directory stored in AWS (lightweight). **AWS Managed Microsoft AD** = full managed multi-AZ AD, supports trusts + schema extensions. **Simple AD** = Samba-based, <5,000 users, no MFA/trusts.

**Scenario patterns + distractor reasoning**
1. *"EC2 app needs S3 access without storing credentials."* ✅ **IAM role (instance profile).** ✗ Hardcoded keys (leak/rotation risk). ✗ Keys in Secrets Manager (still long-lived; role gives auto-rotated STS creds). ✗ Bucket policy by account (authorizes, doesn't *authenticate* the instance).
2. *"Restrict every member account to eu-west-1."* ✅ **SCP with `aws:RequestedRegion` condition.** ✗ IAM policy per user (doesn't scale, not org-wide). ✗ Permissions boundary (caps a principal's max perms, not an org region lock). ✗ Config rule (detective, not preventive).
3. *"Cross-account read-only for auditors."* ✅ **Cross-account IAM role + `sts:AssumeRole` + SecurityAudit managed policy.** ✗ IAM user per account (credential sprawl). ✗ Resource policy (not all services support). ✗ Cognito (end-user identity, not workforce auditor).

**Numbers/limits:** IAM roles/account 1,000 (raisable); managed policies/role 10 (→20); policy doc 6,144 chars; STS session 15 min–12 h (role-chaining caps at 1 h); IAM Identity Center is free.

---

# TOPIC 2 — VPC

**Dublin deep-dives**
- **Coinbase Ireland** — *VERIFIED* EKS, multi-AZ. *INFERRED* 3-AZ private subnets, NAT per AZ, interface endpoints to MSK/DynamoDB to keep traffic on the AWS network.
- **Fenergo** — *VERIFIED:* deploys across three AZs — "Always On – Active – Active – Active. A failure at one or two AZs will not affect the availability of the application."

**Subnet layout sketch (eu-west-1):**
```
VPC 10.0.0.0/16
  public-a 10.0.0.0/24 (NAT-a, ALB)        eu-west-1a
  public-b 10.0.1.0/24 (NAT-b)             eu-west-1b
  private-app-a/b 10.0.10.0/24,10.0.11.0/24
  private-db-a/b  10.0.20.0/24,10.0.21.0/24
  Gateway endpoints (FREE): S3, DynamoDB
  Interface endpoints: ECR, STS, CloudWatch, Secrets Manager
```

**Section-2: VPC Lattice (App Mesh successor)**
- App Mesh **EOL Sept 30, 2026**; new customers blocked since **Sept 24, 2024**.
- VPC Lattice = fully managed L7 (HTTP/HTTPS/gRPC) + L4 (TLS) application networking, GA March 2023. Components: **Service Network → Services → Listeners → Target Groups** (maps to App Mesh Mesh/Virtual Service/Virtual Node). **No sidecar proxies** (App Mesh used Envoy sidecars). Cross-VPC/cross-account via **RAM** — no Transit Gateway needed. **IAM-based auth** (SIGv4 request signing). Limits: regional only, no mTLS at the data plane, no UDP, no internet-facing entry.
- Decision: **VPC Lattice** (cross-VPC/account, mixed compute EKS+ECS+Lambda+EC2) · **ECS Service Connect** (in-cluster ECS) · **internal ALB** (simple, mature L7) · **API Gateway** (external API management).

**Scenarios + distractors**
1. *"Private EC2 → S3, no internet, lowest cost."* ✅ **S3 Gateway Endpoint (free).** ✗ NAT GW (works but $/GB + hourly). ✗ Interface endpoint for S3 (exists but gateway is free). ✗ IGW (exposes to internet).
2. *"Connect microservices across 3 VPCs + 2 accounts, mixed EKS/Lambda, least ops."* ✅ **VPC Lattice.** ✗ TGW (network routing, no L7/IAM auth). ✗ App Mesh (deprecated 2026). ✗ VPC peering (no transitive routing, mesh complexity).
3. *"Two VPCs with overlapping CIDR must communicate."* ✅ **PrivateLink.** ✗ Peering/TGW (both fail on overlapping CIDR). ✗ VPN.

**Numbers:** 5 VPCs/region (raisable); 200 subnets/VPC; 5 CIDRs/VPC (→50). Interface endpoint ≈ $0.01/hr/AZ + $0.01/GB; NAT GW ≈ $0.045/hr + $0.045/GB; S3/DynamoDB gateway endpoint **free**.

---

# TOPIC 3 — EC2

**Dublin deep-dives**
- **Ryanair** — *VERIFIED:* migrated Java + Go services to **Graviton**; uses **EC2 Image Builder** (free) to bake hardened golden AMIs (Amazon Linux 2 base), a Lambda writes the new AMI ID to SSM Parameter Store, and ECS/EC2 launches reference it. Switched gp2→gp3 and x86→Graviton2 "in 15 minutes" by changing one pipeline parameter; ~30% cost reduction on migrated services. *Interview line:* "Ryanair's platform team bakes golden AMIs with EC2 Image Builder and publishes the AMI ID to Parameter Store via Lambda, so every deploy references the latest approved image."
- **HubSpot Dublin** — *VERIFIED:* runs HBase on **Graviton** (ARM) for price/performance; stack is AWS + Kubernetes.
- **Coinbase** — *VERIFIED (AWS case study):* "Since 2022, Coinbase has reduced its operating costs by 62 percent"; migrated **3,500 services from EC2 to Amazon EKS and AWS Graviton**, with Graviton delivering ~20% lower cost and a 68% reduction in resources used by migrated services.

**Section-2 deep-dives**
- **Hibernation:** saves RAM to the **encrypted EBS root volume**, reloads on start (encrypted EBS is required). Beats stop/start when the app has a long warm-up or large in-memory cache. While hibernated you pay EBS (incl. RAM storage) + EIP, not the instance.
- **EBS Multi-Attach:** **io1/io2 only**, up to **16 instances**, **same AZ only**, requires a **cluster-aware filesystem (GFS2, OCFS2)** — *not* ext4/xfs/NTFS unless cluster-aware. Not for boot volumes.
- **EBS Snapshot Lock** = compliance/governance WORM hold (can't delete). **Snapshot Archive** = ~75% cheaper tier, restore 24–72 h — use for snapshots kept >90 days, rarely restored.

**Scenarios + distractors**
1. *"Shared block storage for a clustered app, same AZ."* ✅ **io2 Multi-Attach + cluster filesystem.** ✗ EFS (file, not block). ✗ gp3 Multi-Attach (unsupported — io1/io2 only). ✗ Instance store (ephemeral, not shared).
2. *"Resume with in-memory state after off-hours."* ✅ **Hibernation.** ✗ Stop/start, AMI, warm-pool-stopped — all lose RAM.
3. *"Retain snapshots 7 yrs cheapest, restore delay OK."* ✅ **Snapshot Archive.** ✗ Standard snapshots (costly). ✗ Manual Glacier copy (not supported). ✗ Snapshot Lock (compliance, not cost).

**Numbers:** gp3 baseline 3,000 IOPS / 125 MB/s free, up to 16,000 IOPS; io2 Block Express up to 256,000 IOPS / 4,000 MB/s / 64 TB. Spot up to 90% off, 2-min interruption notice. Placement groups: cluster (low latency) / spread (max 7 per AZ) / partition (big data).

---

# TOPIC 4 — Auto Scaling Groups

**Dublin deep-dives**
- **Ryanair** — *VERIFIED* business pressure: Brexit/seasonal traffic volatility. *INFERRED* predictive + target-tracking scaling on the booking tier, mixed-instances Graviton fleet.
- **Intercom** — *VERIFIED:* "Each year on Black Friday, as many of our customers hit their busiest period, our infrastructure scales to match without human intervention" — target-tracking on Rails worker fleets.

**Mixed-instances policy sketch (Stripe-style API tier, INFERRED):**
```
MixedInstancesPolicy:
  LaunchTemplate: api-template (Graviton)
  Overrides: [c7g.large, c6g.large, m7g.large]
  InstancesDistribution: { OnDemandBaseCapacity: 4, OnDemandPercentageAboveBaseCapacity: 20, SpotAllocationStrategy: capacity-optimized }
TargetTracking: ALBRequestCountPerTarget = 1000
LifecycleHook: Terminating:Wait → graceful connection drain
```

**Section-2: Warm Pools**
- States: **Stopped** (cheapest — pay EBS + EIP only), **Running** (full price, fastest, discouraged), **Hibernated** (pay EBS incl. RAM, fast + warm memory).
- Default pool size = **Max − Desired**. Lifecycle hooks delay stop/hibernate until init completes. Instance-reuse policy (return to pool on scale-in) is **CLI/SDK only**.
- Warm pool = for long boot times (load GBs of data); predictive scaling = for known daily/weekly patterns. **Cannot combine a Mixed Instances Policy with a Warm Pool.**

**Scenarios + distractors**
1. *"App boots in 15 min, need fast scale-out."* ✅ **Warm Pool (Stopped).** ✗ Larger min capacity (wasteful). ✗ Predictive alone (still cold boot). ✗ Step scaling (doesn't fix boot time).
2. *"Scale ahead of predictable Monday 9am surge."* ✅ **Predictive (or scheduled) scaling.** ✗ Simple/target-tracking (reactive lag). ✗ Warm pool (speeds boot, not timing).
3. *"Graceful drain before terminate."* ✅ **Lifecycle hook (Terminating:Wait) + ELB connection draining.** ✗ Termination policy (chooses *which*, not graceful). ✗ Cooldown. ✗ Scale-in protection (prevents termination).

**Numbers:** default cooldown 300 s; health-check grace 300 s; target tracking auto-creates CloudWatch alarms. **Launch Configuration = LEGACY → eliminate (use Launch Template).**

---

# TOPIC 5 — Load Balancers (ALB / NLB / GWLB)

**Dublin deep-dives**
- **Ryanair** — *VERIFIED:* "Access is protected by AWS WAF and AWS Shield Advanced" on the Ryanair Connect serverless app behind an ALB.
- **Flutter/PokerStars** — *VERIFIED:* AWS Cloud WAN backbone for low-latency global gaming. *INFERRED* NLB for poker traffic, ALB for web.

**Section-2: WAF & Shield Advanced**
- **WAF attaches to:** CloudFront, ALB, API Gateway (REST), AppSync, Cognito user pool, App Runner, Amplify, Verified Access — **NOT NLB**.
- WAF rule types: AWS managed rule groups, third-party (Marketplace), rate-based, custom, IP set, regex pattern sets.
- WAF pricing: $5/web ACL/mo, $1/rule/mo, $0.60/million requests; Bot Control +$10/mo +$1/million.
- **Shield Standard** = free, automatic, L3/L4. **Shield Advanced** — per AWS Shield pricing page: "requires a **1-year subscription commitment**" at **$3,000/month**; includes SRT access (needs Business/Enterprise support), cost-protection credits for DDoS-driven scaling, and "**up to 50 billion requests per subscribed payer ID** to AWS Shield protected WAF resources in a calendar month."
- **Shield Advanced waives WAF web ACL + rule + base request fees** for protected resources: "Because the Amazon CloudFront Distribution is already protected under AWS Shield Advanced, there are no additional charges for AWS WAF web ACL, rule or request fees." **Caveat (verbatim):** "Managed rule groups such as Targeted Bots and Account Takeover Prevention are also not included in the Shield Advanced subscription" (nor Bot Control, CAPTCHA, >1,500 WCU). Practical use: if WAF spend >$3,000/mo across many accounts, Shield Advanced caps it.
- **Triggers:** "DDoS + cost protection / SLA credits / DRT" → Shield Advanced · "block SQLi/XSS" → WAF managed rules · "rate limit by IP" → WAF rate-based rule · "attach WAF to NLB" → **TRAP** (unsupported).

**Scenarios + distractors**
1. *"Route /api → service A, /web → service B."* ✅ **ALB path-based routing.** ✗ NLB (L4, no path). ✗ Classic LB (legacy). ✗ Route 53 (DNS, not in-LB path).
2. *"Static IP + extreme TPS + TLS passthrough."* ✅ **NLB.** ✗ ALB (L7, no native static IP). ✗ GWLB (firewall appliances). ✗ CloudFront.
3. *"Insert third-party firewall appliances transparently."* ✅ **GWLB (GENEVE port 6081).** ✗ NLB/ALB/WAF.
4. *"Block L7 HTTP flood with managed mitigation."* ✅ **Shield Advanced automatic L7 mitigation + WAF rate rule.** ✗ Shield Standard (L3/4 only). ✗ NACL (L4). ✗ Security Group (no rate logic).

**Numbers:** ALB = HTTP/HTTPS/gRPC/WebSocket, content routing; NLB = TCP/UDP/TLS, static/EIP per AZ, preserves source IP, millions req/s; GWLB = GENEVE 6081. Cross-zone: **ALB on by default (free); NLB off by default** (cross-AZ charges if enabled).

---

# TOPIC 6 — S3

**Dublin deep-dives**
- **Ryanair** — *VERIFIED:* company-wide **data lake on S3** with real-time **Kinesis** analytics; used **S3 Object Lambda** for the COVID travel-wallet; CloudFront fronts MyRyanair.
- **Coinbase** — *VERIFIED:* S3 stores snapshots from PostgreSQL and DynamoDB feeding Databricks/Delta Lake.

**Section-2: Mountpoint for Amazon S3** — FUSE file-system-like access to S3 from Linux. Use for ML training, HPC, sequential log writing. *Not* full POSIX (no random mid-file writes, no rename semantics). Compare: S3 API (full control); FSx for Lustre (true high-perf POSIX, sub-ms, for HPC).

**Scenarios + distractors**
1. *"ML training reads millions of S3 objects as files on Linux, least change."* ✅ **Mountpoint for S3.** ✗ FSx Lustre (faster but more cost/ops). ✗ EFS (requires copy). ✗ Download to EBS (doesn't scale).
2. *"Prevent accidental/malicious deletion of compliance objects."* ✅ **S3 Object Lock (compliance mode WORM) + versioning + MFA delete.** ✗ Bucket policy (mutable). ✗ Glacier vault lock (Glacier only). ✗ SCP.
3. *"Static website + HTTPS + low-latency global."* ✅ **S3 + CloudFront + OAC.** ✗ S3 website endpoint alone (no HTTPS on custom domain). ✗ ALB (overkill). ✗ Global Accelerator (no static caching).

**Numbers:** 11 nines durability; object max 5 TB, multipart recommended >100 MB (required >5 GB); strong read-after-write consistency. Cheapest→ priciest: Deep Archive $0.00099 < Glacier Flexible $0.0036 < Glacier IR $0.004 < One Zone-IA < Standard-IA $0.0125 < Standard $0.023 < Express One Zone $0.16. Min duration: IA 30 d, Glacier IR/Flexible 90 d, Deep Archive 180 d; min billable object 128 KB (IA/GIR).

---

# TOPIC 7 — Route 53

**Dublin deep-dives**
- **Ryanair** — *VERIFIED* Route 53 + RDS for DR; *INFERRED* failover + latency routing.
- **Stripe / Intercom** (US/EU/AU regions) — *INFERRED* latency- or geolocation-based routing to the nearest region for data-residency.

**Scenarios + distractors**
1. *"EU users → eu-west-1, US → us-east-1 for compliance."* ✅ **Geolocation routing.** ✗ Latency (perf, not residency). ✗ Weighted (no geo). ✗ Geoproximity (traffic bias, not strict residency).
2. *"Active-passive DR failover."* ✅ **Failover routing + health checks.** ✗ Weighted (active-active). ✗ Multivalue (no priority). ✗ Latency (no failover semantics).
3. *"Distribute by lowest latency across regions."* ✅ **Latency-based routing.** ✗ Geolocation/simple/weighted.

**Numbers:** policies — simple, weighted, latency, failover, geolocation, geoproximity (needs Traffic Flow), multivalue answer, IP-based. Alias records free (to ALB/CloudFront/S3). Private hosted zones for VPC.

---

# TOPIC 8 — CloudFront & Global Accelerator

**Dublin deep-dives**
- **Ryanair** — *VERIFIED:* CloudFront fronts MyRyanair to reduce latency.
- **Squarespace / Hostelworld Dublin** — *INFERRED* CloudFront for global static-asset delivery.

**Section-2: CloudFront Origin Groups for failover** — primary + secondary origin; failover triggers on the status codes you specify (500/502/503/504, 403/404). Works with S3, ALB, custom origins — CloudFront-level origin HA.

**Scenarios + distractors**
1. *"Failover to secondary S3 bucket on 5xx."* ✅ **CloudFront Origin Group.** ✗ Route 53 failover (DNS-level, slower). ✗ S3 CRR (replication, not failover). ✗ Lambda@Edge (custom logic, more ops).
2. *"Global TCP/UDP perf, static anycast IPs, non-HTTP."* ✅ **Global Accelerator.** ✗ CloudFront (HTTP caching). ✗ Route 53 latency (DNS). ✗ NLB (single region).
3. *"Cache + restrict S3 to CloudFront with SSE-KMS."* ✅ **CloudFront + OAC.** ✗ **OAI (legacy — fails with SSE-KMS; eliminate).** ✗ Public bucket. ✗ Signed URLs only.

**Numbers:** CloudFront 450+ PoPs; Lambda@Edge / CloudFront Functions; **OAC > OAI** (OAC supports SSE-KMS and all regions). Global Accelerator: 2 static anycast IPs, AWS backbone, fast regional failover, TCP/UDP, no caching.

---

# TOPIC 9 — RDS

**Dublin deep-dives**
- **Ryanair** — *VERIFIED:* migrated **Microsoft SQL Server → Aurora**, now runs ~22 million marketing emails/day "at a fraction of the cost."
- **Intercom** — *VERIFIED:* 13 Aurora MySQL clusters; **ProxySQL** connection pooling around the **16,000-connection Aurora MySQL limit**; migrating to Vitess/PlanetScale.

**Section-2: DMS + SCT** — homogeneous & heterogeneous migrations; **full load + CDC** (change data capture) for minimal downtime; **SCT** converts heterogeneous schema/code; DMS Fleet Advisor for discovery. Triggers: "Oracle → Aurora PostgreSQL minimal downtime" → **SCT + DMS full load + CDC**; "continuous on-prem → AWS replication" → **DMS CDC**.
**RDS quirks:** Oracle/SQL Server support BYOL vs License-Included; **RAC not supported on RDS** (use Multi-AZ); RDS Custom for OS/DB-level access.

**Scenarios + distractors**
1. *"On-prem Oracle → Aurora PostgreSQL, minimal downtime."* ✅ **SCT (schema) + DMS full load + CDC.** ✗ Native dump/restore (downtime + incompatible). ✗ Snowball (no schema conversion). ✗ DataSync (files, not DB).
2. *"Synchronous standby HA with auto-failover."* ✅ **Multi-AZ deployment.** ✗ Read replica (async, manual promote). ✗ (Multi-AZ cluster = valid newer 3-instance option). ✗ Backup restore.
3. *"Offload read/reporting traffic."* ✅ **Read replicas.** ✗ Multi-AZ (classic standby not readable). ✗ Bigger instance. ✗ ElastiCache.

**Numbers:** Multi-AZ = sync standby, no reads; read replicas async, up to 5 (15 Aurora), cross-region; backup retention 1–35 d; RDS Proxy pools connections for Lambda; storage autoscaling.

---

# TOPIC 10 — Aurora

**Dublin deep-dives**
- **Ryanair** — *VERIFIED:* Aurora for email marketing; AWS evangelist cited Backtrack as "as close as we can come… to an 'undo' option for reality."
- **Fenergo** — *VERIFIED* DynamoDB primary; *INFERRED* Aurora for relational tenant config.
- **Intercom** — *VERIFIED:* Aurora MySQL source-of-truth; built **per-customer databases across multiple smaller clusters** (completed early 2020) to scale horizontally.

**Section-2 deep-dives**
- **Backtrack vs Clone vs PITR:** Backtrack = in-place rewind, **MySQL only**, up to 72 h, no new cluster, seconds (undo a fat-finger). Clone = copy-on-write, separate cluster, instant, only changed pages billed (test/staging from prod). PITR = restore to a **NEW** cluster, up to 35 d retention (full recovery).
- **Aurora Limitless** (GA Nov 2024): horizontal sharding for Aurora **PostgreSQL 16.4**; two-layer routers + shards; sharded / reference / standard tables; **requires I/O-Optimized**; each shard max 128 TiB; millions of writes/sec. Use when single-writer write throughput is exceeded.

**Scenarios + distractors**
1. *"Sub-second cross-region reads + global DR."* ✅ **Aurora Global Database** (<1 s replication, RPO ~1 s, RTO <1 min). ✗ Multi-AZ (single region). ✗ RDS cross-region replica (slower). ✗ DynamoDB Global (NoSQL).
2. *"Undo a bulk delete from the last hour, MySQL."* ✅ **Backtrack.** ✗ PITR (new cluster, slower). ✗ Snapshot restore. ✗ Clone (doesn't undo).
3. *"Spin a test copy of 5 TB prod instantly, cheap."* ✅ **Clone (copy-on-write).** ✗ Snapshot restore (slow, full storage). ✗ Read replica (not isolated). ✗ Dump.
4. *"Scale writes beyond a single writer, PostgreSQL, single endpoint."* ✅ **Aurora Limitless.** ✗ Read replicas (read only). ✗ Multi-AZ (no write scale). ✗ App-level sharding (ops overhead).

**Numbers:** 6 storage copies across 3 AZs; up to 15 read replicas; storage auto to 128 TB; Global DB <1 s cross-region; switch to **I/O-Optimized if I/O >25% of bill**.

---

# TOPIC 11 — DynamoDB

**Dublin deep-dives**
- **Intercom** — *VERIFIED:* moved user storage MongoDB → DynamoDB (>6 TB, ~5k writes/s, >10k reads/s) while keeping **Aurora for identity/uniqueness constraints**; built a User History Tool on **DynamoDB Streams + Lambda**.
- **Coinbase** — *VERIFIED:* migrated Users Service to DynamoDB serving **>1.5 million reads/sec at peak**; used an **auxiliary table + multi-item transactions** to enforce uniqueness (DynamoDB lacks native unique constraints) and optimistic concurrency control (version field + If-Match).
- **Fenergo** — *VERIFIED:* DynamoDB as primary NoSQL store.

**Section-2 deep-dives**
- **Adaptive capacity** (automatic, free on every table): handles hot partitions; **"split for heat"** splits a hot partition into two, doubling capacity; a single hot item can reach the partition max **3,000 RCU / 1,000 WCU**. 2024 guidance: adaptive capacity + split-for-heat handle most uneven access — you don't always need to redesign keys. **LSI prevents splits** (10 GB item-collection limit). Burst capacity retains 5 min (300 s) of unused throughput.
- **Streams + Lambda:** iterator types TRIM_HORIZON / LATEST; retry until expire (24 h stream retention); bisect-on-error; parallelization factor; event filtering. Use for materialized views, change capture, fan-out.

**Scenarios + distractors**
1. *"Single-digit-ms key-value, spiky traffic, no capacity planning."* ✅ **DynamoDB On-Demand.** ✗ Provisioned (needs planning). ✗ Aurora (relational). ✗ RDS.
2. *"Multi-region active-active low-latency writes."* ✅ **Global Tables.** ✗ DAX (cache, single region). ✗ Cross-region replica. ✗ Aurora Global (relational).
3. *"Microsecond read cache for hot items."* ✅ **DAX.** ✗ ElastiCache (more ops, not DynamoDB-native). ✗ Global Tables. ✗ RCU increase.
4. *"Trigger Lambda on item change for a downstream view."* ✅ **DynamoDB Streams + Lambda.** ✗ Scheduled scan (lag/cost). ✗ SQS poll. ✗ Kinesis.

**Numbers:** item max 400 KB; partition max 3,000 RCU / 1,000 WCU; strongly-consistent read = 1 RCU/4 KB, eventual = 0.5 RCU; 1 WCU = 1 KB; Streams retention 24 h; PITR 35 d; Global Tables multi-active.

---

# TOPIC 12 — ElastiCache

**Dublin deep-dives**
- **Intercom** — *VERIFIED:* a memcached caching layer (ElastiCache) sits in front of Aurora.
- **Coinbase** — *VERIFIED:* migrated caching from Redis to **ValKey** (AWS-managed).
- **Stripe** (stripe.dev guidance) — *VERIFIED:* ElastiCache + DynamoDB for API-response caching in Lambda.

**Scenarios + distractors**
1. *"Cache with persistence + replication + pub/sub."* ✅ **Redis/ValKey.** ✗ Memcached (no persistence/replication). ✗ DAX (DynamoDB only). ✗ CloudFront.
2. *"Simple multi-threaded cache, sharding, no persistence."* ✅ **Memcached.** ✗ Redis (single-threaded per node). ✗ DynamoDB.
3. *"Session store for stateless web tier."* ✅ **Redis.** ✗ Instance store. ✗ DynamoDB (works — distractor if "lowest latency" emphasized). ✗ Local memory.

**Numbers:** Redis = persistence, replication, Multi-AZ failover, cluster mode, pub/sub, sorted sets; Memcached = multi-threaded, sharding, no persistence/failover; ValKey = cheaper Redis fork.

---

# TOPIC 13 — SQS

**Dublin deep-dives:** Intercom — *INFERRED* SQS for async Rails workers; Ryanair — *INFERRED* SQS decoupling in serverless apps.

**Section-2: Amazon MQ** — managed ActiveMQ & RabbitMQ; supports JMS, AMQP, STOMP, MQTT, OpenWire, WSS; Single-instance / Active-Standby / Cluster. Triggers: "migrate existing JMS/AMQP/on-prem broker with least code change" → **Amazon MQ**; "new cloud-native" → SQS/SNS; "very high steady throughput, cheaper" → MQ (billed per broker-hour) can beat SQS (per-message). SQS $0.40/million (Standard), $0.50/million (FIFO).

**Scenarios + distractors**
1. *"Lift an existing JMS app to AWS without rewriting messaging."* ✅ **Amazon MQ.** ✗ SQS (requires SDK rewrite). ✗ SNS. ✗ Kinesis.
2. *"Decouple with exactly-once ordered processing."* ✅ **SQS FIFO.** ✗ SQS Standard (best-effort order, at-least-once). ✗ SNS. ✗ Kinesis.
3. *"Buffer requests, process when capacity frees, retries + DLQ."* ✅ **SQS + DLQ.** ✗ SNS (no buffering). ✗ Direct invoke. ✗ Kinesis.

**Numbers:** message 256 KB (up to 2 GB with extended client + S3); retention 1 min–14 d (default 4 d); visibility timeout 0–12 h (default 30 s); FIFO 300 TPS (3,000 batched); long polling 20 s.

---

# TOPIC 14 — SNS

**Dublin deep-dives:** Ryanair — *INFERRED* SNS fan-out for Ryanair Connect alerts; HubSpot — *INFERRED* SNS for AWS-native fan-out alongside its heavy Kafka use.

**Scenarios + distractors**
1. *"One event triggers multiple parallel consumers."* ✅ **SNS fan-out to multiple SQS queues.** ✗ SQS alone (single consumer). ✗ EventBridge (works — distractor if no content routing / SaaS source). ✗ Kinesis.
2. *"Ordered fan-out with dedup."* ✅ **SNS FIFO → SQS FIFO.** ✗ SNS Standard. ✗ Kinesis. ✗ MQ.
3. *"Durable retry if a subscriber is down."* ✅ **SNS + SQS (SQS buffers).** ✗ SNS alone (message lost if no subscriber). ✗ Direct HTTP.

**Numbers:** Standard (best-effort order, at-least-once) vs FIFO (ordered, dedup, 300 TPS); subscribers SQS/Lambda/HTTP(S)/email/SMS/Firehose/mobile push; message filtering; 256 KB; DLQ supported.

---

# TOPIC 15 — EventBridge

**Dublin deep-dives**
- **Ryanair** — *VERIFIED:* event-driven airport gate system built on **Amazon MSK**; event-based architecture behind Ryanair Connect.
- **Fenergo** — *VERIFIED:* **event sourcing (EventStoreDB) + CQRS**; *INFERRED* EventBridge for AWS-native cross-service events.

**Section-2: Step Functions** — Standard up to **1 year**, exactly-once, **$0.025/1,000 state transitions**, 2,000+ exec/s, 90-day history. Express up to **5 min**, at-least-once (async)/at-most-once (sync), **100,000+ exec/s**, billed by executions + duration + memory, **~25–40× cheaper** for high-volume short workloads. State types: Task, Choice, Parallel, Map, Wait, Pass, Succeed, Fail, Catch/Retry. 200+ direct service integrations (no Lambda glue); `.sync` and `.waitForTaskToken` patterns. Triggers: "orchestrate multiple Lambda with retry/error handling, least ops" → Step Functions; "high-volume short event processing, cheap" → Express.

**Scenarios + distractors**
1. *"Route SaaS (Zendesk/Datadog) events to AWS targets by content."* ✅ **EventBridge** (SaaS partner sources + content rules). ✗ SNS (no content filtering / SaaS sources). ✗ SQS. ✗ Kinesis.
2. *"Schedule a task daily at 6am."* ✅ **EventBridge Scheduler / cron rule.** ✗ Lambda + in-code cron. ✗ CloudWatch alarm. ✗ SQS delay.
3. *"Orchestrate an 8-step workflow with retries and a human-approval wait."* ✅ **Step Functions Standard (`waitForTaskToken`).** ✗ Chained Lambda (no state/retry mgmt). ✗ Express (5-min limit, no exactly-once). ✗ SQS chain.

**Numbers:** EventBridge $1/million events; schema registry; archive + replay; buses default/custom/partner; Pipes for point-to-point.

---

# TOPIC 16 — Kinesis

**Dublin deep-dives**
- **Ryanair** — *VERIFIED:* S3 data lake with **Kinesis** real-time analytics; **MSK** for the Manchester Airports Group gate system.
- **Coinbase** — *VERIFIED (engineering blog "How we scaled data streaming using AWS MSK"):* reduced end-to-end latency "by ~95% when switching from Kinesis (~200 msec e2e latency) to Kafka (<10 msec e2e latency)," with capacity to grow "3x the number of broker nodes in our prod cluster (30 → 90 nodes)."
- **HubSpot** — *VERIFIED ("Our Journey to Multi-Region"):* "As of July 2022, we have roughly **4,000 Kafka topics spread across 80 clusters**." Evaluated MirrorMaker/Replicator but built a simple custom aggregation instead.
- **Flutter/PokerStars** — *VERIFIED:* adopted MSK to free developers from managing Kafka clusters.

**Section-2: MSK** — Provisioned vs Serverless. Kafka beats Kinesis when: existing Kafka code/skills, partition counts exceed Kinesis shard limits, finer consumer-offset control, MirrorMaker cross-cluster replication, MSK Connect connectors. Triggers: "migrate on-prem Kafka to managed, least ops" → **MSK**; "real-time AWS-native simple" → Kinesis Data Streams; "load streaming to S3/Redshift no code" → Firehose.

**Scenarios + distractors**
1. *"Migrate self-managed Kafka, keep code/connectors."* ✅ **Amazon MSK.** ✗ KDS (rewrite). ✗ Firehose. ✗ SQS.
2. *"Real-time ingest, multiple consumers, replay, AWS-native."* ✅ **Kinesis Data Streams.** ✗ SQS (no replay/multi-consumer on same data). ✗ Firehose (no replay). ✗ SNS.
3. *"Deliver streaming data to S3 with transform, no servers."* ✅ **Firehose + Lambda transform.** ✗ KDS (needs a consumer). ✗ MSK. ✗ Glue.

**Numbers:** KDS shard = 1 MB/s or 1,000 rec/s in, 2 MB/s out; retention 24 h–365 d; enhanced fan-out 2 MB/s per consumer; Firehose near-real-time (≥60 s buffer); MSK Serverless auto-scales partitions.

---

# TOPIC 17 — Lambda

**Dublin deep-dives:** Ryanair — *VERIFIED* Lambda + S3 Object Lambda (COVID wallet), serverless Ryanair Connect; Intercom/Coinbase — *VERIFIED* Lambda processing DynamoDB Streams; Fenergo — *VERIFIED* Lambda-first across 3 AZs.

**Section-2: Event-Source-Mapping batching** — batch size: Kinesis/MSK default 100 (max 10,000), DynamoDB 100 (max 1,000), SQS 10 (max 10,000 with batch window). Batch window 0–300 s. **Parallelization factor** (Kinesis/DynamoDB only) 1–10 concurrent batches per shard, preserves per-partition-key order. **Partial batch response** (`ReportBatchItemFailures`): retry only failed records. **Bisect-on-error**: split a failing batch in two. **Tumbling windows** 0–900 s for stateful aggregation per shard.

**Scenarios + distractors**
1. *"Process Kinesis — one bad record shouldn't retry the whole batch."* ✅ **`ReportBatchItemFailures` (partial batch response).** ✗ Bisect alone (still reprocesses good records). ✗ DLQ only. ✗ Smaller batch.
2. *"Increase stream throughput without adding shards, keep order."* ✅ **Parallelization factor.** ✗ More memory. ✗ More shards (the question says *without*). ✗ Provisioned concurrency.
3. *"Eliminate cold starts for a latency-sensitive API."* ✅ **Provisioned concurrency.** ✗ Reserved concurrency (limits, doesn't warm). ✗ More memory. ✗ SnapStart (Java only).

**Numbers:** timeout max 15 min; memory 128 MB–10,240 MB (CPU scales); /tmp 512 MB–10 GB; payload 6 MB sync / 256 KB async; default concurrency 1,000/region; container image up to 10 GB.

---

# TOPIC 18 — API Gateway

**Dublin deep-dives:** Fintech pattern (Stripe/Wayflyer/TransferMate, *INFERRED*) — API Gateway + WAF + Lambda/Fargate backend with per-module APIs and request validation; Maya/Banfico (*VERIFIED* AWS FS blog) — API management platform on API Gateway.

**Section-2: AppSync** — managed GraphQL; real-time subscriptions via WebSockets; data sources DynamoDB / RDS (Data API) / Lambda / OpenSearch / HTTP / EventBridge; caching + conflict resolution (offline sync). Triggers: "mobile real-time subscription + offline sync" → AppSync; "GraphQL aggregating multiple sources" → AppSync; "REST + usage plans/API keys" → API Gateway REST.

**Scenarios + distractors**
1. *"Mobile app needs real-time data sync + offline."* ✅ **AppSync (GraphQL subscriptions).** ✗ API GW WebSocket (no GraphQL / offline conflict res). ✗ REST polling. ✗ IoT Core.
2. *"REST API with throttling, API keys, usage plans, caching."* ✅ **API Gateway REST.** ✗ HTTP API (fewer features — distractor if usage plans required). ✗ ALB. ✗ AppSync.
3. *"Lowest-cost, low-latency HTTP proxy to Lambda, no usage plans."* ✅ **API Gateway HTTP API.** ✗ REST API (more cost/features). ✗ ALB. ✗ AppSync.

**Numbers:** REST = usage plans/keys/validation/caching/WAF; HTTP API ~70% cheaper, lower latency, JWT auth, fewer features; WebSocket API; throttle default 10,000 RPS, burst 5,000; integration timeout 29 s.

---

# TOPIC 19 — ECS / EKS / Fargate

**Dublin deep-dives**
- **Coinbase** — *VERIFIED (blog "From EC2 to EKS"):* "50% faster scaling speeds … a 68% reduction in resources used"; then moved EKS workloads to **Graviton** ("20% lower cost") with Karpenter further cutting infra cost ~20%.
- **HubSpot** — *VERIFIED:* Kubernetes (EKS) + AWS running thousands of microservices.
- **Flutter UKI** — *VERIFIED:* chose **MWAA over self-managed EKS** to reduce operational complexity for data orchestration; PokerStars runs containerized on AWS.
- **Appreciate Wealth (fintech build pattern)** — *VERIFIED:* 65+ microservices on **Amazon ECS**, multi-AZ VPC, Secrets Manager.

**Section-2: ECS Service Connect** — service-to-service discovery + traffic mgmt for ECS (managed, no sidecar-management burden). vs App Mesh (deprecated), vs Cloud Map (DNS discovery only). Built-in retries + observability. Decision: in-cluster ECS → **Service Connect**; cross-VPC/account mixed compute → **VPC Lattice**; simple DNS → **Cloud Map**.

**Scenarios + distractors**
1. *"Run containers, no server/cluster management, per-task billing."* ✅ **Fargate.** ✗ ECS on EC2 (manage instances). ✗ EKS on EC2. ✗ Lambda (not long-running containers).
2. *"Kubernetes-native, portable, existing k8s tooling."* ✅ **EKS.** ✗ ECS (AWS-proprietary). ✗ Fargate alone. ✗ App Runner.
3. *"ECS service discovery, least ops, no App Mesh."* ✅ **ECS Service Connect.** ✗ App Mesh (deprecated 2026). ✗ Cloud Map alone (no traffic mgmt). ✗ ALB per service (cost).

**Numbers:** Fargate 0.25–16 vCPU, 0.5–120 GB; EKS control plane $0.10/hr/cluster; ECR with interface endpoints to pull images privately.

---

# TOPIC 20 — Encryption & Secrets (KMS, CloudHSM, Secrets Manager, Parameter Store, ACM)

**Dublin deep-dives**
- **Stripe** — *VERIFIED:* "All card numbers are encrypted at rest with **AES-256**. Decryption keys are stored on separate machines … We tokenize PANs internally" — the Card Data Vault runs in an isolated AWS environment (PCI Service Provider Level 1).
- **Coinbase** — *VERIFIED* security-first; *INFERRED* KMS + CloudHSM for crypto-key custody.
- **AIB / Fenergo** — *INFERRED* per-tenant KMS CMKs, Secrets Manager for DB-credential rotation.

**Scenarios + distractors**
1. *"Auto-rotate RDS DB credentials, managed."* ✅ **Secrets Manager (native rotation).** ✗ Parameter Store (no native rotation). ✗ KMS (keys, not secrets). ✗ Env vars.
2. *"Store config params free, hierarchical, no rotation."* ✅ **Parameter Store (Standard, free).** ✗ Secrets Manager ($0.40/secret/mo). ✗ KMS. ✗ DynamoDB.
3. *"FIPS 140-2 Level 3 dedicated single-tenant HSM, control keys."* ✅ **CloudHSM.** ✗ KMS (multi-tenant). ✗ Secrets Manager. ✗ ACM.
4. *"Free public TLS certs that auto-renew for ALB/CloudFront."* ✅ **ACM.** ✗ Imported cert (manual renew). ✗ CloudHSM. ✗ IAM cert store (legacy).

**Numbers:** KMS symmetric/asymmetric, $1/key/mo, automatic annual rotation (configurable since 2024), envelope encryption; CloudHSM dedicated single-tenant FIPS 140-2 L3; Secrets Manager $0.40/secret/mo + native Lambda rotation; Parameter Store Standard free / Advanced $0.05/param; ACM free public certs (no private-key export).

---

# TOPIC 21 — Cognito

**Dublin deep-dives:** Ryanair — *INFERRED* Cognito/custom IdP for MyRyanair + employee auth; SaaS (Intercom/Workhuman) — *INFERRED* Cognito user pools for B2C + federation SSO.

**Scenarios + distractors**
1. *"Add sign-up/sign-in + social login to a web/mobile app."* ✅ **Cognito User Pools.** ✗ IAM (AWS access, not app users). ✗ Identity Center (workforce SSO). ✗ Identity Pools alone (creds, not authentication).
2. *"Give authenticated app users temporary AWS creds for S3."* ✅ **Cognito Identity Pools (federated identities).** ✗ User Pools alone. ✗ IAM user per app user. ✗ Access keys.
3. *"Workforce SSO to AWS accounts via Okta."* ✅ **IAM Identity Center** (not Cognito). ✗ Cognito (app users). ✗ SAML to IAM directly.

**Numbers:** User Pools = authentication; Identity Pools = authorization to AWS (temp creds). **Cognito Sync = LEGACY → eliminate (use AppSync).** MFA, hosted UI, SAML/OIDC/social federation.

---

# TOPIC 22 — CloudTrail, CloudWatch, Config (+ GuardDuty, Inspector, Macie, Security Hub, Detective, Audit Manager)

**Dublin deep-dives:** AIB — *VERIFIED* investment in cyber resilience + fraud detection; *INFERRED* GuardDuty + Security Hub + Config org-wide with a CloudTrail org trail to a central S3 bucket. Regulated fintech (Fenergo/Stripe) — *INFERRED* immutable CloudTrail logs (S3 Object Lock), Config compliance rules, Macie for PII discovery.

**Service map:** CloudTrail (API audit — *who did what*); CloudWatch (metrics/logs/alarms/dashboards); Config (config history + compliance rules — detective); GuardDuty (threat detection via ML on VPC Flow/DNS/CloudTrail); Inspector (vulnerability scanning EC2/ECR/Lambda); Macie (PII discovery in S3); Security Hub (aggregates findings, CIS/PCI standards); Detective (root-cause investigation graphs); Audit Manager (compliance reports — PCI/GDPR).

**Scenarios + distractors**
1. *"Who deleted the S3 bucket / API-call audit."* ✅ **CloudTrail.** ✗ CloudWatch (metrics). ✗ Config (config state). ✗ Flow Logs (network).
2. *"Detect compromised EC2 / crypto-mining / anomalous API calls."* ✅ **GuardDuty.** ✗ Inspector (vuln scan). ✗ Macie (PII). ✗ Config.
3. *"Discover PII / credit-card numbers in S3."* ✅ **Macie.** ✗ GuardDuty. ✗ Inspector. ✗ Config.
4. *"Check resources comply (e.g. EBS encrypted) + auto-remediate."* ✅ **Config rules + SSM remediation.** ✗ CloudTrail. ✗ Security Hub (aggregates, doesn't remediate). ✗ Inspector.
5. *"Scan EC2/container images for CVEs."* ✅ **Inspector.** ✗ GuardDuty. ✗ Macie. ✗ Config.

**Numbers:** CloudTrail 90-day event history free (trail to S3 for longer); Config per-config-item charge; GuardDuty/Macie/Inspector per-data/resource; Security Hub aggregates multi-account.

---

# TOPIC 23 — Storage (EFS, FSx, Storage Gateway, DataSync, Snow, Transfer)

**Dublin deep-dives:** Ryanair — *VERIFIED:* switched from tape backup to **Storage Gateway Tape Gateway**, "driving savings of 65 percent"; S3 + EBS for archiving. HPC/ML (Coinbase/Datadog) — *INFERRED* FSx for Lustre for ML training, EFS for shared app data.

**Service map:** EFS (NFS, multi-AZ, Linux, elastic, lifecycle to IA); FSx Windows (SMB, AD-integrated), FSx Lustre (HPC/ML, S3-linked, sub-ms), FSx ONTAP/OpenZFS; Storage Gateway (File NFS/SMB→S3, Volume iSCSI, Tape VTL→Glacier); DataSync (online bulk on-prem↔AWS, scheduled); Snow Family (Snowcone 8 TB, Snowball Edge ~80 TB, Snowmobile retired); Transfer Family (managed SFTP/FTPS/FTP → S3/EFS).

**Scenarios + distractors**
1. *"Shared POSIX file system, multiple Linux EC2, multi-AZ."* ✅ **EFS.** ✗ EBS (single AZ/instance). ✗ FSx Windows (SMB). ✗ S3 (object).
2. *"Migrate 500 TB in 10 days, limited bandwidth."* ✅ **Snowball Edge.** ✗ DataSync (bandwidth-bound). ✗ Direct Connect (provisioning lead time). ✗ Transfer Family.
3. *"Ongoing scheduled on-prem NFS → S3 sync over the network."* ✅ **DataSync.** ✗ Snowball (offline, one-time). ✗ Storage Gateway File (caching gateway, not bulk migrate). ✗ Transfer.
4. *"Replace physical tape backup, keep the backup app."* ✅ **Tape Gateway.** ✗ S3 direct (app expects VTL). ✗ DataSync. ✗ Glacier direct.
5. *"Windows app needs an SMB share + AD."* ✅ **FSx for Windows.** ✗ EFS (NFS/Linux). ✗ FSx Lustre. ✗ Storage Gateway.
6. *"HPC/ML high-throughput scratch linked to S3."* ✅ **FSx for Lustre.** ✗ EFS (lower throughput). ✗ EBS. ✗ S3 direct.

**Numbers:** EFS Standard/IA/One Zone, bursting/provisioned/elastic throughput; FSx Lustre hundreds of GB/s; Snowball Edge ~80 TB usable; Transfer Family per-endpoint-hour + per-GB.

---

# TOPIC 24 — Disaster Recovery

**Dublin deep-dives**
- **Coinbase** — *VERIFIED (postmortem of the May 7, 2026 outage):* "an AWS thermal event triggered a Coinbase outage … A defect in the AWS MSK control plane prevented automatic partition-leader reelection. Two of our MSK clusters became stuck in a 'healing' state with producers unable to write." Remediation: **migrating the 2-AZ Kafka cluster to a 3-AZ deployment** + improving cross-zone standbys. *(Excellent real-world AZ-failure DR teaching case: single-AZ-locked components + managed-service control-plane failure.)*
- **Ryanair** — *VERIFIED* Route 53 + RDS for DR.
- **Fenergo** — *VERIFIED* 3-AZ active-active, multi-region capable.

**DR strategies:** Backup & Restore (cheapest, RPO/RTO hours); Pilot Light (core DB running, rest off, RTO 10s of min); Warm Standby (scaled-down full stack running, RTO minutes); Multi-site Active-Active (RTO ~0, RPO ~0, costliest).
**Section-2:** **Resilience Hub** (continuous assessment vs RTO/RPO targets, recommendations, integrates FIS); **FIS** (Fault Injection Simulator — chaos: inject AZ/instance failures); **MGN** (Application Migration Service — lift-and-shift rehost, replaces deprecated SMS); **DRS** (Elastic Disaster Recovery — continuous block replication, fast failover); **DMS** (database migration). Clarify: MGN = migration rehost; DRS = DR replication; SMS = deprecated; DMS = DB migration.

**Scenarios + distractors**
1. *"RTO seconds, RPO near-zero, global."* ✅ **Multi-site active-active (Aurora Global + DynamoDB Global Tables + Route 53).** ✗ Pilot light / warm standby (RTO minutes). ✗ Backup/restore (hours).
2. *"Cheapest DR, RTO hours acceptable."* ✅ **Backup & Restore.** ✗ Active-active (costly). ✗ Warm standby. ✗ Pilot light.
3. *"Continuous replication to DR region, fast failover, minimal idle cost."* ✅ **AWS DRS (Elastic DR).** ✗ MGN (migration, not DR). ✗ DMS (DB only). ✗ Snapshots.
4. *"Test resilience by simulating an AZ failure."* ✅ **FIS.** ✗ Resilience Hub (assesses, doesn't inject). ✗ Manual GameDay. ✗ Synthetics.

**Numbers:** RPO = data-loss tolerance; RTO = downtime tolerance. Aurora Global RPO ~1 s / RTO <1 min; DynamoDB Global Tables multi-active.

---

# TOPIC 25 — Cost Optimization

**Dublin deep-dives**
- **Ryanair** — *VERIFIED:* ~30% cost reduction from Graviton, 65% savings from Tape Gateway, gp2→gp3 savings, EC2 Image Builder (free; replaced Jenkins-on-EC2).
- **Intercom** — *VERIFIED:* dedicated FinOps cost-optimization practice; "Run Less Software" technical strategy ("use the tools you're already using").
- **Flutter/PokerStars** — *VERIFIED:* 20% TCO reduction migrating PokerStars to AWS.

**Cost allocation tags & cost categories:** user-defined vs AWS-generated tags; must be **activated in the Billing console** (≈24 h to appear); **Cost Categories** group accounts/services/tags into reporting buckets (Dev vs Prod, per-team). Surfaced in Cost Explorer, Budgets, CUR.

## Section 5 — PRICING-MATH QUESTION PATTERNS
- **S3 storage-class crossover:** Standard $0.023/GB vs Standard-IA $0.0125/GB + **$0.01/GB retrieval** → IA wins when accessed **< ~once/month**. Glacier IR $0.004/GB ≈ 68% cheaper than IA when accessed **≤ once/quarter** (min 90 d). Deep Archive $0.00099/GB (retrieve 12–48 h, min 180 d). **Trap:** transitioning many <128 KB objects costs more in transition fees than storage saved — AWS skips <128 KB objects by default since Sept 2024.
- **NAT Gateway vs Interface Endpoint:** NAT ≈ $0.045/hr (~$32–38/mo/AZ) + $0.045/GB; interface endpoint ≈ $0.01/hr/AZ (~$7.30–8.76/mo/AZ) + $0.01/GB; **S3/DynamoDB gateway endpoint = FREE**. At ~100 GB/mo to a *single* service the endpoint beats NAT; but **6–10 services × 2 AZ** of endpoints (~$146/mo) can exceed two NAT GWs (~$65/mo). Crossover: endpoints win with *few services + high volume*; NAT wins with *many services + low volume*. Always use the free S3/DynamoDB gateway endpoints.
- **Aurora I/O-Optimized vs Standard:** Standard $0.10/GB storage + $0.20/million I/O; I/O-Optimized $0.225/GB (2.25×) + ~25–30% higher instance, **zero I/O charge**. **Rule: if I/O > 25% of the total Aurora bill → switch to I/O-Optimized** (saves up to ~40%); below 25%, Standard is cheaper. Switch once per 30 days. (Global DB replicated-write I/O is still charged even on I/O-Optimized.)
- **RI / Savings Plans break-even:** 1-yr No-Upfront ≈ 40% off; 3-yr All-Upfront up to ~72% off. 1-yr break-even ≈ 7–9 months. Steady workloads >60–70% utilization → RI/SP beats On-Demand/Serverless.
- **Step Functions:** Standard $0.025/1,000 transitions; Express ~25–40× cheaper for high-volume short workloads.
- **Lambda vs Fargate vs EC2:** Lambda for spiky/low-duty-cycle/event-driven; Fargate for steady containers without server management; EC2 (with RI/Spot) cheapest for steady high-utilization.
- **DynamoDB On-Demand vs Provisioned:** On-Demand for spiky/unpredictable; Provisioned + auto-scaling + reserved capacity for steady predictable load.
- **CloudFront vs Global Accelerator:** CloudFront for cacheable HTTP (cheaper egress + caching); GA for non-HTTP/static-IP (per-GB premium, no caching).

**Scenarios + distractors**
1. *"Aurora bill: I/O is 40% of cost — reduce it."* ✅ **Switch to I/O-Optimized.** ✗ Smaller instance (perf hit). ✗ Read replicas (more cost). ✗ Standard (already on it).
2. *"Steady 24/7 EC2 workload, lowest cost, 3-yr commit OK."* ✅ **3-yr Reserved Instance / Savings Plan.** ✗ Spot (interruption). ✗ On-Demand. ✗ Serverless.
3. *"Data accessed once/quarter, instant retrieval, cheapest."* ✅ **Glacier Instant Retrieval.** ✗ Standard-IA (costlier for quarterly). ✗ Deep Archive (12 h retrieval). ✗ Standard.

---

# SECTION 7 — CROSS-TOPIC INTEGRATION ARCHITECTURES
1. **Serverless event-driven:** API GW → Lambda → DynamoDB + Streams → Lambda → SNS/SQS + S3. Frame: "least-ops scalable backend."
2. **Global HA web:** Route 53 latency → CloudFront → ALB → ASG → Aurora Global + DynamoDB Global Tables. Frame: "global low-latency + cross-region DR."
3. **Data lake:** S3 + Glue + Athena + QuickSight + Lake Formation. Frame: "serverless analytics on S3."
4. **Real-time analytics:** Kinesis → Firehose → Lambda → OpenSearch / S3. *(Ryanair pattern.)*
5. **Container microservices:** ECS Fargate + ALB + RDS Proxy + Aurora + ElastiCache + Secrets Manager + ECR *(Coinbase/HubSpot EKS variant)*.
6. **Hybrid:** Direct Connect + VPN (backup) + Transit Gateway + DRS + Storage Gateway.
7. **Migration:** DMS + SCT + DataSync + MGN. *(Ryanair MS SQL → Aurora.)*
8. **Multi-account landing zone:** Organizations + Control Tower + Identity Center + SCPs + CloudTrail org trail + Config + Security Hub + GuardDuty delegated admin. *(AIB/regulated.)*
9. **Big-data ETL:** S3 + Glue + EMR + Athena + Redshift. *(Flutter MWAA/Airflow orchestration.)*
10. **DR active-active:** Aurora Global + DynamoDB Global + Route 53 + ALB + CloudFront.
11. **Streaming at scale:** MSK → Flink/Lambda → DynamoDB + S3. *(Coinbase: 30→90 broker nodes, <10 ms.)*
12. **Secure payments:** API GW + WAF + Shield Advanced + Fargate + Aurora + KMS + tokenized card vault in an isolated account. *(Stripe pattern.)*
13. **CQRS / event sourcing:** EventStoreDB/Kinesis + Lambda + DynamoDB read models + AppSync/WebSocket. *(Fenergo pattern.)*
14. **ML pipeline:** S3 + Glue + SageMaker/Databricks + feature store (DynamoDB) + Athena. *(Coinbase/Ryanair.)*
15. **Content delivery + bot defense:** CloudFront + WAF (rate-based + Bot Control) + Shield Advanced + Origin Group failover.

---

# SECTION 6 — META-PATTERNS
- **65 questions / 130 min = 2 min/question.** Single-select + multiple-select (choose 2/3 of 5+).
- **Two-pass strategy:** answer confident ones first, flag the rest, return on a second pass.
- **Tiebreakers:** if both options work → choose **least operational overhead** (managed/serverless). If cost is the qualifier → choose **cheapest viable**. "MOST cost-effective" + it works → cheapest.
- **Read the LAST sentence of the stem first** — the qualifier (cost / latency / least ops / HA / compliance) usually lives there.
- **Watch qualifiers:** MOST, LEAST, ALL, ONLY, "without managing servers", "minimal changes", "real-time", "globally", "minimal downtime".
- **Eliminate legacy answers automatically:** NAT Instance (→ NAT GW), Classic LB (→ ALB/NLB), **OAI** (→ OAC, especially with SSE-KMS), Launch Configuration (→ Launch Template), Aurora Multi-Master (gone), Cognito Sync (→ AppSync), **App Mesh** (→ VPC Lattice / ECS Service Connect; EOL Sept 30, 2026), SMS (→ MGN).

---

## CAVEATS & SOURCE-QUALITY NOTES
- **Inferred-only companies:** Wayflyer and TransferMate/CurrencyFair AWS stacks could not be confirmed from primary engineering sources — treat as industry-pattern inference only.
- **Stripe:** the isolated AWS Card Data Vault + AES-256 + SAML/SCIM/JIT are *verified* from Stripe's security docs; specific Aurora/DynamoDB/Kafka usage and eu-west-1 (Ireland) data residency are commonly assumed but **not confirmed** in Stripe primary sources.
- **HubSpot:** "4,000 Kafka topics across 80 clusters" is verified (HubSpot blog, July 2022). A widely-repeated "100 billion messages/day" figure is **NOT HubSpot's** (it belongs to LINE/Confluent) — dropped here.
- **Coinbase MSK:** verified figures are the ~200 ms→<10 ms latency improvement and 30→90 broker-node headroom; the "~17 TB/broker" figure is unverified and excluded.
- **Coinbase outage:** the May 7, 2026 AWS thermal-event postmortem describes a real incident (MSK control-plane defect, 2-AZ→3-AZ remediation) — use as a concrete AZ-failure DR example.
- **Pricing figures** are region/time-sensitive (us-east-1/eu-west-1 examples); the SAA-C03 exam tests *relative ordering and crossover logic*, not exact dollar amounts.