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

## ✅ ALL SECTIONS COMPLETE (S15–S28)

For each: build **Masterclass** + **Exam Cracker**, page divided into the **top tabs** listed.

- [x] **S16 · AWS Storage Extras** ← *DONE: `16_AWS_Storage_Extras/` — tabs Snow · Storage Gateway · FSx · DataSync/Transfer; 21 Qs; pricing in file 6.*

- [x] **S17 · Decoupling: SQS, SNS, Kinesis, Amazon MQ** ← *DONE: `17_Decoupling_SQS_SNS_Kinesis_MQ/`; 22 Qs; pricing in file 6.*

- [x] **S18 · Containers: ECS, Fargate, ECR, EKS** ← *DONE: `18_Containers_ECS_Fargate_ECR_EKS/`; 22 Qs; pricing in file 6.*

- [x] **S19 · Serverless Overviews** ← *DONE: `19_Serverless_Lambda_DynamoDB_APIGW_Cognito/`; 24 Qs; pricing in file 6.*

- [x] **S20 · Serverless Solution Architectures** ← *DONE: `20_Serverless_Architecture_Patterns/` — tabs Web/Mobile · Static Hosting · Microservices · Event Pipelines; 14 design Qs.*

- [x] **S21 · Databases in AWS** ← *DONE: `21_Databases_in_AWS/` — tabs Choosing/Relational/NoSQL&In-Memory/Purpose-Built; 18 Qs; specialized DB pricing in file 6.*

- [x] **S22 · Data & Analytics** ← *DONE: `22_Data_and_Analytics/` — tabs Athena/Glue/Lake Formation · Redshift · EMR/OpenSearch · MSK/QuickSight; 18 Qs; pricing in file 6.*

- [x] **S23 · Machine Learning** ← *DONE: `23_Machine_Learning/` — tabs Vision&Docs · Speech&Language · SageMaker · Specialized AI; 16 Qs.*

- [x] **S24 · Monitoring & Audit** ← *DONE: `24_Monitoring_CloudWatch_CloudTrail_Config/` — tabs CloudWatch · CloudTrail · Config; 16 Qs; pricing in file 6.*

- [x] **S25 · IAM Advanced** ← *DONE: `25_IAM_Advanced/` — tabs Policies&Evaluation · STS&Cross-Account · Federation&SSO · Organizations&SCP; 18 Qs.*

- [x] **S26 · Security & Encryption** ← *DONE: `26_Security_Encryption/` — tabs KMS&CloudHSM · Secrets/Params/ACM · WAF&Shield · Threat Detection; 20 Qs; pricing in file 6.*

- [x] **S27 · Networking — VPC** ← *DONE: `27_Networking_VPC/` — tabs Fundamentals · NAT&Security · Connectivity · Hybrid&FlowLogs; 22 Qs; pricing in file 6.*

- [x] **S28 · Disaster Recovery & Migrations** ← *DONE: `28_DR_and_Migrations/` — tabs DR Strategies · Database Migration · Server/Data Migration · DR Tooling; 18 Qs.*

---

## 🏁 STATUS: COMPLETE
All Stephane Maarek SAA-C03 sections **15–28** built — 14 sections × 2 docs = **28 HTML files**, **~270 scored practice questions**, all wired into the chapter-nav (42 pages total). Pricing for every new service added to `6_AWS_Pricing_Reference_2026.md`. Next: drill the Exam Crackers + timed mocks.

---

## Open questions (answer before building)
1. **Multi-service page structure** — for a section like S15, do the top tabs = the **sub-services**
   (CloudFront | Global Accelerator), with cheat-sheets/triggers/questions living *inside* each tab?
   Or keep the old shape (separate Masterclass + ExamCracker files)?
2. **Build order** — start at S15 and go in order, or prioritise the heavy/high-weight ones (S27 VPC, S26 Security, S19 Serverless) first?
