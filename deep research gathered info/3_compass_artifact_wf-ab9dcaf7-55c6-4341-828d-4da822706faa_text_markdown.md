# SAA-C03 Deep Research Gap-Fill Notes — Next-Layer Depth (compiled June 5, 2026)

**TL;DR**
- **The exam's hardest points cluster in 2024–2026 service additions and "MOST cost-effective / LEAST operational overhead" qualifier traps** — your guide most likely under-weights S3 Express One Zone, Aurora I/O-Optimized & Serverless v2 scale-to-zero, Lambda SnapStart (Python/​.NET), EventBridge Pipes, OAC (replacing OAI), Network Firewall, WAF/Shield Advanced, DataSync, Compute Optimizer, S3 Storage Lens, AWS Backup, Aurora Backtrack, and EBS Multi-Attach. All are covered below per-topic in section A.
- **Decision discipline beats memorization**: the recurring decision rules are Multi-AZ = HA (≠ read scaling, ≠ Multi-Region DR), managed/serverless wins "least ops," gateway endpoint (free, S3/DynamoDB only) vs interface/PrivateLink (paid, everything else), CloudFront caches / Global Accelerator does not, and "deny beats allow" in IAM.
- **Use this as source material**, not final study text: each of the 25 topics has A) gaps, B) decision trees, C) real-world architecture, D) 2024–2026 exam patterns, E) trigger-phrase maps, F) traps, G) numbers to memorize, H) cross-topic integration — followed by **META-INSIGHTS (top 20 cross-cutting rules)**.

---

## KEY FINDINGS (read these first)

1. **New-service facts verified to AWS sources** (use these exact numbers): **S3 Express One Zone** delivers up to **10× faster** access and **request costs up to 80% lower** than S3 Standard; on **April 10, 2025** AWS cut its prices — **storage −31%, PUT −55%, GET −85%, data transfer −60%** — bringing US-East-1 storage to **$0.11/GB-month** (was $0.16). Directory buckets support **up to 2,000,000 requests/sec**.
2. **Aurora I/O-Optimized** saves **up to 40%** "when your I/O spend exceeds 25% of your current Aurora database spend" (AWS GA blog, May 2023); switchable **once every 30 days**, no reboot. **Aurora Serverless v2** now supports **scale-to-zero / auto-pause** (min 0 ACUs; setting 0.5+ disables auto-pause), pricing **$0.12/ACU-hr** Standard (**$0.156** I/O-Optimized).
3. **Lambda SnapStart** went GA for **Python 3.12+ and .NET 8+ in Nov 2024** (sub-second cold starts) and Java since 2022; it **does not support provisioned concurrency, EFS, container images, or ephemeral storage > 512 MB**.
4. **OAC replaces OAI** as the recommended way to lock an S3 origin to CloudFront — and **OAC is the only one that works with SSE-KMS-encrypted objects** (OAI cannot decrypt KMS).
5. The exam's two most decisive qualifiers are **"MOST cost-effective"** and **"LEAST operational overhead"** — they almost always push you toward managed/serverless and away from EC2-with-scripts, NAT-for-S3, or Multi-Region-when-Multi-AZ-suffices.

---

## DETAILS — THE 25 TOPICS

> Section legend per topic: **A** Gaps · **B** Decision trees · **C** Real-world architecture · **D** 2024–26 exam patterns · **E** Trigger→answer map · **F** Traps · **G** Numbers · **H** Cross-topic integration.

### 1. IAM
**A — Gaps:** Permission Boundaries (max permissions a principal can have — they *cap*, they don't *grant*); SCPs (org-level guardrails, also only cap, never grant; don't apply to management account); **IAM Identity Center** (successor to AWS SSO — the modern multi-account human-access answer); **Access Analyzer** (finds resources shared externally; now also unused-access findings); **IAM Roles Anywhere** (X.509 certs for on-prem/non-AWS workloads to get temp creds — newer, under-covered); the policy evaluation logic itself.
**B — Decision trees:**
- Cross-account access → **IAM Role + STS AssumeRole** (never share long-term keys).
- "Restrict what an entire OU/account can do regardless of admin" → **SCP**. "Cap what *delegated admins* can grant to others" → **Permission Boundary**.
- "Workforce users, many accounts, central login, federated to Azure AD/Okta" → **IAM Identity Center**. "App users / mobile sign-in" → **Cognito** (not IAM Identity Center).
- "On-prem servers need AWS creds without static keys" → **IAM Roles Anywhere**.
**Eval order:** explicit **Deny** → SCP → resource policy / boundary / session policy → explicit **Allow**; default = implicit deny. **Explicit deny always wins.**
**C — Real-world:** Multi-account landing zone (Control Tower) → SCPs deny disallowed regions/services org-wide; Identity Center maps Okta groups → permission sets → roles per account. Fintech (Monzo/Revolut-style): least-privilege task roles per microservice; Access Analyzer in CI to catch public S3/role exposure.
**D — Patterns:** (1) "limit S3 bucket to org accounts, least ops" → **`aws:PrincipalOrgID` condition in bucket policy** (distractors: tagging each user, CloudTrail monitoring, OU paths — more ops). (2) "EC2 app needs S3 access" → **instance profile/role**, never embedded keys. (3) "developers must not exceed X permissions even if they write their own policies" → **permission boundary**.
**E — Triggers:** "temporary credentials" → STS · "cross-account" → AssumeRole role · "central login many accounts / workforce" → IAM Identity Center · "external app users" → Cognito · "cap delegated permissions" → permission boundary · "org-wide guardrail" → SCP · "who shared my resource externally" → Access Analyzer · "rotate/avoid long-term keys" → roles · "on-prem cert-based AWS creds" → Roles Anywhere · "MFA for sensitive API" → IAM condition `aws:MultiFactorAuthPresent`.
**F — Traps:** SCP/boundary "granting" permissions (they never grant); using IAM users instead of roles; thinking SCP affects management account; confusing Identity Center (workforce) with Cognito (customers).
**G — Numbers:** managed policies per principal **10** (quota-raisable); policy doc **6,144 chars**; STS session **15 min–12 hr** (role chaining capped 1 hr); SCP doc **5,120 chars**; up to **5** SCPs per OU/account.
**H — Integration:** IAM + S3 (bucket policy + PrincipalOrgID), IAM + KMS (key policy is authoritative), IAM + STS + Cognito identity pools, IAM roles for EC2/ECS/Lambda.

### 2. VPC
**A — Gaps:** **Network Firewall** (managed stateful IDS/IPS, deep-packet inspection — distinct from SG/NACL/WAF); **Transit Gateway** vs peering nuance; **Gateway Load Balancer** for 3rd-party appliances; **AWS RAM** (share subnets, *not* TGW) vs TGW (connect VPCs); IPv4 public addresses now **billed hourly**; egress-only IGW (IPv6).
**B — Decision trees:**
- Private S3/DynamoDB access → **Gateway VPC endpoint (free)**. Private access to *any other* AWS service / on-prem / cross-region / peered VPC → **Interface endpoint (PrivateLink, paid ~$0.01/hr/AZ + $0.01/GB)**.
- Many VPCs hub-and-spoke / transitive routing → **Transit Gateway**. Few one-to-one, simple → **VPC peering** (non-transitive, no overlapping CIDRs). Share subnets across accounts → **RAM** (TGW connects, does not share).
- Outbound internet from private subnet → **NAT Gateway per AZ** (managed, HA within AZ). NAT Instance only if "lowest cost, low throughput, self-manage OK."
- Hybrid: quick/cheap/over-internet → **Site-to-Site VPN**; consistent/dedicated/high-throughput → **Direct Connect** (slow to provision); both for failover.
- "Inspect/filter traffic, IDS/IPS, domain filtering" → **Network Firewall** (not SG/NACL).
**SG vs NACL:** SG = stateful, instance-level, allow-only. NACL = stateless, subnet-level, allow+deny, ordered rules, ephemeral ports needed for return traffic.
**C — Real-world:** 3-tier: public subnets (ALB) / private (app, ASG) / private (RDS). Gateway endpoint to S3 saves NAT data-processing $. Centralized egress + Network Firewall via TGW for inspection. Dublin fintech: Direct Connect to on-prem core banking + VPN backup.
**D — Patterns:** (1) "EC2 in private subnet read S3 without internet, least cost" → **Gateway endpoint** (distractors: NAT GW = costs, IGW = public). (2) "single NAT GW" flagged as **SPOF + cross-AZ charges** → one NAT per AZ. (3) "connect 50 VPCs" → **TGW** (peering = mesh sprawl). (4) "share subnets across accounts" → **RAM** (TGW is the distractor).
**E — Triggers:** "private S3/DynamoDB" → gateway endpoint · "private to SQS/KMS/API/on-prem" → interface endpoint/PrivateLink · "hundreds of VPCs / transitive" → TGW · "overlapping CIDR / non-transitive" → peering limitation · "subnet-level deny specific IP" → NACL · "stateful instance firewall" → SG · "IDS/IPS / deep packet inspection" → Network Firewall · "dedicated consistent bandwidth" → Direct Connect · "quick encrypted hybrid" → VPN · "audit accepted/rejected traffic" → VPC Flow Logs · "static outbound IP for private subnet" → NAT GW.
**F — Traps:** Gateway endpoint for non-S3/DynamoDB (invalid); NAT for S3 (wasteful); NACL stateful confusion; expecting peering transitivity; WAF on NLB (no); thinking TGW shares subnets.
**G — Numbers:** /16 to /28 subnets; 5 reserved IPs/subnet; gateway endpoint = $0; interface endpoint 10 Gbps/ENI burst 100; NAT GW up to 100 Gbps, 55k connections/dest; default 5 VPCs/region.
**H — Integration:** VPC + EC2/ASG/ALB (HA web tier), VPC endpoints + IAM (endpoint policies), Flow Logs + CloudWatch/Athena/GuardDuty, TGW + Direct Connect + VPN (hybrid).

### 3. EC2
**A — Gaps:** **Savings Plans** (Compute vs EC2-Instance — more flexible than RIs); **gp3 decoupling IOPS/throughput from size** (cheaper than gp2); **io2 Block Express**; **EBS Multi-Attach** (io1/io2 only, same-AZ, up to 16 instances, cluster-aware FS required); **Snapshot Archive tier** (75% cheaper, 24–72h restore); **Hibernation** (RAM→EBS root); **EC2 Image Builder**; **Capacity Blocks for ML**; **On-Demand Capacity Reservations**; RI single-customer restriction from June 1 2025.
**B — Decision trees:**
- Steady 24/7 → **Reserved Instances / Savings Plans** (up to ~72%). Mixed/flexible commitment → **Savings Plans**. Fault-tolerant/interruptible/batch → **Spot** (up to 90% off). Bring-your-own-license / compliance / per-socket → **Dedicated Hosts**. Short-term can't-interrupt + capacity guarantee → **On-Demand Capacity Reservation**.
- Low-latency between instances → **Cluster placement group**. HA spread across hardware → **Spread** (max 7/AZ). Many groups needing AZ isolation → **Partition**.
- Need shared block volume across instances same AZ → **io2 Multi-Attach**. Highest IOPS single → **io2 Block Express**. Throughput HDD (big sequential, logs) → **st1**. Coldest cheapest HDD → **sc1**.
**C — Real-world:** Web tier ASG on Savings-Plan-covered baseline + Spot for burst; gp3 root volumes (3,000 IOPS/125 MB/s baseline free). Image Builder bakes hardened golden AMIs on schedule. Snapshot Archive for compliance retention.
**D — Patterns:** (1) "slow at 9am then fine" → **scheduled/predictive scaling / warm pool** pre-warm. (2) "interruptible batch cheapest" → **Spot**. (3) "consistent high-perf DB volume" → **io2**, not gp2. (4) "shared storage 2 EC2 same AZ" → **Multi-Attach io2** (EFS if multi-AZ/NFS). (5) "license-bound to physical cores" → **Dedicated Hosts**.
**E — Triggers:** "interruptible/batch/cheapest compute" → Spot · "steady 1–3yr" → RI/Savings Plan · "flexible across families" → Compute Savings Plan · "per-socket BYOL/compliance" → Dedicated Host · "lowest network latency between nodes / HPC" → cluster placement · "max instance separation" → spread · "independent IOPS scaling cheaply" → gp3 · "highest single-volume IOPS" → io2 Block Express · "shared block multi-instance same AZ" → EBS Multi-Attach · "archive old snapshots cheap" → Snapshot Archive · "resume to prior RAM state" → Hibernation · "automated golden AMI pipeline" → Image Builder.
**F — Traps:** gp2 when gp3 is cheaper/better; instance store for persistence (ephemeral — lost on stop); EBS Multi-Attach with non-cluster FS / multi-AZ (no); Spot for stateful DB; assuming RI is flexible across families (Savings Plan is).
**G — Numbers:** Spot ≤90% off; RI/SP ≤72%; gp3 baseline 3,000 IOPS/125 MB/s, max 16,000 IOPS/1,000 MB/s; io2 up to 256,000 IOPS (Block Express); Multi-Attach ≤16 instances; spread ≤7/AZ; snapshot archive ≥90-day min, 24–72h restore; max EBS volume 64 TiB.
**H — Integration:** EC2 + ASG + ALB + Route 53 (HA web), EC2 + EBS snapshots + DLM/AWS Backup, EC2 role + S3/Secrets Manager.

### 4. Auto Scaling Groups
**A — Gaps:** **Predictive scaling** (ML, pre-scales ahead of forecast); **Warm Pools** (pre-initialized stopped instances for fast scale-out — directly addresses "slow at start of day"); **Launch Templates** (versioned, modern — Launch Configurations are legacy/deprecated answer); lifecycle hooks for bootstrap/cleanup; instance refresh.
**B — Decision trees:** Maintain metric (e.g., CPU 50%) → **Target Tracking** (simplest, default answer). Granular thresholds → **Step**. Known time pattern → **Scheduled**. Recurring forecastable demand → **Predictive**. Long bootstrap causing slow scale-out → **Warm Pool**. Run script on launch/terminate → **Lifecycle Hook**.
**C — Real-world:** Web ASG, target-tracking on RequestCountPerTarget behind ALB; warm pool for apps with 5-min boot; lifecycle hook drains connections + ships logs before terminate. Mixed instances policy: on-demand base + Spot.
**D — Patterns:** (1) "slow first hours each morning" → **scheduled or predictive + warm pool**. (2) "must run config script before serving" → **lifecycle hook (pending:wait)**. (3) "replace instances with new AMI gradually" → **instance refresh**. (4) "still using Launch Configuration" → migrate to **Launch Template**.
**E — Triggers:** "maintain average CPU/X" → target tracking · "scale at 9am" → scheduled · "predictable recurring" → predictive · "pre-warmed instances" → warm pool · "run code before terminate" → lifecycle hook · "Spot + On-Demand mix" → mixed instances policy · "versioned launch config" → launch template.
**F — Traps:** Launch Configuration (legacy); ASG alone = HA (must span ≥2 AZs); confusing health check types (EC2 vs ELB health check — use ELB to replace unhealthy app).
**G — Numbers:** default cooldown 300s; health check grace period default 300s; min/max/desired; termination policy default = oldest launch template/config then closest-to-billing-hour.
**H — Integration:** ASG + ALB health checks + Route 53 + CloudWatch alarms (the canonical HA web tier).

### 5. Load Balancers (ELB)
**A — Gaps:** **GWLB** (3rd-party virtual appliances — firewalls/IDS, GENEVE 6081); **ALB authentication via Cognito/OIDC**; cross-zone LB (ALB on/free; NLB off-by-default/charged); SNI multi-cert; **WAF attaches to ALB/CloudFront/API GW but NOT NLB**; CLB = legacy answer.
**B — Decision trees:** HTTP/HTTPS, path/host routing, redirects, Lambda targets, auth → **ALB**. TCP/UDP/TLS, static IP, ultra-low latency, millions req/s, extreme spikes → **NLB**. 3rd-party security appliances → **GWLB**. Global static IPs + fast cross-region failover + TCP/UDP → **Global Accelerator in front of NLB/ALB**.
**C — Real-world:** ALB → ECS/EKS target groups, path routing /api vs /static; NLB for gaming/VoIP/MQTT; GWLB fronting Palo Alto/Fortinet fleet for inspection.
**D — Patterns:** (1) "static IP for whitelisting + TCP" → **NLB** (or GA). (2) "route /images vs /api" → **ALB**. (3) "authenticate users at LB before backend" → **ALB + Cognito**. (4) "preserve client source IP, L4" → **NLB**. (5) "insert firewall appliances transparently" → **GWLB**.
**E — Triggers:** "path/host-based / HTTP" → ALB · "TCP/UDP/static IP/millions req" → NLB · "3rd-party appliance/IDS inline" → GWLB · "global static anycast IP" → Global Accelerator · "authenticate at LB" → ALB+Cognito · "preserve source IP L4" → NLB · "WAF + LB" → ALB (not NLB) · "huge sudden spike, no pre-warm" → NLB.
**F — Traps:** Classic LB (legacy); WAF on NLB (unsupported); assuming NLB cross-zone is free/on (it's off by default and charged); ALB for non-HTTP.
**G — Numbers:** ALB idle timeout 60s (configurable); NLB preserves source IP; GWLB GENEVE port 6081; ALB supports gRPC/HTTP2/3 via... (NLB needed for HTTP/3 / UDP); deregistration delay default 300s.
**H — Integration:** ALB + ASG + ACM (TLS) + WAF + Cognito; GA + NLB multi-region; NLB + PrivateLink endpoint service.

### 6. S3
**A — Gaps:** **S3 Express One Zone** (directory buckets, single-AZ, up to 10× faster, request costs up to 80% lower than Standard); **DSSE-KMS** (dual-layer); **S3 Object Lambda**; **Access Points / Multi-Region Access Points**; **Requester Pays**; **Object Lock + MFA Delete**; **Glacier Instant vs Flexible vs Deep Archive** distinctions; **Storage Lens**; **128KB lifecycle skip default** (Sept 2024).
**B — Decision trees:**
- Frequent → **Standard**. Unknown/changing pattern → **Intelligent-Tiering** (no retrieval fees). Infrequent, multi-AZ → **Standard-IA**. Infrequent, single-AZ, re-creatable → **One Zone-IA**. Archive, ms retrieval → **Glacier Instant Retrieval**. Archive, minutes-hours → **Glacier Flexible**. Coldest, 12h, cheapest → **Glacier Deep Archive**. Latency-critical co-located compute, single-AZ OK → **Express One Zone**.
- Encryption: default audit-free → **SSE-S3**. Audit/control/rotation → **SSE-KMS** (key auto-rotate yearly). Customer supplies key → **SSE-C**. Highest compliance dual-layer → **DSSE-KMS**.
- Aggregate global uploads fast, least ops → **Transfer Acceleration** (+ multipart).
**C — Real-world:** Static site → S3 + CloudFront + OAC; data lake → S3 + Athena/Glue; lifecycle Standard→IA→Glacier; CRR for DR/compliance; Object Lock WORM for regulators; Storage Lens to find cold data.
**D — Patterns:** (1) "encrypt + key rotated yearly, least ops" → **SSE-KMS customer-managed + auto rotation** (SSE-S3 distractor lacks control/audit). (2) "millions of global static page views" → **CloudFront + S3 origin** (presigned/CRR distractors). (3) "ingest 500GB/site globally to one bucket fast" → **Transfer Acceleration + multipart**. (4) "immutable/WORM compliance" → **Object Lock (compliance mode)**. (5) "analyze JSON logs in place, least ops" → **Athena** (not Redshift/EMR).
**E — Triggers:** "unknown access pattern, no retrieval fee" → Intelligent-Tiering · "ms archive retrieval" → Glacier Instant · "cheapest archive 12h ok" → Deep Archive · "single-AZ cheap re-creatable" → One Zone-IA · "co-located ultra-low-latency" → Express One Zone · "audit who used key" → SSE-KMS · "WORM/immutable" → Object Lock · "accidental delete protection" → Versioning (+MFA Delete) · "global upload speed" → Transfer Acceleration · "query subset of object" → S3 Select · "transform on GET" → Object Lambda · "consumer pays transfer" → Requester Pays.
**F — Traps:** SSE-S3 when audit/control demanded; CloudFront answer when "nearest healthy region, no caching" (that's Route 53/GA); Deep Archive when ms retrieval needed; forgetting min-duration charges; OAI for KMS objects (use OAC).
**G — Numbers:** max object **5 TB**; single PUT **5 GB**; multipart part **5 MB** min (except last), max 10,000 parts; IA/One Zone-IA min **30 days**, 128KB min billable; Glacier Instant/Flexible min **90 days**; Deep Archive min **180 days**; Standard durability 11 9's; lifecycle skips objects <128KB by default (since Sept 2024); Express One Zone storage ~$0.11/GB-mo US-East-1, up to 2M req/s.
**H — Integration:** S3 + CloudFront + Lambda@Edge/OAC; S3 events → SNS/SQS/Lambda; S3 + Athena + Glue + QuickSight; S3 CRR + KMS multi-region keys.

### 7. Route 53
**A — Gaps:** **Geoproximity vs Geolocation** distinction; **bias (+1 to +99 / −1 to −99)** requires Traffic Flow; **Multivalue answer** (≤8 healthy records, not an LB substitute); **DNSSEC**; calculated/CloudWatch health checks; Alias-at-apex.
**B — Decision trees:** one resource → **Simple**. % split / blue-green → **Weighted**. lowest-latency region → **Latency**. active-passive failover → **Failover + health checks**. by user's country (compliance/licensing) → **Geolocation**. bias traffic toward a resource region → **Geoproximity**. several healthy IPs randomized → **Multivalue**. by source CIDR → **IP-based**.
- **Alias** (free, apex-capable, AWS targets) vs **CNAME** (charged, no apex).
**C — Real-world:** Latency routing across us-east-1/eu-west-1 ALBs; failover to S3 static error page when ALB unhealthy; geolocation to satisfy data-residency.
**D — Patterns:** (1) "point example.com (apex) to ALB/CloudFront" → **Alias** (CNAME illegal at apex). (2) "send X% to new version" → **Weighted**. (3) "fastest response globally" → **Latency**. (4) "shift more traffic to bigger datacenter" → **Geoproximity bias**. (5) "restrict by country" → **Geolocation**.
**E — Triggers:** "apex/root domain to AWS resource" → Alias · "A/B / gradual" → weighted · "lowest latency" → latency · "DR active-passive" → failover · "user location/compliance" → geolocation · "bias/shift by resource region" → geoproximity · "multiple healthy IPs" → multivalue · "sign DNS responses" → DNSSEC.
**F — Traps:** CNAME at apex; geolocation vs geoproximity swap; thinking DNS failover is instant (TTL caching delays — GA is faster); multivalue ≠ ELB.
**G — Numbers:** geoproximity bias −99..+99; multivalue ≤8 records; health check interval 30s (10s fast); default TTL matters for failover speed.
**H — Integration:** Route 53 + ALB/CloudFront (alias) + health checks + failover to S3; Route 53 + Aurora Global DB for DR.

### 8. CloudFront & Global Accelerator
**A — Gaps:** **OAC replaces OAI** (OAC supports **SSE-KMS**, all regions, all HTTP methods, dynamic; OAI cannot decrypt KMS); **CloudFront Functions vs Lambda@Edge**; field-level encryption; GA = no caching, no S3 endpoint, 2 static anycast IPs.
**B — Decision trees:**
- Lock S3 to CloudFront → **OAC** (OAI legacy; for KMS objects OAC is mandatory).
- Single private file → **Signed URL**; many files / whole video without changing URLs → **Signed Cookies**; let user upload one object w/o IAM → **S3 presigned URL**.
- Header/URL rewrite, sub-ms, millions req/s, cheapest → **CloudFront Functions** (JS, ≤1ms, 2MB, 10KB code, viewer events only). Heavier logic, Node/Python, network/SDK calls, origin events, request body → **Lambda@Edge** (5s viewer/30s origin).
- Cache HTTP content → **CloudFront**. Static IP + TCP/UDP + fast non-DNS failover → **Global Accelerator**.
**C — Real-world:** Streaming: S3 + CloudFront + signed cookies + OAC + KMS; CloudFront Functions normalize cache keys; Lambda@Edge for SSR/auth at origin. Global API/gaming: GA → NLBs in 2 regions, static IPs for client whitelisting.
**D — Patterns:** (1) "restrict S3 to CloudFront with KMS-encrypted objects" → **OAC** (OAI is wrong distractor). (2) "deliver confidential media globally with caching + access control" → **CloudFront signed URLs/cookies**. (3) "static IP, TCP, fast regional failover" → **GA** (CloudFront distractor — it caches/HTTP). (4) "simple header insert at scale cheapest" → **CloudFront Functions** (Lambda@Edge = overkill/costlier).
**E — Triggers:** "restrict S3 to CDN / KMS objects behind CDN" → OAC · "single file CDN access" → signed URL · "multiple files/whole site no URL change" → signed cookies · "upload to S3 no creds" → S3 presigned · "sub-ms header/URL rewrite, cheapest" → CloudFront Functions · "origin request/response, network call, Node/Python" → Lambda@Edge · "cache content globally" → CloudFront · "static anycast IP / TCP-UDP / no DNS TTL failover" → Global Accelerator.
**F — Traps:** OAI for KMS (fails); Lambda@Edge where CloudFront Functions suffice (cost/scale); GA with S3 endpoint (unsupported); GA "caching" (it doesn't).
**G — Numbers (subagent-verified):** CloudFront Functions: JS-only, **<1 ms**, **2 MB** mem, **10 KB** code, **$0.10/1M**, viewer events only. Lambda@Edge: Node/Python, **5s viewer / 30s origin**, up to **10 GB** mem, **$0.60/1M** + duration (~6× costlier), must be us-east-1 + numbered version. GA: **2 static anycast IPs** (4 dual-stack), AWS backbone, TCP/UDP, ~30s failover (no DNS TTL), no caching, ALB/NLB/EC2/EIP endpoints (no S3). GA ~$0.025/accelerator/hr.
**H — Integration:** CloudFront + S3 (OAC) + WAF + Shield + ACM (cert in us-east-1) + Lambda@Edge; GA + NLB/ALB multi-region + Route 53.

### 9. RDS
**A — Gaps:** **Multi-AZ DB cluster** (2 readable standbys, faster failover) vs classic Multi-AZ (1 standby, not readable); **RDS Proxy** (connection pooling — fixes Lambda connection storms); **RDS Custom**; **Blue/Green deployments** (near-zero-downtime upgrades); IAM DB auth; Performance Insights; cross-region read replicas.
**B — Decision trees:** HA/failover → **Multi-AZ** (synchronous standby, not for reads). Read scaling → **Read Replicas** (async, can lag, promote for DR). Lambda exhausting DB connections → **RDS Proxy**. Major-version upgrade with minimal downtime → **Blue/Green**. Cross-region DR → **cross-region read replica** or snapshot copy. Need OS/db access → **RDS Custom**.
**C — Real-world:** Multi-AZ Postgres + RDS Proxy in front of Lambda; read replicas for reporting; Secrets Manager rotation; Blue/Green for engine upgrades.
**D — Patterns:** (1) "automatic failover minimal effort" → **Multi-AZ** (read replica is the trap — needs manual promotion). (2) "offload read reporting" → **read replica**. (3) "Lambda 'too many connections' during upgrades/spikes" → **RDS Proxy**. (4) "retain daily backups 2 years" → **AWS Backup / manual snapshots** (automated backup max 35 days). (5) "DB upgrade near-zero downtime" → **Blue/Green**.
**E — Triggers:** "automatic failover/HA" → Multi-AZ · "read scaling" → read replica · "connection pooling / Lambda+RDS" → RDS Proxy · "near-zero-downtime upgrade" → Blue/Green · "cross-region DR DB" → cross-region read replica · "auth without passwords" → IAM DB auth · ">35 day retention" → AWS Backup · "find slow queries" → Performance Insights.
**F — Traps:** Multi-AZ for read scaling (it isn't); read replica for automatic failover (manual); automated backups beyond 35 days (use Backup); Multi-AZ = Multi-Region (no, single region).
**G — Numbers:** automated backup retention **0–35 days**; up to **15** read replicas (Postgres/MySQL/MariaDB); Multi-AZ failover 60–120s (classic), faster for cluster; RDS Proxy reduces failover time ~66%.
**H — Integration:** RDS + Lambda + RDS Proxy + Secrets Manager; RDS Multi-AZ + Route 53; read replica + reporting tier.

### 10. Aurora
**A — Gaps:** **I/O-Optimized** (switch when I/O >25% of bill, up to 40% savings, no reboot, toggle once/30 days); **Serverless v2 scale-to-zero**; **Backtrack** (rewind in-place, MySQL — no restore needed); **Global Database** (cross-region <1s replication, ~1min RTO); cloning (copy-on-write); Multi-Master deprecated; Parallel Query; Database Activity Streams.
**B — Decision trees:** Variable/spiky/dev-test → **Serverless v2** (scales 0.5+ ACU, now to 0). Steady high utilization (>60–70%) → **provisioned + RIs**. I/O-heavy (>25% of bill) → **I/O-Optimized**. Cross-region DR/global reads, <1s lag → **Global Database**. "Undo" recent bad write fast (MySQL) → **Backtrack** (no new cluster). Test copy of prod data instantly → **clone** (copy-on-write).
**C — Real-world:** Hybrid: provisioned writer (RI) + Serverless v2 readers (variable read scaling). Global Database for multi-region active-passive DR with near-zero RPO. Backtrack to recover from accidental bulk delete.
**D — Patterns:** (1) "DB cost predictability, I/O charges high" → **I/O-Optimized**. (2) "intermittent dev/test, pay only when used" → **Serverless v2 (scale-to-zero)**. (3) "rewind DB minutes after bad deploy without restore" → **Backtrack**. (4) "cross-region DR, RPO seconds, fast promote" → **Aurora Global Database**. (5) "spin up prod-like test data instantly, cheap" → **clone**.
**E — Triggers:** "6 copies/3 AZ storage" → Aurora architecture · "up to 15 readers" → Aurora replicas · "<1s cross-region / global reads" → Global Database · "scales to zero / per-second billing" → Serverless v2 · "I/O >25% of spend" → I/O-Optimized · "rewind/undo in place" → Backtrack · "instant copy of data" → clone · "audit DB activity stream" → Database Activity Streams.
**F — Traps:** Serverless v2 for steady high load (provisioned+RI cheaper); Backtrack = backup (it's a rewind, MySQL); Multi-Master (deprecated answer); Global Database = Serverless.
**G — Numbers:** **6 copies across 3 AZs**; up to **15 read replicas**; storage auto-grows to **128 TiB**; Serverless v2 0.5-ACU increments (1 ACU ≈ 2 GiB), min 0 (auto-pause) or 0.5+; Global Database <1s replication, ~1min RTO; I/O-Optimized switch once/30 days; storage $0.10/GB (Standard) vs $0.225/GB (I/O-Optimized).
**H — Integration:** Aurora + RDS Proxy + Lambda; Global Database + Route 53 failover; Serverless v2 + API Gateway + Lambda (serverless stack).

### 11. DynamoDB
**A — Gaps:** **GSI vs LSI** strong-consistency nuance (LSI supports strong reads + created only at table creation, shares partition; GSI eventually-consistent only, added anytime, own capacity); **DAX** (microsecond cache); **Global Tables** (multi-region multi-active); **PITR**; **TTL**; **PartiQL**; on-demand vs provisioned + auto-scaling; transactions; conditional writes.
**B — Decision trees:** Microsecond reads / hot reads → **DAX** (not ElastiCache for DynamoDB). Multi-region active-active → **Global Tables**. Query non-key attribute, add later, cross-partition → **GSI**. Same partition key, alt sort key, strong reads → **LSI** (at creation only). Unpredictable traffic → **on-demand**; steady → **provisioned + auto-scaling**. Auto-delete old items → **TTL**. Continuous backup → **PITR**.
**C — Real-world:** Serverless app: API GW → Lambda → DynamoDB (on-demand) + DAX for read-heavy; Streams → Lambda fan-out; Global Tables for global low-latency.
**D — Patterns:** (1) "single-digit ms→microsecond read caching for DynamoDB" → **DAX** (ElastiCache distractor). (2) "multi-region active-active NoSQL" → **Global Tables**. (3) "query by email when PK is userID, added after launch" → **GSI** (LSI can't be added later). (4) "auto-expire sessions" → **TTL**. (5) "restore to any second last 35 days" → **PITR**.
**E — Triggers:** "microsecond reads" → DAX · "multi-region multi-active" → Global Tables · "non-key query added later" → GSI · "strong read alt sort key" → LSI · "spiky unpredictable" → on-demand · "expire items automatically" → TTL · "continuous PITR" → PITR · "all-or-nothing writes" → transactions · "prevent overwrite" → conditional write · "react to item changes" → Streams.
**F — Traps:** ElastiCache for DynamoDB caching (use DAX); LSI added after creation (impossible); GSI strong consistency (eventually only); thinking GSI shares table capacity (own capacity in provisioned).
**G — Numbers:** item max **400 KB**; LSI ≤**5**/table, GSI ≤**20**/table; RCU = 1 strong (or 2 eventual) read/s ≤4KB; WCU = 1 write/s ≤1KB; PITR window **35 days**; LSI shares 10GB partition limit.
**H — Integration:** DynamoDB + Lambda + API Gateway (serverless); Streams → Lambda → SNS/SQS; DynamoDB + S3 (gateway endpoint); Global Tables + Route 53.

### 12. ElastiCache
**A — Gaps:** **Redis vs Memcached** decision; cluster mode; **Multi-AZ + automatic failover (Redis only)**; **Redis AUTH / in-transit encryption**; **ElastiCache Serverless** (newer); caching strategies.
**B — Decision trees:** Persistence, replication, HA/failover, pub/sub, sorted sets, geospatial, backup → **Redis**. Simple, multi-threaded, horizontal scale, no persistence → **Memcached**. Reduce DB read load → cache layer. Lazy loading (cache-aside) for read-heavy; write-through for freshness; TTL to bound staleness.
**C — Real-world:** Session store + leaderboard → Redis cluster mode + Multi-AZ; DB offload for read-heavy product catalog (lazy loading + TTL).
**D — Patterns:** (1) "DB overloaded by reads, least change" → **add ElastiCache** (redesign distractor). (2) "need failover/HA + persistence" → **Redis Multi-AZ** (Memcached lacks failover/persistence). (3) "simple object cache, scale horizontally" → **Memcached**. (4) "leaderboard/pub-sub/geospatial" → **Redis**.
**E — Triggers:** "persistence/replication/HA/pub-sub/sorted set" → Redis · "multi-threaded simple cache" → Memcached · "microsecond DB read offload (relational)" → ElastiCache · "session store" → Redis · "encrypt cache + auth token" → Redis AUTH/TLS.
**F — Traps:** Memcached for HA/persistence (Redis only); ElastiCache for DynamoDB (DAX); thinking Memcached replicates.
**G — Numbers:** Redis backup/snapshot; Multi-AZ auto-failover Redis only; cluster mode shards.
**H — Integration:** ElastiCache + RDS/Aurora (read offload); + EC2/ECS app tier; Redis + ALB sticky alternative (session externalization).

### 13. SQS
**A — Gaps:** **FIFO** ordering/exactly-once + **message group ID** + **deduplication ID**; **DLQ + maxReceiveCount**; **visibility timeout** tuning; **long vs short polling**; delay queues; retention.
**B — Decision trees:** Order + no duplicates → **FIFO** (300 TPS, 3,000 batched). High throughput, order not critical → **Standard** (near-unlimited, at-least-once). Reduce empty receives/cost → **long polling (≤20s)**. Failed messages isolation → **DLQ**. Postpone delivery → **delay queue**. Parallel ordered streams → **message group ID**.
**C — Real-world:** Order processing FIFO with per-customer message group; Standard queue buffering Lambda workers; DLQ + CloudWatch alarm for poison messages.
**D — Patterns:** (1) "decouple, exactly-once, ordered" → **FIFO**. (2) "messages processed twice" → increase **visibility timeout** / make consumer idempotent. (3) "reduce API cost of polling" → **long polling**. (4) "isolate repeatedly failing messages" → **DLQ**.
**E — Triggers:** "order matters / no duplicates" → FIFO · "decouple producers/consumers" → SQS · "poison messages" → DLQ · "reduce empty responses" → long polling · "delay 15min" → delay queue · "parallel ordered streams" → message group ID · "buffer spikes before Lambda/EC2" → SQS.
**F — Traps:** Standard guarantees order (no); FIFO unlimited throughput (capped); SQS pub-sub fan-out (that's SNS); thinking SQS pushes (it's pull).
**G — Numbers:** message ≤**256 KB** (2GB via S3 extended client); retention **1 min–14 days** (default 4 days); visibility timeout **0s–12h** (default 30s); long poll ≤**20s**; delay ≤**15 min**; FIFO **300 TPS** (3,000 batched, higher throughput mode more); in-flight 120,000 (standard).
**H — Integration:** SNS → SQS fan-out; SQS → Lambda (event source); S3 events → SQS; SQS DLQ + CloudWatch.

### 14. SNS
**A — Gaps:** **Fan-out (SNS→multiple SQS)**; **message filtering** (attribute + payload-based); **FIFO topics** (only SQS FIFO subscriber); Firehose subscription; mobile push; A2A vs A2P.
**B — Decision trees:** One-to-many push, multiple subscribers → **SNS**. Durable parallel processing per subscriber → **SNS → SQS fan-out**. Subset routing → **message filtering**. Ordered pub-sub → **FIFO topic** (SQS FIFO target only). Deliver streaming to S3/Redshift → **SNS → Firehose**.
**C — Real-world:** S3 upload → SNS → 3 SQS queues (thumbnail, index, audit) each with own Lambda; price alerts to SMS/email/HTTP.
**D — Patterns:** (1) "one event, many independent consumers, durable" → **SNS+SQS fan-out**. (2) "route only matching messages to a queue" → **filter policy**. (3) "broadcast to email/SMS/mobile" → **SNS A2P**. (4) "ordered pub-sub no dupes" → **FIFO topic**.
**E — Triggers:** "fan-out / pub-sub push" → SNS · "multiple durable consumers" → SNS+SQS · "filter by attribute" → SNS message filtering · "SMS/email/push" → SNS · "ordered topic" → SNS FIFO · "stream to S3/Redshift" → SNS→Firehose.
**F — Traps:** SNS for durable single-consumer queue (use SQS); SNS retains messages (it doesn't — pair with SQS); FIFO topic with non-SQS-FIFO subscriber.
**G — Numbers:** message ≤256 KB; up to 12.5M subscriptions/topic (standard); FIFO 300 msg/s; retry policies for HTTP.
**H — Integration:** SNS fan-out + SQS + Lambda; CloudWatch alarms → SNS; S3/RDS events → SNS.

### 15. EventBridge
**A — Gaps:** **Pipes** (point-to-point source→filter→enrich→target; sources include SQS/Kinesis/DynamoDB Streams/MSK/MQ); **Archive & Replay**; **Schema Registry**; **content-based filtering** across full event; **scheduler**; vs SNS/SQS.
**B — Decision trees:** React to AWS/SaaS/custom events, many-to-many routing, content filtering, SaaS integration → **EventBridge bus**. Point-to-point with transform/enrich from a stream/queue → **Pipes**. High fan-out to millions → **SNS**. Decouple + buffer single consumer → **SQS**. Need replay of past events → **EventBridge archive/replay** (or Kinesis for stream replay).
**C — Real-world:** Order events → EventBridge → route by rule to fulfillment/analytics/Lambda; Pipes: SQS → enrich via Lambda → Step Functions; cron via EventBridge Scheduler.
**D — Patterns:** (1) "route events from SaaS (Datadog/Shopify) to AWS" → **EventBridge** (only one with SaaS partners). (2) "filter on event content, fan to many targets" → **EventBridge rules**. (3) "connect a queue/stream to a target with filtering/enrichment, point-to-point" → **Pipes**. (4) "replay past events for debugging" → **archive + replay**.
**E — Triggers:** "SaaS event integration" → EventBridge · "content/pattern-based routing" → EventBridge rules · "schedule/cron" → EventBridge Scheduler · "point-to-point stream→target + enrich" → Pipes · "schema discovery" → Schema Registry · "replay events" → archive/replay · "high fan-out millions" → SNS · "real-time replay of stream" → Kinesis Data Streams.
**F — Traps:** EventBridge for ultra-high-throughput/low-latency fan-out (SNS better); using SQS when content routing needed; EventBridge latency (~half-second) for sub-ms needs.
**G — Numbers:** event ≤256 KB; 300 rules/bus (raisable), 5 targets/rule; archive retention configurable/infinite; SLA 99.99%.
**H — Integration:** EventBridge → Lambda/SQS/SNS/Step Functions/Kinesis; Pipes (SQS/DynamoDB Streams source) → enrichment → bus; CloudTrail events → EventBridge rules.

### 16. Kinesis
**A — Gaps:** **Data Streams** (shards, partition key, retention up to 365 days, **replay**, consumer manages position); **Firehose** (near-real-time delivery to S3/Redshift/OpenSearch, no replay, serverless); **Managed Service for Apache Flink** (was Data Analytics); **Video Streams**; on-demand vs provisioned shards; vs SQS vs MSK.
**B — Decision trees:** Real-time streaming, multiple consumers, **ordering per partition**, **replay** → **Data Streams**. Load streaming to S3/Redshift/OpenSearch with transform, least ops → **Firehose**. SQL/Flink analytics on stream → **Managed Service for Apache Flink**. Kafka-compatible / migrate existing Kafka → **MSK**. Simple decoupling single consumer → **SQS** (not Kinesis).
**C — Real-world:** Clickstream → Data Streams → Flink real-time + Firehose → S3 data lake; IoT telemetry; Video Streams for camera ingestion.
**D — Patterns:** (1) "real-time, multiple consumers, must replay" → **Data Streams** (SQS distractor — no replay/ordering across consumers). (2) "deliver streaming data to S3/Redshift least ops" → **Firehose** (fully managed, no shards). (3) "Kafka migration" → **MSK**. (4) "massive clickstream cheapest at scale" → **Kinesis** (vs paying per SQS message).
**E — Triggers:** "real-time replay / ordered stream / multiple consumers" → Data Streams · "deliver to S3/Redshift/OpenSearch, near-real-time, no management" → Firehose · "SQL/Flink on stream" → Managed Service for Apache Flink · "Kafka compatible" → MSK · "ingest video" → Video Streams · "shard / partition key" → Data Streams.
**F — Traps:** Firehose for real-time (it's near-real-time, ~60s buffer, no replay); SQS for replay/streaming analytics; thinking Firehose has shards (it auto-scales).
**G — Numbers:** shard = **1 MB/s or 1,000 records/s in**, **2 MB/s out**; retention **24h default, up to 365 days**; Firehose buffer 60s–900s / 1–128MB; enhanced fan-out 2MB/s per consumer per shard.
**H — Integration:** Data Streams → Lambda/Flink/Firehose → S3 → Athena; Firehose + Lambda transform; EventBridge Pipes with Kinesis source.

### 17. Lambda
**A — Gaps:** **SnapStart** (Python 3.12+/.NET 8+ Nov 2024, Java since 2022; sub-second; **no PC/EFS/container/>512MB ephemeral**); **reserved vs provisioned concurrency** distinction; container image support (10 GB); **Destinations**; extensions; VPC integration (Hyperplane ENIs); cold starts; Lambda@Edge.
**B — Decision trees:** Predictable consistent low latency, eliminate cold start → **Provisioned Concurrency**. Java/Python/.NET cold starts on spiky traffic, no code change → **SnapStart** (free for Java). Guarantee/limit concurrency for a function → **Reserved Concurrency**. >15 min / >10GB RAM / persistent / GPU → **Fargate/ECS** instead. Async failure routing → **Destinations / DLQ**.
- **Lambda fails, Fargate wins when:** runtime >15 min, need >10 GB RAM, GPU, persistent connections, large containers >10GB, predictable steady high utilization.
**C — Real-world:** API GW → Lambda → DynamoDB; SnapStart on Java auth function; Provisioned Concurrency for latency-sensitive checkout; RDS Proxy to avoid connection storms.
**D — Patterns:** (1) "reduce Java/Python cold starts cheaply, no code change" → **SnapStart**. (2) "consistent double-digit-ms latency, predictable" → **Provisioned Concurrency**. (3) "job runs 30 min" → **Fargate/ECS** (Lambda 15-min cap). (4) "Lambda exhausts RDS connections" → **RDS Proxy**.
**E — Triggers:** "sub-second cold start, no code change, Java/Python/.NET" → SnapStart · "always warm, predictable latency" → Provisioned Concurrency · "cap/guarantee concurrency" → Reserved Concurrency · ">15 min or >10GB or GPU" → Fargate · "async retry/route on success-fail" → Destinations · "run at edge" → Lambda@Edge · "package >250MB" → container image (10GB).
**F — Traps:** Lambda for >15-min jobs; SnapStart with provisioned concurrency/EFS/container (unsupported); reserved vs provisioned confusion (reserved limits, provisioned pre-warms); Lambda in VPC slow (improved with Hyperplane).
**G — Numbers:** max timeout **15 min**; memory **128 MB–10 GB**; /tmp **512 MB–10 GB**; default concurrency **1,000/region** (raisable); deployment zip **50 MB** (250MB unzipped) / container **10 GB**; payload sync 6MB/async 256KB; layers ≤5.
**H — Integration:** API GW + Lambda + DynamoDB; S3/SQS/SNS/Kinesis/EventBridge triggers; Lambda + RDS Proxy; Lambda@Edge + CloudFront.

### 18. API Gateway
**A — Gaps:** **REST vs HTTP API** (HTTP API cheaper/faster/fewer features; REST has API keys/usage plans/caching/WAF); **WebSocket API**; authorizers (Lambda/Cognito/IAM); usage plans + API keys; caching; mapping templates; **VPC Link** (private integration to NLB/ALB); throttling; CORS.
**B — Decision trees:** Simple proxy to Lambda/HTTP, low cost, low latency → **HTTP API**. Need API keys, usage plans, caching, request validation, WAF, edge-optimized → **REST API**. Real-time bidirectional → **WebSocket API**. Auth with user pool → **Cognito authorizer**; custom logic → **Lambda authorizer**; AWS principals → **IAM authorizer**. Private backend in VPC → **VPC Link**.
**C — Real-world:** Public REST API → Lambda + Cognito authorizer + usage plans/throttling + WAF; HTTP API for internal microservice proxy; WebSocket for chat.
**D — Patterns:** (1) "manage org's users, control REST API access, least ops" → **Cognito user pool authorizer**. (2) "monetize/throttle per customer" → **usage plans + API keys (REST)**. (3) "cheapest simple Lambda proxy" → **HTTP API**. (4) "private integration to internal ALB/NLB" → **VPC Link**.
**E — Triggers:** "API keys / usage plans / caching / per-client throttle" → REST API · "cheapest low-latency proxy" → HTTP API · "real-time bidirectional" → WebSocket · "authenticate with user pool" → Cognito authorizer · "custom token validation" → Lambda authorizer · "private VPC backend" → VPC Link · "protect API from SQLi/XSS" → WAF on REST API.
**F — Traps:** HTTP API when API keys/usage plans/caching needed (REST only); WAF on HTTP API (REST/CloudFront); thinking throttling = caching.
**G — Numbers:** default throttle **10,000 req/s, burst 5,000**; payload **10 MB**; integration timeout **29s**; caching 0.5GB–237GB.
**H — Integration:** API GW + Lambda + DynamoDB + Cognito + WAF; API GW + VPC Link + NLB + ECS; API GW + Step Functions.

### 19. ECS / EKS / Fargate
**A — Gaps:** **Task Role vs Execution Role** (execution role = ECS agent pulls ECR image + ships logs + reads secrets; task role = your app code's AWS perms); Fargate vs EC2 launch type; **Capacity Providers** + Fargate Spot; service auto scaling (tasks) vs cluster auto scaling (instances); EKS basics; ECR; Service Discovery (Cloud Map); App Mesh (EOL Sept 2026 → VPC Lattice).
**B — Decision trees:** No infra management, variable/bursty, microservices, least ops → **Fargate**. GPU, special instance types, daemonsets, max control, steady high utilization cheapest → **EC2 launch type**. Kubernetes / multi-cloud portability → **EKS**. App code needs S3/DynamoDB → **task role**. Pull ECR/ship logs/read Secrets → **execution role**.
**C — Real-world:** Fargate services behind ALB, task role per service (least privilege), Fargate Spot for non-critical via capacity provider weights; EKS for teams standardized on K8s; EFS mounted to Fargate for shared persistent storage.
**D — Patterns:** (1) "run containers no server management, least ops" → **Fargate**. (2) "container needs to write to S3" → **task role** (execution role is distractor). (3) "GPU container" → **EC2 launch type** (Fargate no GPU). (4) "cost-optimize non-critical containers" → **Fargate Spot**. (5) "shared multi-AZ storage for containers" → **EFS**.
**E — Triggers:** "serverless containers / no infra" → Fargate · "GPU/daemonset/special instances" → EC2 launch type · "Kubernetes" → EKS · "app AWS API perms" → task role · "pull image/ship logs/secrets" → execution role · "container registry" → ECR · "service-to-service discovery" → Cloud Map · "Spot for containers" → Fargate Spot.
**F — Traps:** Execution role vs task role swap (classic); Fargate for GPU (no); thinking Fargate is Windows-only (false); App Mesh as future answer (EOL → VPC Lattice).
**G — Numbers:** Fargate ~$0.04048/vCPU-hr, $0.004445/GB-hr (x86), 20% cheaper Graviton; task def ≤10 containers; Fargate Spot up to 70% off.
**H — Integration:** ECS/Fargate + ALB + ASG/capacity providers + ECR + task role→S3/DynamoDB + EFS + CloudWatch Container Insights.

### 20. Encryption & Secrets
**A — Gaps:** **KMS multi-region keys**; key policy is authoritative (not just IAM); **grants**; asymmetric keys; **automatic rotation** (yearly for CMK; SSE-S3 keys); **CloudHSM** (dedicated, FIPS 140-2 L3, single-tenant); **Secrets Manager rotation + cross-account + replication**; **SSM Parameter Store Standard vs Advanced**; **ACM** (free public certs, auto-renew); **Private CA**.
**B — Decision trees:**
- Managed secret with **automatic rotation** (RDS/Redshift/DocumentDB), cross-account, multi-region replication → **Secrets Manager** ($0.40/secret/mo). Config/secrets, **no rotation needed, free/cheap** → **SSM Parameter Store** (Standard free; Advanced $0.05/param for >10k, 8KB, policies).
- Dedicated single-tenant HSM, FIPS 140-2 L3, full control, key ceremony → **CloudHSM**. Managed multi-tenant KMS → **KMS**.
- Free public TLS cert, auto-renew on ALB/CloudFront → **ACM**. Internal/private cert hierarchy → **ACM Private CA**.
- Use same key across regions (CRR, DR) → **KMS multi-region keys**.
**C — Real-world:** RDS creds in Secrets Manager auto-rotated; app config in Parameter Store; ACM cert on ALB; KMS CMK per data classification with key policy; CloudHSM for regulated key custody.
**D — Patterns:** (1) "rotate DB credentials automatically, least ops" → **Secrets Manager**. (2) "store config/license keys cheaply, no rotation" → **Parameter Store Standard** (Secrets Manager = unnecessary cost). (3) "FIPS 140-2 Level 3 / dedicated HSM / key custody" → **CloudHSM**. (4) "free auto-renewing TLS cert" → **ACM**. (5) "encrypt across regions same key" → **multi-region KMS keys**.
**E — Triggers:** "auto-rotate secret / RDS creds" → Secrets Manager · "free config store no rotation" → Parameter Store · "dedicated single-tenant HSM / FIPS L3" → CloudHSM · "free public cert auto-renew" → ACM · "internal CA" → Private CA · "same key multiple regions" → multi-region keys · "control + audit key use" → KMS CMK · "cross-account secret" → Secrets Manager.
**F — Traps:** Secrets Manager when no rotation needed (Parameter Store cheaper); Parameter Store for auto-rotation (Secrets Manager); KMS for FIPS L3 dedicated (CloudHSM); ACM cert for CloudFront not in us-east-1 (must be us-east-1).
**G — Numbers:** Secrets Manager $0.40/secret/mo + $0.05/10k API; Parameter Store Standard free ≤10k (4KB), Advanced $0.05/param (8KB, >10k); KMS CMK $1/mo + $0.03/10k; CMK rotation yearly; CloudHSM FIPS 140-2 L3.
**H — Integration:** Secrets Manager + RDS/Lambda/ECS; KMS + S3/EBS/RDS/Secrets Manager; ACM + ALB/CloudFront/API GW; Parameter Store + ECS/Lambda.

### 21. Cognito
**A — Gaps:** **User Pool (authentication, directory, sign-up/in, MFA, social/SAML/OIDC, hosted UI, JWT)** vs **Identity Pool (authorization → temp AWS creds via STS for S3/DynamoDB)**; ALB & API Gateway integration; vs IAM Identity Center (workforce); guest/unauthenticated access.
**B — Decision trees:** Authenticate app/mobile/web users, sign-up/in, federation → **User Pool**. Grant authenticated users **temporary AWS credentials** to hit S3/DynamoDB directly → **Identity Pool**. Both (login + AWS access) → **User Pool → Identity Pool**. Authenticate API GW/ALB requests with user directory → **Cognito authorizer / ALB-Cognito**. Workforce SSO across accounts → **IAM Identity Center** (not Cognito).
**C — Real-world:** Mobile app → User Pool (sign-in, JWT) → API GW Cognito authorizer → Lambda → DynamoDB; Identity Pool issues scoped creds for direct S3 upload.
**D — Patterns:** (1) "manage app users sign-up/in, social login, least ops" → **User Pool**. (2) "let signed-in users upload directly to S3 with temp creds" → **Identity Pool**. (3) "authenticate ALB users without building login" → **ALB + Cognito User Pool**. (4) "workforce many AWS accounts" → **IAM Identity Center** (Cognito distractor).
**E — Triggers:** "external app/mobile users / sign-up-in / social / SAML" → User Pool · "temporary AWS credentials for users" → Identity Pool · "authenticate at ALB/API GW" → Cognito authorizer · "hundreds/millions of customers" → Cognito · "workforce SSO" → IAM Identity Center.
**F — Traps:** IAM for external app users (Cognito); User Pool vs Identity Pool swap (auth vs AWS-creds); Cognito for workforce SSO (Identity Center).
**G — Numbers:** JWT tokens; MFA SMS/TOTP; supports OIDC/SAML 2.0/OAuth 2.0; scales to millions.
**H — Integration:** Cognito + API Gateway/ALB; User Pool→Identity Pool→S3/DynamoDB; Cognito + Lambda triggers.

### 22. CloudTrail / CloudWatch / Config & Security services
**A — Gaps:** **CloudTrail (who-did-what API audit)** vs **Config (resource configuration/compliance over time)** vs **CloudWatch (metrics/logs/alarms)**; **GuardDuty** (threat detection from CloudTrail/VPC Flow/DNS; **Extended Threat Detection** re:Invent 2024 correlates attack sequences); **Inspector** (vuln/CVE + now SAST/IaC scanning); **Macie** (PII/sensitive data in S3); **Security Hub** (aggregator/CSPM); **Detective** (root-cause investigation graph); **Audit Manager**; Logs Insights; **Synthetics** (canaries); **RUM**; **Container Insights**.
**B — Decision trees:** "Who made this API call / audit trail" → **CloudTrail**. "Is resource config compliant / track config changes" → **Config**. "Metrics/alarms/dashboards/logs" → **CloudWatch**. "Detect threats/compromised instances/crypto-mining" → **GuardDuty**. "Find software vulnerabilities/CVEs" → **Inspector**. "Discover PII in S3" → **Macie**. "Single pane aggregating findings/compliance score" → **Security Hub**. "Investigate root cause of finding" → **Detective**. "Synthetic uptime monitoring" → **Synthetics canaries**. "Real-user browser performance" → **RUM**.
**C — Real-world:** GuardDuty org-wide + findings → Security Hub → EventBridge → Lambda auto-remediation; Config rules enforce encryption/tagging; CloudTrail to S3 + Athena for forensics; Macie scans data lake for PII pre-compliance audit.
**D — Patterns:** (1) "detect compromised EC2 / unusual API / crypto-mining" → **GuardDuty**. (2) "find PII/PHI in S3 buckets" → **Macie**. (3) "scan EC2/ECR for CVEs" → **Inspector**. (4) "who deleted the bucket" → **CloudTrail**. (5) "ensure all volumes encrypted, alert on drift" → **Config**. (6) "centralize all security findings" → **Security Hub**.
**E — Triggers:** "API audit / who-did-what" → CloudTrail · "config compliance/history" → Config · "metrics/alarms/logs" → CloudWatch · "threat detection" → GuardDuty · "vulnerabilities/CVE" → Inspector · "PII/sensitive data S3" → Macie · "aggregate findings/compliance" → Security Hub · "investigate root cause" → Detective · "synthetic canary" → Synthetics · "real user monitoring" → RUM · "container metrics" → Container Insights · "query logs SQL-like" → Logs Insights.
**F — Traps:** CloudTrail vs Config swap (API calls vs resource config); GuardDuty vs Inspector (threats vs vulnerabilities); Macie for threats (it's data classification); Security Hub generates findings (it aggregates).
**G — Numbers:** CloudTrail 90-day event history free (longer → S3); Config records configuration items; GuardDuty 30-day trial; Detective up to 1 year data.
**H — Integration:** GuardDuty/Inspector/Macie → Security Hub → EventBridge → Lambda/SNS; CloudTrail → S3 → Athena; Config + SNS for drift; CloudWatch alarms → ASG/SNS.

### 23. Storage (FSx / EFS / Storage Gateway / DataSync / Snow / Transfer)
**A — Gaps:** **FSx four flavors** (Windows/SMB+AD; Lustre HPC+S3; NetApp ONTAP multi-protocol+SnapMirror; OpenZFS low-latency NFS); **EFS** (IA lifecycle, throughput modes, performance modes, regional Multi-AZ); **DataSync** (one-time/scheduled migration, fast); **Storage Gateway** types (File/Volume cached+stored/Tape); **Snow Family**; **AWS Transfer Family** (SFTP/FTPS/FTP/AS2).
**B — Decision trees:**
- Windows + Active Directory + SMB → **FSx for Windows**. HPC/ML high throughput + S3 integration → **FSx for Lustre**. Multi-protocol NAS / SnapMirror / dedup / lift-and-shift NetApp → **FSx for ONTAP**. Low-latency NFS + ZFS snapshots → **FSx for OpenZFS**. General Linux NFS, serverless/elastic, Multi-AZ → **EFS**.
- One-time/scheduled bulk migration over network → **DataSync**. Hybrid on-prem cached access to cloud storage → **Storage Gateway**. Petabyte offline transfer / no bandwidth → **Snowball/Snowmobile**; small/edge → **Snowcone**. Managed SFTP/FTPS/AS2 to S3/EFS → **Transfer Family**.
**C — Real-world:** EFS shared across Fargate tasks; FSx Lustre next to GPU fleet hydrating from S3; FSx Windows for .NET app home dirs + AD; DataSync for datacenter→S3 migration; File Gateway for on-prem NFS/SMB with S3 backing.
**D — Patterns:** (1) "Windows file share + AD, managed" → **FSx for Windows**. (2) "HPC/ML scratch + S3" → **FSx for Lustre**. (3) "shared multi-AZ Linux NFS for many EC2" → **EFS**. (4) "migrate 50TB over network, scheduled, least ops" → **DataSync**. (5) "100TB no bandwidth" → **Snowball**. (6) "managed SFTP into S3" → **Transfer Family**. (7) "on-prem app needs local low-latency + cloud backup" → **Storage Gateway (cached volume / File)**.
**E — Triggers:** "SMB/Windows/AD" → FSx Windows · "Lustre/HPC/ML/parallel" → FSx Lustre · "SnapMirror/multi-protocol/NetApp" → FSx ONTAP · "ZFS snapshots/low-latency NFS" → FSx OpenZFS · "elastic shared NFS Multi-AZ" → EFS · "migrate data over network scheduled" → DataSync · "hybrid cached on-prem" → Storage Gateway · "offline petabyte" → Snowball/Snowmobile · "managed SFTP/FTPS/AS2" → Transfer Family.
**F — Traps:** EFS for Windows/SMB (use FSx Windows); EBS for multi-AZ shared (EFS); DataSync vs Storage Gateway (migration vs ongoing hybrid access); Lustre Multi-AZ (was single-AZ; now Multi-AZ GA Oct 2024).
**G — Numbers:** EFS Standard + One Zone, IA lifecycle (7/14/30/60/90 days), 11 9's (regional); FSx Lustre scratch vs persistent; DataSync up to 10x faster than open-source; Snowball Edge ~80TB; Transfer Family SFTP/FTPS/FTP/AS2.
**H — Integration:** EFS + EC2/Fargate/Lambda; FSx Lustre + S3 + EC2 GPU; DataSync + S3 + Storage Gateway; Transfer Family + S3 + Lambda.

### 24. Disaster Recovery Strategies
**A — Gaps:** RPO/RTO mapping per strategy; **AWS Elastic Disaster Recovery (DRS)** (block-level replication, pilot-light-style for servers, not RDS); **AWS Backup** (centralized cross-service, cross-region, PITR); cross-region replication patterns; data-plane vs control-plane for failover.
**B — Decision trees (cheapest → costliest, slowest RTO → fastest):**
- **Backup & Restore** (RPO hours, RTO hours): cheapest; backups + IaC; rebuild on disaster. "Cost is priority, RTO in hours OK."
- **Pilot Light** (RPO minutes, RTO tens of min): data replicated + core (DB) on, compute off. DRS uses this model.
- **Warm Standby** (RPO seconds, RTO minutes): scaled-down full stack always running; scale up on failover.
- **Multi-Site Active/Active** (RPO ~0, RTO ~0): full prod in multiple regions serving traffic; costliest/most complex.
- Server-based on-prem/other-cloud → **DRS**. Managed services → native (S3 CRR, Aurora Global DB, DynamoDB Global Tables, cross-region read replicas).
**C — Real-world:** Pilot light with RDS cross-region read replica + On-Demand Capacity Reservations; warm standby scaled-down ASG + Aurora Global DB; AWS Backup for centralized cross-region compliance backups; Route 53/Global Accelerator for failover routing.
**D — Patterns:** (1) "RTO hours, lowest cost" → **Backup & Restore**. (2) "RTO tens of minutes, data live but compute off" → **Pilot Light**. (3) "RTO minutes, reduced-capacity stack running" → **Warm Standby**. (4) "RTO ~0, zero data loss, serve from both regions" → **Multi-Site Active/Active**. (5) "replicate on-prem servers to AWS for DR, least ops" → **DRS**.
**E — Triggers:** "cheapest DR, RTO hours" → Backup & Restore · "core DB on, compute off" → Pilot Light · "scaled-down running stack" → Warm Standby · "active-active multi-region zero downtime" → Multi-Site · "replicate physical/VM servers" → Elastic Disaster Recovery · "centralized cross-service cross-region backup" → AWS Backup · "DB cross-region near-zero RPO" → Aurora Global Database.
**F — Traps:** Multi-AZ as DR (it's HA single-region — DR = Multi-Region); choosing costliest when RTO allows cheaper; DRS for RDS (use native); relying on control-plane ops during failover.
**G — Numbers:** Backup&Restore RPO/RTO hours; Pilot Light RPO min/RTO tens-min; Warm Standby RPO sec/RTO min; Active/Active RPO~0/RTO~0; PITR can lower RPO to ~5 min.
**H — Integration:** Route 53 failover + Aurora Global DB + S3 CRR + DynamoDB Global Tables; AWS Backup + Organizations cross-account; DRS + EC2.

### 25. Cost Optimisation
**A — Gaps:** **Compute Optimizer** (ML right-sizing recommendations for EC2/ASG/Lambda/EBS); **S3 Storage Lens** (org-wide storage analytics/recommendations); **Cost Explorer** (analyze/forecast); **Budgets** (alerts/actions); **Trusted Advisor** (5 pillars incl. cost checks); analytics services cost profiles (**Athena** $5/TB scanned — partition/Parquet; **Redshift** for steady warehousing; **EMR** for big-data frameworks; **Glue** serverless ETL; **OpenSearch**; **QuickSight**; **Lake Formation**).
**B — Decision trees:**
- "Right-size over-provisioned EC2/Lambda" → **Compute Optimizer**. "Find cold S3 data / storage recommendations org-wide" → **S3 Storage Lens**. "Analyze/forecast spend by tag/service" → **Cost Explorer**. "Alert/stop at budget threshold" → **Budgets** (+ budget actions). "Best-practice cost checks" → **Trusted Advisor**.
- Analytics: ad-hoc SQL on S3, least ops, pay-per-query → **Athena** (partition + Parquet to cut cost). Steady complex BI warehouse → **Redshift**. Hadoop/Spark big data → **EMR**. Serverless ETL/catalog → **Glue**. Dashboards → **QuickSight**. Data lake governance/permissions → **Lake Formation**.
**C — Real-world:** Storage Lens flags cold buckets → lifecycle to IA/Glacier; Compute Optimizer right-sizes ASG; Savings Plans for baseline; Athena+Parquet+partitioning cuts query bills 85–99%; Budgets alerts to FinOps Slack.
**D — Patterns:** (1) "analyze JSON/CSV logs in S3 ad-hoc, least ops, cheapest" → **Athena** (Redshift/EMR distractors = more ops/cost). (2) "right-size instances automatically" → **Compute Optimizer**. (3) "alert when spend exceeds $X" → **Budgets**. (4) "identify underused storage across org" → **Storage Lens**. (5) "reduce Athena cost" → **partition + columnar (Parquet) + compression**. (6) "steady high-concurrency BI" → **Redshift** (Athena cost crosses over).
**E — Triggers:** "right-size EC2/Lambda/EBS" → Compute Optimizer · "S3 storage analytics/recommendations" → Storage Lens · "analyze/forecast cost" → Cost Explorer · "budget alert/action" → Budgets · "best-practice checks" → Trusted Advisor · "ad-hoc SQL on S3 cheapest" → Athena · "data warehouse steady" → Redshift · "Spark/Hadoop" → EMR · "serverless ETL/catalog" → Glue · "BI dashboards" → QuickSight · "data lake permissions" → Lake Formation.
**F — Traps:** Redshift/EMR for simple ad-hoc S3 queries (Athena cheaper/less ops); Cost Explorer to enforce limits (that's Budgets); Trusted Advisor full cost checks need Business/Enterprise support; ignoring Athena partitioning (huge cost).
**G — Numbers:** Athena **$5/TB scanned** (10MB min/query); Compute Optimizer free; Storage Lens free (default metrics) + paid advanced; RI/SP up to 72%; Spot up to 90%; Athena partition+Parquet can cut 85–99%.
**H — Integration:** Storage Lens + S3 lifecycle; Compute Optimizer + ASG/Savings Plans; Athena + Glue + S3 + QuickSight; Cost Explorer + Budgets + Organizations.

---

## RECOMMENDATIONS (how Sanky should use these notes)

**Stage 1 — Build the "gap" deep-dive docs first (week 1).** Prioritize the 11 explicitly under-weighted topics: S3 Express One Zone, Aurora I/O-Optimized & Serverless v2 scale-to-zero, Lambda SnapStart, EventBridge Pipes, OAC-vs-OAI, Network Firewall, WAF/Shield Advanced, DataSync, Compute Optimizer, S3 Storage Lens, plus Aurora Backtrack and EBS Multi-Attach. These are the highest-yield additions because they are newest and least likely in older Maarek/Bonso material. **Benchmark to change plan:** if you score >85% on Tutorials Dojo sections covering these, downshift to Stage 2.

**Stage 2 — Drill the decision-tree section (B) of each topic into flashcards (week 2).** The exam is decided by qualifier discrimination, not recall. Convert every "if X → Y, but if also Z → W" into a single card. Focus especially on the five pairings examiners abuse: Multi-AZ vs read replica vs Multi-Region; gateway vs interface endpoint; CloudFront vs Global Accelerator vs Route 53; Secrets Manager vs Parameter Store; Athena vs Redshift vs EMR.

**Stage 3 — Trigger-phrase mastery (week 3).** Turn every section E map into a two-column quiz doc (phrase → service). Aim for instant recall; in the real exam you'll pattern-match the stem's keywords to the answer in seconds.

**Stage 4 — Trap inoculation (ongoing).** Build one "trap deck" from all section F entries. Every wrong practice answer should be traced to a trap on this list. **Threshold to sit the exam:** consistent 80%+ on full 65-question Bonso timed mocks (Bonso runs ~10% harder than real), with no single domain below 70%.

**Always-apply heuristics during the exam:** read the qualifier first ("MOST cost-effective" / "LEAST operational overhead" / "real-time" / "MOST resilient"), eliminate legacy answers (NAT Instance, CLB, Launch Configuration, OAI, Multi-Master, Cognito Sync), then choose the simplest managed/serverless option that *exactly* meets stated requirements — not the most powerful.

---

## CAVEATS

- **Pricing and limits drift.** Figures here (e.g., S3 Express One Zone $0.11/GB-mo, Aurora ACU $0.12/hr, Fargate vCPU rates) were verified to AWS sources in 2025–2026 but the exam rarely tests exact dollar figures — it tests *relative* cost logic. Treat dollar amounts as directional.
- **Some third-party numbers are estimates.** Global Accelerator failover is described by AWS as "within seconds"; the "~30s" figure is a community estimate — the testable point is "faster than DNS, no TTL dependency," not the exact second.
- **Service status changes.** App Mesh reaches EOL Sept 30, 2026 (→ VPC Lattice); CodeCommit stopped onboarding new customers (July 2024); standalone Glacier and Cognito Sync are legacy. Aurora Multi-Master is deprecated. Don't pick these as "best" answers; AWS sometimes lags exam updates, so if a question references an old service, answer within the question's framing.
- **The exam guide weights shift.** Several 2025–2026 sources report increased Security emphasis (some cite ~30% of scored content) and new performance/cost task statements; confirm the current domain weighting on the official AWS SAA-C03 exam guide before exam day.
- **These are research notes, not verified question banks.** The scenario patterns (section D) are synthesized from Tutorials Dojo, r/AWSCertifications, and Medium pass-stories — they reflect *patterns*, not actual exam questions. Verify each fact against AWS docs/FAQs when building your final masterclass and quiz documents.
- **Edge/security depth (Topic 8, WAF/Shield, Route 53)** came from a focused sub-research pass and is the most independently corroborated section; the analytics-cost crossover points (Topic 25) are the least precise and should be re-verified if you build detailed cost-calculation quiz items.

---

## META-INSIGHTS ACROSS ALL TOPICS — Top 20 cross-cutting decision rules

1. **Managed/serverless almost always wins "LEAST operational overhead."** Lambda > EC2+scripts; Fargate > EC2 launch type; Aurora Serverless > self-managed; Athena > EMR; SQS/SNS > self-hosted brokers.
2. **"MOST cost-effective" ≠ "most resilient."** Pick the cheapest option that *still meets stated requirements* — don't over-engineer Multi-Region when 2-AZ suffices.
3. **Multi-AZ = High Availability (single region). Multi-Region = Disaster Recovery.** They are never interchangeable. Read replica ≠ failover.
4. **In IAM, explicit Deny always beats Allow; SCPs and permission boundaries only *cap*, never *grant*.**
5. **Gateway endpoint = S3/DynamoDB only, free. Interface endpoint/PrivateLink = everything else, paid.** Never put non-S3/DynamoDB on a gateway endpoint.
6. **CloudFront caches; Global Accelerator does not.** "Static IP / TCP-UDP / non-DNS failover" → GA; "cache content / HTTP" → CloudFront; "nearest healthy region, no caching" → Route 53/GA.
7. **"Real-time replay" or "ordered stream, multiple consumers" → Kinesis Data Streams.** "Deliver to S3/Redshift, near-real-time, no mgmt" → Firehose. "Decouple single consumer" → SQS. "Fan-out push" → SNS. "SaaS/content-routing/scheduled" → EventBridge.
8. **OAC replaces OAI — and OAC is mandatory for SSE-KMS objects behind CloudFront.**
9. **Secrets Manager only when you need rotation / cross-account / replication; otherwise Parameter Store (free) wins on cost.**
10. **DAX for DynamoDB caching; ElastiCache for relational (RDS/Aurora) caching.** Don't cross them.
11. **WAF attaches to CloudFront/ALB/API Gateway/AppSync/Cognito — NOT NLB.**
12. **Apex/root domain → Route 53 Alias (free); CNAME is illegal at the apex.**
13. **Avoid legacy/deprecated answers:** NAT Instance, Classic LB, Launch Configuration, OAI, Aurora Multi-Master, standalone Glacier, Cognito Sync, App Mesh (for new designs).
14. **Spot = interruptible/batch (≤90% off); RI/Savings Plans = steady 24/7 (≤72%); On-Demand = unpredictable short-term; Dedicated Host = licensing/compliance.**
15. **GuardDuty = threats; Inspector = vulnerabilities/CVEs; Macie = sensitive data/PII; Security Hub = aggregator/CSPM; Detective = root-cause; CloudTrail = API audit; Config = resource compliance.**
16. **For "encrypt + automatic key rotation + audit," choose SSE-KMS (customer-managed CMK), not SSE-S3.** SSE-S3 lacks per-use audit/control.
17. **Cognito = external app/customer identity; IAM Identity Center = workforce SSO across accounts.** User Pool = authentication; Identity Pool = AWS credentials.
18. **One NAT Gateway per AZ for HA; single NAT GW = SPOF + cross-AZ data charges.** Same logic: a single-AZ anything is not HA.
19. **Decouple to scale independently:** SQS/SNS/EventBridge between tiers; buffer spikes; make consumers idempotent (at-least-once delivery).
20. **Match the qualifier to the strategy tier:** Backup&Restore (RTO hours, cheapest) → Pilot Light (tens of min) → Warm Standby (minutes) → Multi-Site Active/Active (~0, costliest). Read the RPO/RTO words before choosing.