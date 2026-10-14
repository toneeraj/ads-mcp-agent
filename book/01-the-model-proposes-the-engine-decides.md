# 1 · The model proposes and the engine decides

02:10. A competitor drops the price of a printer-ink listing by 18 per cent overnight. The reasoning layer reads the move as clearance stock and proposes matching it at 38.90. The engine runs the proposal against the floor — cost 33.10 plus fees 8.10, so 41.20 — and prices at 41.20. By morning the listing is still profitable, and the record says why it did not follow.

**A model may propose any action; only a deterministic engine decides what is applied. The boundary between them is a contract, not a prompt.**

```
proposal    match competitor at 38.90
            from: reasoning layer
            why:  competitor clearance
floor       41.20 = cost 33.10 + fees 8.10
decision    41.20, clamped to floor
recorded    proposal, floor, decision, why
```

**Advertising bids.** A search term spikes on a Saturday. The model proposes a bid of 2.40 to win it. The engine's ceiling for that term is what a click is worth: a 10 per cent conversion rate times an 18.50 margin, so 1.85. The bid goes in at 1.85, and the proposal is kept beside it.

**Claims adjudication.** The model reads the adjuster's notes and proposes approval: the damage matches the photos and the amount is in range. The policy engine finds the cover lapsed nine days before the loss. The claim routes to denial, and the model's reading travels with it for the adjuster.

## What it paid

The model can be wrong without the business being wrong.

```
                 model decides         engine decides
wrong reading    applied, then found   clamped, recorded
audit question   why did it?           which rule held?
change control   a prompt edit         a contract change
```

The contract is a vocabulary, and the model only speaks half of it.

```
model may      propose a price, a bid, a verdict
model may not  apply one
engine may     accept, clamp, refuse, route
```

## The gap

Nobody reviews the proposals the engine refused. A model clamped at the floor every night for a month is telling the owner something about either the market or the floor, and no role is assigned to listen. → Chapter 3.

## To graduate

A trace where the boundary was crossed: a model given a write tool directly, with no engine between the call and the effect. Amazon's Ads MCP server does exactly that, and the ads-mcp-agent evaluation puts an approval gate and a spend guard back in the engine's place. The write audit from that run pays for this chapter.
