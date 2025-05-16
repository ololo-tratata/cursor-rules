#!/usr/bin/env python3
import uvicorn
import os
import sys
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.config import settings

def main():
    """Run the MCP server."""
    parser = argparse.ArgumentParser(description="Cursor MCP Server")
    parser.add_argument(
        "--host", 
        type=str, 
        default=settings.api_host,
        help=f"Host to bind server (default: {settings.api_host})"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=settings.api_port,
        help=f"Port to bind server (default: {settings.api_port})"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        default=settings.log_level,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"Logging level (default: {settings.log_level})"
    )
    
    args = parser.parse_args()
    
    print(f"Starting Cursor MCP Server on {args.host}:{args.port}")
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level.lower(),
    )

if __name__ == "__main__":
    main() 