# Consolidated Project Log

This file consolidates project activity that is traceable from repository artifacts through 2026-03-29.

## Sources Used

- `Documentation/MeetingMinutes/*.md`
- `Documentation/WorkEntryLogs/*.md`
- `Documentation/WorkEntryLogs/ITR*_archive-logs/*`
- `git log`, merge history, and file history on the current repository

## Traceability Notes

- `Documented` means the detail appears directly in a meeting minute, work log, or commit message.
- `Derived` means the value was computed from logged start and end times.
- `Not documented` means the repository shows the work landed, but no estimate or actual duration was recorded in the checked-in logs.
- This is a repository-based log, not a Jira export, so it only covers work that is traceable from the repo.

## Meeting Minutes Summary

| Meeting | Date | Duration | Main outcomes |
| --- | --- | --- | --- |
| 01 | 2026-01-24 | 1h30m | Team name chosen, GitHub Classroom and Jira set up, recurring Friday meetings established. |
| 02 | 2026-02-09 | ~1h | Planned ITR0/ITR1 work, assigned tasks, discussed project design, set up Jira tasks. |
| 03 | 2026-02-13 | ~1h30m | Closed out ITR0, checked ITR1 release readiness, reviewed GUI demo, planned README, model, and architecture docs. |
| 04 | 2026-02-23 | 4h | Major scope pivot to stitched batch video analytics, removal of live processing, addition of checkout-camera analytics and stronger database focus. |
| 05 | 2026-03-01 | ~2h | Finalized ITR1 presentation, peer review, documentation links, and submission checks. |
| 06 | 2026-03-02 | ~1h30m | Divided work by processing component, prioritized mock data and path construction before integration, flagged disagreement on product placement strategy. |
| 07 | 2026-03-04 | 1h | Removed `race`, changed `age` to categorical ranges, and standardized aisles to vertical orientation. |
| 08 | 2026-03-17 | Not specified | Planned analytics-heavy ITR3: market basket analysis, demographic analytics, heatmaps, graphing, sales import, and synthetic data generation. |
| 09 | 2026-03-18 | 2h | Assigned analytics stories by teammate, standardized graph data format, defined heatmap approach, and split storage between DB path data and CSV sales data. |
| 10 | 2026-03-23 | 2h | Planned ITR3 completion timeline, target date for GUI analytics completion, and next deliverable work. |

## Rationale Behind Plan Changes and Major Design Decisions

| Date / source | Change | Rationale in repo | Impact |
| --- | --- | --- | --- |
| 2026-02-23, Meeting 04 | Shifted from full store map view to a single stitched camera overview | Documented: this simplified processing and aligned the product with analytics instead of surveillance. | Reduced scope and made later video-processing work batch-oriented. |
| 2026-02-23, Meeting 04 | Removed live camera processing | Documented: live mode was considered too complex, redundant with existing security cameras, and misaligned with product focus. | Led directly to KAN-71 and the stitched-video workflow. |
| 2026-02-23, Meeting 04 | Added checkout camera, demographic capture, and market basket analysis | Documented: team wanted purchase-behavior and demographic insights in addition to movement tracking. | Expanded the data model and analytics backlog. |
| 2026-02-23, Meeting 04 | Added database-backed storage for customer, purchase, and movement data | Documented: database integration was needed to persist demographics, purchase behavior, and zone analytics. | Drove database setup, schema changes, and later analytics queries. |
| 2026-03-02, Meeting 06 | Divided work by processing component and prioritized mock data/path construction | Documented: the team agreed to focus on generated data and path construction before full integration. | Reduced integration risk and enabled analytics work before real data collection stabilized. |
| 2026-03-04, Meeting 07 | Removed `race`, changed `age` to age-range strings, and made aisles vertical | Partly documented, partly inferred: the notes record the schema/layout change but do not explain the reason in detail; likely this simplified analytics categories and aligned the store-layout model. | Required model, test, and analytics updates. |
| 2026-03-17, Meeting 08 | Expanded the plan from core processing into analytics dashboards and graphs | Documented: team defined graph types, heatmaps, sales import, and synthetic data generation for the next phase. | Created the KAN-113/116, 125-141, 158, and 163 work cluster. |
| 2026-03-17, Meeting 08 | Assumed self-checkout demographic analysis with temporary negative IDs | Documented: temporary IDs would be reconciled later with path and checkout timestamps. | Introduced an identity-matching assumption and later data-reconciliation risk. |
| 2026-03-18, Meeting 09 | Standardized graph data contracts around dictionaries / paired lists | Documented: the team wanted all graph inputs to follow a matching label/value format. | Helped connect backend analytics modules to the GUI graph window. |
| 2026-03-18, Meeting 09 | Split path data into DB storage and sales data into CSV storage | Documented in meeting notes. | Influenced data generator, import, and analytics implementation boundaries. |
| 2026-03-28 to 2026-03-29, git history | Entered bug-fix and refactor phase for analytics | Documented by PRs and commits fixing aisle averages, customer aisle analytics, customer conversion, and duplicated logic. | Indicates late-stage stabilization after the main analytics stories landed. |

## Concerns With The Project Or Group Members

### Project concerns documented in the repo

- The team explicitly struggled to agree on product placement strategy in Meeting 06.
- The stitched-video design depends on similar camera angles for successful preprocessing, which Meeting 04 records as a constraint.
- Meeting 08 introduced a temporary negative-ID reconciliation assumption for self-checkout demographics; that is a project risk because identity matching is deferred.
- The repo shows several late bug-fix branches after the main analytics merge wave:
  - incorrect aisle-time average denominator
  - incorrect `customer_x_sales` hour field
  - incorrect sex/age mapping in `customerAisleAnalytics`
  - duplicated logic cleanup in section-time analysis
- Work-log coverage is incomplete. Several merged stories have code and PR evidence but no checked-in time log, so time accounting is only partial.

### Group-member concerns found in the repo

- No explicit interpersonal or member-performance concerns were documented in the repository materials I reviewed.
- The only team-composition note is in Meeting 04, where the team recorded that a student had reached out about joining; later records show Sheila participating in assignments and authored meeting minutes.

## Task Assignments Captured In Meetings

### Meeting 06: processing split

| Member | Assigned work |
| --- | --- |
| Ryan | Setup process, stitching logic, aisle positioning / store layout setup |
| Mani | Customer-position detection per frame, multi-customer path generation, database schema updates |
| Jeduson | Single-frame customer demographic processing |
| Sheila | Mock data generation and customer-path construction |
| Everyone | One unified analysis function |

### Meeting 08: analytics split

| Member | Assigned work |
| --- | --- |
| Ryan | GUI, graph generation, sales transaction import |
| Mani | Market basket analysis, data generation, aisle / section / store time analysis |

### Meeting 09: ITR3 analytics split

| Member | Assigned work |
| --- | --- |
| Mani | Basket analysis, data generation, aisle time spent, aisle + section time spent, store time spent |
| Jeduson | Product x gender, product x age, product category x age, product category x gender |
| Sheila | Customer conversion, product x revenue, heat map, product x quantity |
| Ryan | Graphics and graph creation from the analytics functions |

## Development Tasks Per User Story

### ITR0 and ITR1 foundation work

| Story / task | Owner | Development task summary | Evidence | Original allocation | Actual time spent | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Customer meeting summary video | Ryan | Customer interview, video edit, and summary preparation | ITR0 archived work log | 3h | 6h40m | Over estimate by 3h40m. |
| IT0 KAN-7 Vision Statement | Ryan | Drafted the project vision statement | ITR0 archived work log | 2h | 2h15m | Slight overrun. |
| IT0 KAN-9 / KAN-10 User Stories | Jeduson | Created big and detailed user stories | ITR0 archived work log | 4h | 4h | On estimate. |
| KAN-21 Wiki (ITR1) | Jeduson | Base wiki text, formatting, and image formatting | ITR1 archived work log | 2h | 2h | On estimate. |
| KAN-36 Compiled Python App (ITR1) | Ryan | Packaging / compiled app support | ITR1 archived work log | 3h | 1h30m derived | Work log is sparse and may be incomplete. |
| KAN-51 General Layout (ITR1) | Ryan | Built general UI layout | ITR1 archived work log | 4h | 4h by timestamps; 5h as written | Logged durations are internally inconsistent. |

### ITR2 architecture and core pipeline work

| Story / task | Owner | Development task summary | Evidence | Original allocation | Actual time spent | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| KAN-71 Remove Live Camera Feed | Ryan | Removed live camera functionality after the scope pivot | Archived work log + PR #18 | 30m | 45m | Direct follow-through from Meeting 04. |
| KAN-74 / KAN-76 Video Stitching and Zones | Ryan | Implemented stitching and zone tooling in the GUI | Archived work log + branch history | 6h | 9h | Large overrun. |
| KAN-75 Customer Attribute Estimator Logic | Jeduson | Implemented age / sex estimator logic and tests | Archived work log + file history | 9h25m | 9h25m derived | Logged as two time ranges. |
| KAN-77 Construct Customer Path | Sheila | Built path-construction logic and tests | PR #19 + `src/path_constructor.py` history | Not documented | Not documented | Story is traceable in git, but no checked-in time log was found. |
| KAN-101 Customer Video Path Generation | Mani | Researched detection library, implemented coordinate extraction and path tracking, stored results, added tests | Archived work log + PR #24 | 7h | 7h | On estimate. |
| GUI and Integration Testing | Ryan | Added integration and GUI tests for main workflows | Archived work log + test history | 3h | 3h30m | Slight overrun. |
| KAN-29 Wiki Update | Ryan | Wiki update work | Archived work log | 1h | 1h | On estimate. |
| KAN-109 Jupyter Notebook Showcase | Ryan | Built notebook / showcase animation work | Archived work log | 4h | 1h30m | Finished under estimate. |

### ITR3 analytics work

| Story / task | Owner | Development task summary | Evidence | Original allocation | Actual time spent | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| KAN-113 to KAN-116 Customer / product analytics | Jeduson | Implemented product/category x age/sex analytics and tests | Current work log + PR #34 + `customerAisleAnalytics` / `customerProductAnalytics` history | Not documented | 8h | Work log aggregates four analytics stories into one entry. |
| KAN-125 Basket Analysis | Mani | Implemented basket metrics, association rules, summaries, and tests | Current work log + PR #33 | 5h | 5h | On estimate. |
| KAN-126 Data Generation | Mani | Generated product, layout, customer, transaction, and path data plus visualization helpers | Current work log + PR #26 | 2h | 3h | Over estimate by 1h. |
| KAN-127 Aisle Time Spent | Mani | Implemented aisle time analysis and tests | Meeting 09 + PR #27 + `aisleTimeAnalysis.py` history | Not documented | Not documented | Code landed, but no dedicated time log was found. |
| KAN-128 Aisle Section Time Spent | Mani | Implemented section-time analysis and tests | Current work log + PR #28 | 4h | 4h | On estimate. |
| KAN-135 Customer Conversion / Customer x Sales | Sheila | Implemented customer conversion analytics and tests | Meeting 09 + PR #39 + `customer_x_sales.py` history | Not documented | Not documented | Later bug-fix PR on 2026-03-29 corrected the hour field used. |
| KAN-136 Product x Revenue | Sheila | Implemented product revenue aggregation | Meeting 09 + PR #37 + `product_x_revenue.py` history | Not documented | Not documented | No checked-in work log found. |
| KAN-137 Heat Map Generator | Sheila | Implemented core heatmap generation functions and layout overlay support | Meeting 09 + PR #41 + `src/HeatMapGenerator/heatmap_generator.py` history | Not documented | Not documented | KAN-141 later covered UI integration time. |
| KAN-138 Product x Quantity | Sheila | Implemented product quantity analytics and tests | Meeting 09 + PR #38 + `product_x_quantity.py` history | Not documented | Not documented | No checked-in work log found. |
| KAN-139 Graph Views | Ryan | Built analytics window framework, graph wiring, tabs, and view controls | Current work log + `dataAnalyticsWindow.py` history | 10h | 12h45m | Major overrun during UI integration. |
| KAN-140 Sales Transaction Import | Ryan | Added sales-transaction import support for analytics | Current work log + file history | 1h | 20m | Completed under estimate. |
| KAN-141 Heatmap View | Ryan | Integrated heatmap rendering, progress, and video display into the GUI | Current work log + PR #46 + file history | 2h | 4h30m | Significant overrun. |
| KAN-158 Assorted Information View | Ryan | Split analytics into separate tabs and added supporting UI | Current work log + file history | 1h | 1h20m | Slight overrun. |
| KAN-163 Popup Window | Ryan | Added popup / warning window support and related UI hooks | Current work log + PR #32 | 1h | 50m | Completed under estimate. |

## Overall Observations

- The best-documented time accounting is for ITR0, most of ITR2, and the subset of ITR3 stories that have dedicated work-log files.
- The weakest traceability area is several ITR3 analytics stories and some early ITR2 stories: the code and merges are present, but the repository does not include matching time logs.
- Ryan's late-March work shows a transition from base graph scaffolding into integration-heavy UI tasks, especially for graph composition, heatmap display, and packaging/pathing fixes.
- The analytics phase ended with a visible quality-hardening pass in git history, which suggests the team reached functional completeness before it reached full stability.
