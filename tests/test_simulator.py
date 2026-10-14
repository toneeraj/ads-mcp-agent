"""Smoke test: start the simulator over stdio, list tools, read and write."""
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

SERVER = Path(__file__).resolve().parent.parent / "simulator" / "server.py"


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = [t.name for t in (await session.list_tools()).tools]
            print("tools:", tools)
            assert "update_campaign_budget" in tools
            perf = await session.call_tool(
                "get_campaign_performance", {"campaign_id": "c-auto"})
            print("perf:", perf.content[0].text[-200:])
            res = await session.call_tool(
                "update_campaign_budget",
                {"campaign_id": "c-auto", "daily_budget": 6.0})
            print("write:", res.content[0].text)
            bad = await session.call_tool(
                "update_campaign_budget",
                {"campaign_id": "c-auto", "daily_budget": 0.5})
            print("refused:", bad.isError, bad.content[0].text[:80])
            assert bad.isError


asyncio.run(main())
