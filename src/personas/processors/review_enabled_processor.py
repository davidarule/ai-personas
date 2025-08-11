#!/usr/bin/env python3
"""
Review-enabled processor base class that prevents approving empty PRs
"""

import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_processor import BaseProcessor
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from pr_management.pr_validation import PRValidator, ReviewGate, validate_before_review

logger = logging.getLogger(__name__)


class ReviewEnabledProcessor(BaseProcessor):
    """Base processor with enhanced PR review capabilities that prevent empty PR approvals"""
    
    def __init__(self, output_directory: str):
        super().__init__(output_directory)
        self.pr_validator = PRValidator()
        self.review_gate = ReviewGate(self.pr_validator)
        
    async def process_pr_review_task(self, work_item: Any) -> Dict[str, Any]:
        """
        Process a PR review task with proper validation
        
        Args:
            work_item: Work item containing PR review details
            
        Returns:
            Dict with review result and validation status
        """
        pr_info = self._extract_pr_info(work_item)
        
        if not pr_info:
            return {
                'status': 'failed',
                'message': 'Could not extract PR information from work item',
                'review_status': 'not_started'
            }
        
        pr_id = pr_info.get('pr_id')
        repo_id = pr_info.get('repo_id', 'unknown')
        
        logger.info(f"Processing PR review for PR #{pr_id}")
        
        # Validate PR before starting review
        validation_result = await self.pr_validator.validate_pr_for_review(pr_id, repo_id)
        
        if not validation_result['is_valid']:
            error_msg = f"Cannot review PR #{pr_id}: {', '.join(validation_result['errors'])}"
            logger.warning(error_msg)
            
            return {
                'status': 'validation_failed',
                'message': error_msg,
                'review_status': 'blocked',
                'validation_errors': validation_result['errors'],
                'validation_warnings': validation_result['warnings']
            }
        
        # Perform the actual review
        review_result = await self._perform_pr_review(work_item, pr_info, validation_result)
        
        # Check if review meets quality standards
        review_comments = review_result.get('comments', [])
        quality_check = await self.review_gate.enforce_review_quality(
            pr_id, repo_id, review_comments
        )
        
        review_result.update({
            'validation_result': validation_result,
            'quality_check': quality_check,
            'pr_info': pr_info
        })
        
        return review_result
    
    async def _perform_pr_review(self, work_item: Any, pr_info: Dict, 
                                validation_result: Dict) -> Dict[str, Any]:
        """
        Perform the actual PR review - to be implemented by subclasses
        
        Args:
            work_item: Work item with review details
            pr_info: Extracted PR information
            validation_result: PR validation results
            
        Returns:
            Dict with review results
        """
        # Default implementation - subclasses should override this
        review_comments = [
            f"Reviewed PR #{pr_info['pr_id']} from {self.persona_name} perspective",
            f"Found {validation_result['total_changes']} file changes to review",
            "Review completed successfully"
        ]
        
        # Generate review artifacts based on persona type
        artifacts = await self._generate_review_artifacts(work_item, pr_info)
        
        return {
            'status': 'completed',
            'message': f'PR review completed by {self.persona_name}',
            'review_status': 'approved_with_comments',
            'comments': review_comments,
            'artifacts': artifacts,
            'reviewer': self.persona_name
        }
    
    async def _generate_review_artifacts(self, work_item: Any, pr_info: Dict) -> List[Dict]:
        """
        Generate review artifacts specific to the persona type
        To be implemented by subclasses
        """
        return []
    
    def _extract_pr_info(self, work_item: Any) -> Optional[Dict[str, Any]]:
        """
        Extract PR information from work item
        
        Args:
            work_item: Work item containing PR details
            
        Returns:
            Dict with PR information or None if not found
        """
        description = getattr(work_item, 'description', '') or ''
        title = getattr(work_item, 'title', '') or ''
        
        # Look for PR references in title and description
        pr_patterns = [
            r'PR #?(\d+)',
            r'Pull Request #?(\d+)', 
            r'pullrequest/(\d+)',
            r'PR_(\d+)',
            r'REVIEW-(\d+)'
        ]
        
        import re
        
        pr_id = None
        for pattern in pr_patterns:
            match = re.search(pattern, title + ' ' + description, re.IGNORECASE)
            if match:
                try:
                    pr_id = int(match.group(1))
                    break
                except (ValueError, IndexError):
                    continue
        
        if not pr_id:
            return None
        
        # Extract repository information
        repo_info = self._extract_repo_info(description)
        
        return {
            'pr_id': pr_id,
            'repo_id': repo_info.get('repo_id', 'unknown'),
            'repo_name': repo_info.get('repo_name', 'unknown'),
            'organization': repo_info.get('organization', 'unknown'),
            'project': repo_info.get('project', 'unknown')
        }
    
    def _extract_repo_info(self, text: str) -> Dict[str, str]:
        """Extract repository information from text"""
        import re
        
        # Look for Azure DevOps URLs
        azure_pattern = r'https://dev\.azure\.com/([^/]+)/([^/]+)/_git/([^/]+)'
        match = re.search(azure_pattern, text)
        
        if match:
            return {
                'organization': match.group(1),
                'project': match.group(2),
                'repo_name': match.group(3),
                'repo_id': match.group(3)  # Simplified - would need API call for actual ID
            }
        
        return {
            'organization': 'unknown',
            'project': 'unknown', 
            'repo_name': 'unknown',
            'repo_id': 'unknown'
        }
    
    async def can_approve_pr(self, pr_id: int, repo_id: str) -> bool:
        """
        Check if this processor can approve the given PR
        
        Args:
            pr_id: Pull request ID
            repo_id: Repository ID
            
        Returns:
            True if PR can be approved, False otherwise
        """
        result = await self.review_gate.can_approve_pr(pr_id, repo_id, self.persona_name)
        return result['can_approve']
    
    def _is_review_task(self, work_item: Any) -> bool:
        """
        Check if work item is a PR review task
        
        Args:
            work_item: Work item to check
            
        Returns:
            True if this is a review task
        """
        title = getattr(work_item, 'title', '') or ''
        description = getattr(work_item, 'description', '') or ''
        
        review_indicators = [
            'review', 'pr', 'pull request', 'code review',
            'peer review', 'technical review'
        ]
        
        text_to_check = (title + ' ' + description).lower()
        return any(indicator in text_to_check for indicator in review_indicators)
    
    async def process_work_item(self, work_item: Any) -> Dict[str, Any]:
        """
        Enhanced work item processing that handles both regular tasks and PR reviews
        
        Args:
            work_item: Work item to process
            
        Returns:
            Dict with processing results
        """
        # Check if this is a review task
        if self._is_review_task(work_item):
            logger.info(f"{self.persona_name} processing PR review task: {work_item.title}")
            return await self.process_pr_review_task(work_item)
        else:
            # Regular work item processing
            logger.info(f"{self.persona_name} processing regular work item: {work_item.title}")
            return await super().process_work_item(work_item)
    
    def _create_review_summary(self, work_item: Any, review_result: Dict) -> str:
        """
        Create a standardized review summary
        
        Args:
            work_item: Work item that was reviewed
            review_result: Results of the review
            
        Returns:
            Formatted review summary
        """
        pr_info = review_result.get('pr_info', {})
        validation = review_result.get('validation_result', {})
        quality = review_result.get('quality_check', {})
        
        summary = f"""# PR Review Summary - {self.persona_name}

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Reviewer**: {self.persona_name}
**PR**: #{pr_info.get('pr_id', 'Unknown')}
**Status**: {review_result.get('review_status', 'Unknown')}

## Validation Results
- **Reviewable Files**: {validation.get('total_changes', 0)}
- **Validation Status**: {'✅ Passed' if validation.get('is_valid', False) else '❌ Failed'}
- **Errors**: {len(validation.get('errors', []))}
- **Warnings**: {len(validation.get('warnings', []))}

## Review Quality
- **Quality Score**: {quality.get('score', 0)}/10
- **Meets Standards**: {'✅ Yes' if quality.get('meets_standards', False) else '❌ No'}

## Comments
"""
        
        comments = review_result.get('comments', [])
        for i, comment in enumerate(comments, 1):
            summary += f"\n{i}. {comment}"
        
        # Add validation warnings if any
        warnings = validation.get('warnings', [])
        if warnings:
            summary += "\n\n## Warnings\n"
            for warning in warnings:
                summary += f"- ⚠️ {warning}\n"
        
        summary += f"\n\n**Overall Assessment**: {review_result.get('review_status', 'Unknown')}"
        
        return summary