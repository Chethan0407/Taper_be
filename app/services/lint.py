from typing import List, Dict, Any
import json
from fastapi import HTTPException, status
import boto3
from botocore.exceptions import ClientError

from app.schemas.spec import Spec
from app.schemas.lint_result import LintResult, LintIssue, LintSeverity
from app.core.config import settings

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

async def lint_spec(spec: Spec) -> LintResult:
    """
    Lint a spec file from S3.
    """
    try:
        # Download spec file from S3
        response = s3_client.get_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=spec.file_path
        )
        spec_content = response['Body'].read().decode('utf-8')
        
        # Parse spec content
        try:
            spec_data = json.loads(spec_content)
        except json.JSONDecodeError:
            return LintResult(
                spec_id=spec.id,
                issues=[
                    LintIssue(
                        severity=LintSeverity.ERROR,
                        type="INVALID_JSON",
                        message="Spec file is not valid JSON",
                        location="file"
                    )
                ],
                summary="Invalid JSON format"
            )
        
        # Run linting rules
        issues = []
        
        # Check required fields
        required_fields = ["name", "version", "description"]
        for field in required_fields:
            if field not in spec_data:
                issues.append(
                    LintIssue(
                        severity=LintSeverity.ERROR,
                        type="MISSING_FIELD",
                        message=f"Required field '{field}' is missing",
                        location=f"root.{field}"
                    )
                )
        
        # Check version format
        if "version" in spec_data:
            version = spec_data["version"]
            if not isinstance(version, str) or not version.strip():
                issues.append(
                    LintIssue(
                        severity=LintSeverity.ERROR,
                        type="INVALID_VERSION",
                        message="Version must be a non-empty string",
                        location="root.version"
                    )
                )
        
        # Check spec_metadata format
        if "spec_metadata" in spec_data:
            spec_metadata = spec_data["spec_metadata"]
            if not isinstance(spec_metadata, dict):
                issues.append(
                    LintIssue(
                        severity=LintSeverity.ERROR,
                        type="INVALID_METADATA",
                        message="Metadata must be an object",
                        location="root.spec_metadata"
                    )
                )
        
        # Generate summary
        if issues:
            error_count = sum(1 for issue in issues if issue.severity == LintSeverity.ERROR)
            warning_count = sum(1 for issue in issues if issue.severity == LintSeverity.WARNING)
            info_count = sum(1 for issue in issues if issue.severity == LintSeverity.INFO)
            
            summary = f"Found {error_count} errors, {warning_count} warnings, and {info_count} info messages"
        else:
            summary = "No issues found"
        
        return LintResult(
            spec_id=spec.id,
            issues=issues,
            summary=summary
        )
        
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accessing spec file: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during linting: {str(e)}"
        ) 