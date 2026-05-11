import datetime
import re
import time
from dateutil.relativedelta import relativedelta
from celery import shared_task
import numpy as np
import pandas as pd

from nepse.models import Security, SecurityLog
from nepse.utils.nepse import Nepse


@shared_task(
    time_limit=300000,
    retries=3,
    soft_time_limit=300000,
    queue="realtime",
)
def fetch_daily_price_data(business_date: str = None):
    nepse = Nepse()
    today = datetime.date.today()
    valid_past_date = today - relativedelta(years=1)

    security_map = dict(Security.objects.values_list('symbol', 'id'))

    try:
        result = nepse.fetch_data(
            'today_price',
            params={'size': 500}
        )
        raw_data = result.get('content')

    except Exception as e:
        pass

    if raw_data:
        df = pd.DataFrame(raw_data)

        df['securityId'] = df['symbol'].map(security_map)
        df['businessDate'] = (
            pd.to_datetime(df['businessDate'])
            .dt.tz_localize('UTC')
        )
        df['lastUpdatedTime'] = (
            pd.to_datetime(df['lastUpdatedTime'])
            .dt.tz_localize('Asia/Kathmandu')
        )

        df = df.drop(['id', 'securityName', 'symbol'], axis=1)
        df = df.rename(
            columns=lambda x: re.sub(r'(?<!^)(?=[A-Z])', '_', x).lower()
        )
        row_data = df.replace({np.nan: None, pd.NaT: None}).to_dict(orient='records')
        prep_rows = []
        for row in row_data:
            is_new = not (
                SecurityLog.objects
                .filter(
                    security_id=row.get('securityId'),
                    last_updated_time=row.get('lastUpdatedTime'),
                ).exists()
            )
            if is_new:
                prep_rows.append(SecurityLog(**row))

        SecurityLog.objects.bulk_create(prep_rows)
        if prep_rows:
            from portfolio.tasks import check_watchlist_alerts

            check_watchlist_alerts.delay()

        print(f'Done for {valid_past_date}')
        time.sleep(0.125)
        valid_past_date = valid_past_date + relativedelta(days=1)
