import json
import asyncio
import logging
from github import Github
from github.ContentFile import ContentFile
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.rule import Rule, RuleSet
from app.config import settings

logger = logging.getLogger(__name__)

class GitHubService:
    """Service for interacting with GitHub to fetch rules."""
    
    def __init__(self, token: str = settings.github_token, repo_name: str = settings.github_repository):
        try:
            # Use anonymous access if token is empty
            if token:
                self.github = Github(token)
                logger.info("Using authenticated GitHub access")
            else:
                self.github = Github()
                logger.info("Using anonymous GitHub access")
                
            self.repo = self.github.get_repo(repo_name)
            self.authenticated = True
            logger.info(f"Successfully connected to repository: {repo_name}")
        except Exception as e:
            logger.warning(f"Failed to connect to GitHub repository: {str(e)}")
            logger.warning("Falling back to mock data for demonstration purposes")
            self.authenticated = False
            self.mock_rules = {
                "python": self._create_mock_python_rules(),
                "javascript": self._create_mock_javascript_rules(),
                "typescript": self._create_mock_typescript_rules(),
                "swift": self._create_mock_swift_rules(),
            }
    
    def _create_mock_python_rules(self) -> List[Rule]:
        """Create mock Python rules for demonstration."""
        return [
            Rule(
                id="python-linting",
                technology="python",
                file_patterns=["*.py"],
                content={
                    "linters": ["flake8", "black"],
                    "rules": {"max_line_length": 88}
                },
                version="1.0.0"
            ),
            Rule(
                id="python-typing",
                technology="python",
                file_patterns=["*.py"],
                content={
                    "type_checker": "mypy",
                    "rules": {"disallow_untyped_defs": True}
                },
                version="1.0.0"
            )
        ]
    
    def _create_mock_javascript_rules(self) -> List[Rule]:
        """Create mock JavaScript rules for demonstration."""
        return [
            Rule(
                id="javascript-eslint",
                technology="javascript",
                file_patterns=["*.js", "*.jsx"],
                content={
                    "linter": "eslint",
                    "rules": {"semi": "error", "quotes": ["error", "single"]}
                },
                version="1.0.0"
            )
        ]
    
    def _create_mock_typescript_rules(self) -> List[Rule]:
        """Create mock TypeScript rules for demonstration."""
        return [
            Rule(
                id="typescript-tslint",
                technology="typescript",
                file_patterns=["*.ts", "*.tsx"],
                content={
                    "linter": "tslint",
                    "rules": {"indent": [True, "spaces", 2]}
                },
                version="1.0.0"
            )
        ]
    
    def _create_mock_swift_rules(self) -> List[Rule]:
        """Create mock Swift rules for demonstration."""
        return [
            Rule(
                id="swift-swiftlint",
                technology="swift",
                file_patterns=["*.swift"],
                content={
                    "linter": "swiftlint",
                    "rules": {"line_length": 120, "force_cast": "warning"}
                },
                version="1.0.0"
            )
        ]
    
    async def fetch_rules_for_technology(self, technology: str) -> List[Rule]:
        """Fetch rules for a specific technology."""
        logger.info(f"Fetching rules for technology: {technology}")
        
        if not self.authenticated:
            # Return mock data if not authenticated
            return self.mock_rules.get(technology, [])
        
        try:
            # Run GitHub API calls in a thread pool to avoid blocking
            return await asyncio.to_thread(self._fetch_rules_sync, technology)
        except Exception as e:
            logger.error(f"Error fetching rules for {technology}: {str(e)}")
            # Fall back to mock data on error
            return self.mock_rules.get(technology, [])
    
    def _fetch_rules_sync(self, technology: str) -> List[Rule]:
        """Synchronous implementation of rule fetching."""
        rules = []
        
        try:
            # Try to get rules from technology-specific directory
            path = f"rules/{technology}"
            try:
                contents = self.repo.get_contents(path)
            except Exception as e:
                logger.warning(f"Path {path} not found in repository: {str(e)}")
                # Try to get rules from the root directory as fallback
                logger.info(f"Trying to get contents from root directory")
                contents = self.repo.get_contents("")
            
            # Process each rule file
            for content in contents:
                if content.type == "file" and content.name.endswith(".json"):
                    rule = self._parse_rule_content(content, technology)
                    if rule:
                        rules.append(rule)
        except Exception as e:
            logger.warning(f"Could not fetch rules for technology '{technology}': {str(e)}")
        
        return rules
    
    def _parse_rule_content(self, content: ContentFile, technology: str) -> Optional[Rule]:
        """Parse rule content from GitHub file."""
        try:
            # Decode content and parse as JSON
            content_str = content.decoded_content.decode('utf-8')
            rule_data = json.loads(content_str)
            
            # Add required fields if missing
            if "id" not in rule_data:
                rule_data["id"] = content.name.replace(".json", "")
            
            if "technology" not in rule_data:
                rule_data["technology"] = technology
                
            if "updated_at" not in rule_data:
                # Use last commit date for this file
                try:
                    commits = self.repo.get_commits(path=content.path)
                    if commits.totalCount > 0:
                        last_commit = commits[0]
                        rule_data["updated_at"] = last_commit.commit.author.date
                except Exception as e:
                    logger.warning(f"Could not get commits for {content.path}: {str(e)}")
            
            # Create Rule object
            return Rule(**rule_data)
        except Exception as e:
            logger.error(f"Error parsing rule from {content.path}: {str(e)}")
            return None
    
    async def fetch_rules_by_file_pattern(self, file_path: str) -> List[Rule]:
        """Fetch rules that apply to a specific file path."""
        logger.info(f"Fetching rules for file: {file_path}")
        
        # Determine file type based on extension
        file_type = file_path.split(".")[-1] if "." in file_path else None
        
        # Map file extension to technology
        technology_map = {
            "py": "python",
            "js": "javascript",
            "jsx": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
            "swift": "swift",
            "go": "golang",
            "rb": "ruby",
            "java": "java",
            "kt": "kotlin",
            "cs": "csharp",
            "php": "php",
            "rs": "rust",
            # Add more mappings as needed
        }
        
        technology = technology_map.get(file_type, "general")
        return await self.fetch_rules_for_technology(technology) 