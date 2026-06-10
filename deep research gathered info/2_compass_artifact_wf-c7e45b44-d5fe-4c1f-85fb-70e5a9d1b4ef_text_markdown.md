# SAA-C03 exam-accurate topic and subtopic map

The SAA-C03 exam is **less about knowing services and more about pattern-matching trigger phrases to decision points**. Across 600+ candidate-reported angles synthesized from r/AWSCertifications pass posts, ExamTopics community discussions, Tutorials Dojo cheat sheets, and Medium pass stories from 2024-2025, the same ~80 decision points recur repeatedly. The exam weights Domain 1 (Secure Architectures) at 30% and Domain 2 (Resilient Architectures) at 26%, so **IAM, S3, VPC, RDS/Aurora, and DR patterns dominate** — together they represent roughly 35-45 of the 65 questions on most exam forms.

This map gives you, for every service area in scope, the **specific subtopics that have actually appeared**, the **exam angle being tested** (the trick or distractor, not a description), and a **frequency rating** based on candidate convergence. New C03 items vs C02 — Network Firewall, Security Hub, IAM Identity Center, Multi-AZ DB Cluster, Aurora Serverless v2, ElastiCache Serverless, Glue/Lake Formation, OpenSearch, Redshift Serverless, AWS DRS, DataSync, FSx variants, Global Accelerator, SnapStart — are flagged with ⭐ throughout.

**Frequency legend:** **HIGH** = appears in nearly every exam form (1+ questions); **MED** = appears commonly but rotates; **LOW** = occasional/distractor; **UC** = use-case recognition only.

---

## Section 1: IAM and identity (10-15 questions, HIGHEST density)

| Subtopic | Exam angle / decision point | Freq |
|---|---|---|
| IAM roles for EC2 (instance profile) | "App on EC2 needs S3" → role via instance profile, **never access keys**. Almost always the answer when EC2 needs an AWS service. | HIGH |
| Lambda execution role / ECS task role | ECS: **task role** = app's AWS perms; **execution role** = ECS agent (pull ECR, write logs). Distractor pair tested constantly. | HIGH |
| Policy evaluation order | **Explicit Deny > SCP > Permission Boundary > Identity policy > Resource policy**. Default = implicit deny. SCP never grants — only caps. | HIGH |
| Cross-account via STS AssumeRole | Account A creates role with **trust policy** for Account B; B calls `sts:AssumeRole`. Use **ExternalID** for 3rd-party "confused deputy" protection. | HIGH |
| Resource-based policies | S3 bucket policy, KMS key policy, Lambda, SNS, SQS, ECR, Secrets Manager. Cross-account: **both** identity AND resource policy must allow. KMS key policy is **mandatory** — without root statement, key is unmanageable. | HIGH |
| Permission boundaries | "Allow developers to create IAM roles but cap their permissions" → permission boundary. Never grants — only ceilings. | MED |
| ABAC / session tags | "Scale access without creating many roles" / "engineers access resources tagged with their project" → ABAC with `aws:PrincipalTag` + `aws:ResourceTag`. | MED |
| ⭐ IAM Identity Center (formerly SSO) | "Centralized corporate directory for many AWS accounts" → Organizations + IAM Identity Center. **NOT Cognito** — Cognito is for app end-users. Top trap. | HIGH |
| ⭐ IAM Access Analyzer | "Identify resources shared with external accounts" or "generate least-privilege policy from CloudTrail" → Access Analyzer. | MED |
| SAML 2.0 federation (AssumeRoleWithSAML) | "On-prem AD users to AWS console" → ADFS/SAML IdP + AssumeRoleWithSAML, OR IAM Identity Center as front door. | MED |
| Web identity federation | Cognito Identity Pool exchanges Google/FB/Apple/SAML token for temp AWS creds via STS. | MED |
| MFA-protected API | `aws:MultiFactorAuthPresent` condition. **SCP denying actions when MFA absent** = canonical org-wide answer. | MED |
| Policy condition keys | `aws:PrincipalOrgID` (org-only), `aws:SourceVpce`/`aws:SourceVpc` (VPC-only), `aws:SourceIp` (IP allowlist), `aws:SecureTransport` (force HTTPS). Heavy in S3 bucket-policy questions. | HIGH |
| STS session length | Default 1h, max 12h; chained calls capped at 1h. | MED |
| Hybrid: no IAM role on on-prem | Use **SSM Hybrid Activations** or **IAM Roles Anywhere**. Cannot attach IAM role directly to on-prem servers. | LOW |

---

## Section 2: S3 (one of the top three tested services)

S3 appears in **all four exam domains**. Master the storage-class decision tree, encryption variants, access-control modernization (OAC over OAI, ACLs disabled), and pre-signed URLs vs CloudFront signed URLs.

### Storage classes — the decision-point distractors

| Class | Exam trigger phrase | Trap |
|---|---|---|
| **Standard-IA** | "infrequently accessed but needs millisecond access" | Wrong if access <1×/quarter (Glacier Instant Retrieval cheaper) |
| **One Zone-IA** | "re-creatable / thumbnails / secondary copy" | Wrong for compliance/medical (single AZ = data loss risk) |
| **Intelligent-Tiering** | **"unknown / unpredictable / changing access pattern"** ONLY | Wrong if pattern IS known (monitoring fee waste) |
| **Glacier Instant Retrieval** | "long-lived archive accessed ~once/quarter, ms retrieval" | 90-day minimum |
| **Glacier Flexible Retrieval** | "minutes-to-hours retrieval acceptable, large bulk fetches" | 90-day minimum |
| **Glacier Deep Archive** | "7-10 years / regulatory / 12+ hours retrieval OK" | Always cheapest archive answer |

**Storage-class minimum durations** (30/30/30/90/90/180): a lifecycle rule transitioning Standard → IA before 30 days is **invalid** — common distractor.

### S3 — high-density tested subtopics

| Subtopic | Exam angle | Freq |
|---|---|---|
| Versioning + MFA Delete | "Extra protection from accidental deletion" → versioning. **MFA Delete** only enabled by **root via CLI** — IAM with MFA condition is the wrong answer. | HIGH |
| Object Lock — **Compliance mode** | "WORM / SEC 17a-4 / FINRA / **even root cannot delete**" → Compliance mode (not Governance). | HIGH |
| Object Lock — Governance mode | "Most users blocked but admins with `s3:BypassGovernanceRetention` can override" → Governance. | HIGH |
| Object Lock requires versioning **at bucket creation** | Enabling versioning later is not enough — bucket must be created with Object Lock enabled. | MED |
| **CRR / SRR** | CRR for DR/compliance/global readers. Versioning required on both ends. | HIGH |
| Replication Time Control (RTC) | "15-minute replication SLA" → RTC. | MED |
| **S3 Batch Replication for existing objects** | Default replication only applies to NEW objects. "Replicate existing objects" → S3 Batch Replication / Batch Operations Copy. Common trap. | MED |
| **SSE-KMS vs SSE-S3** | "Audit key usage / control over keys / rotate" → SSE-KMS. SSE-S3 has no audit trail. Watch for KMS TPS bottleneck on high-volume traffic. | HIGH |
| **S3 Bucket Keys** | "Reduce KMS request costs" → Bucket Keys (only with SSE-KMS). | MED |
| **Default encryption + bucket policy** | "Enforce encryption on every upload" → bucket policy `Deny` on `s3:PutObject` lacking `x-amz-server-side-encryption` header. Default encryption alone is not enough to enforce. | MED |
| Force HTTPS | Bucket policy with `aws:SecureTransport: false` deny. | MED |
| **ACLs disabled (Bucket Owner Enforced)** | Default for new buckets since Apr 2023. **Legacy ACL-based answers are usually WRONG** in 2024-2025 questions. | MED |
| Block Public Access (BPA) | **Overrides bucket policies** allowing public access. The "ensure no accidental public exposure" answer. | HIGH |
| **`aws:PrincipalOrgID` condition** | "Restrict bucket to AWS Organization with LEAST overhead" → bucket policy condition. Distractor: tagging individual users. | HIGH |
| Access Points / Multi-Region Access Points | MRAP for "global users, single endpoint, automatic failover" + CRR active-active. Distractor: Route 53 latency routing (uses public internet). | MED |
| **Pre-signed URLs** | "Temporary access without IAM" → pre-signed URL. Inherits signer's permissions. **Sign with IAM user, not role** (role's STS session expires before 7-day URL). | HIGH |
| **CloudFront Signed URL vs Cookie** | URL = single file. **Cookie = many files / HLS streaming / subscribers area**. | MED |
| **OAC vs OAI** | OAC is modern; supports SSE-KMS, opt-in regions, PUT/DELETE, SigV4. OAI is legacy but still appears as correct in older question pools. **When both options appear, choose OAC.** | HIGH |
| **Gateway Endpoint for S3** | "EC2 in private subnet needs S3, no internet" → **free Gateway Endpoint**. Interface endpoint for S3 only when on-prem needs private S3 access via DX. | HIGH |
| Multipart Upload + Transfer Acceleration | "Long-distance large-file uploads" → both together. Distractor: Global Accelerator (does not optimize S3 uploads). | HIGH |
| **Prefix-based parallelism** | 3,500 PUT / 5,500 GET per prefix per second. "Increase request rate" → spread across more prefixes. Transfer Acceleration is a wrong answer here. | HIGH |
| S3 Select | "Filter portion of single CSV/JSON object server-side." Distractor: Athena (multi-object, full SQL). | MED |
| Event notifications | Destinations: SNS, SQS Standard (NOT FIFO directly), Lambda, EventBridge. **EventBridge for content-based filtering and multiple targets**. | MED |
| Storage Lens | "Identify all buckets without versioning across org" → Storage Lens. | MED |
| S3 Batch Operations | "Re-encrypt millions of existing objects" / "restore millions from Glacier" → Batch Operations. | MED |

---

## Section 3: VPC and core networking (~6-8 questions)

Networking decision-points dominate. Key recurring traps: **NAT Gateway must be per-AZ for HA**; **WAF cannot attach to NLB**; **ACM cert for CloudFront must be in us-east-1**; **OAC over OAI**; **Gateway over Interface endpoint for S3**.

| Subtopic | Exam angle | Freq |
|---|---|---|
| NAT Gateway AZ resilience | **Zonal — one per AZ + each private subnet routes to NAT GW in its OWN AZ**. Single NAT GW for all AZs = SPOF + cross-AZ data charges. Frequent wrong answer. | HIGH |
| NAT GW data-processing cost trap | For S3/DynamoDB traffic from private subnets, **replace NAT egress with Gateway VPC Endpoint** to eliminate per-GB NAT charges. | HIGH |
| Egress-only IGW | **IPv6 equivalent of NAT Gateway** — outbound only. | MED |
| Security Groups vs NACLs | SG = stateful, allow-only, references SGs by ID. NACL = stateless, **supports DENY**, ephemeral ports must be explicit. **"Block specific malicious IP" → NACL**. **"Allow tier A → tier B" → SG referencing SG**. | HIGH |
| Gateway VPC Endpoint | **S3 + DynamoDB only, free**, route-table entry. **Not accessible from on-prem/peered VPCs/TGW** — major exam trap. | HIGH |
| Interface VPC Endpoint (PrivateLink) | All other AWS services. ENI with private IP, hourly + per-GB. **Accessible from on-prem via DX/VPN** — key differentiator. | HIGH |
| VPC Peering | **Non-transitive**, no overlapping CIDRs. Cross-region/account supported. | HIGH |
| **Transit Gateway** | "3+ VPCs OR transitive routing OR centralize VPN/DX" → TGW. Mesh peering at scale = wrong answer. **TGW + DX Gateway** = standard hybrid pattern. | HIGH |
| Site-to-Site VPN | IPsec over public internet, two tunnels for HA, **encrypted by default**. | MED |
| Direct Connect | Dedicated fiber, **NOT encrypted by default**. Lead time = weeks/months → eliminate when "immediately/soon" appears. | MED |
| DX VIFs | **Private** (one VPC), **Public** (S3/DynamoDB public endpoints), **Transit** (DX Gateway → TGW → multi-region VPCs). | MED |
| DX encryption | (1) **VPN over DX public VIF** (IPsec on top, common answer), or (2) **MACsec** on supported 10/100 Gbps ports. | MED |
| PrivateLink endpoint services | Provider creates **NLB-fronted endpoint service**; consumer creates Interface Endpoint. Used to expose SaaS without VPC peering / CIDR overlap. | MED |
| VPC Flow Logs | At VPC, subnet, or ENI level. Destinations: CloudWatch Logs, S3, Firehose. Metadata only — no packet contents. | MED |
| ⭐ AWS Network Firewall | "Stateful intrusion prevention," "Suricata-compatible rules," "domain-based filtering," "centralized inspection VPC." Different from SG (instance) and WAF (L7). | MED |
| AWS WAF | Attaches to **CloudFront, ALB, API Gateway, AppSync, Cognito** — **NOT NLB**. Managed rule groups, rate-based rules, IP/geo/string match. | HIGH |
| Shield Standard vs Advanced | Standard = free auto L3/L4. Advanced = $3K/mo, **DRT 24/7**, cost protection, advanced reporting. "Large sophisticated DDoS" → Advanced. | MED |
| Firewall Manager | Org-wide policy management for WAF, Shield Advanced, Network Firewall, SGs, Route 53 DNS Firewall. **Per-Region** — cannot span regions. | MED |
| ⭐ IPv6 / BYOIP | Egress-only IGW for v6 outbound. BYOIP for "preserve existing IP whitelisting." | LOW |

---

## Section 4: Route 53, CloudFront, Global Accelerator

The most-confused trio per candidate reports. **CloudFront = HTTP cacheable; Global Accelerator = TCP/UDP non-HTTP with static IPs; Route 53 = DNS-layer routing**.

### Route 53 routing policies

| Policy | When tested | Trap |
|---|---|---|
| **Latency** | "Best/lowest latency" + multi-region | Different from Geolocation |
| **Geolocation** | "Users in Germany must be served from EU" / compliance / regional content | Default record needed for unmatched locations |
| **Geoproximity** | "Bias N% traffic toward region Y" | Requires Traffic Flow |
| **Failover** | Active-passive DR | Requires health check on primary |
| **Multi-value answer** | "Return multiple healthy IPs" | Not a substitute for ELB |
| **Weighted** | Blue/green, canary, A/B | Set weight 0 = drain |

**Alias vs CNAME:** Alias = AWS targets only, free queries, **works at zone apex** (root domain). CNAME = any DNS, charged, **NOT allowed at zone apex**. Question with `example.com` (no www) → Alias.

**Hybrid DNS:** Inbound endpoint (on-prem → AWS resolves private hosted zones) + Outbound endpoint (AWS → on-prem resolver via conditional forwarding).

### CloudFront

| Subtopic | Exam angle | Freq |
|---|---|---|
| **OAC vs OAI** | OAC is modern (supports SSE-KMS, all regions, dynamic methods). Pick OAC when both appear. | HIGH |
| Lambda@Edge vs CloudFront Functions | **Functions** = JS only, sub-ms, no network/file I/O, header rewrites. **Lambda@Edge** = Node/Python, network access, image resize, dynamic origin selection. | MED |
| Field-level encryption | Encrypt specific PII fields (CC#) at edge — only certain backend apps with private key can decrypt. | MED |
| Origin failover (Origin Groups) | Primary + secondary origin; failover on configured 4xx/5xx. **Only GET/HEAD/OPTIONS** — not transactional. | MED |
| **ACM cert region trap** | **CloudFront ACM certs MUST be in us-east-1.** ALB/NLB certs in same region as LB. Frequent distractor. | MED |
| WAF on CloudFront | Standard pattern: CF + WAF + Shield Advanced for global app security. | HIGH |

### Global Accelerator (NEW C03 emphasis)

| Subtopic | Exam angle | Freq |
|---|---|---|
| Static anycast IPs | **Client whitelist requires fixed IPs** → GA. CloudFront has no static IPs. | HIGH |
| TCP/UDP non-HTTP | **Gaming (UDP), IoT (MQTT), VoIP, SIP** → GA. | HIGH |
| Sub-minute regional failover | **Bypasses DNS cache** — faster than Route 53 failover. | HIGH |
| Endpoints | ALB, NLB, EC2, EIPs (NOT S3, NOT CloudFront). | MED |
| **GA vs CloudFront** | CF = HTTP/cacheable. GA = TCP/UDP non-HTTP, static IPs, deterministic regional failover. Both use AWS backbone + Shield Standard. | HIGH |

---

## Section 5: Load balancers (ALB, NLB, GWLB)

| Subtopic | Exam angle | Freq |
|---|---|---|
| ALB host/path-based routing | "/api/* → service A, /web/* → service B" or `api.example.com` vs `www.example.com`. Microservices/ECS pattern. | HIGH |
| ALB Lambda targets | Alternative to API Gateway for HTTP-triggered Lambda. | MED |
| ALB Cognito auth | "Authenticate users at LB before backend" → ALB + Cognito user pool. | MED |
| **NLB static IP / EIP** | **Only ELB with static IPs** — "client whitelist requires fixed IP" or "expose static IP to on-prem." | HIGH |
| NLB source IP preservation | Targets see actual client IP (instance targets preserve; IP targets may need proxy protocol v2). ALB always uses X-Forwarded-For. | MED |
| NLB UDP support | Gaming, DNS, SIP. ALB cannot do UDP. | MED |
| GWLB | **GENEVE port 6081** — inline 3rd-party firewalls/IDS/IPS. Pattern: GWLB endpoint in spoke VPC routes to inspection VPC with appliance fleet. | MED |
| **Cross-zone load balancing** | **ALB: enabled by default, free.** **NLB & GWLB: disabled by default, charged when enabled** (cross-AZ data transfer). Major trap. | HIGH |
| Sticky sessions vs ElastiCache | "MOST scalable" → **store session in ElastiCache/Redis or DynamoDB**, not stickiness. Sticky is the anti-pattern answer when scalability emphasized. | HIGH |
| **WAF on NLB trap** | **WAF cannot attach to NLB.** Pattern: protect NLB with **Shield Advanced** (L3/L4); protect ALB/API GW behind it with **WAF** (L7). | MED |
| ALB-as-NLB-target | Combine NLB static IP + ALB L7 routing by registering ALB as NLB target. | MED |

---

## Section 6: EC2, ASG, and compute pricing

### Pricing model decision tree

| Phrase in question | Pick |
|---|---|
| "Predictable steady-state, EC2 only" | Standard RI or **EC2 Instance Savings Plan** |
| "Predictable, mix of EC2+Fargate+Lambda" | **Compute Savings Plan** (covers all three) |
| "Fault-tolerant, interruptible, cheapest" | Spot (EC2 or Fargate Spot) |
| "BYOL Windows/Oracle/SQL Server" | Dedicated Host |
| "Reserve capacity in specific AZ, no long-term commit" | On-Demand Capacity Reservation |
| "Guaranteed GPU for training run" | ⭐ Capacity Blocks for ML |

**Note:** Spot Blocks are effectively deprecated — do **not** pick them on C03.

### EC2 — high-frequency angles

| Subtopic | Exam angle | Freq |
|---|---|---|
| Instance family mapping | M=general, C=compute, R/X=memory, I/D=storage, P/G/Inf/Trn=accelerator, T=burstable. T-family is wrong for sustained CPU. | HIGH |
| Placement groups | **Cluster** = HPC/low-latency + EFA. **Spread** = critical instances isolated from HW failure. **Partition** = HDFS/Hadoop/Cassandra/Kafka. | HIGH |
| **EFA (Elastic Fabric Adapter)** ⭐ | "ML inter-instance comm" / "tightly coupled HPC" → EFA. Plain ENI = wrong. | MED |
| ⭐ gp3 over gp2 | Default modern answer — cheaper than gp2 with same/better perf, decoupled IOPS from size. | HIGH |
| io2 over io1 | Same price, 100x durability. Use io2 Block Express for SAP HANA/Oracle (256k IOPS). | HIGH |
| EBS Multi-Attach (io1/io2) | **Same AZ only**, ≤16 instances, **cluster-aware FS required**. "Shared block for HA cluster app same AZ." | MED |
| Hibernation | "Preserve in-memory state across stop/start" → hibernation (RAM saved to encrypted EBS root). | MED |
| IMDSv2 | Session-based metadata — picked for SSRF mitigation. | MED |

### Auto Scaling

| Subtopic | Exam angle | Freq |
|---|---|---|
| Launch Templates over Launch Configs | **Always pick Launch Templates** on C03. Launch Configs are legacy/distractor. | HIGH |
| Target Tracking | Default modern answer when "maintain target utilization." | HIGH |
| Scale on **SQS queue depth** | Custom metric: `ApproximateNumberOfMessagesVisible` or **Backlog per Instance** target tracking. NOT CPU/memory. | HIGH |
| Lifecycle hooks | "Run config script before in-service" / "drain connections before termination" → lifecycle hook + Lambda via EventBridge. | MED |
| EC2 vs ELB health checks | "App-level errors not detected" → enable **ELB health checks** on ASG. | HIGH |
| Mixed Instances Policy | "Cost-effective resilient ASG" → On-Demand baseline + Spot for burst across multiple instance types. | HIGH |
| Warm pools | "Slow-booting AMI / app initializes slowly, faster scale-out" → warm pools. | MED |

---

## Section 7: Lambda and API Gateway

| Subtopic | Exam angle | Freq |
|---|---|---|
| Memory–CPU coupling | CPU scales with memory (up to 10 GB). **CPU-intensive function** → increase memory → faster + often cheaper. | HIGH |
| 15-min max timeout | Workload >15 min → **NOT Lambda**. Use ECS, Fargate, Step Functions, Batch. Common eliminator. | HIGH |
| **Reserved concurrency** | Caps and reserves, free. **Protect downstream RDS** from being overwhelmed; guarantee critical function capacity. | HIGH |
| **Provisioned concurrency** | Pre-initialized envs, costs $$. "Cold start latency unacceptable + predictable spike." | HIGH |
| ⭐ **SnapStart** | "Java + reduce cold starts + MOST cost-effective" → SnapStart (free), not Provisioned Concurrency. Now extends to Python and .NET. | MED |
| VPC Lambda | Hyperplane ENIs — no longer slow. ENI exhaustion = subnet IP space issue. | HIGH |
| **Lambda + RDS** | "Connection storms" / "reduce failover impact" → **RDS Proxy**. | HIGH |
| Lambda Destinations vs DLQ | **Destinations** (SQS/SNS/Lambda/EventBridge) modern; DLQ legacy. Destinations preferred on C03. | MED |
| Execution role vs resource policy | "Lambda needs S3 access — most secure" → IAM execution role, NOT embedded keys. | HIGH |
| /tmp 10 GB ephemeral | "Larger working storage" without EFS — increase /tmp. | LOW |

### API Gateway

| Subtopic | Exam angle | Freq |
|---|---|---|
| REST vs HTTP vs WebSocket | HTTP API = cheaper, fewer features (no caching, usage plans, API keys, validation). REST = full features. | MED |
| Cognito User Pool authorizer | "Cognito users + REST API + LEAST operational overhead" → Cognito authorizer (NOT Lambda authorizer). | HIGH |
| API keys + Usage plans | "3rd-party developers, quota per partner" → API key + usage plan. | HIGH |
| Edge-Optimized vs Regional vs Private | "Global users, lowest latency" → Edge-Optimized (CloudFront-fronted). "Same region or own CF control" → Regional. "VPC-only" → Private + Interface Endpoint. | HIGH |
| API GW + SQS direct integration | "FIFO ordering for orders" → API GW → SQS FIFO → Lambda. No Lambda in middle. | HIGH |

---

## Section 8: ECS, EKS, Fargate

**Decision rule:** "No infrastructure to manage" + containers + no K8s requirement → **ECS on Fargate**. Pick EKS only when "Kubernetes" or "K8s API/portability" is explicitly required.

| Subtopic | Exam angle | Freq |
|---|---|---|
| Fargate launch type | Default modern container answer on C03 when "minimal operational overhead" + containers. | HIGH |
| **Task Role vs Execution Role** | Task role = app's AWS perms (e.g., S3 access). Execution role = ECS agent (pull ECR, write logs). Distractor pair. | HIGH |
| Capacity Providers | Mix Fargate + Fargate Spot + EC2 + EC2 Spot. "24/7 HA + burst cost optimization" → Fargate steady + **Fargate Spot** for burst. | HIGH |
| Service Auto Scaling | Target tracking on CPU/mem/ALBRequestCountPerTarget/SQS via CloudWatch. | HIGH |
| ALB dynamic port mapping | "Multiple replicas of same task on one EC2 host." | MED |
| awsvpc network mode | Each task gets own ENI + SG (required for Fargate). | MED |
| ⭐ ECS Anywhere | "ECS-managed containers in cloud + on-prem in single solution" → Fargate (cloud) + ECS Anywhere (on-prem). | MED |
| EFS on Fargate task | "Containers need persistent shared file store with OS-level perms, fully managed" → ECS Fargate + EFS. | HIGH |
| EKS — IRSA / Pod Identity | "Most secure way to give pods AWS perms" → **IRSA** (or newer **Pod Identity**), NOT node instance role. | MED |
| EKS Fargate profiles | "Kubernetes + no node management." | MED |

---

## Section 9: Databases (4-8 RDS questions, 4-7 DynamoDB)

### RDS — the critical traps

| Subtopic | Exam angle | Freq |
|---|---|---|
| **Multi-AZ standby is NOT readable** | Multi-AZ = HA only. **For read scaling use Read Replicas.** "Use the standby for reads" = always wrong. | HIGH |
| Read Replicas | Async, up to 15, promotable, cross-region (max 5 cross-region per primary). | HIGH |
| ⭐ **Multi-AZ DB Cluster** (1 writer + 2 readable standbys) | New in C03. "MySQL/PG + HA + extra read capacity + lower write latency" → Multi-AZ DB Cluster (NOT classic Multi-AZ). MySQL/PostgreSQL only. ~35s failover. | HIGH (newer) |
| **Encryption at rest** | **Cannot encrypt existing unencrypted instance directly.** Workaround: snapshot → copy snapshot **with encryption enabled** → restore. | HIGH |
| **RDS Proxy** | "Lambda + frequent connections / connection storms" → RDS Proxy. Also reduces failover time perceived by app. | HIGH |
| IAM database authentication | MySQL & PostgreSQL only. Often paired with RDS Proxy. | MED |
| Cross-account encrypted snapshot share | Must use **customer-managed CMK** (default `aws/rds` key cannot be shared) + add target account to KMS key policy. | MED |
| Storage Auto Scaling | "DB storage growing unpredictably, avoid downtime" → enable Storage Auto Scaling. | MED |
| Engine choice vs Aurora | Aurora supports MySQL/PG only. **"Lift-and-shift Oracle/SQL Server with minimal refactoring" → RDS for that engine**. | HIGH |

### Aurora

| Subtopic | Exam angle | Freq |
|---|---|---|
| 6 copies across 3 AZs, self-healing | Highest durability/auto-recovery for relational. | MED |
| Aurora Replicas | Up to 15, sub-100ms lag, ~30s failover. **Read scaling for MySQL/PG with fastest failover** → Aurora over RDS Read Replicas. | HIGH |
| Aurora endpoints | Writer / **Reader (load-balanced reads)** / **Custom (specific replica group, e.g., reporting)** / Instance. | MED |
| **Aurora Global Database** | **"<1 second cross-region replication," "RPO ~1s, RTO <1 min," "global low-latency reads"** → Aurora Global Database. NOT cross-region Read Replica, NOT DynamoDB Global Tables. | HIGH |
| ⭐ **Aurora Serverless v2** | Instant ACU scaling, full feature parity, no v1 cold pauses. "Unpredictable/spiky relational, dev/test, infrequent runs" → Serverless v2. Replaces v1 in answers. | HIGH (newer) |
| Backtrack | **MySQL only**, in-place rewind up to 72h. PostgreSQL Aurora must use PITR. | LOW |
| Cloning | Instant copy-on-write same-region — for dev/staging. | LOW |

### DynamoDB

| Subtopic | Exam angle | Freq |
|---|---|---|
| **On-Demand vs Provisioned** | "Unpredictable / spiky / sudden bursts" → On-Demand. "Predictable steady" → Provisioned + Auto Scaling. | HIGH |
| **LSI vs GSI** | LSI = same partition key, **must be created at table creation**, max 5. GSI = different keys, can be added anytime, max 20. **"New query pattern on existing table" → GSI** (LSI can't be added later). | HIGH |
| **Global Tables** | "Multi-region active-active writes, NoSQL" → Global Tables. Requires Streams enabled. | HIGH |
| **DAX** | "Microsecond DynamoDB reads, no app code changes" → DAX (DDB-API compatible). ElastiCache requires app changes. | HIGH |
| TTL | "Auto-expire items at no extra cost" → TTL (no WCU consumed). NOT a Lambda cleanup job. | HIGH |
| PITR | Continuous backup, restore to any second in last 35 days. For >35 days → on-demand backups. | MED |
| Streams | 24-hr retention, Lambda trigger; **prerequisite for Global Tables**. | HIGH |
| Item size 400 KB | Larger payloads → store in S3, reference key in DDB. | MED |
| Hot partitions | Adaptive capacity helps but not the design fix — **redesign partition key for higher cardinality** (write sharding). | MED |
| Export to S3 | Run Athena analytics on DDB data without impacting prod. Requires PITR enabled. | LOW |

### ElastiCache

| Subtopic | Exam angle | Freq |
|---|---|---|
| Redis vs Memcached | **Redis** = persistence, replication, Multi-AZ, pub/sub, sorted sets, transactions. **Memcached** = simple, multi-threaded, no persistence. "Leaderboard / pub-sub" → Redis. | HIGH |
| **Session store** | "Users lose sessions when ALB routes to different instance" / "make app stateless" → ElastiCache Redis as session store. **Sticky sessions = wrong distractor** when scalability emphasized. | HIGH |
| Cluster mode enabled | Sharding for "scale write throughput / dataset > one node memory." | MED |
| Caching strategies | Lazy loading (cache-aside) vs write-through. | MED |
| Encryption | Redis: in-transit + at-rest. Memcached: neither. PCI/HIPAA → Redis. | MED |
| ⭐ ElastiCache Serverless | "No capacity planning, spiky cache traffic." | MED (newer) |
| MemoryDB vs ElastiCache | MemoryDB = primary durable Redis-compatible DB. ElastiCache = cache. | LOW |

---

## Section 10: Messaging and streaming

### SQS / SNS / EventBridge / Kinesis decision matrix

| Trigger phrase | Pick |
|---|---|
| Decouple producer/consumer, buffer load | **SQS Standard** |
| **Order preserved / exactly-once / no duplicates** | **SQS FIFO** (or FIFO SNS + FIFO SQS) |
| ASG scaling on backlog | SQS + ASG target tracking on backlog/instance |
| Fan-out single event to many durable consumers | **SNS → multiple SQS** |
| Push to email/SMS/mobile/HTTP | **SNS** |
| Content-based filtering, SaaS source, schedule, archive/replay | **EventBridge** |
| Real-time, multiple consumers, replay, per-key ordering, custom processing | **Kinesis Data Streams** (+ Enhanced Fan-Out for many consumers) |
| Stream → S3/Redshift/OpenSearch with **least operational overhead, near-real-time** | **Kinesis Data Firehose** |
| Existing Kafka clients / migrate on-prem Kafka | ⭐ **Amazon MSK** |
| Multi-step workflow with retries, branching, long-running | **Step Functions Standard** |
| Lift-and-shift JMS/AMQP/MQTT app | **Amazon MQ** (NOT SQS/SNS) |

### SQS — recurring traps

| Subtopic | Exam angle | Freq |
|---|---|---|
| Visibility timeout | Default 30s, max 12h. **Must be ≥ 6× Lambda timeout** to prevent duplicate processing. | HIGH |
| Long polling (1-20s) | "Reduce empty receives / reduce SQS API costs" → long polling. | HIGH |
| Dead-letter queue | Configured on **source queue** with `maxReceiveCount`. Same type only (Std↔Std, FIFO↔FIFO). | HIGH |
| Retention | Default 4 days, max 14 days. If consumer offline >14 days, SQS is wrong. | HIGH |
| Delay queues | Up to 15 min. >15 min → Step Functions Wait or EventBridge Scheduler. | MED |
| 256 KB message size | Larger payloads → SQS Extended Client Library + S3. | MED |
| API GW → SQS → Lambda | "Burst traffic, DB can't keep up, no lost orders" → buffer with SQS. | HIGH |

### Kinesis

| Subtopic | Exam angle | Freq |
|---|---|---|
| Shard limits | 1 MB/s write or 1,000 records/s; 2 MB/s shared read. Throttling → re-shard. | HIGH |
| Retention | Default 24h, extended to 7 days, long-term to 365 days. **"Consumer reads every 2 days, data missing" → increase retention** (NOT add shards). | HIGH |
| Enhanced Fan-Out | Dedicated 2 MB/s per consumer, ~70ms latency. "Multiple consumers same stream simultaneously" → EFO. | HIGH |
| Firehose vs Streams | Firehose = managed delivery, no consumer code, near-real-time, no shards. Streams = custom processing, multiple consumers, replay. | HIGH |
| Firehose ≠ DynamoDB destination | Trap: Firehose does NOT write to DDB. Use Streams + Lambda. | MED |
| ⭐ Firehose to OpenSearch | "Stream CW Logs / app logs to OpenSearch with least ops" → CW Logs subscription → Firehose → OpenSearch. | HIGH |

### EventBridge — increasing emphasis

| Subtopic | Exam angle | Freq |
|---|---|---|
| Rules — event pattern matching | Beats SNS for content-based routing. | HIGH |
| ⭐ EventBridge Scheduler | Cron jobs >15 min → **Scheduler + Fargate RunTask** (Lambda's 15-min limit doesn't apply). | MED |
| Targets breadth | 20+ targets including ECS RunTask, Step Functions, Kinesis, API destinations. | HIGH |
| Partner/SaaS event bus | "Integrate Zendesk/Datadog/PagerDuty" → EventBridge (NOT SNS). | MED |
| ⭐ EventBridge Pipes | Point-to-point with optional filter/transform/enrich. Replaces glue Lambdas. | LOW |
| EventBridge vs SNS decision | EventBridge = filter on content/schema/SaaS/schedule/replay. SNS = simple high-throughput pub/sub fan-out, mobile push, SMS. | HIGH |

---

## Section 11: Encryption and secrets

| Subtopic | Exam angle | Freq |
|---|---|---|
| Customer-managed CMK | "Audit key usage / control / rotate" → customer-managed CMK. AWS-managed keys cannot have edited policies. | HIGH |
| Key policy is **mandatory** | Without root statement, key is unmanageable. IAM policies alone cannot grant KMS access — key policy must allow. | HIGH |
| Cross-region encrypted snapshot copy | Must **re-encrypt with destination region KMS key**. | MED |
| ⭐ Multi-Region keys | "Encrypt and replicate without re-encrypting on read" → multi-Region KMS keys. Used with DynamoDB Global Tables, S3 CRR. | MED |
| Envelope encryption / GenerateDataKey | KMS encrypts up to 4KB; for larger data, service uses data key returned by GenerateDataKey, stores encrypted DEK alongside data. | MED |
| **CloudHSM** | **"FIPS 140-2 Level 3," "dedicated hardware," "single-tenant"** — only then. Otherwise KMS. | UC |
| CloudHSM custom key store | "KMS API + own hardware" → KMS custom key store backed by CloudHSM. | LOW |
| **Secrets Manager vs Parameter Store** | Secrets Manager has **native rotation** for RDS/Aurora/Redshift/DocumentDB. Parameter Store Standard tier = **free**. "Auto-rotate DB credentials" → Secrets Manager. "Cost-effective config" → Parameter Store. | HIGH |
| Secrets Manager cross-region replication | DR for secrets — Parameter Store does not support this. | MED |
| Hardcoded credentials in code | Always wrong. Replace with Secrets Manager / Parameter Store + IAM role retrieval. | HIGH (as distractor) |
| ACM | Auto-renews **only ACM-issued public certs** (NOT imported). **Cannot be exported** (except Private CA). Used on ALB/NLB(TLS)/CloudFront/API GW — never directly on EC2. | HIGH |

---

## Section 12: Cognito

| Subtopic | Exam angle | Freq |
|---|---|---|
| User Pool = authentication (WHO) | "Authenticate web/mobile end users" → User Pool. Issues JWT. Supports MFA, social IdP, SAML. | HIGH |
| Identity Pool = AWS creds (WHAT they can access) | "App user uploads directly to S3 / calls DynamoDB" → Identity Pool exchanges JWT for IAM-role temp creds. | HIGH |
| API Gateway authorizer | Cognito User Pool authorizer = least ops for Cognito-authenticated REST APIs. | HIGH |
| ALB authentication | ALB offloads auth to Cognito or OIDC IdP before forwarding. | MED |
| **Cognito ≠ workforce SSO** | Cognito is for app users. **Workforce/employee SSO into AWS Console = IAM Identity Center**. Top trap. | HIGH |

---

## Section 13: Observability — CloudWatch, CloudTrail, Config

| Service | Distinction | Frequency |
|---|---|---|
| **CloudTrail** | WHO did WHAT API call | HIGH |
| **AWS Config** | WHAT did the resource look like over time + compliance | HIGH |
| **CloudWatch** | Performance metrics, logs, alarms | HIGH |

### CloudWatch

| Subtopic | Exam angle | Freq |
|---|---|---|
| **CloudWatch Agent** | "Memory, disk, swap" → Agent (default EC2 metrics do NOT include memory/disk). Also for on-prem hybrid monitoring. | HIGH |
| Detailed Monitoring | 1-min vs default 5-min. | HIGH |
| Subscription filters | Logs → Kinesis/Firehose/Lambda in near-real-time. **Logs → Firehose → OpenSearch** is the canonical least-ops pattern. | HIGH |
| Metric filters | Extract metric from log pattern (count "ERROR") → alarm. | MED |
| **Logs Insights vs Athena** | Logs in CW Logs → Insights. Logs in S3 (CloudTrail, ALB, VPC Flow) → Athena. | HIGH |
| Export logs to S3 | "Retain logs >2 years cheaply" → export + lifecycle to Glacier. | MED |
| Composite alarms | Reduce noisy alerts when multiple conditions. | LOW-MED |
| Cross-account observability | Single pane of glass across Org accounts. | LOW-MED |

### CloudTrail

| Subtopic | Exam angle | Freq |
|---|---|---|
| **Management vs Data events** | Mgmt events logged by default. **Data events (S3 object-level, Lambda Invoke, DDB) NOT logged by default — extra cost.** "Audit at all levels of stored data" → enable Data Events. | HIGH |
| Event History (free 90-day) vs Trail | History = console-only, 90 days, mgmt events only. Trail = permanent S3, custom retention, all event types. | HIGH |
| Organization Trail | Single trail in mgmt account covers all members; members can't disable. | HIGH |
| Log file integrity validation | SHA-256 + digital signing — proves no tampering. | MED |
| ⭐ CloudTrail Lake | SQL-queryable immutable event store, up to 7-yr retention, ingest non-AWS sources. | LOW-MED |
| "Who deleted X" | Always CloudTrail (NOT Config, NOT CloudWatch). | HIGH |
| Aurora/RDS DB logins NOT in CloudTrail | DB engine logs → CW Logs. | MED |

### AWS Config

| Subtopic | Exam angle | Freq |
|---|---|---|
| Configuration history | "What did this resource look like 30 days ago" → Config. | HIGH |
| Managed Config Rules | Continuous compliance checks (e.g., `s3-bucket-public-read-prohibited`, `encrypted-volumes`). | HIGH |
| **Auto-remediation via SSM Automation** | "Auto-encrypt unencrypted EBS when detected" → Config Rule + SSM Automation document. | HIGH |
| Aggregator | Multi-account/region single view via Organizations. | MED |
| Conformance Packs | YAML rule collections (HIPAA, PCI-DSS, CIS) deployed to org. | MED |
| **Detective vs Preventive** | Config detects AFTER creation. **Pair with SCP for prevention.** | MED |

---

## Section 14: Security services — GuardDuty, Inspector, Macie, Security Hub

The most-asked decision in this domain. Memorize verbatim:

| Service | Trigger phrase | Frequency |
|---|---|---|
| **GuardDuty** | **Active threats**: "compromised IAM creds," "crypto-mining," "communication with malicious IP," "automatically detect malicious activity" | HIGH |
| **Inspector** | **Vulnerabilities/CVEs**: "scan EC2/ECR images/Lambda for known vulnerabilities" | HIGH |
| **Macie** | **PII in S3**: "discover sensitive data," "find credit cards/SSN in S3" | UC |
| ⭐ **Security Hub** | **Aggregator**: "single pane of glass for security findings across accounts/regions" | HIGH |

| Subtopic | Exam angle | Freq |
|---|---|---|
| GuardDuty data sources | VPC Flow + CloudTrail (mgmt + S3 data) + DNS + EKS audit + RDS login + Lambda + Malware Protection. **Agentless.** | MED |
| GuardDuty + EventBridge | Findings → EventBridge → Lambda/SSM → isolate EC2 / disable IAM key. Auto-remediation pattern. | MED |
| ⭐ Inspector v2 (agentless via SSM) | New continuous architecture. Pair with **SSM Patch Manager** for detection + remediation. | MED |
| Macie ≠ Inspector ≠ GuardDuty | Common trap to use Macie for unencrypted EBS or threat detection. | HIGH (as trap) |
| Security Hub compliance standards | CIS, PCI DSS, AWS Foundational, NIST 800-53. | MED |
| Security Hub multi-account | Designate aggregation Region + delegated admin via Organizations. | MED |

---

## Section 15: Organizations, SCPs, Control Tower

| Subtopic | Exam angle | Freq |
|---|---|---|
| **SCPs cap, never grant** | SCP only restricts; identity/resource policies still need to allow. | HIGH |
| **SCP does NOT apply to management account** | Critical detail. Even SCP at root won't restrict the management/payer account. | HIGH (trap) |
| Tag policies vs SCPs | **Tag policies enforce ALLOWED VALUES** of tags. **SCPs enforce tag PRESENCE / prevent tag deletion.** | MED |
| ⭐ Control Tower | "Set up secure multi-account environment with guardrails quickly" → Control Tower. Account Factory, log archive + audit accounts. | MED |
| Control Tower controls | **Preventive = SCPs** (block API). **Detective = Config rules** (alert on drift). ⭐ **Proactive = CloudFormation Hooks** (validate before deploy). | MED |
| **AWS RAM** | "Share VPC subnet/TGW/Resolver rule across accounts" → RAM, NOT VPC peering. | MED |

---

## Section 16: Storage (non-S3) — EFS, FSx, Storage Gateway, DataSync

### EFS

| Subtopic | Exam angle | Freq |
|---|---|---|
| EFS = NFS, POSIX, multi-AZ | "Linux, multiple EC2 across AZs, POSIX, NFSv4" → EFS (not EBS, not FSx Windows). | HIGH |
| Throughput modes | **Elastic** for spiky/unpredictable. **Provisioned** when need >what file size allows. **Bursting** default. | MED |
| Storage classes + Lifecycle | Auto-tier files unaccessed for 30/60/90 days to IA → Archive. Cost-saving canonical. | HIGH |
| Sub-millisecond | EFS is millisecond-class. **"Sub-ms / HPC" → FSx for Lustre, NEVER EFS**. | HIGH |
| One mount target per AZ | Not per instance, not per VPC. | MED |
| ⭐ EFS Replication | Cross-region/AZ DR for file system. | LOW-MED |

### FSx — pick the right flavor

| Flavor | Trigger | Freq |
|---|---|---|
| **FSx for Windows** | SMB, AD integration, Windows ACLs, DFS, home directories | HIGH |
| **FSx for Lustre** | HPC, ML, sub-ms, parallel file system, **S3-integrated** (lazy load + write-back) | HIGH |
| **FSx for NetApp ONTAP** | Multi-protocol (SMB+NFS+iSCSI), ONTAP migration, snapshots/clones | MED |
| **FSx for OpenZFS** | NFS, snapshots, clones, ZFS migration | LOW |

### Storage Gateway

| Subtopic | Exam angle | Freq |
|---|---|---|
| **S3 File Gateway** | "On-prem app needs NFS/SMB, data in S3 long-term, local cache" | HIGH |
| Volume Gateway — Cached | Primary in S3, hot data cached on-prem; iSCSI block. | MED |
| Volume Gateway — Stored | Primary on-prem, async EBS-snapshot backup to S3. | MED |
| **Tape Gateway (VTL)** | "Replace LTO library, use existing Veeam/NetBackup" → Tape Gateway. | MED |

### DataSync ⭐ NEW C03 emphasis

| Subtopic | Exam angle | Freq |
|---|---|---|
| Bulk migration on-prem ↔ AWS | 10× faster than rsync/cp. Sources/targets: S3, EFS, all FSx variants. | HIGH |
| **DataSync vs Storage Gateway** | DataSync = one-shot/scheduled **migration**. SG = **ongoing hybrid access**. | HIGH |
| DataSync vs Snowball | <10-15 TB w/ bandwidth → DataSync. Tens of PB or no bandwidth → Snowball. | HIGH |
| DataSync to FSx Windows | Preserves NTFS ACLs and metadata. | MED |

### Snowball — recurring traps

| Subtopic | Exam angle | Freq |
|---|---|---|
| **Snowball lands in S3 only** | Cannot land directly in EFS, FSx, EBS, Glacier vault. Goes to S3 first then lifecycle/integrate. | MED |
| Calculate transfer time vs bandwidth | Staple math question — pick DataSync or Snowball based on deadline feasibility. | HIGH |

### AWS Backup

| Subtopic | Exam angle | Freq |
|---|---|---|
| Centralized service | EBS, EFS, RDS, Aurora, DDB, FSx, EC2 AMIs, Storage Gateway, S3, Neptune, DocDB, Redshift. "Single service to back up many AWS resources." | HIGH |
| Cross-region/cross-account copy | DR backups in second region; centralized backup account via Organizations. | HIGH |
| **Vault Lock — Compliance mode** | "Immutable backups, ransomware protection, SEC 17a-4 / FINRA / CFTC" → Vault Lock Compliance. Even root cannot delete after 72h cooling. | HIGH |

---

## Section 17: Disaster recovery patterns

| Pattern | RTO/RPO | When picked | Freq |
|---|---|---|---|
| **Backup & Restore** | Hours / hours | Lowest cost, non-critical | HIGH |
| **Pilot Light** | 10s of min / min | Core data replicated + minimal infra running; **must be turned on + scaled up** | HIGH |
| **Warm Standby** | Minutes / seconds | **Already serving at reduced capacity** — just scale up | HIGH |
| **Multi-Site Active-Active** | Seconds / near-zero | Both regions live, R53/GA distribute | MED |

**Key trap:** "Already running at reduced capacity" = warm standby. "Minimal core only, must scale up" = pilot light. Most-missed DR question.

| DR-supporting service | Exam angle | Freq |
|---|---|---|
| **Multi-AZ ≠ DR** | Multi-AZ = HA inside one Region; DR = multi-Region. Trap: "DR" question with Multi-AZ as distractor. | HIGH |
| Aurora Global Database | RPO ~1s, RTO <1 min. Pair with pilot light or warm standby. | HIGH |
| RDS cross-region Read Replica | Manual promote; worse RPO/RTO than Aurora Global. | MED |
| DynamoDB Global Tables | Multi-region active-active writes. | HIGH |
| S3 CRR (with RTC) | 99.99% within 15 min for RTC. | HIGH |
| ⭐ **AWS Elastic Disaster Recovery (DRS)** | Block-level continuous replication to staging area; **RPO seconds, RTO 5-20 min**; cheaper than warm standby because compute launched only on failover/drill. Replaces CloudEndure. **C03 cheap pilot-light-like option.** | HIGH (newer) |
| AWS MGN (Application Migration Service) | Sister service: same agent as DRS but for one-way migration, NOT DR. Don't confuse. | LOW |

---

## Section 18: Cost optimization

### EC2 purchasing — the recurring matrix

| Phrase | Pick |
|---|---|
| Predictable steady-state, EC2 only, locked family/region | **Standard RI** or **EC2 Instance SP** (up to 72%) |
| Mixed compute (EC2+Fargate+Lambda), max flexibility | **Compute Savings Plan** (up to 66%) |
| Predictable but might change family | Convertible RI (~54%) |
| Need capacity guarantee in specific AZ | Zonal RI (or On-Demand Capacity Reservation) |
| Fault-tolerant, batch, CI, big data | Spot (up to 90%) |
| BYOL Windows/Oracle/SQL Server | Dedicated Hosts |

### Tools

| Tool | When picked | Freq |
|---|---|---|
| **Compute Optimizer** | "Right-size EC2/EBS/Lambda/Fargate" → ML-based recommendations. | HIGH |
| **Trusted Advisor** | "Identify idle EC2/ELB / underutilized" + RI recommendations. Business/Enterprise support for full checks. | HIGH |
| Cost Explorer | Forecast, top spenders, RI/SP utilization & coverage. | MED |
| Budgets | Alerts on threshold breach. | MED |
| Cost & Usage Report | Most granular billing → S3 → Athena. | LOW |

### Network/data-transfer cost recurring traps

| Trap | Fix | Freq |
|---|---|---|
| Single NAT GW shared across AZs | One NAT GW per AZ + same-AZ routing | HIGH |
| EC2 → S3 via NAT GW expensive | **VPC Gateway Endpoint** (free) | HIGH |
| High-volume to AWS services via NAT | **Interface Endpoints** (PrivateLink) cheaper | HIGH |
| gp2 EBS volumes | Migrate to **gp3** (cheaper + better baseline) | MED |
| KMS request costs high on S3 | Enable **S3 Bucket Keys** (up to 99% reduction) | MED |

---

## Section 19: Analytics

| Service | Trigger phrase | Frequency |
|---|---|---|
| **Athena** | "Ad-hoc SQL on S3, no infra, least operational overhead" | HIGH |
| **Redshift** | "Petabyte warehouse, complex BI joins repeated daily" | MED-HIGH |
| **Redshift Spectrum** | "Combine Redshift table joins WITH S3 data" (Athena cannot join Redshift internal tables) | MED |
| ⭐ **Redshift Serverless** | "Data warehouse with intermittent workloads, no cluster mgmt" | MED |
| **EMR** | "Existing Spark/Hadoop code, big cluster" | MED |
| ⭐ **EMR Serverless** | "Run Spark/Hive without provisioning cluster" | LOW-MED |
| ⭐ **Glue (serverless ETL)** | "Serverless ETL," PySpark transformations | MED-HIGH |
| ⭐ **Glue Data Catalog** | "Central metadata store across Athena/EMR/Redshift Spectrum" / "Hive metastore replacement" | HIGH |
| ⭐ **Glue Crawler** | "Auto-discover schema in S3" (canonical pairing with Athena) | HIGH |
| ⭐ **Lake Formation** | "Fine-grained access control to data lake" / "row/column/cell-level security" | MED |
| ⭐ **OpenSearch Service** | "Log analytics with dashboards" / "full-text search" | MED |
| **QuickSight** | "Interactive dashboards / BI / visualize data lake" | MED |
| **Kinesis Data Analytics / Managed Flink** | "Real-time SQL on streams / windowed aggregates / anomaly detection" | LOW-MED |

**Key recurring patterns:**
- **Stream → S3/OpenSearch/Redshift, least ops, near-real-time** → Kinesis Firehose chain
- **CloudTrail / VPC Flow / ALB logs analysis** → Athena on the S3 bucket
- **Column-level access in QuickSight on data lake** → Lake Formation + Athena + QS
- **OLTP → DW without ETL pipeline** → ⭐ Aurora zero-ETL to Redshift
- **Athena cannot read client-side encrypted S3** — common trap

---

## Section 20: ML services — pick by use case keyword

| Use case keyword | Service |
|---|---|
| "Detect faces / objects / inappropriate images / video" | **Rekognition** |
| "Extract text/tables/forms from scanned documents" | **Textract** (NOT Rekognition for OCR — common trap) |
| "Sentiment / entities / language / PII detection in text" | **Comprehend** |
| "Medical conditions/medications from clinical notes" | **Comprehend Medical** |
| "Translate text between languages" | **Translate** |
| "Speech-to-text / transcribe calls / live captions" | **Transcribe** |
| "Text-to-speech / lifelike voice" | **Polly** |
| "Time-series forecast (demand/inventory)" | **Forecast** |
| "Real-time product recommendations" | **Personalize** |
| "Build chatbot (Alexa engine)" | **Lex** |
| "Intelligent enterprise search of internal docs" | **Kendra** |
| "Online payment/account fraud" | **Fraud Detector** |
| ⭐ "Generative AI / foundation models / LLM-based app" | **Bedrock** |
| "Build, train, deploy custom ML model" | **SageMaker** (last resort when no purpose-built service fits) |

---

## Section 21: 30 highest-leverage decision phrases

1. **"Unknown / unpredictable access pattern"** → S3 Intelligent-Tiering (NOT Standard-IA)
2. **"Even root cannot delete / WORM / SEC 17a-4"** → S3 Object Lock Compliance Mode
3. **"Replicate EXISTING S3 objects"** → S3 Batch Replication (NOT enabling CRR alone)
4. **"Restrict to AWS Organization with LEAST overhead"** → bucket policy with `aws:PrincipalOrgID`
5. **"EC2 in private subnet needs S3 without internet"** → Gateway VPC Endpoint
6. **"On-prem must access S3 privately"** → Interface Endpoint via DX (Gateway endpoint can't)
7. **"Hundreds of VPCs / centralized hub"** → Transit Gateway
8. **"Block specific malicious IP"** → NACL deny rule (SG can't deny)
9. **"Static IP + global app + non-HTTP"** → Global Accelerator
10. **"Premium subscriber accessing many videos"** → CloudFront Signed Cookies
11. **"Multi-region active-active writes, NoSQL"** → DynamoDB Global Tables
12. **"<1s cross-region replication, RTO <1 min, relational"** → Aurora Global Database
13. **"MySQL/PG + HA + extra read capacity + lower write latency"** → ⭐ Multi-AZ DB Cluster
14. **"Application runs 2 hrs/week, MySQL"** → ⭐ Aurora Serverless v2
15. **"Microsecond DynamoDB reads, no code change"** → DAX (NOT ElastiCache)
16. **"Lambda + RDS connection storms"** → RDS Proxy + VPC Lambda
17. **"Auto-delete DDB items at no cost"** → DynamoDB TTL
18. **"Sessions lost when ALB routes to different instance"** → ElastiCache Redis as session store
19. **"Java + reduce cold starts + most cost-effective"** → ⭐ Lambda SnapStart
20. **"ECS task needs S3 access"** → Task Role (NOT execution role)
21. **"Order preserved + fan-out to multiple consumers"** → FIFO SNS → multiple FIFO SQS
22. **"Stream → OpenSearch with least ops"** → CW Logs subscription → Firehose → OpenSearch
23. **"Existing Kafka clients / migrate on-prem Kafka"** → ⭐ Amazon MSK
24. **"Centralized corporate directory for many AWS accounts"** → ⭐ IAM Identity Center (NOT Cognito)
25. **"Auto-rotate DB credentials"** → Secrets Manager
26. **"FIPS 140-2 Level 3 / dedicated hardware"** → CloudHSM
27. **"Discover PII in S3"** → Macie (only S3 + sensitive data keywords)
28. **"Single pane of security findings across accounts"** → ⭐ Security Hub
29. **"Pilot light vs warm standby"** → Already-running-reduced = warm standby; minimal-core-only = pilot light
30. **"Lift-and-shift DR with RPO seconds, RTO minutes, cheap"** → ⭐ AWS Elastic Disaster Recovery (DRS)

---

## Conclusion: how this changes study strategy

Most candidates over-study services and under-study **decision points**. Three insights from the data:

**The exam tests phrase-to-service mapping more than feature memorization.** ~70% of questions hinge on identifying a single trigger keyword: "unknown access pattern" (Intelligent-Tiering), "static IPs + non-HTTP" (Global Accelerator), "ordered fan-out" (FIFO SNS+SQS), "least operational overhead + serverless ETL" (Glue). Build a flashcard deck of the 30 decision phrases above and you cover roughly 35-45 questions.

**C03's biggest study delta vs C02 isn't more services — it's modernized correct answers.** Where C02 questions accepted OAI, classic Multi-AZ, Aurora Serverless v1, EMR clusters, Cognito for workforce SSO, and CloudEndure, C03 questions increasingly mark these as wrong distractors and reward **OAC, Multi-AZ DB Cluster, Aurora Serverless v2, Glue/EMR Serverless, IAM Identity Center, and AWS DRS**. When two answers seem equally valid, **pick the newer one**.

**The five highest-leverage trap families are worth disproportionate study time:** (1) NAT Gateway per-AZ vs single-AZ + cost via Endpoints, (2) RDS Multi-AZ standby is not readable (Read Replicas for read scaling), (3) WAF cannot attach to NLB and ACM for CloudFront must be in us-east-1, (4) DataSync (migration) vs Storage Gateway (ongoing hybrid) vs Snowball (PB-scale), and (5) Pilot Light (must scale up) vs Warm Standby (already serving). Candidates who get these five right consistently report passing scores in the 800-900 range. Candidates who confuse any of them report failing in the 650-720 range.

The exam rewards **architectural pattern recognition** over deep service knowledge. Use this map as a question-generator: for each row, ask yourself "what would the question wording look like that makes this the right answer, and what's the most plausible distractor?" If you can answer that for 80% of the rows, you'll pass.