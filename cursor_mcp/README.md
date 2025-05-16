# Cursor MCP Server

Model Context Protocol (MCP) server for Cursor rules integration. This server connects to a GitHub repository (default: `ololo-tratata/cursor-rules`) to fetch appropriate rules based on file context.

## Features

- Fetch Cursor rules based on file type/context
- Deploy rules to local project directories
- Automatic technology detection based on file extensions and project structure
- Rule caching for improved performance
- REST API for integration with Cursor IDE

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/your-username/cursor-mcp.git
cd cursor-mcp
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create an environment file:
```bash
# Create a .env file with the following content:
# GitHub API Token (optional but recommended to avoid rate limits)
GITHUB_TOKEN=your_github_token_here

# GitHub Repository with Cursor Rules
GITHUB_REPOSITORY=ololo-tratata/cursor-rules

# MCP Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Rules Settings
RULES_CACHE_TTL=3600
RULES_LOCAL_PATH=./rules
```

## Usage

### Starting the Server

Run the server with default settings:
```bash
python run.py
```

Or with custom settings:
```bash
python run.py --host 127.0.0.1 --port 8080 --reload --log-level DEBUG
```

The server will be available at `http://127.0.0.1:8000` (or your custom host/port).

### API Documentation

Once the server is running, you can access the Swagger UI documentation at:
```
http://127.0.0.1:8000/docs
```

## API Endpoints

- **GET /api/v1/technologies** - List all available technologies
- **GET /api/v1/technologies/{technology}/rules** - Get all rules for a specific technology
- **GET /api/v1/technologies/{technology}/rules/{rule_id}** - Get a specific rule
- **POST /api/v1/context/rules** - Get rules applicable to a specific file context
- **POST /api/v1/deploy** - Deploy rules to a target project directory

## Integration with Cursor

1. Start the MCP server
2. Configure Cursor to connect to the MCP server
3. The MCP server will automatically fetch and deploy appropriate rules based on the file context

## Example: Deploy Rules to a Project

```bash
# Using curl
curl -X POST "http://localhost:8000/api/v1/deploy" \
  -H "Content-Type: application/json" \
  -d '{"target_dir": "/path/to/your/project", "technology": "python"}'

# Technology is optional - will be auto-detected if not provided
curl -X POST "http://localhost:8000/api/v1/deploy" \
  -H "Content-Type: application/json" \
  -d '{"target_dir": "/path/to/your/project"}'
```

## Example: Get Rules for a File

```bash
curl -X POST "http://localhost:8000/api/v1/context/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/your/project/main.py",
    "file_type": "py",
    "project_type": "python"
  }'
```

## License

MIT 