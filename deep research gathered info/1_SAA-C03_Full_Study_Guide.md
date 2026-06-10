# SAA-C03 Complete Study Guide
### Beginner-Friendly | Exam-Focused | Every Topic

---

## HOW TO READ THIS GUIDE
Each concept has 4 parts:
- **What it is** — simple explanation
- **Exam tip** — what the question is really testing
- **Compare** — how it differs from similar services
- **Trap** — the mistake most people make

---

---

# TOPIC 1 — IAM (Identity & Access Management)

IAM controls WHO can do WHAT on AWS. Think of it as the security guard system.

---

### Users
**What it is:** A single person or application with a username and password (or access keys) to access AWS.
**Exam tip:** Users are for humans or apps that need long-term access. Give them only the permissions they need (least privilege).
**Trap:** Don't give users admin access unless required. The exam will penalise answers that over-provision permissions.

---

### Groups
**What it is:** A collection of users. You attach a policy to the group and all users in it inherit those permissions.
**Exam tip:** Always prefer attaching policies to groups, not individual users. Easier to manage.
**Trap:** Groups cannot be nested (no group inside a group).

---

### Roles
**What it is:** A set of permissions that can be assumed temporarily — by an EC2 instance, Lambda function, or another AWS account. No username/password.
**Exam tip:** Any time a question says "EC2 needs to access S3" or "Lambda needs to write to DynamoDB" — the answer is an IAM Role, not a user with access keys.
**Compare:** User = permanent identity. Role = temporary identity assumed as needed.
**Trap:** Never hard-code access keys in EC2/Lambda code. Always use roles.

---

### Policies
**What it is:** A JSON document that defines what actions are allowed or denied on which resources.
**Exam tip:** Two types — Identity-based (attached to user/group/role) and Resource-based (attached to the resource like S3 bucket policy).
**Trap:** An explicit DENY always wins, even if another policy says ALLOW. Remember: Deny > Allow.

---

### SCPs (Service Control Policies)
**What it is:** Organisation-level guardrails that limit what accounts in AWS Organisations can do. Applied at the OU (Organisational Unit) or account level.
**Exam tip:** SCPs do NOT grant permissions — they only restrict what's possible. You still need IAM policies to actually grant access.
**Compare:** SCP = ceiling on what's possible. IAM Policy = what's actually allowed within that ceiling.
**Trap:** Even the root user of a member account is blocked by SCPs. Many think root is exempt — it is not.

---

### Permission Boundaries
**What it is:** A limit on the maximum permissions a user or role can have, even if their policy grants more.
**Exam tip:** Used when you want to let developers create IAM roles but prevent them from creating roles with too much power.
**Trap:** Permission boundary does not grant permissions — it just caps them.

---

### Cross-Account Roles & STS AssumeRole
**What it is:** A way for users or services in Account A to temporarily access resources in Account B by assuming a role.
**Exam tip:** The answer whenever a question says "Company A needs to access Company B's AWS resources" — create a role in Account B, trust Account A.
**Compare:** Cross-account role = safe, temporary access. Sharing access keys = insecure, avoid.

---

---

# TOPIC 2 — VPC (Virtual Private Cloud)

A VPC is your own private network inside AWS. Like having your own section of the internet.

---

### Subnets
**What it is:** A subdivision of your VPC. Public subnet = has a route to the internet. Private subnet = no direct internet access.
**Exam tip:** Web servers go in public subnets. Databases go in private subnets.
**Trap:** A subnet is public only if it has a route to an Internet Gateway (IGW) in its route table. Just because it's called "public" doesn't make it public.

---

### Internet Gateway (IGW)
**What it is:** The door between your VPC and the internet. Attach one IGW to a VPC to enable internet access.
**Exam tip:** Required for any resource in a public subnet to reach/be reached from the internet.
**Trap:** One IGW per VPC. If a subnet has no route pointing to the IGW, it cannot reach the internet even if the IGW exists.

---

### NAT Gateway vs NAT Instance
**What it is:** Allows resources in a PRIVATE subnet to reach the internet (e.g., to download updates) without being reachable from the internet.
**Exam tip:** NAT Gateway is the default correct answer — it's managed, scalable, highly available in one AZ. NAT Instance is the answer ONLY when the question says "cheapest solution" or "very low traffic."
**Compare:**

| | NAT Gateway | NAT Instance |
|---|---|---|
| Managed by | AWS | You |
| High Availability | Yes (per AZ) | No (manual) |
| Cost | Higher | Lower |
| Exam default | YES | Only if "cheapest" |

**Trap:** NAT Gateway is per-AZ. For HA across 2 AZs, you need 2 NAT Gateways (one per AZ).

---

### Security Groups vs NACLs
**What it is:** Both are firewalls but work differently.

| | Security Group | NACL |
|---|---|---|
| Level | Instance level | Subnet level |
| State | Stateful (return traffic auto-allowed) | Stateless (must allow both directions) |
| Rules | Allow only | Allow AND Deny |
| Rule order | All rules evaluated | Rules evaluated in number order, first match wins |

**Exam tip:** Security Groups are almost always the answer. NACLs come up when the question says "block a specific IP" (since SGs can't deny, only allow).
**Trap:** NACL rules are evaluated in order. If rule 100 allows something and rule 200 denies it, the allow wins because it's evaluated first.

---

### VPC Endpoints
**What it is:** A private connection from your VPC to AWS services (like S3, DynamoDB) without going through the internet.

**Two types:**
- **Gateway Endpoint** — free, works only for S3 and DynamoDB, added to route table
- **Interface Endpoint (PrivateLink)** — paid (~$0.01/hr/AZ + data), works for almost every other AWS service, creates an ENI in your subnet

**Exam tip:** If the question says "connect to S3 without internet, cheapest way" — Gateway Endpoint. Anything else — Interface Endpoint.
**Trap:** Don't mix these up. Gateway = S3/DynamoDB only. Interface = everything else.

---

### VPC Peering
**What it is:** A direct network connection between two VPCs (same or different accounts/regions).
**Exam tip:** Use when two VPCs need to talk to each other directly. Simple, no bandwidth bottleneck.
**Trap:** VPC Peering is NOT transitive. If A peers with B and B peers with C, A cannot talk to C. You must peer A and C directly.

---

### Transit Gateway
**What it is:** A central hub that connects multiple VPCs and on-premises networks together. Think of it as a router for many VPCs.
**Exam tip:** Use when you have 5+ VPCs that all need to communicate. Much simpler than peering each pair.
**Compare:** VPC Peering = point-to-point, non-transitive. Transit Gateway = hub-and-spoke, transitive, scales to thousands of VPCs.
**Trap:** Transit Gateway has a cost per attachment and per GB. Not free like VPC Peering.

---

### Site-to-Site VPN vs Direct Connect
**What it is:** Both connect your on-premises data centre to AWS.

| | Site-to-Site VPN | Direct Connect |
|---|---|---|
| Setup time | Minutes | Weeks/months |
| Speed | Up to 1.25 Gbps | 1–100 Gbps |
| Reliability | Over internet | Dedicated private line |
| Cost | Low | High |
| Use case | Quick setup, backup | High throughput, consistent latency |

**Exam tip:** "Fastest to set up" = VPN. "Most reliable, consistent bandwidth" = Direct Connect.
**Trap:** Direct Connect alone is not redundant. For HA, pair it with a VPN as backup.

---

---

# TOPIC 3 — EC2 (Elastic Compute Cloud)

EC2 is renting virtual servers on AWS. You pick the size, OS, and pay by the hour.

---

### Pricing Models
**On-Demand:** Pay per second, no commitment. Use for unpredictable workloads.
**Reserved Instances:** Commit to 1 or 3 years. Up to 72% discount. Use for steady, predictable workloads.
**Savings Plans:** Like Reserved but more flexible — applies to EC2, Lambda, and Fargate. Commit to a spend per hour, not a specific instance type.
**Spot Instances:** Up to 90% cheaper but AWS can terminate with 2-minute warning. Use for fault-tolerant batch jobs.

**Exam tip:** "Cost-effective for steady workload" = Reserved or Savings Plans. "Cheapest for flexible/interruptible" = Spot.
**Trap:** Spot Instances are not suitable for databases, web servers, or anything that can't be interrupted.

---

### Placement Groups
**Cluster:** All instances packed close together in one AZ. Low latency, high network throughput. Use for HPC.
**Spread:** Instances spread across different hardware racks. Max 7 instances per AZ. Use for critical instances that must not fail together.
**Partition:** Instances spread across partitions (different racks). Up to 7 partitions per AZ. Use for Hadoop, Cassandra, Kafka.

**Exam tip:** "Low latency between instances" = Cluster. "Reduce correlated failures" = Spread.
**Trap:** Cluster group gives low latency but if one rack fails, all instances fail together.

---

### Instance Store vs EBS
**Instance Store:** Physically attached storage to the EC2 host. Extremely fast. But — data is LOST when the instance stops or terminates.
**EBS:** Network-attached storage. Persists independently of the instance lifecycle.

**Exam tip:** Instance Store = temporary high-speed scratch space. EBS = persistent storage you need to keep.
**Trap:** If you stop (not just reboot) an EC2 instance, instance store data is gone forever.

---

---

# TOPIC 4 — Auto Scaling Groups (ASG)

ASG automatically adds or removes EC2 instances based on demand. Like hiring/firing staff based on how busy you are.

---

### Scaling Policies
**Target Tracking:** Keep a metric at a target (e.g., CPU at 50%). Simplest and most recommended.
**Step Scaling:** Add/remove specific number of instances when alarms breach thresholds.
**Scheduled Scaling:** Scale at a specific time (e.g., add 10 instances every Monday 9am).

**Exam tip:** "Automatically adjust to maintain performance" = Target Tracking. "Scale at known busy times" = Scheduled.

---

### Launch Templates vs Launch Configurations
**Launch Template:** Newer, preferred. Supports multiple versions, Spot + On-Demand mix, T2/T3 unlimited.
**Launch Configuration:** Older, being deprecated. Can't be modified after creation.

**Exam tip:** Always prefer Launch Templates in answers. If a question offers both, pick Launch Template.

---

### Lifecycle Hooks
**What it is:** Pause an instance during launch or termination to run custom scripts (e.g., install software before the instance serves traffic, or drain connections before termination).
**Exam tip:** When a question asks "how to run a script when an instance launches before it gets traffic" — Lifecycle Hook.

---

---

# TOPIC 5 — Load Balancers (ELB)

A load balancer sits in front of your servers and distributes incoming traffic across them.

---

### ALB (Application Load Balancer)
**What it is:** Layer 7 load balancer — understands HTTP/HTTPS. Can route based on URL path, hostname, headers, query strings.
**Exam tip:** Use ALB when you need HTTP routing rules, microservices, containers, WebSockets, or Cognito authentication.
**Example:** Route /api/* to one group of servers and /images/* to another.
**Trap:** ALB doesn't have a static IP address. Use NLB or Global Accelerator if you need static IPs.

---

### NLB (Network Load Balancer)
**What it is:** Layer 4 load balancer — works with TCP/UDP/TLS. Extremely fast (millions of requests/second).
**Exam tip:** Use NLB when you need static IPs per AZ, ultra-low latency, or are dealing with non-HTTP traffic.
**Compare:** ALB = smart HTTP routing. NLB = raw speed + static IPs.
**Trap:** NLB preserves the source IP of the client. ALB does not by default (use X-Forwarded-For header).

---

### GWLB (Gateway Load Balancer)
**What it is:** Routes traffic through third-party virtual appliances (firewalls, intrusion detection systems) transparently. Uses GENEVE protocol on port 6081.
**Exam tip:** Any question mentioning "inspection appliances," "third-party firewalls," or "transparent network inspection" = GWLB.
**Trap:** GWLB is not for balancing your application servers — it's specifically for inserting security appliances into traffic flow.

---

---

# TOPIC 6 — S3 (Simple Storage Service)

S3 is object storage — store any file (images, videos, backups, logs) at any scale.

---

### Storage Classes
**Standard:** Frequently accessed data. High cost, millisecond retrieval.
**Standard-IA (Infrequent Access):** Cheaper storage, but you pay per retrieval. Min 30-day storage.
**One Zone-IA:** Like Standard-IA but only in 1 AZ. Cheaper, less resilient. Min 30 days.
**Glacier Instant Retrieval:** Archive data retrieved in milliseconds. Min 90 days.
**Glacier Flexible Retrieval:** Archive, retrieved in minutes to hours. Min 90 days.
**Glacier Deep Archive:** Cheapest. Retrieved in 12–48 hours. Min 180 days.
**Intelligent-Tiering:** AWS automatically moves objects between tiers based on access. Small monthly monitoring fee.

**Exam tip:** Read the retrieval time clue in the question. "Milliseconds" = Standard or Glacier Instant. "Hours" = Flexible. "Cheapest archive" = Deep Archive.
**Trap:** If you delete an object before its minimum storage duration, you still pay for the full duration.

---

### Lifecycle Rules
**What it is:** Automatically transition objects between storage classes or delete them after a certain time.
**Exam tip:** "Reduce S3 costs for data that is rarely accessed after 30 days" = create a lifecycle rule to move to Standard-IA at 30 days, then Glacier at 90 days.
**Trap:** You can only transition to a colder (cheaper) class, not a warmer one via lifecycle rules.

---

### Versioning & Object Lock
**Versioning:** Keeps every version of every object. Deleting just adds a "delete marker" — old versions still exist.
**Object Lock:** WORM (Write Once Read Many). Objects cannot be deleted or overwritten for a set period. Required for compliance.
**MFA Delete:** Requires MFA to delete object versions or disable versioning. Extra protection.

**Exam tip:** "Protect against accidental deletion" = enable Versioning. "Regulatory compliance, cannot be deleted" = Object Lock.

---

### Replication
**CRR (Cross-Region Replication):** Copies objects to a bucket in another region. For DR and compliance.
**SRR (Same-Region Replication):** Copies within the same region. For log aggregation, dev/prod sync.

**Exam tip:** "DR for S3 in another region" = CRR. Both require Versioning enabled on source and destination.
**Trap:** Replication is not retroactive. Only new objects after enabling replication are replicated.

---

### Encryption
**SSE-S3:** AWS manages the keys. Simplest option. You do nothing.
**SSE-KMS:** You use KMS keys. You control key rotation and access. Audit trail in CloudTrail.
**SSE-C:** You provide and manage your own keys. AWS does the encryption but never stores your key.
**DSSE-KMS:** Dual-layer encryption with KMS. For highest compliance needs.

**Exam tip:** "Customer manages the keys" = SSE-KMS or SSE-C. "AWS manages everything" = SSE-S3. "Audit who used which key" = SSE-KMS (CloudTrail logs KMS usage).
**Trap:** SSE-C requires you to send the key with every request. AWS never stores it — if you lose the key, you lose the data.

---

### Presigned URLs
**What it is:** A temporary URL that grants time-limited access to a private S3 object without making the bucket public.
**Exam tip:** "Allow a user to download a private S3 file for 1 hour" = presigned URL.
**Trap:** The presigned URL's permissions are based on the creator's permissions at the time of creation. If those permissions are revoked, the URL stops working.

---

---

# TOPIC 7 — Route 53

Route 53 is AWS's DNS service — translates domain names (example.com) into IP addresses.

---

### Routing Policies

**Simple:** One record, one or more values. No health checks. Random selection if multiple values.

**Weighted:** Split traffic by percentage. 70% to v1, 30% to v2. Good for A/B testing.

**Latency:** Routes to the region with lowest network latency for the user.

**Failover:** Primary/secondary setup. Routes to secondary only if primary fails health check. For DR.

**Geolocation:** Routes based on user's country or continent.

**Geoproximity:** Routes based on geographic distance. Can shift traffic by adding bias. Requires Route 53 Traffic Flow.

**Multi-Value:** Returns multiple IPs, does health checks, removes unhealthy ones. NOT a load balancer but helps distribute DNS traffic.

**Exam tip:**
- "Distribute 10% of traffic to new version" = Weighted
- "Route users to nearest region" = Latency
- "DR switchover if primary fails" = Failover
- "Route European users to EU servers" = Geolocation

**Trap:** Latency routing ≠ geolocation routing. Latency picks the region that responds fastest (network speed). Geolocation picks based on where the user is located. A US user might get routed to EU if the EU region has lower latency.

---

---

# TOPIC 8 — CloudFront & Global Accelerator

Both improve performance for global users, but in different ways.

---

### CloudFront
**What it is:** A CDN (Content Delivery Network). Caches your content (images, videos, HTML, APIs) at 400+ edge locations worldwide. Reduces load on your origin and speeds up delivery.
**Exam tip:** "Reduce latency for global users accessing static content" = CloudFront.
**Trap:** CloudFront caches content. If you update your origin, users might still get old cached content. You need to create an invalidation to force fresh content.

---

### Lambda@Edge vs CloudFront Functions
**Lambda@Edge:** Runs on all 4 CloudFront events (viewer request/response, origin request/response). Supports Node.js and Python. Can make network calls.
**CloudFront Functions:** Runs only on viewer request/response. Sub-millisecond execution. Cheaper. No network calls.

**Exam tip:** "Modify headers, redirect based on cookies before reaching origin" = CloudFront Functions (simple, fast). "Complex logic, call an external API" = Lambda@Edge.

---

### Global Accelerator
**What it is:** Uses AWS's private global network to route traffic. Gives you 2 static anycast IPs that work globally. Traffic enters AWS network at the nearest edge and stays on AWS backbone to your region.
**Exam tip:** "Static IP addresses that work globally" or "non-HTTP workloads (TCP/UDP)" or "fast failover without DNS propagation delays" = Global Accelerator.
**Compare:**

| | CloudFront | Global Accelerator |
|---|---|---|
| Protocol | HTTP/HTTPS only | Any TCP/UDP |
| Caching | Yes | No |
| Static IPs | No | Yes (2 anycast IPs) |
| Use case | Cache content | Speed up non-HTTP, static IPs |

**Trap:** CloudFront is for HTTP content caching. Global Accelerator is NOT a cache — it just routes traffic faster on AWS's network.

---

---

# TOPIC 9 — RDS (Relational Database Service)

RDS is managed SQL databases — AWS handles backups, patching, and hardware. You just use the database.

---

### Multi-AZ
**What it is:** RDS creates a standby copy in a different AZ. If the primary fails, AWS automatically fails over to the standby. Standby is NOT readable — it's only for failover.
**Exam tip:** "High availability for database" = Multi-AZ. Automatic failover in ~60 seconds.
**Trap:** Multi-AZ standby CANNOT be used for read traffic in standard RDS. It's only for failover. (Aurora is different — see below.)

---

### Read Replicas
**What it is:** Async copy of your database. Can be in same region or different region. You can read from it to offload read traffic from the primary.
**Exam tip:** "Database is getting too many read requests" = Add Read Replicas. "Cross-region disaster recovery for database" = cross-region Read Replica.
**Compare:**

| | Multi-AZ | Read Replica |
|---|---|---|
| Purpose | High availability | Read scaling |
| Replication | Synchronous | Asynchronous |
| Readable? | No | Yes |
| Auto-failover | Yes | No (manual promotion) |

**Trap:** Read Replicas can have replication lag — slightly behind the primary. Don't use for applications that need the latest data.

---

### RDS Proxy
**What it is:** A connection pool between your application and RDS. Particularly useful for Lambda functions that open/close many short-lived database connections.
**Exam tip:** "Lambda connecting to RDS causing 'too many connections' error" = Add RDS Proxy.
**Trap:** RDS Proxy is not a performance booster — it's a connection manager. It won't make queries faster, but it prevents connection exhaustion.

---

---

# TOPIC 10 — Aurora

Aurora is AWS's own relational database. Compatible with MySQL and PostgreSQL but much faster and more resilient.

---

### Why Aurora is special
- Automatically stores 6 copies of data across 3 AZs
- Up to 15 Read Replicas (vs 5 for RDS)
- Storage auto-grows up to 128TB
- Faster failover than RDS Multi-AZ (under 30 seconds)

---

### Aurora Global Database
**What it is:** Replicates your Aurora database to up to 5 other regions. Primary region handles writes. Secondary regions can handle reads and can be promoted to primary in < 1 minute.
**Exam tip:** "RPO of seconds and RTO under 1 minute for a cross-region database" = Aurora Global Database. This is the SAA answer for cross-region DB DR.
**Trap:** Don't confuse Aurora Multi-AZ (within one region, HA) with Aurora Global Database (cross-region, DR).

---

### Aurora Serverless v2
**What it is:** Aurora that automatically scales database capacity up and down in fractions of a second based on demand.
**Exam tip:** "Unpredictable or variable database workload, want to minimise cost" = Aurora Serverless.
**Trap:** Aurora Serverless is not the same as "serverless architecture." It's still a relational database — you just don't pick an instance size.

---

---

# TOPIC 11 — DynamoDB

DynamoDB is AWS's fully managed NoSQL (non-relational) database. No servers to manage, scales automatically.

---

### Partition Key Design
**What it is:** The main key used to distribute data across storage nodes. Good partition key = even distribution. Bad one = "hot partition" (one node gets all traffic).
**Exam tip:** "Hot partition causing throttling" = redesign your partition key to be more distributed (e.g., add a random suffix).

---

### GSI vs LSI
**GSI (Global Secondary Index):** Create an index with a completely different partition key. Can be added any time. Eventually consistent reads only.
**LSI (Local Secondary Index):** Same partition key as the table but different sort key. Must be created at table creation time. Supports strongly consistent reads.

**Exam tip:** "Need to query on a different attribute" = GSI (most common answer). LSI only comes up when the question specifically needs strongly consistent reads on the same partition.
**Trap:** LSI cannot be added after table creation. GSI can.

---

### DAX (DynamoDB Accelerator)
**What it is:** In-memory cache for DynamoDB. Reduces read latency from milliseconds to microseconds.
**Exam tip:** "DynamoDB reads are too slow, need microsecond latency" = DAX.
**Compare:** ElastiCache can also cache DynamoDB, but DAX is purpose-built and simpler to set up for DynamoDB specifically.
**Trap:** DAX only helps with reads. It does not speed up write operations.

---

### DynamoDB Streams + Global Tables
**Streams:** Captures every change (insert, update, delete) in the table as a stream. Used to trigger Lambda or replicate data.
**Global Tables:** Multi-region, multi-active DynamoDB. All regions can read AND write. AWS handles replication.

**Exam tip:** "Real-time reaction to DynamoDB changes" = Streams. "Multi-region, active-active NoSQL" = Global Tables.

---

---

# TOPIC 12 — ElastiCache

ElastiCache is managed in-memory caching — stores frequently accessed data in RAM for ultra-fast access.

---

### Redis vs Memcached

| | Redis | Memcached |
|---|---|---|
| Data structures | Rich (lists, sets, sorted sets) | Simple key-value only |
| Persistence | Yes (optional) | No |
| Replication / HA | Yes (Multi-AZ) | No |
| Pub/Sub | Yes | No |
| Multi-threading | No | Yes |
| Use case | Sessions, leaderboards, real-time analytics, pub/sub | Simple caching, highest throughput |

**Exam tip:** "Need caching with failover and persistence" = Redis. "Need pure speed, simple caching, scale horizontally" = Memcached.
**Trap:** If any of these features are mentioned — persistence, replication, pub/sub, sorted sets — the answer is Redis, not Memcached.

---

### Caching Strategies
**Lazy Loading:** Only cache data when it's requested. Cache miss = fetch from DB, then store in cache. Simple but can have stale data.
**Write-Through:** Write to cache and DB simultaneously. Data always fresh, but doubles write operations.

**Exam tip:** "Ensure cache is always up to date" = Write-Through. "Reduce database load for reads" = Lazy Loading.

---

---

# TOPIC 13 — SQS (Simple Queue Service)

SQS is a message queue — one service puts a message in, another service picks it up and processes it. They don't need to talk to each other directly.

---

### Standard vs FIFO

| | Standard | FIFO |
|---|---|---|
| Order | Best-effort (not guaranteed) | Guaranteed strict order |
| Delivery | At-least-once (possible duplicates) | Exactly-once (no duplicates) |
| Throughput | Nearly unlimited | 300 msg/sec (3000 with batching) |

**One-line rule:** FIFO = order matters + no duplicates. Standard = max throughput, order doesn't matter.
**Exam tip:** "Process orders in exact sequence" = FIFO. "High volume log processing" = Standard.
**Trap:** FIFO queue names must end in `.fifo`. FIFO is slower — don't use it unless you need ordering.

---

### Key Concepts
**Visibility Timeout:** After a consumer picks up a message, it becomes invisible to others for X seconds. If not deleted in time, it reappears (for retry).
**Dead Letter Queue (DLQ):** Where messages go after failing N times. Use to inspect failed messages.
**Long Polling:** Consumer waits up to 20 seconds for a message instead of repeatedly asking (short polling). Cheaper, fewer empty responses.

**Exam tip:** "Messages keep being reprocessed and failing" = set up a DLQ. "Too many empty API calls, high cost" = enable long polling.

---

---

# TOPIC 14 — SNS (Simple Notification Service)

SNS sends messages from one publisher to many subscribers instantly (push model).

---

### Fan-Out Pattern
**What it is:** SNS sends one message to multiple SQS queues simultaneously. Each queue can be processed independently.
**Exam tip:** "Process the same event in multiple ways simultaneously" (e.g., send email AND process in Lambda AND log to S3) = SNS → multiple SQS queues (fan-out).
**Compare:** SQS = one consumer pulls one message. SNS = one message pushed to many subscribers.
**Trap:** If you write directly to multiple SQS queues, you lose reliability (what if one write fails?). SNS fan-out ensures all queues get the message atomically.

---

---

# TOPIC 15 — EventBridge

EventBridge is a serverless event bus — routes events from AWS services, your own apps, or SaaS tools to targets based on rules.

---

**What it is:** Like a smart router for events. Define rules that say "when THIS event happens, send it to THAT target."
**Exam tip:** "React to AWS service events with content-based filtering" = EventBridge. "EC2 instance state changes trigger Lambda" = EventBridge rule.
**Compare:**

| | SQS | SNS | EventBridge |
|---|---|---|---|
| Model | Pull (consumer polls) | Push (publisher pushes) | Event-driven routing |
| Filtering | No | Basic attribute filter | Rich content-based filter |
| Sources | Your app | Your app | AWS services, SaaS, your app |
| Best for | Decoupling, retry | Fan-out notifications | Event routing, automation |

**Trap:** EventBridge is not a queue — it doesn't store messages for retry like SQS does.

---

---

# TOPIC 16 — Kinesis

Kinesis is for real-time data streaming — think millions of events per second (logs, clickstreams, IoT data).

---

### Kinesis Data Streams
**What it is:** Real-time data streaming. You can replay data (retained up to 365 days). Multiple consumers can read the same stream independently.
**Exam tip:** "Real-time processing" or "replay capability" = Kinesis Data Streams.

---

### Kinesis Data Firehose
**What it is:** Near real-time delivery to destinations (S3, Redshift, OpenSearch). Fully managed, no shards to manage. No replay.
**Exam tip:** "Load streaming data into S3 or Redshift automatically" = Firehose.

---

### Kinesis vs SQS

| | Kinesis Data Streams | SQS |
|---|---|---|
| Real-time? | Yes | Near real-time |
| Replay? | Yes (up to 365 days) | No (deleted after processing) |
| Multiple consumers? | Yes, independently | No (one consumer per message) |
| Best for | Analytics, logs, IoT streaming | Decoupling, task queues |

**Exam tip:** Question says "real-time" or "replay" = Kinesis. Question says "decouple services" or "retry failed jobs" = SQS.
**Trap:** SQS messages are deleted after being processed. Kinesis retains data — multiple consumers can process the same data independently.

---

---

# TOPIC 17 — Lambda

Lambda is serverless compute — you just write code and AWS runs it. No servers to manage.

---

### Key Limits (memorise these)
- Max execution time: **15 minutes**
- Max memory: **10 GB**
- Max /tmp storage: **10 GB**
- Default concurrency limit: **1000 per region**

**Exam tip:** If the question describes a job that takes more than 15 minutes — Lambda is WRONG. Use Fargate or EC2.
**Trap:** Many students choose Lambda for long-running tasks. The 15-minute limit is a hard stop.

---

### Triggers
Lambda is triggered by: S3 events, SQS messages, SNS notifications, API Gateway, EventBridge rules, DynamoDB Streams, Kinesis streams, and more.

---

### Reserved vs Provisioned Concurrency
**Reserved Concurrency:** Guarantees a number of concurrent executions are always available for this function (and prevents it from using more).
**Provisioned Concurrency:** Pre-warms Lambda instances to eliminate cold start latency.

**Exam tip:** "Lambda cold starts causing latency issues" = Provisioned Concurrency.

---

### Lambda@Edge vs CloudFront Functions (recap)

| | Lambda@Edge | CloudFront Functions |
|---|---|---|
| Events | All 4 (viewer + origin) | Viewer only |
| Languages | Node.js, Python | JavaScript only |
| Network calls | Yes | No |
| Latency | Milliseconds | Sub-millisecond |
| Cost | Higher | Lower |

---

---

# TOPIC 18 — API Gateway

API Gateway is a managed service to create, publish, and secure APIs.

---

### Types
**REST API:** Feature-rich. Supports caching, API keys, usage plans, resource policies.
**HTTP API:** Simpler, cheaper, faster. No caching. Best for Lambda and HTTP backends.
**WebSocket API:** For real-time two-way communication (chat, live updates).

**Exam tip:** "Low cost, simple Lambda proxy" = HTTP API. "Need caching, usage plans, full features" = REST API. "Real-time bidirectional" = WebSocket.

---

---

# TOPIC 19 — ECS / EKS / Fargate

For running containers (Docker) on AWS.

---

### ECS (Elastic Container Service)
AWS's own container orchestration. You define tasks and services. Can run on EC2 (you manage instances) or Fargate (serverless).

---

### Fargate
Serverless containers — no EC2 instances to manage. You just define CPU and memory for each container task.
**Exam tip:** "Run containers without managing servers" = Fargate. "LEAST operational overhead for containers" = Fargate.

---

### EKS (Elastic Kubernetes Service)
Managed Kubernetes. Use when your team already knows Kubernetes or you need Kubernetes-specific features.

**Compare:**

| | ECS on EC2 | ECS on Fargate | EKS |
|---|---|---|---|
| Manage servers? | Yes | No | Yes (nodes) or No (Fargate) |
| Complexity | Medium | Low | High |
| When to use | Custom EC2 control | Simplest containers | Already use Kubernetes |

**Trap:** EKS is not automatically simpler than ECS just because it's "managed Kubernetes." Kubernetes itself has complexity. The exam doesn't reward EKS unless the question specifically mentions Kubernetes.

---

---

# TOPIC 20 — Encryption & Secrets

---

### KMS (Key Management Service)
**What it is:** AWS manages encryption keys for you. Multi-tenant (shared infrastructure). Supports automatic key rotation (annual).
**Exam tip:** Default answer for "encrypt data at rest" on AWS services (S3, EBS, RDS, etc.).
**Trap:** KMS key policies AND IAM policies both must allow access. One alone is not enough.

---

### CloudHSM
**What it is:** A dedicated hardware security module — physically yours (single-tenant). FIPS 140-2 Level 3 compliant. You manage the keys entirely — AWS has no access.
**Exam tip:** "Regulatory compliance requires dedicated hardware," "FIPS 140-2 Level 3," "full control over keys" = CloudHSM.
**Compare:** KMS = AWS manages keys (shared). CloudHSM = you manage keys (dedicated hardware).
**Trap:** If you lose your CloudHSM keys, they're gone forever. AWS cannot recover them.

---

### Secrets Manager
**What it is:** Store and automatically rotate secrets (passwords, API keys, database credentials). Has built-in rotation for RDS, Redshift, DocumentDB.
**Exam tip:** "Automatically rotate database password" = Secrets Manager.
**Compare:** Secrets Manager = rotation + cost (~$0.40/secret/month). Parameter Store = cheaper, no native rotation.
**Trap:** Don't use Parameter Store when the question asks about automatic rotation. Only Secrets Manager does that natively.

---

### SSM Parameter Store
**What it is:** Store configuration data and secrets. Free tier available. SecureString uses KMS for encryption.
**Exam tip:** "Store config values or non-sensitive parameters cheaply" = Parameter Store. "Store secrets without rotation" = Parameter Store (SecureString).
**Trap:** Parameter Store does NOT auto-rotate secrets. It's config storage, not a secrets rotation service.

---

---

# TOPIC 21 — Cognito

Cognito handles user authentication and authorisation for your applications.

---

### User Pools
**What it is:** A user directory. Handles sign-up, sign-in, MFA, social login (Google, Facebook). Returns JWT tokens.
**Exam tip:** "Add login/signup to your app" = User Pool. "ALB authentication" = User Pool integration.

---

### Identity Pools
**What it is:** Exchanges tokens (from User Pool, Google, SAML, etc.) for temporary AWS credentials via STS. Lets users directly access AWS services (S3, DynamoDB).
**Exam tip:** "Let users upload directly to S3 after login" = Identity Pool (gives temporary AWS credentials).
**Compare:** User Pool = who you are (authentication). Identity Pool = what AWS resources you can access (authorisation).
**Trap:** Don't confuse them. User Pool alone cannot give AWS credentials. You need Identity Pool for that.

---

---

# TOPIC 22 — CloudTrail, CloudWatch & Config

The three main monitoring/audit services.

---

### CloudTrail
**What it is:** Records every API call made in your AWS account — who did what, when, from where.
**Exam tip:** "Audit who deleted an S3 bucket" or "track API calls for compliance" = CloudTrail.
**Trap:** CloudTrail logs are NOT real-time. There's a ~15-minute delay. For real-time security alerts, use CloudWatch Events or GuardDuty.

---

### CloudWatch
**What it is:** Monitoring and observability. Collects metrics (CPU, memory), logs, and triggers alarms.
- **Metrics:** Numbers over time (CPU usage, request count)
- **Logs:** Log files from EC2, Lambda, etc.
- **Alarms:** Trigger actions when a metric breaches a threshold
- **Dashboards:** Visualise metrics

**Exam tip:** "Alert when CPU > 80%" = CloudWatch Alarm. "Collect application logs centrally" = CloudWatch Logs.
**Trap:** EC2 memory and disk metrics are NOT automatically sent to CloudWatch. You need the CloudWatch Agent installed on the instance.

---

### AWS Config
**What it is:** Tracks resource configuration changes over time and checks compliance against rules.
**Exam tip:** "Ensure all S3 buckets have encryption enabled" or "get notified when a security group opens port 22 to the world" = AWS Config rule.
**Compare:** CloudTrail = who made the API call. Config = what is the current and historical configuration of resources.
**Trap:** Config doesn't prevent changes — it detects and reports them. For prevention, use SCPs or IAM policies.

---

### GuardDuty
**What it is:** ML-based threat detection that analyses VPC Flow Logs, DNS logs, and CloudTrail events to find suspicious activity.
**Exam tip:** "Detect if an EC2 instance is communicating with a known malware domain" = GuardDuty.
**Trap:** GuardDuty needs no agents — it analyses existing logs. Just enable it.

---

### Inspector
**What it is:** Automated vulnerability scanning for EC2 instances and container images (ECR).
**Exam tip:** "Scan EC2 for CVEs and software vulnerabilities" = Inspector.
**Compare:** GuardDuty = runtime threat detection. Inspector = vulnerability assessment.

---

### Macie
**What it is:** Uses ML to discover and protect sensitive data (PII, financial data) stored in S3.
**Exam tip:** "Automatically detect if S3 contains personal data like credit card numbers" = Macie.

---

---

# TOPIC 23 — Storage (FSx, EFS, Storage Gateway)

---

### EFS (Elastic File System)
**What it is:** Managed NFS (Network File System) for Linux. Can be mounted by multiple EC2 instances simultaneously across AZs.
**Exam tip:** "Multiple EC2 instances need to share the same file system" (Linux) = EFS.
**Trap:** EFS is for Linux only. For Windows shared storage, use FSx for Windows.

---

### FSx for Windows
**What it is:** Managed Windows file server. Supports SMB protocol and Active Directory integration.
**Exam tip:** "Windows applications need shared file storage" or "SMB protocol" or "Active Directory integration" = FSx for Windows.

---

### FSx for Lustre
**What it is:** High-performance parallel file system for HPC and ML workloads. Can be linked to S3.
**Exam tip:** "Machine learning training with fast storage" or "HPC workload" = FSx for Lustre.

---

### Storage Gateway
**What it is:** Connects on-premises storage to AWS. Three modes:

**File Gateway:** On-premises apps access S3 via NFS/SMB. Files stored as S3 objects.
**Volume Gateway Cached:** Primary data in S3, frequently accessed data cached on-premises.
**Volume Gateway Stored:** Primary data on-premises, async backup to S3.
**Tape Gateway:** Replace physical tape backup with virtual tapes in S3/Glacier.

**Exam tip:** "On-premises application needs to store files in S3" = File Gateway. "Replace physical tape backup" = Tape Gateway.

---

---

# TOPIC 24 — Disaster Recovery Strategies

Four strategies in order of cost and recovery speed:

---

### Backup & Restore
**What it is:** Take regular backups, restore from scratch when disaster strikes.
**RPO:** Hours. **RTO:** Hours (< 24h).
**Cost:** Lowest.
**Exam trigger:** "Non-critical workload," "tolerate hours of downtime."

---

### Pilot Light
**What it is:** Core components (database replication) always running in DR region, but servers are off. Turn on servers when disaster strikes.
**RPO:** Minutes. **RTO:** 10s of minutes.
**Exam trigger:** "Core data replicated but infrastructure not running."

---

### Warm Standby
**What it is:** A scaled-down but fully functional version of your system always running in DR region. Scale it up during disaster.
**RPO:** Seconds. **RTO:** Minutes.
**Exam trigger:** "Scaled-down always-on copy."

---

### Multi-Site Active/Active
**What it is:** Full production environment running in multiple regions simultaneously. Traffic goes to all regions.
**RPO:** Near-zero. **RTO:** Near-zero.
**Cost:** Highest.
**Exam trigger:** "Lowest possible RTO and RPO," "active traffic in multiple regions."

**Trap:** Multi-AZ ≠ Multi-Region. Multi-AZ is HA within one region. Multi-Region is DR across regions.

---

---

# TOPIC 25 — Cost Optimisation

---

### EC2 Pricing Quick Reference
- **On-Demand:** No commitment, pay per second. Use for unpredictable.
- **Reserved (1 or 3yr):** Up to 72% off. Use for steady, predictable.
- **Savings Plans:** Flexible reserved. Applies to EC2 + Fargate + Lambda.
- **Spot:** Up to 90% off but interruptible. Use for batch, fault-tolerant.

**Exam tip:** "Reduce cost for a web server running 24/7" = Reserved or Savings Plans. "Reduce cost for batch jobs that can restart" = Spot.

---

### S3 Cost Tips
- Move data to cheaper tiers with lifecycle rules
- Use Intelligent-Tiering for unknown access patterns
- Glacier Deep Archive is the cheapest for long-term archiving

---

### Analytics Services — When to Use Each

| Service | What it does | When to use |
|---|---|---|
| Athena | SQL queries on S3 | "Query S3 data without loading it" |
| Redshift | Data warehouse | "Complex analytics on petabytes of structured data" |
| EMR | Managed Hadoop/Spark | "Big data processing, custom frameworks" |
| Glue | Serverless ETL | "Transform and move data between services" |
| OpenSearch | Search & analytics | "Log analytics, full-text search" |
| QuickSight | BI dashboards | "Visualise data, create reports" |

**Trap:** "Query data in S3 with SQL" = Athena (not Redshift). Redshift requires loading data into it first.

---

---

# QUICK REFERENCE — MOST TESTED COMPARISONS

| Question clue | Answer |
|---|---|
| "Strict order + no duplicates" | SQS FIFO |
| "Real-time streaming + replay" | Kinesis Data Streams |
| "Fan-out to multiple consumers" | SNS + SQS |
| "Route events with content filter" | EventBridge |
| "HA within one region (DB)" | RDS Multi-AZ |
| "Read scaling for DB" | RDS Read Replicas |
| "Cross-region DB DR, RPO seconds" | Aurora Global Database |
| "Multi-region NoSQL active-active" | DynamoDB Global Tables |
| "Microsecond DynamoDB cache" | DAX |
| "Cache for SQL DB" | ElastiCache Redis |
| "Auto-rotate DB password" | Secrets Manager |
| "Cheap config store" | SSM Parameter Store |
| "Dedicated encryption hardware" | CloudHSM |
| "Managed encryption" | KMS |
| "App login / user directory" | Cognito User Pools |
| "Temp AWS credentials after login" | Cognito Identity Pools |
| "Serverless containers" | Fargate |
| "Long-running container > 15 min" | ECS/Fargate (not Lambda) |
| "Static IPs globally" | Global Accelerator |
| "Cache HTTP content globally" | CloudFront |
| "Linux shared file system" | EFS |
| "Windows SMB file system" | FSx for Windows |
| "HPC / ML file system" | FSx for Lustre |
| "Block specific IP" | NACL (not Security Group) |
| "Free private S3 connection" | Gateway VPC Endpoint |
| "Connect many VPCs" | Transit Gateway |
| "Detect threats automatically" | GuardDuty |
| "Scan EC2 for vulnerabilities" | Inspector |
| "Find PII in S3" | Macie |
| "Audit API calls" | CloudTrail |
| "Resource compliance rules" | AWS Config |

---

*End of SAA-C03 Study Guide*
