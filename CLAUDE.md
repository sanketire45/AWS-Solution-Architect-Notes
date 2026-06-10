When research files conflict, later-numbered files override earlier ones
5 then 4 then 3 , 2, 1. As this all research are built on top of each other.this was a part of project where we created notes earlier for some topics 
projects section in cluade.
For generating the notes check this above reserach info files first if enough info is nout found search on internet as well at that same moment for more specific details. dont rely on this above info only as it can be lesser. you can use your own knowledge as well no worries full freedom on this as well how to gather the info to form the structured notes.

In this current aws masterclass folder I have already generated some notes for some topics this were generated in Project section chats in claude. 
The instruction i gave there to write the files are as below remember this are not the strict rule you have to follow thisis just the one way i gave to genreate the notes but you have your own free will to generate the masterclass main goal to look for the direction towards is to be master at aws and crack the solution architect associate. True maseter of aws like no one will be able to deny me the job i want to reach that ultimate level.

Tihs was the erlier prompt i gave read each thing very carefully its really good one:

Topic : 
I want you to create two documetns (html files NICE AND READABLE bigger font texts use full page width, Extremeley comfortable to eyes and to read and best visual viewing experience of all time is major task, less fatigue i can read entire page without brain or eye fatigue) : 1st: THis is for focusing on aws part concepts and in general concepts, like to become master of aws as a solution architect and overall. ( it means the first file should contains all the exam specific info+ what and how actual industry is using + aws hands on spcecifications and features and inforamtion on aws) Create a one single masterclass docoumnet covering everything of this topics first search in the attached files about the info for this topic. i want the why part behind each concept in the topic like why was this even needed what problem it solves in very simple language and examples, aws exam tests how would you solve this problem so if i know for each topic why was it even built in the first place i will understand everything. next add the actual part of this topic like how is it being used in companies what their architecture , get the company in dublin do deep search on this first. i dont want generic use of this but how actually its being used and implemented in the specific company. and its architecture. this will help me understand the actual industry as i dont have that much of experience in actual day to day cloud work in a company so now clue how things works internally and hence will be confidant in the interviews its like yess i have worked on it and i know it. so to reduce this gap from a personal knowledge vs the actual industry internals.
then you can use your own knowledge as well for the explanation part or any other gap if you found. (but use only correct and updated information) so cover exam in generatl , aws actual info, and industry focused. now how to write the doc: Act like a best teacher in the world start from scratch teach everything like explaining to a kid or beginner. I am noob at all the basics and depth behind the aws so while using the jargons also explain those concepts before, start from start go on then like a smooth butter from start to end, until the end i should be able to know this whole topic very easily and everything and able to connect all the dots. use very simple language with real world examples(actual indusrty usecases as well) Draw diragrams , arcthitectures, charts plots etc.. i mean best visuals possible where needed (only if impactfull) order the content like a very smartly like i will understood concepts one by one very easily from start and built on top of it until end. where applicatble and provides value give exam triggers and traps. 

2nd file: this file is to crack the aws exam specific. for this get the specifics from exam perspectives for each releated topic/point given in the 1st document wrt to the exam ( it means the first file should contains all the exam specific info+ what and how actual industry is using + aws hands on spcecifications and features and inforamtion of aws). give all the info like how much quesitons from this topic in exam, cheat sheet tables diagrams etc. after all the imp points now create a nice tricky and hard questions exactly similar to actual aws saa exam different variety of questions types are also there i guess. the number of  quesitons depends on how much and what type of it asks from the current topic cover all. Quality of questions matters the most rather than just more number of quesitons.put High quality very hard questions than the actual exam as well in it. 
At the start of this file add the weightage of the current topic and number of quesions asked in exam from this topic.
first for this current chat focus on first documnet so that you would be able to focus and able to create nice one. once done i will ask for the second. Build both files like it creates a muscle memory for each concept and that will happen when i know the whole concepts and its actual industry use, and wire both files like first i will read 1st file it will give me whole context. and while reading second file it will again trigger those exam specific things it will revise me and builds nice memory and concepts.some very hard means majority of them very hard not like what concepts are exactly given in exam cracker sheet or maseterclass notes, many of the current questions are like that only , i dont think so its the case in actual exam.
so best thing is to analyse the deep research and then prepare questons accordingly.

do some additional in depth research on internet for the info/specific concept or topic that is not available in files folder related to the above current topic. continue deep researching , for each subtopic go in depth no hesitation collect as much info as you can i dont want you to go for another deep research wasting my time and token for the gap in this current research so just go all in in one this research only.


i have another idea now 
I want to add the pricing for each service inside each topic in masterclass file. becuase this gives the fair idea of how much will it cost this pertifuclar thing and makes the mind clear and makes understand the aws architecture and their thinking more.
the pricing of each specific thing inside the each topic per month , per hour , per day, if combined with other services how much total will it cost , actual industry parigins of services and their estimated costs,  and all other useful info related to this.
so like then if i am solution architect and i have a certain task to architect something i will already have this most important aspect of pricing , and the actual usecase or problem statement and what is the best trade off possible , this thing will already cleare in my mind which will make me take proper good best decisions. and i want that info to add in maseterclass files, so all in one shot. 

---

## How to write the pricing into each masterclass file (HYBRID — inline tags + end synthesis)

Goal: make cost **concrete at the moment you learn each thing** *and* tie it all together at the end — so as a Solution Architect
the price is already in your head while you design. This is interview gold, not just exam trivia. Use a **hybrid of two layers:**

### Layer 1 — Inline price-tags (bind the number to the concept)

Right where each service / option / tier is taught, drop a **small, plain-English price-tag** — not a big box.
Keep the language dead simple and **always give a per-month estimate, and a per-day one where it helps the feel**:

- *"💵 gp3 storage is about **$0.08 per GB a month** — so a 100 GB disk ≈ **$8/month** (~27¢/day). gp2 is $0.10/GB; io2 is $0.125/GB plus an IOPS charge."*
- *"💵 A t3.medium is roughly **$0.04/hour ≈ $30/month** if left on 24/7 (~$1/day)."*
- *"💵 Spot can be **up to 90% cheaper** than that — the same box for ~$3–9/month — but AWS can reclaim it."*

Rules for inline tags: one or two lines, simple words, round numbers, lead with the monthly figure (people budget monthly).
Show *per-day* when it makes a spiky/short-lived cost click. No big tables inline — that's Layer 2's job.

### Layer 2 — The `💰 COST REALITY` synthesis section (near the end, before the Dublin/industry section)

This is the architect's overview — make it **genuinely visual where it adds value**: clean tables, and **simple SVG bar
charts / comparison bars** for things that are inherently visual (e.g. the storage-class price ladder, On-Demand vs
Reserved vs Spot, Multi-AZ doubling). A chart must *earn its place* — show a ratio or gap the reader should feel; don't draw a chart for two numbers. Reach for *roughly* these beats, and **adapt freely** (a free service like IAM gets two lines, not six):

1. **What you're billed *on*** — the billing dimensions (per-hour? per-GB stored? per-GB out? per-request?). The real gotcha, ~70% of the value.
2. **The headline numbers** — per-hour / per-month (month = 730 hrs), common sizes, in a clean table.
3. **A visual** — an SVG bar chart / ladder where a ratio or gap is the point (storage tiers, pricing models). Only if it adds insight.
4. **The hidden costs** — egress, cross-AZ, NAT data processing, idle resources, retrieval fees. The surprises.
5. **A combined-architecture total** — "small prod app ≈ $X/mo" makes it tangible.
6. **Industry-scale ballpark** — a named-company estimate (clearly labelled an *estimate*).
7. **The one cost lever** — the single trade-off that moves the bill most.

### Sourcing rule (applies to BOTH layers)

**Don't invent numbers per file.** All figures live in the single source of truth:
`deep research gathered info/6_AWS_Pricing_Reference_2026.md` (verified June 2026). Update *there*, then propagate, so the inline
tags, the end tables, and combined examples never contradict each other. **Anchor on us-east-1**, note where **eu-west-1
(Ireland/Dublin)** differs (usually +~10%). Re-verify the exact cents on the AWS pricing page before quoting — prices drift.
Use `💰` for both layers so they read as one connected story.