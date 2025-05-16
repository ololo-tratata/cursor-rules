import os
import json
import logging
import aiofiles
from typing import Dict, Any, List, Optional
import shutil

from app.config import settings

logger = logging.getLogger(__name__)

class FileSystemService:
    """Service for handling file system operations."""
    
    def __init__(self, rules_dir: str = settings.rules_local_path):
        self.rules_dir = rules_dir
        os.makedirs(self.rules_dir, exist_ok=True)
        logger.info(f"Initialized FileSystemService with rules dir: {self.rules_dir}")
    
    async def deploy_rules(self, target_dir: str, technology: str) -> bool:
        """Deploy rules for a specific technology to a target project directory."""
        source_dir = os.path.join(self.rules_dir, technology)
        target_rules_dir = os.path.join(target_dir, ".cursor-rules")
        
        logger.info(f"Deploying rules from {source_dir} to {target_rules_dir}")
        
        if not os.path.exists(source_dir):
            logger.error(f"Source rules directory doesn't exist: {source_dir}")
            return False
        
        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_rules_dir, exist_ok=True)
            
            # Create technology subdirectory
            target_tech_dir = os.path.join(target_rules_dir, technology)
            os.makedirs(target_tech_dir, exist_ok=True)
            
            # Copy all rule files
            for filename in os.listdir(source_dir):
                if filename.endswith(".json"):
                    source_file = os.path.join(source_dir, filename)
                    target_file = os.path.join(target_tech_dir, filename)
                    shutil.copy2(source_file, target_file)
                    logger.debug(f"Copied rule file: {source_file} -> {target_file}")
            
            # Create or update index file
            await self._update_index_file(target_rules_dir, technology)
            
            logger.info(f"Successfully deployed rules to {target_rules_dir}")
            return True
        except Exception as e:
            logger.error(f"Error deploying rules to {target_dir}: {str(e)}")
            return False
    
    async def _update_index_file(self, rules_dir: str, technology: str) -> None:
        """Update the index file with available technologies and rules."""
        index_path = os.path.join(rules_dir, "index.json")
        index_data = {"technologies": {}}
        
        # Read existing index if it exists
        if os.path.exists(index_path):
            try:
                async with aiofiles.open(index_path, "r") as f:
                    content = await f.read()
                    index_data = json.loads(content)
            except Exception as e:
                logger.warning(f"Failed to read existing index file: {str(e)}")
        
        # Scan technology directory for rules
        tech_dir = os.path.join(rules_dir, technology)
        if os.path.exists(tech_dir):
            rules = []
            for filename in os.listdir(tech_dir):
                if filename.endswith(".json"):
                    rule_id = filename.replace(".json", "")
                    rules.append(rule_id)
            
            # Update index with this technology's rules
            index_data["technologies"][technology] = {
                "rules": rules,
                "updated": True
            }
        
        # Write updated index
        try:
            async with aiofiles.open(index_path, "w") as f:
                await f.write(json.dumps(index_data, indent=2))
            logger.debug(f"Updated index file at {index_path}")
        except Exception as e:
            logger.error(f"Failed to write index file: {str(e)}")
    
    async def detect_project_type(self, project_dir: str) -> Optional[str]:
        """Attempt to detect the main technology of a project directory."""
        logger.info(f"Detecting project type for: {project_dir}")
        
        # Check for specific files that indicate project type
        indicators = {
            "package.json": "javascript",
            "tsconfig.json": "typescript",
            "requirements.txt": "python",
            "setup.py": "python",
            "Cargo.toml": "rust",
            "go.mod": "golang",
            "pom.xml": "java",
            "build.gradle": "java",
            "Gemfile": "ruby",
            "composer.json": "php",
            ".swift-version": "swift",
            "Package.swift": "swift",
        }
        
        for file, tech in indicators.items():
            if os.path.exists(os.path.join(project_dir, file)):
                logger.info(f"Detected project type: {tech} based on {file}")
                return tech
        
        # Count file extensions as fallback
        extensions = {}
        for root, _, files in os.walk(project_dir):
            for file in files:
                if "." in file:
                    ext = file.split(".")[-1]
                    extensions[ext] = extensions.get(ext, 0) + 1
        
        if extensions:
            # Map extensions to technologies
            ext_to_tech = {
                "py": "python",
                "js": "javascript",
                "jsx": "javascript", 
                "ts": "typescript",
                "tsx": "typescript",
                "java": "java",
                "rb": "ruby",
                "php": "php",
                "go": "golang",
                "rs": "rust",
                "swift": "swift",
                "cs": "csharp"
            }
            
            # Find most common extension with known technology mapping
            most_common = None
            max_count = 0
            for ext, count in extensions.items():
                if ext in ext_to_tech and count > max_count:
                    most_common = ext
                    max_count = count
            
            if most_common:
                logger.info(f"Detected project type: {ext_to_tech[most_common]} based on file extensions")
                return ext_to_tech[most_common]
        
        logger.info("Could not detect project type")
        return None 