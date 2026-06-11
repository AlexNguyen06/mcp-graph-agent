import asyncio
import sys
from contextlib import AsyncExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_ROOT = Path(__file__).resolve().parents[1]


SERVER_MODULES = {
    "invalidator": "mcp_servers.mcp_invalidator_server",
    "graph_tools": "mcp_servers.mcp_graph_tools_server",
    "generator": "mcp_servers.mcp_conjecture_generator_server",
    "prover": "mcp_servers.mcp_prover_server",
}


@dataclass
class MCPTool:
    server: str
    name: str
    description: str
    input_schema: dict[str, Any]

    @property
    def agent_name(self) -> str:
        return f"{self.server}__{self.name}"


class MCPGraphClient:
    def __init__(self) -> None:
        self._stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self.tools: dict[str, MCPTool] = {}

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def connect(self) -> None:
        for server_name, module in SERVER_MODULES.items():
            params = StdioServerParameters(
                command=sys.executable,
                args=["-m", module],
                cwd=str(PROJECT_ROOT),
            )
            read_stream, write_stream = await self._stack.enter_async_context(stdio_client(params))
            session = await self._stack.enter_async_context(ClientSession(read_stream, write_stream))
            await session.initialize()
            self.sessions[server_name] = session

            listed = await session.list_tools()
            for tool in listed.tools:
                schema = getattr(tool, "inputSchema", None) or {}
                description = getattr(tool, "description", "") or ""
                mcp_tool = MCPTool(server_name, tool.name, description, schema)
                self.tools[mcp_tool.agent_name] = mcp_tool

    async def close(self) -> None:
        await self._stack.aclose()

    def ollama_tools(self) -> list[dict[str, Any]]:
        schemas = []
        for tool in self.tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.agent_name,
                    "description": tool.description,
                    "parameters": tool.input_schema or {"type": "object", "properties": {}},
                },
            })
        return schemas

    async def call_tool(self, server: str, tool: str, arguments: dict[str, Any]) -> Any:
        session = self.sessions[server]
        result = await session.call_tool(tool, arguments)
        if result.content:
            first = result.content[0]
            return getattr(first, "text", first)
        return result

    async def call_agent_tool(self, agent_tool_name: str, arguments: dict[str, Any]) -> Any:
        tool = self.tools[agent_tool_name]
        return await self.call_tool(tool.server, tool.name, arguments)


async def smoke_test() -> dict[str, list[str]]:
    async with MCPGraphClient() as client:
        return {
            server: sorted(tool.name for tool in client.tools.values() if tool.server == server)
            for server in SERVER_MODULES
        }


if __name__ == "__main__":
    print(asyncio.run(smoke_test()))
