from django.conf import settings

class NepseSettings:
    BASE_URL = 'https://nepalstock.com'
    AUTHENTICATE_URL = '/api/authenticate/prove'
    REFRESH_URL = '/api/authenticate/refresh-token'
    NEPSE_OPEN_URL = '/api/nots/nepse-data/market-open'

    CSS_WASM_PATH = settings.BASE_DIR / 'nepse/utils/css.wasm'

    ENDPOINTS = {
        'nepse_open': {
            'method': 'get',
            'url': '/api/nots/nepse-data/market-open'
        },
        'sector': {
            'method': 'get',
            'url': '/api/nots/sector'
        },
        'share_group': {
            'method': 'get',
            'url': '/api/nots/security/shareGroup/'
        },
        'price_volume': {
            'method': 'get',
            'url': '/api/nots/securityDailyTradeStat/58'
        },
        'summary': {
            'method': 'get',
            'url': '/api/nots/market-summary/'
        },
        'top_ten_trade': {
            'method': 'get',
            'url': '/api/nots/top-ten/trade'
        },
        'top_ten_transaction': {
            'method': 'get',
            'url': '/api/nots/top-ten/transaction'
        },
        'top_ten_turnover': {
            'method': 'get',
            'url': '/api/nots/top-ten/turnover'
        },
        'supply_demand': {
            'method': 'get',
            'url': '/api/nots/nepse-data/supplydemand'
        },
        'top_gainers': {
            'method': 'get',
            'url': '/api/nots/top-ten/top-gainer'
        },
        'top_losers': {
            'method': 'get',
            'url': '/api/nots/top-ten/top-loser'
        },
        'nepse_index': {
            'method': 'get',
            'url': '/api/nots/nepse-index'
        },
        'nepse_subindices': {
            'method': 'get',
            'url': '/api/nots'
        },
        'live_market': {
            'method': 'get',
            'url': '/api/nots/lives-market'
        },
        'market_depth': {
            'method': 'get',
            'url': '/api/nots/nepse-data/marketdepth/'
        },
        'turnover': {
            'method': 'get',
            'url': '/api/nots/top-ten/turnover'
        },
        'todays_price': {
            'method': 'post',
            'payload_alias': 'floorsheet',
            'url': '/api/nots/nepse-data/today-price'
        },
        'nepse_index_daily_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/58'
        },
        'sensitive_index_daily_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/57'
        },
        'float_index_daily_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/62'
        },
        'sensitive_float_index_daily_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/63'
        },
        'banking_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/51'
        },
        'development_bank_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/55'
        },
        'finance_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/60'
        },
        'hotel_tourism_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/52'
        },
        'hydro_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/54'
        },
        'investment_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/67'
        },
        'life_insurance_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/65'
        },
        'manufacturing_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/56'
        },
        'microfinance_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/64'
        },
        'mutual_fund_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/66'
        },
        'non_life_insurance_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/59'
        },
        'others_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/53'
        },
        'trading_sub_index_graph': {
            'method': 'post',
            'payload_alias': 'basic',
            'url': '/api/nots/graph/index/61'
        },
        'company': {
            'method': 'get',
            'url': '/api/nots/company/list'
        },
        'security': {
            'method': 'get',
            'url': '/api/nots/security'
        },
        'company_price_volume_history': {
            'method': 'get',
            'url': '/api/nots/market/history/security/'
        },
        'company_daily_graph': {
            'method': 'post',
            'payload_alias': 'scrips',
            'url': '/api/nots/market/graphdata/daily/'
        },
        'company_details': {
            'method': 'post',
            'payload_alias': 'scrips',
            'url': '/api/nots/security/'
        },
        'floor_sheet': {
            'method': 'post',
            'payload_alias': 'floorsheet',
            'url': '/api/nots/nepse-data/floorsheet'
        },
        'company_floorsheet': {
            'method': 'post',
            'payload_alias': 'floorsheet',
            'url': '/api/nots/security/floorsheet/'
        }
    }

    DUMMY_DATA = [
        147, 117, 239, 143, 157, 312, 161, 612, 512, 804, 
        411, 527, 170, 511, 421, 667, 764, 621, 301, 106,
        133, 793, 411, 511, 312, 423, 344, 346, 653, 758,
        342, 222, 236, 811, 711, 611, 122, 447, 128, 199,
        183, 135, 489, 703, 800, 745, 152, 863, 134, 211,
        142, 564, 375, 793, 212, 153, 138, 153, 648, 611,
        151, 649, 318, 143, 117, 756, 119, 141, 717, 113,
        112, 146, 162, 660, 693, 261, 362, 354, 251, 641,
        157, 178, 631, 192, 734, 445, 192, 883, 187, 122,
        591, 731, 852, 384, 565, 596, 451, 772, 624, 691,
    ]

    HEADERS = {
        "Host": "",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
        "Referer": "",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers"
    }
    HEADERS["Host"] = BASE_URL.replace("https://", "")
    HEADERS["Referer"] = BASE_URL.replace("https://", "")

    @classmethod
    def abs_url(cls, url):
        return f"{cls.BASE_URL}{url}"

    @classmethod
    def generate_url(cls, url_alias):
        if url_alias in cls.ENDPOINTS:
            return cls.abs_url(cls.ENDPOINTS.get(url_alias).get('url'))

        return None

    @classmethod
    def get_url_data(cls, url_alias):
        url_data = cls.ENDPOINTS.get(url_alias, '')
        partial_url = url_data.get('url')
        raw_params = url_data.get('params', {})

        if raw_params:
            params = '&'.join(f'{key}={val}' for key, val in raw_params.items())
            partial_url = f'{partial_url}?&{params}'

        return url_data.get('method'), partial_url, url_data.get('payload_alias')
