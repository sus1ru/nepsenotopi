import functools
import re
from urllib.parse import urlparse, urlunparse
import numpy as np
import pandas as pd

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps

from nepse.models import Company, InstrumentType, Sector, Security, ShareGroup
from nepse.utils.nepse import Nepse
# from polls.models import Question as Poll

class Command(BaseCommand):
    help = "Initialize the NEPSE prerequisites."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SETTINGS = {
            'sector': {
                'db_table': 'nepse.Sector',
                'callback': self.sync_sector,
                'unique_field': ['sector_description'],
            },
            'share_group': {
                'db_table': 'nepse.ShareGroup',
                'callback': self.sync_share_group,
                'unique_field': ['name'],
            },
            'instrument_type': {
                'db_table': 'nepse.InstrumentType',
                'callback': self.sync_instrument_type,
                'unique_field': ['description'],
            },
            'security': {
                'db_table': 'nepse.Security',
                'callback': self.sync_security,
                'unique_field': ['symbol'],
            },
            'company': {
                'db_table': 'nepse.Company',
                'callback': self.sync_company,
                'unique_field': ['symbol'],
            }
        }

    def add_arguments(self, parser):
        sync_alias_choices = list(self.SETTINGS.keys()) + ['all']
        parser.add_argument(
            '--sync', type=str, default='all',
            choices=sync_alias_choices,
            help='Specify what to sync from Nepse API',
        )

    def handle(self, *args, **options):
        nepse = Nepse()
        alias = options.get('sync')
        func = self.SETTINGS.get(alias, {}).get('callback', self.sync_all)
        func(nepse, alias)

    def _print_sync_status(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            _alias = args[1]
            table_title = ' '.join(tk.capitalize() for tk in _alias.split('_'))
            msg = self.style.WARNING(f'Started: {table_title}!')
            self.stdout.write(msg)

            try:
                result = func(self, *args, **kwargs)
                msg = self.style.SUCCESS(f'Completed: {table_title}!')

            except Exception as e:
                msg = self.style.ERROR(f'Error: {table_title}: {str(e)}')
                result = None

            finally:
                self.stdout.write(msg)
                return result

        return wrapper

    def sync_all(self, nepse: Nepse, alias: str):
        for alias, setting in self.SETTINGS.items():
            setting.get('callback')(nepse, alias)

    @_print_sync_status
    def sync_sector(self, nepse: Nepse, alias: str):
        raw_data = nepse.fetch_data(alias).get('sectors')
        self._sync(alias, raw_data)

    @_print_sync_status
    def sync_share_group(self, nepse: Nepse, alias: str):
        raw_data = nepse.fetch_data(alias)
        self._sync(alias, raw_data)

    @_print_sync_status
    def sync_share_group(self, nepse: Nepse, alias: str):
        raw_data = nepse.fetch_data(alias)
        self._sync(alias, raw_data)

    @_print_sync_status
    def sync_instrument_type(self, nepse: Nepse, alias: str):
        raw_data = [
            {
                'code': code,
                'description': desc,
                'active_status': 'A'
            }
            for code, desc in InstrumentType.INSTRUMENT_TYPE_CODES
        ]
        self._sync(alias, raw_data)

    @_print_sync_status
    def sync_security(self, nepse: Nepse, alias: str):
        raw_data = nepse.fetch_data(alias)
        df = pd.DataFrame(raw_data)
        df['isPromoter'] = 'Y'

        raw_data_np = nepse.fetch_data(alias, params={'nonPromoter': True})
        df_np = pd.DataFrame(raw_data_np)

        df.loc[df['symbol'].isin(df_np['symbol']), 'isPromoter'] = 'N'

        raw_data = df.to_dict(orient='records')
        self._sync(alias, raw_data)

    @_print_sync_status
    def sync_company(self, nepse: Nepse, alias: str):
        def clean_url(url):
            if not url.startswith(('http://', 'https://')):
                parsed = urlparse(f'https://{url}')
            else:
                parsed = urlparse(url)

            scheme = 'https'
            netloc = parsed.netloc
            if netloc.startswith('www.'):
                netloc = netloc[4:]

            if netloc:
                cleaned = parsed._replace(
                    scheme=scheme,
                    netloc=netloc,
                    fragment=''
                )
                return urlunparse(cleaned)

            return ''

        for _alias in ['sector', 'security', 'instrument_type']:
            self.SETTINGS.get(_alias).get('callback')(nepse, _alias)

        security_map = dict(Security.objects.values_list('symbol', 'id'))
        sector_map = dict(Sector.objects.values_list('sector_description', 'id'))
        instr_type_map = dict(InstrumentType.objects.values_list('description', 'id'))

        raw_data = nepse.fetch_data('company')
        df = pd.DataFrame(raw_data)
        df['sectorId'] = (
            df['sectorName']
            .map(sector_map)
            .fillna(Sector.objects.get(sector_description='Others').id)
            .astype('Int64')
        )
        df['securityId'] = df['symbol'].map(security_map)
        df['instrumentTypeId'] = df['instrumentType'].map(instr_type_map)
        df['website'] = df['website'].apply(clean_url)
        df['activeStatus'] = df['status']

        df = df.drop(
            [
                'securityName', 'sectorName', 'status',
                'regulatoryBody', 'instrumentType'
            ],
            axis=1
        )
        raw_data = df.to_dict(orient='records')
        self._sync(alias, raw_data)

    def _sync(self, alias, raw_data):
        table = apps.get_model(self.SETTINGS.get(alias).get('db_table'))
        unique_fields = self.SETTINGS.get(alias).get('unique_field')
        cleaned_data, fields = self.clean_data(raw_data)
        update_fields = [
            field for field in fields
            if field not in unique_fields
        ]
        prep_rows = []

        for row in cleaned_data:
            prep_rows.append(table(**row))

        table.objects.bulk_create(
            prep_rows, batch_size=1024,
            update_conflicts=True,
            update_fields=update_fields,
            unique_fields=unique_fields
        )

    def clean_data(self, raw_data):
        df = pd.DataFrame.from_dict(raw_data)
        df = df.rename(
            columns=lambda x: re.sub(r'(?<!^)(?=[A-Z])', '_', x).lower()
        )
        df = df.drop('id', axis=1, errors='ignore')

        return df.to_dict(orient='records'), list(df.columns)
