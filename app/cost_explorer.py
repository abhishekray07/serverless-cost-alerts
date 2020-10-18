import boto3
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class CostExplorer:
    TODAY_DATE = datetime.utcnow().date()
    CUR_MONTH_DATE = TODAY_DATE.replace(day=1)
    PREV_MONTH_DATE: date = CUR_MONTH_DATE - relativedelta(months=+1)

    def __init__(self):
        self.client = boto3.client("ce")
        self.metrics = ["UNBLENDED_COST"]
        self.currency:str = "USD"

        self.daily_report_kwargs = {
            "TimePeriod": self._get_timeperiod(
                start=self.TODAY_DATE - timedelta(days=2), # start_dt is inclusive
                end=self.TODAY_DATE, # end_dt is exclusive
            ),
            "Metrics": self.metrics,
            "Granularity": "DAILY"
        }

        self.monthly_report_kwargs = {
            "TimePeriod": self._get_timeperiod(
                start=self.PREV_MONTH_DATE, # start_dt is inclusive
                end=self.TODAY_DATE, # end_dt is exclusive
            ),
            "Metrics": self.metrics,
            "Granularity": "MONTHLY"
        }

    def _get_timeperiod(self, start: date, end: date):
        return {
            "Start": start.isoformat(),
            "End": end.isoformat(),
        }

    def _get_data(self, results):
        """
        Retrieves the individual billing rows from cost explorer data.
        """
        rows = []
        for v in results:
            row = {"date":v["TimePeriod"]["Start"]}
            for i in v["Groups"]:
                key = i["Keys"][0]
                row.update({key:float(i["Metrics"]["UnblendedCost"]["Amount"])})
            row.update({"Total":float(v["Total"]["UnblendedCost"]["Amount"])})
            rows.append(row)

        return [f"{row['date']}: {round(row['Total'], 2)}" for row in rows]

    def generate_report(self, report_kwargs):
        """
        Get cost data based on the granularity, start date and end date.
        """
        response = self.client.get_cost_and_usage(**report_kwargs)
        return self._get_data(response["ResultsByTime"])
