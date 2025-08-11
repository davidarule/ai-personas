"""
Steve Workflow Processor - Security Architect with Workflow Capabilities

Enhanced version of Steve that can execute workflows for security-related tasks.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

from .workflow_enabled_processor import WorkflowEnabledProcessor

logger = logging.getLogger(__name__)


class SteveWorkflowProcessor(WorkflowEnabledProcessor):
    """
    Security Architect processor with workflow execution capabilities.
    
    Can execute workflows for:
    - Security feature development
    - Security patch deployment
    - Vulnerability remediation
    - Compliance implementation
    """
    
    def __init__(self, debug: bool = False):
        """Initialize Steve with workflow capabilities."""
        super().__init__(name="SteveBot", debug=debug)
        self.persona_id = "steve"
        
        # Security-specific workflow preferences
        self.security_workflows = [
            'security-feature-development',
            'vulnerability-fix',
            'security-hotfix',
            'compliance-implementation'
        ]
    
    async def process_work_item(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a work item, potentially using workflows."""
        logger.info(f"Steve (Workflow) processing work item #{work_item.get('id')}: {work_item.get('title')}")
        
        # Check if we should use a workflow
        recommended_workflows = self.get_recommended_workflows(work_item)
        
        # Add security-specific workflow recommendations
        if self._is_security_work_item(work_item):
            recommended_workflows = self._enhance_security_recommendations(
                work_item, recommended_workflows
            )
        
        if recommended_workflows:
            # Use the first recommended workflow
            workflow_id = recommended_workflows[0]
            logger.info(f"Using workflow '{workflow_id}' for this work item")
            
            # Process with workflow
            result = await self.process_work_item_with_workflow(work_item, workflow_id)
            
            if result['success']:
                # Enhance with security-specific outputs
                await self._add_security_artifacts(work_item, result)
            
            return result
        else:
            # Fall back to traditional processing
            return await self._process_without_workflow(work_item)
    
    def _is_security_work_item(self, work_item: Dict[str, Any]) -> bool:
        """Check if work item is security-related."""
        security_keywords = [
            'security', 'vulnerability', 'cve', 'threat', 'risk',
            'compliance', 'audit', 'penetration', 'encryption',
            'authentication', 'authorization', 'ssl', 'tls',
            'owasp', 'nist', 'iso27001', 'gdpr', 'hipaa'
        ]
        
        text = f"{work_item.get('title', '')} {work_item.get('description', '')}".lower()
        return any(keyword in text for keyword in security_keywords)
    
    def _enhance_security_recommendations(self, work_item: Dict[str, Any], 
                                        recommendations: List[str]) -> List[str]:
        """Add security-specific workflow recommendations."""
        text = f"{work_item.get('title', '')} {work_item.get('description', '')}".lower()
        
        # Map security scenarios to workflows
        if 'vulnerability' in text or 'cve' in text:
            if 'critical' in text or 'high' in text:
                recommendations.insert(0, 'wf2')  # hotfix
            else:
                recommendations.insert(0, 'wf1')  # bug-fix
        
        elif 'compliance' in text or 'audit' in text:
            recommendations.insert(0, 'wf0')  # feature-development
        
        elif 'threat' in text or 'risk' in text:
            recommendations.append('wf3')  # branch-creation
        
        return recommendations
    
    async def _add_security_artifacts(self, work_item: Dict[str, Any], 
                                    result: Dict[str, Any]) -> None:
        """Add security-specific artifacts to workflow output."""
        workflow_outputs = result.get('workflow_result', {}).get('outputs', {})
        
        # Generate security documents based on workflow type
        if workflow_outputs.get('BRANCH_NAME'):
            branch_name = workflow_outputs['BRANCH_NAME']
            
            # Generate threat model for the feature
            if 'feature' in branch_name:
                threat_model = self._generate_threat_model_summary(work_item)
                output_path = self._save_output(
                    f"threat_model_{work_item.get('id')}.md",
                    threat_model,
                    metadata={
                        'type': 'threat_model',
                        'branch': branch_name,
                        'work_item_id': work_item.get('id')
                    }
                )
                logger.info(f"Generated threat model: {output_path}")
            
            # Generate security checklist
            checklist = self._generate_security_checklist(work_item)
            checklist_path = self._save_output(
                f"security_checklist_{work_item.get('id')}.md",
                checklist,
                metadata={
                    'type': 'security_checklist',
                    'branch': branch_name,
                    'work_item_id': work_item.get('id')
                }
            )
            logger.info(f"Generated security checklist: {checklist_path}")
    
    def _generate_threat_model_summary(self, work_item: Dict[str, Any]) -> str:
        """Generate a threat model summary."""
        return f"""# Threat Model Summary

## Work Item
- **ID**: {work_item.get('id')}
- **Title**: {work_item.get('title')}

## Threat Analysis

### Data Flow
- Input validation required
- Output sanitization needed
- Data encryption in transit and at rest

### Trust Boundaries
- User authentication boundary
- API gateway boundary
- Database access boundary

### Potential Threats (STRIDE)
1. **Spoofing**: Implement strong authentication
2. **Tampering**: Use integrity checks
3. **Repudiation**: Enable audit logging
4. **Information Disclosure**: Encrypt sensitive data
5. **Denial of Service**: Implement rate limiting
6. **Elevation of Privilege**: Apply principle of least privilege

### Recommended Mitigations
- Implement input validation
- Add authentication checks
- Enable audit logging
- Apply encryption
- Configure rate limiting

### Security Testing Required
- Static code analysis
- Dynamic security testing
- Penetration testing
"""
    
    def _generate_security_checklist(self, work_item: Dict[str, Any]) -> str:
        """Generate a security checklist."""
        return f"""# Security Checklist

## Work Item: {work_item.get('id')} - {work_item.get('title')}

### Pre-Development
- [ ] Threat model reviewed
- [ ] Security requirements defined
- [ ] Compliance requirements identified

### Development
- [ ] Input validation implemented
- [ ] Output encoding applied
- [ ] Authentication/authorization checks added
- [ ] Sensitive data encrypted
- [ ] Security headers configured
- [ ] Error handling prevents information leakage

### Testing
- [ ] Static code analysis passed
- [ ] Dynamic security testing completed
- [ ] Dependency vulnerabilities scanned
- [ ] Security unit tests written

### Deployment
- [ ] Security configuration reviewed
- [ ] Secrets management configured
- [ ] Monitoring and alerting enabled
- [ ] Incident response plan updated

### Post-Deployment
- [ ] Security monitoring active
- [ ] Vulnerability scanning scheduled
- [ ] Security metrics tracked
"""
    
    async def _process_without_workflow(self, work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Traditional processing without workflows."""
        # Generate security architecture document
        output = self._generate_security_architecture(work_item)
        
        output_path = self._save_output(
            f"security_arch_{work_item.get('id')}.md",
            output,
            metadata={
                'type': 'security_architecture',
                'work_item_id': work_item.get('id')
            }
        )
        
        return {
            'success': True,
            'output_path': output_path,
            'message': 'Processed without workflow'
        }
    
    def _generate_security_architecture(self, work_item: Dict[str, Any]) -> str:
        """Generate a security architecture document."""
        return f"""# Security Architecture

## Overview
Security architecture for: {work_item.get('title')}

## Security Principles
1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimal access rights
3. **Zero Trust**: Verify explicitly
4. **Separation of Duties**: Divided responsibilities

## Architecture Components

### Authentication Layer
- Multi-factor authentication
- OAuth 2.0 / OIDC implementation
- Session management

### Authorization Layer
- Role-based access control (RBAC)
- Attribute-based access control (ABAC)
- Policy enforcement points

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Key management service

### Network Security
- Web application firewall
- DDoS protection
- Network segmentation

### Monitoring & Response
- Security information and event management (SIEM)
- Intrusion detection system (IDS)
- Incident response procedures

## Compliance Considerations
- GDPR requirements
- SOC 2 controls
- Industry-specific regulations
"""
    
    async def execute_security_workflow(self, workflow_type: str, 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a security-specific workflow."""
        # Map security workflow types to actual workflow IDs
        workflow_mapping = {
            'vulnerability_fix': 'wf1',  # bug-fix
            'security_feature': 'wf0',   # feature-development
            'emergency_patch': 'wf2',    # hotfix
            'security_review': 'wf5'     # pull-request-creation
        }
        
        workflow_id = workflow_mapping.get(workflow_type, workflow_type)
        
        # Add security-specific inputs
        inputs = context.copy()
        inputs['PRIORITY'] = 'high'  # Security items are high priority
        
        return await self.execute_workflow(workflow_id, inputs)