# AWS Masterclass — Notes Roadmap (SAA-C03 · Stephane Maarek course)

> **Goal:** Become a true AWS master + crack SAA-C03. Each topic gets two HTML docs:
> **Masterclass** (concepts + industry + Dublin + pricing) and **Exam Cracker** (cheat sheets,
> triggers & traps, practice questions).
>
> **Page layout rule:** long pages are split into **top tabs** to kill scroll-fatigue (like the S3 docs).
> For **multi-service sections**, the **top tabs = the sub-services** (e.g. Section 15 → `CloudFront` | `Global Accelerator`).
> `[needs confirm]` markers below = my proposed tab split that you should sanity-check.
>
> **Design conventions (locked from S15 review — apply to every file):**
> 1. **Full page width** — Masterclass `max-width: 1300px` / padding `0 60px`; ExamCracker `1200px` (match the S3 docs).
> 2. **Compact heading bars** — `.part-header` padding ~`20px 28px`, h2 `clamp(22px,2.1vw,28px)` (don't let the coloured heading blocks get tall).
> 3. **On-this-page index** at the top of each service tab — clean names, **no "Part N" numbers**, dot-bullet links jumping to each section (`scroll-margin-top` so the sticky tab bar doesn't cover the target).
> 4. Comfort first: big readable body text, generous line-height, diagrams/tables only where they add insight.

---

## ✅ DONE
- [x] EC2
- [x] ELB & ASG
- [x] IAM
- [x] RDS / Aurora / ElastiCache
- [x] Route 53
- [x] S3  ← *(Masterclass now tab-split into 15 parts; ExamCracker has Cheat / Triggers / Questions tabs)*
- [x] **S15 · CloudFront & Global Accelerator** ← *DONE: `15_CloudFront_Global_Accelerator/` — Masterclass (CloudFront | GA tabs) + ExamCracker (service tabs → cheat/triggers/questions sub-tabs, 21 Qs). Pricing added to file 6.*

---

## 🟡 REMAINING — Sections 23–28

For each: build **Masterclass** + **Exam Cracker**, page divided into the **top tabs** listed.

- [x] **S16 · AWS Storage Extras** ← *DONE: `16_AWS_Storage_Extras/` — tabs Snow · Storage Gateway · FSx · DataSync/Transfer; 21 Qs; pricing in file 6.*

- [x] **S17 · Decoupling: SQS, SNS, Kinesis, Amazon MQ** ← *DONE: `17_Decoupling_SQS_SNS_Kinesis_MQ/`; 22 Qs; pricing in file 6.*

- [x] **S18 · Containers: ECS, Fargate, ECR, EKS** ← *DONE: `18_Containers_ECS_Fargate_ECR_EKS/`; 22 Qs; pricing in file 6.*

- [x] **S19 · Serverless Overviews** ← *DONE: `19_Serverless_Lambda_DynamoDB_APIGW_Cognito/`; 24 Qs; pricing in file 6.*

- [x] **S20 · Serverless Solution Architectures** ← *DONE: `20_Serverless_Architecture_Patterns/` — tabs Web/Mobile · Static Hosting · Microservices · Event Pipelines; 14 design Qs.*

- [x] **S21 · Databases in AWS** ← *DONE: `21_Databases_in_AWS/` — tabs Choosing/Relational/NoSQL&In-Memory/Purpose-Built; 18 Qs; specialized DB pricing in file 6.*

- [x] **S22 · Data & Analytics** ← *DONE: `22_Data_and_Analytics/` — tabs Athena/Glue/Lake Formation · Redshift · EMR/OpenSearch · MSK/QuickSight; 18 Qs; pricing in file 6.*

- [ ] **S23 · Machine Learning**  *(0/13 · 26min)*
      → Tabs: **Rekognition** · **Transcribe / Polly / Translate** · **Comprehend / Lex** · **SageMaker** · **Forecast / Kendra / Personalize / Textract**  `[needs confirm]`

- [ ] **S24 · Monitoring & Audit: CloudWatch, CloudTrail, Config**  *(0/19 · 1h19min)*
      → Tabs (3): **CloudWatch** · **CloudTrail** · **Config**

- [ ] **S25 · IAM — Advanced**  *(0/11 · 49min)*
      → Tabs: **Advanced Policies** · **STS & Cross-Account** · **Identity Federation** · **AWS Organizations & SCP** · **IAM Identity Center**  `[needs confirm]`

- [ ] **S26 · Security & Encryption: KMS, SSM Parameter Store, Shield, WAF**  *(0/22 · 1h27min)*
      → Tabs: **KMS** · **SSM Parameter Store / Secrets Manager** · **Shield & WAF** · **Other (GuardDuty, Inspector, Macie, CloudHSM, ACM, Firewall Mgr)**  `[needs confirm]`

- [ ] **S27 · Networking — VPC**  *(1/39 · 2h40min)*  ← *biggest section*
      → Tabs: **VPC Fundamentals (Subnets/IGW/Route Tables)** · **NAT & Security (NACL/SG/NAT GW)** · **Connectivity (Peering/Endpoints/PrivateLink)** · **Hybrid (VPN/Direct Connect/Transit Gateway)** · **Flow Logs & Advanced**  `[needs confirm]`

- [ ] **S28 · Disaster Recovery & Migrations**  *(0/12 · 44min)*
      → Tabs: **DR Strategies** · **Database Migration (DMS/SCT)** · **Data Migration (Snow/DataSync/Transfer)** · **AWS Backup / MGN / Discovery**  `[needs confirm]`

---

## Open questions (answer before building)
1. **Multi-service page structure** — for a section like S15, do the top tabs = the **sub-services**
   (CloudFront | Global Accelerator), with cheat-sheets/triggers/questions living *inside* each tab?
   Or keep the old shape (separate Masterclass + ExamCracker files)?
2. **Build order** — start at S15 and go in order, or prioritise the heavy/high-weight ones (S27 VPC, S26 Security, S19 Serverless) first?
