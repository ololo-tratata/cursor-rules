from fastapi import APIRouter, Depends, HTTPException, Body, Path, Query
from typing import List, Dict, Any

from app.models.rule import Rule, RuleSet, FileContext
from app.services.github import GitHubService
from app.services.rule_manager import RuleManager
from app.services.file_system import FileSystemService

# Create router
router = APIRouter(prefix="/api/v1")

# Service instances
github_service = GitHubService()
rule_manager = RuleManager(github_service)
fs_service = FileSystemService()

@router.get("/technologies", response_model=List[str], tags=["Technologies"])
async def list_technologies():
    """List all available technologies with rules."""
    # Get unique technology list from GitHub
    try:
        # In a real implementation, this would fetch the list from GitHub
        # For simplicity, we'll return a hardcoded list of common technologies
        return [
            "python", "javascript", "typescript", "rust", "golang", 
            "java", "kotlin", "swift", "ruby", "csharp", "php"
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch technologies: {str(e)}")

@router.get("/technologies/{technology}/rules", response_model=RuleSet, tags=["Rules"])
async def get_rules_for_technology(
    technology: str = Path(..., description="Technology name")
):
    """Get all rules for a specific technology."""
    try:
        return await rule_manager.get_rules_for_technology(technology)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rules: {str(e)}")

@router.get("/technologies/{technology}/rules/{rule_id}", response_model=Rule, tags=["Rules"])
async def get_rule_by_id(
    technology: str = Path(..., description="Technology name"),
    rule_id: str = Path(..., description="Rule ID")
):
    """Get a specific rule by ID."""
    try:
        rule = await rule_manager.get_rule_by_id(rule_id, technology)
        if not rule:
            raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found for {technology}")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rule: {str(e)}")

@router.post("/context/rules", response_model=RuleSet, tags=["Context"])
async def get_rules_for_context(
    file_context: FileContext = Body(..., description="File context information")
):
    """Get rules applicable to a specific file context."""
    try:
        return await rule_manager.get_rules_for_file(file_context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rules: {str(e)}")

@router.post("/deploy", response_model=Dict[str, Any], tags=["Deployment"])
async def deploy_rules(
    target_dir: str = Body(..., embed=True, description="Target project directory"),
    technology: str = Body(None, embed=True, description="Technology to deploy rules for")
):
    """Deploy rules to a target project directory."""
    try:
        # If technology is not specified, try to detect it
        if not technology:
            detected_tech = await fs_service.detect_project_type(target_dir)
            if not detected_tech:
                raise HTTPException(
                    status_code=400, 
                    detail="Could not detect project type. Please specify technology parameter."
                )
            technology = detected_tech
        
        # Make sure we have rules for this technology
        ruleset = await rule_manager.get_rules_for_technology(technology)
        if not ruleset.rules:
            raise HTTPException(
                status_code=404, 
                detail=f"No rules found for technology: {technology}"
            )
        
        # Deploy rules
        success = await fs_service.deploy_rules(target_dir, technology)
        if not success:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to deploy rules to {target_dir}"
            )
        
        return {
            "success": True,
            "technology": technology,
            "rules_count": len(ruleset.rules),
            "target_dir": target_dir
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deploy rules: {str(e)}") 