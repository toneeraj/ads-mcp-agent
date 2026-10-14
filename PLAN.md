# Plan — what happens while the book is in review

**Purpose:** the working checklist for the ads-mcp-agent evaluation, from book review through API access. Ticked items are done.

## Gate status

| Gate | Status |
|---|---|
| Book submitted to KDP | Done 14 Oct 2026 — in review (up to 72 hours) |
| Book live on Amazon | Waiting |
| One week of Sponsored Products history | Not started |
| Ads API access approved | Not applied |

## Owner — can do now

- [x] Anthropic API key in its own workspace, spend limit set, stored in 1Password
- [x] Book written and submitted
- [ ] Create an Amazon Developer account at developer.amazon.com, with the same personal Amazon login
- [ ] Create a Login with Amazon security profile named `ads-mcp-agent`; store its client ID and secret in 1Password
- [ ] Read the Amazon Ads Advanced Tools Center MCP page and note the official tool list (fills the simulator's biggest assumption)
- [ ] Decide the campaign budget: suggested $5 a day, automatic targeting, one week
- [ ] Draft three to five plain-language questions you will ask the agent first (what you actually want to know about the campaign)

## Owner — once the book is live

- [ ] Check the Amazon page: author line, description, price, cover as a thumbnail
- [ ] KDP → Marketing → Amazon Ads → one Sponsored Products campaign, $5 a day, automatic targeting
- [ ] After about a week: apply for Ads API access as a direct advertiser
- [ ] When approved: consent from the author profile only; refresh token into 1Password

## Builder — can do now (no credentials needed)

- [x] A1 Ads MCP simulator: eight tools (five reads, three writes) over fixture data for the book's campaigns — `simulator/server.py`, smoke test `tests/test_simulator.py`
- [ ] A2 Agent orchestrator, MCP client, approval gate, spend guard
- [ ] A3 Chat interface and change history page
- [ ] A4 Write audit, invocation log, coverage gaps
- [ ] A5 Run guide: one command to start, keys read from 1Password
- [ ] A6 Token manager and Amazon endpoint behind the endpoint selector
- [ ] A7 Fly.io deployment configuration: Flycast, secrets, volume, daily machine check

## Book — can do anytime

- [ ] Rewrite chapter 1 in your own words (first step towards AI-assisted)
- [ ] Note the real surprise behind two or three of the rules in chapter 18
- [ ] Add each new surprise from the experiment as it happens; one row in the revision history per edition

---

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-14 | Plan created while the book is in review |
| 0.2 | 2026-10-14 | A1 simulator built and tested |
