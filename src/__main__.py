#!/usr/bin/env python3
"""
Main entry point for Windows ChatGPT MCP Tool
"""

import asyncio

if __name__ == "__main__":
    from .mcp_server import main
    asyncio.run(main())