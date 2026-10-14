"""Ads MCP simulator: a local stand-in for Amazon's Ads MCP server.

Implements a small set of Sponsored Products tools against fixture data in a
local SQLite file, so the agent loop can be built and tested without Amazon
API access. Tool names and shapes are modelled on published third-party Ads
MCP servers; Amazon's official catalogue may differ (see README, Assumptions).

Run over stdio:  python simulator/server.py
Reset state:     python simulator/server.py --reset
"""
from __future__ import annotations

import random
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DB_PATH = Path(__file__).with_name("state.db")
PROFILE_ID = "sim-author-us-1"
TODAY = date(2026, 10, 14)

mcp = FastMCP("ads-mcp-simulator")


# --- storage ---------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS campaigns (
  campaign_id TEXT PRIMARY KEY, profile_id TEXT, name TEXT,
  targeting TEXT, state TEXT, daily_budget REAL);
CREATE TABLE IF NOT EXISTS keywords (
  keyword_id TEXT PRIMARY KEY, campaign_id TEXT, text TEXT,
  match_type TEXT, state TEXT, bid REAL);
CREATE TABLE IF NOT EXISTS performance (
  campaign_id TEXT, day TEXT, impressions INTEGER, clicks INTEGER,
  spend REAL, orders INTEGER, sales REAL,
  PRIMARY KEY (campaign_id, day));
CREATE TABLE IF NOT EXISTS search_terms (
  campaign_id TEXT, term TEXT, impressions INTEGER, clicks INTEGER,
  spend REAL, orders INTEGER);
"""


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def seed(con: sqlite3.Connection) -> None:
    """Fixture data: one author profile, the book's two campaigns."""
    con.executescript(SCHEMA)
    if con.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]:
        return
    con.executemany(
        "INSERT INTO campaigns VALUES (?,?,?,?,?,?)",
        [("c-auto", PROFILE_ID, "AI-First Design - Auto", "auto",
          "enabled", 5.00),
         ("c-manual", PROFILE_ID, "AI-First Design - Manual", "manual",
          "paused", 3.00)])
    con.executemany(
        "INSERT INTO keywords VALUES (?,?,?,?,?,?)",
        [("k-1", "c-manual", "ai agent design", "phrase", "enabled", 0.60),
         ("k-2", "c-manual", "ai system architecture", "phrase",
          "enabled", 0.55),
         ("k-3", "c-manual", "human in the loop ai", "exact", "enabled",
          0.45)])
    rng = random.Random(42)
    for i in range(14, 0, -1):
        day = (TODAY - timedelta(days=i)).isoformat()
        impressions = rng.randint(300, 900)
        clicks = rng.randint(2, 12)
        spend = round(min(clicks * rng.uniform(0.35, 0.65), 5.00), 2)
        orders = 1 if rng.random() < 0.25 else 0
        con.execute("INSERT INTO performance VALUES (?,?,?,?,?,?,?)",
                    ("c-auto", day, impressions, clicks, spend, orders,
                     round(orders * 2.99, 2)))
    con.executemany(
        "INSERT INTO search_terms VALUES (?,?,?,?,?,?)",
        [("c-auto", "ai design book", 1840, 22, 10.12, 2),
         ("c-auto", "agentic ai", 2310, 31, 15.50, 1),
         ("c-auto", "machine learning textbook", 980, 14, 6.30, 0),
         ("c-auto", "prompt engineering", 1205, 9, 4.05, 0)])
    con.commit()


def open_db() -> sqlite3.Connection:
    con = connect()
    seed(con)
    return con


def campaign_row(con, campaign_id: str) -> dict:
    row = con.execute("SELECT * FROM campaigns WHERE campaign_id=?",
                      (campaign_id,)).fetchone()
    if row is None:
        raise ValueError(f"No campaign with id {campaign_id!r}")
    return dict(row)


# --- read tools --------------------------------------------------------------

@mcp.tool()
def list_profiles() -> list[dict]:
    """List advertising profiles this account can reach. Cheapest call; use
    it first to find the profile_id."""
    return [{"profile_id": PROFILE_ID, "country": "US", "currency": "USD",
             "account_type": "author", "name": "Neeraj Singh (simulated)"}]


@mcp.tool()
def list_campaigns(profile_id: str) -> list[dict]:
    """List Sponsored Products campaigns for a profile, with state and daily
    budget in USD."""
    with open_db() as con:
        rows = con.execute("SELECT * FROM campaigns WHERE profile_id=?",
                           (profile_id,)).fetchall()
    return [dict(r) for r in rows]


@mcp.tool()
def get_campaign_performance(campaign_id: str, days: int = 7) -> dict:
    """Daily impressions, clicks, spend, orders and sales for a campaign over
    the last `days` days (max 14), plus totals and ACoS (spend / sales).
    Sales for the most recent days may still grow as late orders are
    attributed."""
    days = max(1, min(days, 14))
    with open_db() as con:
        campaign_row(con, campaign_id)
        rows = [dict(r) for r in con.execute(
            "SELECT * FROM performance WHERE campaign_id=? "
            "ORDER BY day DESC LIMIT ?", (campaign_id, days)).fetchall()]
    totals = {k: round(sum(r[k] for r in rows), 2)
              for k in ("impressions", "clicks", "spend", "orders", "sales")}
    totals["acos"] = (round(totals["spend"] / totals["sales"], 3)
                      if totals["sales"] else None)
    return {"campaign_id": campaign_id, "days": list(reversed(rows)),
            "totals": totals}


@mcp.tool()
def get_search_terms(campaign_id: str) -> list[dict]:
    """Shopper search terms that triggered the campaign's ads, with clicks,
    spend and orders. Useful for finding wasted spend."""
    with open_db() as con:
        campaign_row(con, campaign_id)
        rows = con.execute("SELECT * FROM search_terms WHERE campaign_id=? "
                           "ORDER BY spend DESC", (campaign_id,)).fetchall()
    return [dict(r) for r in rows]


@mcp.tool()
def list_keywords(campaign_id: str) -> list[dict]:
    """Keywords in a manual campaign, with match type, state and bid in
    USD."""
    with open_db() as con:
        campaign_row(con, campaign_id)
        rows = con.execute("SELECT * FROM keywords WHERE campaign_id=?",
                           (campaign_id,)).fetchall()
    return [dict(r) for r in rows]


# --- write tools ---------------------------------------------------------------

@mcp.tool()
def update_campaign_budget(campaign_id: str, daily_budget: float) -> dict:
    """WRITE. Set a campaign's daily budget in USD. Changes live spend.
    Returns the previous and new values."""
    if daily_budget < 1.0:
        raise ValueError("Daily budget must be at least 1.00 USD")
    with open_db() as con:
        before = campaign_row(con, campaign_id)["daily_budget"]
        con.execute("UPDATE campaigns SET daily_budget=? WHERE campaign_id=?",
                    (round(daily_budget, 2), campaign_id))
    return {"campaign_id": campaign_id, "field": "daily_budget",
            "before": before, "after": round(daily_budget, 2)}


@mcp.tool()
def update_campaign_state(campaign_id: str, state: str) -> dict:
    """WRITE. Set a campaign's state to 'enabled' or 'paused'. Returns the
    previous and new values."""
    if state not in ("enabled", "paused"):
        raise ValueError("state must be 'enabled' or 'paused'")
    with open_db() as con:
        before = campaign_row(con, campaign_id)["state"]
        con.execute("UPDATE campaigns SET state=? WHERE campaign_id=?",
                    (state, campaign_id))
    return {"campaign_id": campaign_id, "field": "state",
            "before": before, "after": state}


@mcp.tool()
def update_keyword_bid(keyword_id: str, bid: float) -> dict:
    """WRITE. Set a keyword's bid in USD per click. Returns the previous and
    new values."""
    if not 0.02 <= bid <= 10.0:
        raise ValueError("Bid must be between 0.02 and 10.00 USD")
    with open_db() as con:
        row = con.execute("SELECT bid FROM keywords WHERE keyword_id=?",
                          (keyword_id,)).fetchone()
        if row is None:
            raise ValueError(f"No keyword with id {keyword_id!r}")
        con.execute("UPDATE keywords SET bid=? WHERE keyword_id=?",
                    (round(bid, 2), keyword_id))
    return {"keyword_id": keyword_id, "field": "bid",
            "before": row["bid"], "after": round(bid, 2)}


if __name__ == "__main__":
    if "--reset" in sys.argv:
        DB_PATH.unlink(missing_ok=True)
        open_db().close()
        print(f"reset {DB_PATH}")
    else:
        mcp.run()
