#!/usr/bin/env python3
"""
PR Validation Module - Prevents approval of empty PRs
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PRValidationError(Exception):
    """Exception raised when PR validation fails"""
    pass


class PRValidator:
    """Validates PR content before allowing reviews"""
    
    def __init__(self, azure_client=None):
        self.azure_client = azure_client
        
    async def validate_pr_for_review(self, pr_id: int, repo_id: str) -> Dict[str, Any]:
        """
        Validate that PR has reviewable content before allowing approval
        
        Args:
            pr_id: Pull request ID
            repo_id: Repository ID
            
        Returns:
            Dict with validation status and details
        """
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'reviewable_files': [],
            'total_changes': 0
        }
        
        try:
            # Check if PR has file changes
            if self.azure_client:
                file_changes = await self._get_pr_file_changes(pr_id, repo_id)
                validation_result['reviewable_files'] = file_changes
                validation_result['total_changes'] = len(file_changes)
                
                if not file_changes:
                    validation_result['errors'].append("PR contains no file changes")
                    validation_result['is_valid'] = False
                    return validation_result
                
                # Check for meaningful changes (not just whitespace/comments)
                meaningful_changes = await self._count_meaningful_changes(file_changes)
                
                if meaningful_changes == 0:
                    validation_result['warnings'].append("PR contains only whitespace or comment changes")
                
                # Validate file types are appropriate
                invalid_files = self._validate_file_types(file_changes)
                if invalid_files:
                    validation_result['warnings'].extend([
                        f"Suspicious file type detected: {f}" for f in invalid_files
                    ])
                
                # Check for required documentation
                has_docs = any(self._is_documentation_file(f['path']) for f in file_changes)
                if not has_docs and len(file_changes) > 5:
                    validation_result['warnings'].append("Large PR without documentation updates")
                
                # Validation passed if no blocking errors
                validation_result['is_valid'] = len(validation_result['errors']) == 0
                
            else:
                # Fallback validation without Azure client
                validation_result['warnings'].append("Azure client not available - limited validation")
                validation_result['is_valid'] = True
                
        except Exception as e:
            logger.error(f"PR validation failed: {e}")
            validation_result['errors'].append(f"Validation error: {str(e)}")
            validation_result['is_valid'] = False
            
        return validation_result
    
    async def _get_pr_file_changes(self, pr_id: int, repo_id: str) -> List[Dict[str, Any]]:
        """Get list of file changes in the PR"""
        try:
            # This would call the Azure DevOps API to get PR changes
            # For now, return empty list since we don't have the API method
            logger.warning("Azure DevOps API method for PR file changes not implemented")
            return []
        except Exception as e:
            logger.error(f"Failed to get PR file changes: {e}")
            return []
    
    async def _count_meaningful_changes(self, file_changes: List[Dict]) -> int:
        """Count meaningful (non-whitespace) changes"""
        meaningful_count = 0
        
        for file_change in file_changes:
            # This would analyze the actual diff content
            # For now, assume all changes are meaningful
            if file_change.get('changeType') in ['add', 'edit', 'delete']:
                meaningful_count += 1
                
        return meaningful_count
    
    def _validate_file_types(self, file_changes: List[Dict]) -> List[str]:
        """Validate that file types are appropriate"""
        suspicious_files = []
        
        suspicious_extensions = {'.exe', '.dll', '.so', '.dylib', '.bin'}
        suspicious_patterns = {'password', 'secret', 'key', 'token'}
        
        for file_change in file_changes:
            file_path = file_change.get('path', '')
            file_name = Path(file_path).name.lower()
            
            # Check file extension
            if any(file_path.endswith(ext) for ext in suspicious_extensions):
                suspicious_files.append(f"{file_path} (binary file)")
            
            # Check for sensitive patterns in filename
            if any(pattern in file_name for pattern in suspicious_patterns):
                suspicious_files.append(f"{file_path} (potentially sensitive)")
                
        return suspicious_files
    
    def _is_documentation_file(self, file_path: str) -> bool:
        """Check if file is documentation"""
        doc_patterns = {'.md', '.rst', '.txt', '/docs/', '/documentation/'}
        return any(pattern in file_path.lower() for pattern in doc_patterns)


class ReviewGate:
    """Enforces review validation before allowing approvals"""
    
    def __init__(self, validator: PRValidator):
        self.validator = validator
        
    async def can_approve_pr(self, pr_id: int, repo_id: str, reviewer_id: str) -> Dict[str, Any]:
        """
        Check if PR can be approved by the reviewer
        
        Returns:
            Dict with approval status and reasoning
        """
        gate_result = {
            'can_approve': False,
            'reason': '',
            'validation_details': {},
            'reviewer': reviewer_id
        }
        
        try:
            # Validate PR content
            validation_result = await self.validator.validate_pr_for_review(pr_id, repo_id)
            gate_result['validation_details'] = validation_result
            
            if not validation_result['is_valid']:
                gate_result['can_approve'] = False
                gate_result['reason'] = "PR validation failed: " + ", ".join(validation_result['errors'])
                return gate_result
            
            # Check if there are reviewable files
            if validation_result['total_changes'] == 0:
                gate_result['can_approve'] = False
                gate_result['reason'] = "Cannot approve PR with no file changes"
                return gate_result
            
            # All checks passed
            gate_result['can_approve'] = True
            gate_result['reason'] = f"PR has {validation_result['total_changes']} reviewable changes"
            
            # Add warnings to reason if any
            if validation_result['warnings']:
                gate_result['reason'] += f" (Warnings: {'; '.join(validation_result['warnings'])})"
                
        except Exception as e:
            logger.error(f"Review gate check failed: {e}")
            gate_result['can_approve'] = False
            gate_result['reason'] = f"Review gate error: {str(e)}"
            
        return gate_result
    
    async def enforce_review_quality(self, pr_id: int, repo_id: str, 
                                   review_comments: List[str]) -> Dict[str, Any]:
        """
        Enforce minimum review quality standards
        
        Args:
            pr_id: Pull request ID
            repo_id: Repository ID
            review_comments: List of review comments
            
        Returns:
            Dict with quality assessment
        """
        quality_result = {
            'meets_standards': False,
            'score': 0,
            'feedback': [],
            'required_improvements': []
        }
        
        # Check comment quality
        meaningful_comments = [c for c in review_comments if len(c.strip()) > 10]
        
        if not meaningful_comments:
            quality_result['required_improvements'].append("Add detailed review comments")
            quality_result['score'] += 0
        else:
            quality_result['score'] += len(meaningful_comments) * 2
        
        # Check for specific review areas
        review_areas = {
            'security': ['security', 'vulnerability', 'auth', 'permission'],
            'performance': ['performance', 'optimization', 'speed', 'memory'],
            'maintainability': ['maintainability', 'readable', 'clean', 'structure'],
            'testing': ['test', 'coverage', 'validation', 'verify']
        }
        
        covered_areas = []
        for area, keywords in review_areas.items():
            if any(any(keyword in comment.lower() for keyword in keywords) 
                   for comment in meaningful_comments):
                covered_areas.append(area)
                quality_result['score'] += 3
        
        quality_result['feedback'].append(f"Covered review areas: {covered_areas}")
        
        # Minimum quality threshold
        quality_result['meets_standards'] = quality_result['score'] >= 5
        
        if not quality_result['meets_standards']:
            quality_result['required_improvements'].append("Provide more comprehensive review feedback")
        
        return quality_result


# Example usage for persona processors
async def validate_before_review(pr_id: int, repo_id: str, azure_client=None) -> bool:
    """
    Utility function for persona processors to validate PR before reviewing
    
    Returns:
        True if PR is valid for review, False otherwise
    """
    validator = PRValidator(azure_client)
    gate = ReviewGate(validator)
    
    result = await gate.can_approve_pr(pr_id, repo_id, "system")
    
    if not result['can_approve']:
        logger.warning(f"PR {pr_id} cannot be reviewed: {result['reason']}")
        return False
    
    return True