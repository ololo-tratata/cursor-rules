#!/usr/bin/env python3
"""
Cursor MCP Client

A simple client script to interact with the MCP server.
This can be integrated with Cursor IDE to automatically deploy rules.
"""

import argparse
import json
import os
import sys
import requests
from typing import Dict, Any, Optional

# Default server settings
DEFAULT_SERVER = "http://localhost:8000"
API_PREFIX = "/api/v1"

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Cursor MCP Client")
    
    # Server settings
    parser.add_argument(
        "--server", 
        type=str, 
        default=DEFAULT_SERVER,
        help=f"MCP server URL (default: {DEFAULT_SERVER})"
    )
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy rules to a project")
    deploy_parser.add_argument(
        "--target", 
        type=str, 
        default=".",
        help="Target project directory (default: current directory)"
    )
    deploy_parser.add_argument(
        "--technology", 
        type=str, 
        help="Technology to deploy rules for (optional, auto-detected if not provided)"
    )
    
    # Get rules command
    get_rules_parser = subparsers.add_parser("get-rules", help="Get rules for a file")
    get_rules_parser.add_argument(
        "--file", 
        type=str, 
        required=True,
        help="Path to the file"
    )
    get_rules_parser.add_argument(
        "--project-type", 
        type=str, 
        help="Project type (optional)"
    )
    
    # List technologies command
    subparsers.add_parser("list-technologies", help="List available technologies")
    
    return parser.parse_args()

def make_request(server: str, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make a request to the MCP server."""
    url = f"{server}{API_PREFIX}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"Error: Unsupported HTTP method: {method}")
            sys.exit(1)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to MCP server: {e}")
        sys.exit(1)

def deploy_rules(server: str, target_dir: str, technology: Optional[str] = None) -> None:
    """Deploy rules to a target project directory."""
    data = {"target_dir": os.path.abspath(target_dir)}
    if technology:
        data["technology"] = technology
    
    print(f"Deploying rules to {target_dir}...")
    result = make_request(server, "/deploy", method="POST", data=data)
    
    if result.get("success"):
        print(f"Successfully deployed {result.get('rules_count', 0)} rules for {result.get('technology')}.")
    else:
        print(f"Failed to deploy rules: {result.get('detail', 'Unknown error')}")

def get_rules_for_file(server: str, file_path: str, project_type: Optional[str] = None) -> None:
    """Get rules applicable to a specific file."""
    file_context = {
        "file_path": file_path,
        "project_type": project_type
    }
    
    if "." in file_path:
        file_context["file_type"] = file_path.split(".")[-1]
    
    print(f"Getting rules for {file_path}...")
    result = make_request(server, "/context/rules", method="POST", data=file_context)
    
    print(f"Found {result.get('total', 0)} rules:")
    for rule in result.get("rules", []):
        print(f"- {rule.get('id')}: {rule.get('technology')} {rule.get('version')}")

def list_technologies(server: str) -> None:
    """List available technologies."""
    print("Fetching available technologies...")
    result = make_request(server, "/technologies")
    
    print("Available technologies:")
    for tech in result:
        print(f"- {tech}")

def main():
    """Main entry point."""
    args = parse_args()
    
    if args.command == "deploy":
        deploy_rules(args.server, args.target, args.technology)
    elif args.command == "get-rules":
        get_rules_for_file(args.server, args.file, args.project_type)
    elif args.command == "list-technologies":
        list_technologies(args.server)
    else:
        print("Error: No command specified. Use --help for usage information.")
        sys.exit(1)

if __name__ == "__main__":
    main() 