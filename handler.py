from app.cost_explorer import CostExplorer
from app.email import EmailClient


def generate_report(event, context):
    ce = CostExplorer()
    daily_report = ce.generate_report(ce.daily_report_kwargs)
    monthly_report = ce.generate_report(ce.monthly_report_kwargs)

    email_client = EmailClient()
    email_client.send(
        daily_billing_report=daily_report,
        monthly_billing_report=monthly_report
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": "success",
    }

