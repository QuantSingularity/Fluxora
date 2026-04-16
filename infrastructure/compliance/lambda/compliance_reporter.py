import csv
import io
import json
import logging
import os
from datetime import datetime
from typing import Any

import boto3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def lambda_handler(event: Any, context: Any) -> Any:
    """
    Lambda function to generate compliance reports for PCI DSS, GDPR, and SOC 2
    """
    config_client = boto3.client("config")
    s3_client = boto3.client("s3")
    sns_client = boto3.client("sns")
    app_name = os.environ["APP_NAME"]
    environment = os.environ["ENVIRONMENT"]
    bucket_name = os.environ["BUCKET_NAME"]
    sns_topic = os.environ["SNS_TOPIC"]
    try:
        report_data = generate_compliance_report(config_client, app_name, environment)
        csv_content = create_csv_report(report_data)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_key = (
            f"compliance-reports/{environment}/{timestamp}_compliance_report.csv"
        )
        s3_client.put_object(
            Bucket=bucket_name,
            Key=report_key,
            Body=csv_content.encode("utf-8"),
            ContentType="text/csv",
            ServerSideEncryption="aws:kms",
        )
        summary = generate_summary_report(report_data)
        send_notification(sns_client, sns_topic, summary, report_key, bucket_name)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Compliance report generated successfully",
                    "report_location": f"s3://{bucket_name}/{report_key}",
                    "summary": summary,
                }
            ),
        }
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}", exc_info=True)
        error_message = f"Failed to generate compliance report: {str(e)}"
        try:
            sns_client.publish(
                TopicArn=sns_topic,
                Subject=f"Compliance Report Generation Failed - {app_name} {environment}",
                Message=error_message,
            )
        except Exception as sns_err:
            logger.error(f"Failed to send SNS failure notification: {str(sns_err)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def generate_compliance_report(
    config_client: Any, app_name: str, environment: str
) -> dict:
    """
    Generate comprehensive compliance report data
    """
    report_data: dict = {"pci_dss": [], "gdpr": [], "soc2": [], "general": []}
    paginator = config_client.get_paginator("describe_config_rules")
    for page in paginator.paginate():
        for rule in page["ConfigRules"]:
            rule_name = rule["ConfigRuleName"]
            try:
                results_paginator = config_client.get_paginator(
                    "get_compliance_details_by_config_rule"
                )
                for results_page in results_paginator.paginate(
                    ConfigRuleName=rule_name
                ):
                    for result in results_page["EvaluationResults"]:
                        compliance_data = {
                            "rule_name": rule_name,
                            "resource_type": result["EvaluationResultIdentifier"][
                                "EvaluationResultQualifier"
                            ]["ResourceType"],
                            "resource_id": result["EvaluationResultIdentifier"][
                                "EvaluationResultQualifier"
                            ]["ResourceId"],
                            "compliance_type": result["ComplianceType"],
                            "result_recorded_time": result[
                                "ResultRecordedTime"
                            ].isoformat(),
                            "annotation": result.get("Annotation", ""),
                            "config_rule_invoked_time": result[
                                "ConfigRuleInvokedTime"
                            ].isoformat(),
                        }
                        if "pci" in rule_name.lower():
                            report_data["pci_dss"].append(compliance_data)
                        elif "gdpr" in rule_name.lower():
                            report_data["gdpr"].append(compliance_data)
                        elif "soc2" in rule_name.lower():
                            report_data["soc2"].append(compliance_data)
                        else:
                            report_data["general"].append(compliance_data)
            except Exception as e:
                logger.warning(
                    f"Error getting compliance details for rule {rule_name}: {str(e)}"
                )
                continue
    return report_data


def create_csv_report(report_data: dict) -> str:
    """
    Create CSV format compliance report
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Framework",
            "Rule Name",
            "Resource Type",
            "Resource ID",
            "Compliance Status",
            "Last Evaluated",
            "Rule Invoked Time",
            "Annotation",
        ]
    )
    for framework, data in report_data.items():
        for item in data:
            writer.writerow(
                [
                    framework.upper(),
                    item["rule_name"],
                    item["resource_type"],
                    item["resource_id"],
                    item["compliance_type"],
                    item["result_recorded_time"],
                    item["config_rule_invoked_time"],
                    item["annotation"],
                ]
            )
    return output.getvalue()


def generate_summary_report(report_data: dict) -> dict:
    """
    Generate summary statistics for compliance report
    """
    summary: dict = {
        "total_resources_evaluated": 0,
        "compliant_resources": 0,
        "non_compliant_resources": 0,
        "frameworks": {},
    }
    for framework, data in report_data.items():
        framework_summary: dict = {
            "total": len(data),
            "compliant": 0,
            "non_compliant": 0,
            "compliance_percentage": 0.0,
        }
        for item in data:
            if item["compliance_type"] == "COMPLIANT":
                framework_summary["compliant"] += 1
                summary["compliant_resources"] += 1
            elif item["compliance_type"] == "NON_COMPLIANT":
                framework_summary["non_compliant"] += 1
                summary["non_compliant_resources"] += 1
        if framework_summary["total"] > 0:
            framework_summary["compliance_percentage"] = round(
                framework_summary["compliant"] / framework_summary["total"] * 100, 2
            )
        summary["frameworks"][framework] = framework_summary
        summary["total_resources_evaluated"] += framework_summary["total"]
    if summary["total_resources_evaluated"] > 0:
        summary["overall_compliance_percentage"] = round(
            summary["compliant_resources"] / summary["total_resources_evaluated"] * 100,
            2,
        )
    else:
        summary["overall_compliance_percentage"] = 0.0
    return summary


def send_notification(
    sns_client: Any, sns_topic: str, summary: dict, report_key: str, bucket_name: str
) -> None:
    """
    Send notification with compliance report summary
    """
    message = (
        f"\nCompliance Report Generated Successfully\n\n"
        f"Overall Compliance: {summary['overall_compliance_percentage']}%\n"
        f"Total Resources Evaluated: {summary['total_resources_evaluated']}\n"
        f"Compliant Resources: {summary['compliant_resources']}\n"
        f"Non-Compliant Resources: {summary['non_compliant_resources']}\n\n"
        f"Framework Breakdown:\n"
    )
    for framework, data in summary["frameworks"].items():
        message += (
            f"\n{framework.upper()}:\n"
            f"  - Total: {data['total']}\n"
            f"  - Compliant: {data['compliant']}\n"
            f"  - Non-Compliant: {data['non_compliant']}\n"
            f"  - Compliance Rate: {data['compliance_percentage']}%\n"
        )
    message += (
        f"\nReport Location: s3://{bucket_name}/{report_key}\n\n"
        f"Generated at: {datetime.utcnow().isoformat()}Z\n"
    )
    sns_client.publish(
        TopicArn=sns_topic,
        Subject=f"Compliance Report - {summary['overall_compliance_percentage']}% Overall Compliance",
        Message=message,
    )
