# ads-mcp-agent

**Purpose:** a personal experiment to find out what an AI agent can and cannot do to a real Amazon Ads account through Amazon's hosted MCP server, before anything bespoke is built.

## The MCP server is a new caller for the same Ads API, not a new capability

Every tool the server exposes ends up as one or more ordinary Ads API calls. Rate limits, costs and account permissions are exactly what they would be if those calls were made directly. The server earns its place only when a model decides at run time which tool to call. Fixed, scheduled work — pausing at five, nightly reconciles — stays on the direct API with no model involved.

```
you ─▶ chat page ─▶ model ──picks a tool──▶ MCP server
          │                                    │
          ▼                                    ▼
     write log + cap check            Amazon Ads (or fake)
```

## Terms and definitions

| Term | Meaning |
|---|---|
| **MCP server** | A service that lists tools an AI agent may call and turns each call into real API requests. Amazon hosts one for Ads at a regional endpoint. |
| **Tool** | One named operation on the MCP server, such as reading campaign performance or updating a budget. One tool may make several Ads API calls. |
| **MCP client** | The code that asks the server which tools exist and calls them. Here it lives in this app. |
| **Profile** | One advertiser account in one marketplace. Every Ads call is scoped to a profile. |
| **Fake server** | A local MCP server in this repo with the same tool shapes, used until Amazon approves API access. |
| **Write** | Any tool call that changes the account: budget, bid, status, targeting. |
| **Cap** | A spend ceiling this app checks before letting a write through. |

## What the experiment answers

| Question | How it gets answered |
|---|---|
| Which plain-language asks map to a tool, and which don't | Asking for everything an ad manager would want |
| How many API calls one ask costs | Counting calls per conversation |
| Whether Amazon previews a write before applying it | The first budget change |
| Whether an author profile works through the MCP server | Listing profiles once access is approved |
| Where the agent needs knowledge Amazon doesn't hold | Asks about cannibalisation, organic sales, which product leads |

## The agent is allowed to act

This is deliberately AI-managed: the agent makes changes itself, because finding its limits is the point. Three guardrails keep that cheap.

| Guardrail | Why |
|---|---|
| Agent states the change and waits for yes | Tests whether intent survives translation |
| Every write logged by this app, with before and after values | The MCP result is not an audit trail |
| Writes refused above the cap | A misread "make it bigger" costs little |

## Scope

| In | Out |
|---|---|
| One chat page, one profile | Scheduling, dayparting execution, nightly jobs |
| Reads: campaigns, spend, performance, search terms | Multiple accounts or marketplaces |
| Writes: budget, bid, status | Anything from merc-ads-service's domain model |

## Build choices

| Choice | Decided | Rejected option's cost |
|---|---|---|
| Language | Python | Spring Boot: slower to change while the questions are still moving |
| Model | Claude API, called directly | Databricks: needs a personal workspace for no gain here |
| Until approval | Fake server first, Amazon's endpoint behind one setting | Amazon only: nothing runs for weeks |

## Path to a live account

| Step | Gate it clears |
|---|---|
| Publish a short ebook on KDP; run one Sponsored Products campaign in the console for a week | Real advertising activity for the API application |
| Apply for Ads API access as a direct advertiser | API credentials |
| Point this app at Amazon's MCP endpoint and list profiles | Whether an author profile is accepted |
| If not, create an AUTHOR test account from a second Amazon login | A no-spend account that works through the API |
| If neither works, open a Professional seller account | Sponsored Products as a seller, with the Buy Box delay |

## Assumptions

| Assumption | Why it matters | Load-bearing |
|---|---|---|
| Amazon's MCP server accepts a Login with Amazon access token plus client-ID header, as reported for the closed beta | The app's auth is built on it | Yes |
| A KDP author profile is reachable through the Ads API | The cheap route to a live account depends on it | Yes |
| A small account with a week of campaigns is approved as a direct advertiser | Nothing live happens without it | Yes |
| Test accounts work through the MCP server, not only the direct API | The no-spend fallback depends on it | No |
| The official tool list resembles the third-party lists used to shape the fake server | The fake server's value depends on it | No |

---

| Version | Date | Prepared by | Change |
|---|---|---|---|
| 0.1 | 2026-10-14 | Neeraj Singh | First proposal |
