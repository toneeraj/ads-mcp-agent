# ads-mcp-agent

**Purpose:** a personal experiment to find out what an AI agent can and cannot do to a real Amazon Ads account through Amazon's hosted MCP server, before anything bespoke is built.

## The MCP server is a new caller for the same Ads API, not a new capability

Every tool the server exposes ends up as one or more ordinary Ads API calls. Rate limits, costs and account permissions are exactly what they would be if those calls were made directly. The server earns its place only when a model decides at run time which tool to call. Fixed, scheduled work — pausing at five, nightly reconciles — stays on the direct API with no model involved.

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
| **Flycast** | A Fly.io option that gives an app only a private address, with no public IP. |
| **WireGuard** | The VPN Fly.io uses to let your own devices join that private network. |

## What the experiment answers

| Question | How it gets answered |
|---|---|
| Which plain-language asks map to a tool, and which don't | Asking for everything an ad manager would want |
| How many API calls one ask costs | Counting calls per conversation |
| Whether Amazon previews a write before applying it | The first budget change |
| Whether an author profile works through the MCP server | Listing profiles once access is approved |
| Where the agent needs knowledge Amazon doesn't hold | Asks about cannibalisation, organic sales, which product leads |

## Architecture

![ads-mcp-agent architecture](docs/architecture.svg)

| Layer | Box | What it does |
|---|---|---|
| People | You | The only user: asks in plain words and approves every write |
| What you open | Chat page | Where you ask, read the agent's plan, and answer yes or no |
| | Write log page | Every change made, with before and after values |
| What runs | Agent loop | Sends the conversation and the tool list to the model; gets back the tool it wants to call |
| | Confirm gate | Holds any write until you say yes; reads pass straight through |
| | Cap check | Refuses a write that would take a budget above the cap |
| | MCP client | Lists the server's tools and calls the one the model chose |
| What it writes | Write log | Each change, its previous value, and the yes that allowed it |
| | Call log | Each ask, the tools it used, and how many calls it took |
| | Tool gaps | Asks the agent could not answer with any tool |
| How it reaches Amazon | Endpoint switch | One setting: the fake server, or Amazon's North America endpoint |
| | Token refresher | Swaps the stored refresh token for an access token every hour |
| | Secrets | API keys and the refresh token, held by the host and never committed |
| Everything else | Claude API | The model, called directly |
| | Fake MCP server | Same tool shapes as Amazon's, so the whole loop runs today |
| | Amazon Ads MCP | Amazon's hosted server, used once access is approved |
| | Login with Amazon | Issues the access tokens Amazon's server requires |

The diagram is generated: edit `docs/architecture.py` and run it, never the SVG.

## The agent is allowed to act

This is deliberately AI-managed: the agent makes changes itself, because finding its limits is the point. The confirm gate, the cap check and the write log are what keep that cheap.

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
| Until approval | Fake server first, Amazon's endpoint behind the endpoint switch | Amazon only: nothing runs for weeks |
| Where it runs, phase 1 | Your laptop | Fly.io now: hosting a fake server buys nothing |
| Where it runs, phase 2 | Fly.io, private only, through Flycast | Public URL with a login: one auth bug exposes a key that can spend money |

## Fly.io only once the app holds a real token

Before Amazon approves access, nothing in the app is worth protecting and the laptop is enough. Once the refresh token is real, the app can change live spend, and Fly.io earns its place: the app runs while the laptop is off, secrets live with the host, and a volume keeps the logs.

| Protection | What it stops |
|---|---|
| Deploy with Flycast: the app gets a private address and no public IP | Anyone on the internet reaching the chat page |
| Reach it over WireGuard from your laptop and phone only | Every device you haven't joined to the network |
| A shared access token checked by the app itself | Anything else on the private network calling it; Flycast is not authentication |
| API keys and the refresh token set as Fly secrets, never in the repo | A leaked repo leaking credentials |
| Consent for the refresh token given only on the test or author profile | The agent reaching any other account |
| Cap check in the app, plus a low daily budget on the campaign itself | A wrong write spending more than a few dollars |
| A monthly spend limit on the Claude API key | A runaway loop running up model costs |
| Revoke the app's Login with Amazon consent when the experiment ends | A token outliving its purpose |

## The book exists to give the experiment real data

A KDP ebook is the cheapest way to a live advertising profile. What it needs is search terms people actually use, so the campaign gets impressions and clicks for the agent to reason about.

| Option | What it gives the experiment | Cost |
|---|---|---|
| A short first volume of the AI-First Design book, written by you | Real, competitive search terms; content worth reading | Bids are higher on busy terms; $100 buys fewer clicks |
| A short guide on a narrow hobby topic | Cheap clicks, quick data | Thin search volume; fewer impressions to learn from |
| Anything about Amazon advertising | — | Overlaps with your day job; avoid |

KDP requires disclosure when text or images were created by AI, even if heavily edited afterwards. Material you wrote yourself, with AI only editing or checking it, does not need disclosing. A book you write keeps both the listing and the experiment clean.

## Path to a live account

| Step | Gate it clears |
|---|---|
| Publish the ebook on KDP; run one Sponsored Products campaign in the console for a week | Real advertising activity for the API application |
| Apply for Ads API access as a direct advertiser | API credentials |
| Switch the endpoint to Amazon's and list profiles | Whether an author profile is accepted |
| If not, create an AUTHOR test account from a second Amazon login | A no-spend account that works through the API |
| If neither works, open a Professional seller account | Sponsored Products as a seller, with the Buy Box delay |

## Assumptions

| Assumption | Why it matters | Load-bearing |
|---|---|---|
| Amazon's MCP server accepts a Login with Amazon access token plus client-ID header, as reported for the closed beta | The token refresher and endpoint switch are built on it | Yes |
| A KDP author profile is reachable through the Ads API | The cheap route to a live account depends on it | Yes |
| A small account with a week of campaigns is approved as a direct advertiser | Nothing live happens without it | Yes |
| Test accounts work through the MCP server, not only the direct API | The no-spend fallback depends on it | No |
| The official tool list resembles the third-party lists used to shape the fake server | The fake server's value depends on it | No |

---

| Version | Date | Prepared by | Change |
|---|---|---|---|
| 0.1 | 2026-10-14 | Neeraj Singh | First proposal |
| 0.2 | 2026-10-14 | Neeraj Singh | Architecture diagram, Fly.io hosting and security, book choice |
