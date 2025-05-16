import os
import json
import logging
import asyncio
import aiofiles
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from app.models.rule import Rule, RuleSet, FileContext
from app.services.github import GitHubService
from app.config import settings

logger = logging.getLogger(__name__)

class RuleManager:
    """Service for managing and caching rules."""
    
    def __init__(self, github_service: GitHubService = None):
        self.github_service = github_service or GitHubService()
        self.cache: Dict[str, Tuple[RuleSet, datetime]] = {}
        self.cache_ttl = timedelta(seconds=settings.rules_cache_ttl)
        self.rules_dir = settings.rules_local_path
        
        # Create rules directory if it doesn't exist
        os.makedirs(self.rules_dir, exist_ok=True)
        logger.info(f"Initialized RuleManager with cache TTL: {self.cache_ttl}")
    
    async def get_rules_for_technology(self, technology: str) -> RuleSet:
        """Get rules for a specific technology from cache or GitHub."""
        logger.debug(f"Getting rules for technology: {technology}")
        
        # Check cache first
        if technology in self.cache:
            ruleset, timestamp = self.cache[technology]
            if datetime.utcnow() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for technology: {technology}")
                return ruleset
        
        # Fetch from GitHub if not in cache or cache expired
        rules = await self.github_service.fetch_rules_for_technology(technology)
        ruleset = RuleSet(rules=rules, total=len(rules))
        
        # Update cache
        self.cache[technology] = (ruleset, datetime.utcnow())
        
        # Save rules locally
        await self._save_rules_locally(technology, ruleset)
        
        return ruleset
    
    async def get_rules_for_file(self, file_context: FileContext) -> RuleSet:
        """Get rules applicable to a specific file."""
        logger.info(f"Getting rules for file: {file_context.file_path}")
        
        file_type = file_context.file_type
        if not file_type and "." in file_context.file_path:
            file_type = file_context.file_path.split(".")[-1]
        
        # Determine technology based on file type
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
        if file_context.project_type:
            # If we know the project type, prioritize that
            technology = file_context.project_type
        
        return await self.get_rules_for_technology(technology)
    
    async def _save_rules_locally(self, technology: str, ruleset: RuleSet) -> None:
        """Save rules to local directory."""
        tech_dir = os.path.join(self.rules_dir, technology)
        os.makedirs(tech_dir, exist_ok=True)
        
        # Save each rule separately
        for rule in ruleset.rules:
            rule_path = os.path.join(tech_dir, f"{rule.id}.json")
            try:
                async with aiofiles.open(rule_path, "w") as f:
                    await f.write(rule.json(indent=2))
                logger.debug(f"Saved rule to {rule_path}")
            except Exception as e:
                logger.error(f"Error saving rule {rule.id} to {rule_path}: {str(e)}")
    
    async def get_rule_by_id(self, rule_id: str, technology: str) -> Optional[Rule]:
        """Get a specific rule by ID and technology."""
        ruleset = await self.get_rules_for_technology(technology)
        for rule in ruleset.rules:
            if rule.id == rule_id:
                return rule
        return None 