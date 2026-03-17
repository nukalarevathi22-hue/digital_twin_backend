#!/usr/bin/env python3
"""
Render MCP Server - Manage Render deployments from Copilot Chat
"""

import os
import json
import asyncio
import requests
from typing import Any
import subprocess
import sys

# MCP SDK imports
try:
    from mcp.server import Server, stdio_server
    from mcp.types import (
        Tool, 
        TextContent,
        ToolResult,
    )
except ImportError:
    print("Installing MCP SDK...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server import Server, stdio_server
    from mcp.types import Tool, TextContent, ToolResult

# Initialize MCP Server
server = Server("render-mcp-server")

RENDER_API_URL = "https://api.render.com/v1"
RENDER_API_TOKEN = os.getenv("RENDER_API_TOKEN")

if not RENDER_API_TOKEN:
    print("Error: RENDER_API_TOKEN not set")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {RENDER_API_TOKEN}",
    "Content-Type": "application/json"
}

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> ToolResult:
    """Handle MCP tool calls"""
    
    if name == "get_services":
        return await get_services()
    
    elif name == "get_service_status":
        service_id = arguments.get("service_id")
        return await get_service_status(service_id)
    
    elif name == "get_service_logs":
        service_id = arguments.get("service_id")
        limit = arguments.get("limit", 100)
        return await get_service_logs(service_id, limit)
    
    elif name == "restart_service":
        service_id = arguments.get("service_id")
        return await restart_service(service_id)
    
    elif name == "update_env_var":
        service_id = arguments.get("service_id")
        key = arguments.get("key")
        value = arguments.get("value")
        return await update_env_var(service_id, key, value)
    
    elif name == "get_deployments":
        service_id = arguments.get("service_id")
        return await get_deployments(service_id)
    
    else:
        return ToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            is_error=True
        )

async def get_services() -> ToolResult:
    """List all Render services"""
    try:
        url = f"{RENDER_API_URL}/services"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        services = response.json()
        result = json.dumps(services, indent=2)
        
        return ToolResult(
            content=[TextContent(type="text", text=result)]
        )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            is_error=True
        )

async def get_service_status(service_id: str) -> ToolResult:
    """Get status of a specific service"""
    try:
        url = f"{RENDER_API_URL}/services/{service_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        service = response.json()
        status_info = {
            "id": service.get("id"),
            "name": service.get("name"),
            "status": service.get("status"),
            "createdAt": service.get("createdAt"),
            "updatedAt": service.get("updatedAt"),
        }
        
        result = json.dumps(status_info, indent=2)
        return ToolResult(
            content=[TextContent(type="text", text=result)]
        )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            is_error=True
        )

async def get_service_logs(service_id: str, limit: int = 100) -> ToolResult:
    """Get recent logs from a service"""
    try:
        url = f"{RENDER_API_URL}/services/{service_id}/logs"
        params = {"limit": limit}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        logs = response.json()
        result = json.dumps(logs, indent=2)
        
        return ToolResult(
            content=[TextContent(type="text", text=result)]
        )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            is_error=True
        )

async def restart_service(service_id: str) -> ToolResult:
    """Restart a Render service"""
    try:
        url = f"{RENDER_API_URL}/services/{service_id}/restart"
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        return ToolResult(
            content=[TextContent(type="text", text="Service restart initiated")]
        )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            is_error=True
        )

async def update_env_var(service_id: str, key: str, value: str) -> ToolResult:
    """Update an environment variable"""
    try:
        url = f"{RENDER_API_URL}/services/{service_id}"
        data = {
            "envVars": [
                {
                    "key": key,
                    "value": value
                }
            ]
        }
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        
        return ToolResult(
            content=[TextContent(type="text", text=f"Environment variable {key} updated")]
        )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            is_error=True
        )

async def get_deployments(service_id: str) -> ToolResult:
    """Get deployment history"""
    try:
        url = f"{RENDER_API_URL}/services/{service_id}/deploys"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        deployments = response.json()
        result = json.dumps(deployments, indent=2)
        
        return ToolResult(
            content=[TextContent(type="text", text=result)]
        )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            is_error=True
        )

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="get_services",
            description="List all Render services in your account",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_service_status",
            description="Get the status of a specific Render service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {"type": "string", "description": "The Render service ID"}
                },
                "required": ["service_id"]
            }
        ),
        Tool(
            name="get_service_logs",
            description="Get recent logs from a Render service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {"type": "string", "description": "The Render service ID"},
                    "limit": {"type": "integer", "description": "Number of log lines to retrieve", "default": 100}
                },
                "required": ["service_id"]
            }
        ),
        Tool(
            name="restart_service",
            description="Restart a Render service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {"type": "string", "description": "The Render service ID"}
                },
                "required": ["service_id"]
            }
        ),
        Tool(
            name="update_env_var",
            description="Update an environment variable for a service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {"type": "string", "description": "The Render service ID"},
                    "key": {"type": "string", "description": "Environment variable name"},
                    "value": {"type": "string", "description": "Environment variable value"}
                },
                "required": ["service_id", "key", "value"]
            }
        ),
        Tool(
            name="get_deployments",
            description="Get deployment history for a service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {"type": "string", "description": "The Render service ID"}
                },
                "required": ["service_id"]
            }
        ),
    ]

async def main():
    """Run the MCP server"""
    async with stdio_server(server) as (read_stream, write_stream):
        await server.run(read_stream, write_stream, asyncio.get_running_loop())

if __name__ == "__main__":
    asyncio.run(main())
