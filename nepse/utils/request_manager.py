import functools
import json
from datetime import date
import pywasm

from nepse.utils.nepse_settings import NepseSettings
from nepse.utils.nepse_errors import NepseNetworkError


class RequestManager(NepseSettings):
    def __init__(self, httpx_client=None):
        self.httpx_client = httpx_client
        # self.TOKEN_EXPIRATION_IN_SECONDS = 45

        self.init_auth_url = self.abs_url(self.AUTHENTICATE_URL)
        self.refresh_token_url = self.abs_url(self.REFRESH_URL)

        self.token_parser = TokenParser()
        self.parsed_token_data = {}
        self.request_requisites = {}

        self.init_tokens()

    @property
    def access_token(self):
        return self.parsed_token_data.get('accessToken')

    @property
    def refresh_token(self):
        return self.parsed_token_data.get('refreshToken')

    @property
    def token_time_stamp(self):
        return self.parsed_token_data['serverTime'] // 1000

    @property
    def salts(self):
        return self.parsed_token_data.get('salts')

    @property
    def init_id(self):
        return self.request_requisites.get('id')

    @property
    def auth_headers(self):
        return {
            "Authorization": f"Salter {self.access_token}",
            "Content-Type": "application/json",
            **self.HEADERS,
        }

    def fetch_payload_id(self, payload_alias='basic'):
        """
        payload_alias: 'basic', 'floorsheet', 'scrips'
        """
        return self.request_requisites.get(payload_alias)

    def __post_process_tokens(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            response = func(self, *args, **kwargs)
            status_code = response.status_code

            if status_code != 200:
                raise NepseNetworkError

            try:
                response = response.json()
                response['salts'] = [response[f'salt{i}'] for i in range(1, 6)]
                self.parsed_token_data = (
                    self
                    .token_parser
                    .parse_token_response(response)
                    .copy()
                )

                self.refresh_request_requisites()

            except json.JSONDecodeError:
                return {
                    'result': False,
                    'code': 400,
                    'error': response.text
                }

            return response

        return wrapper

    @__post_process_tokens
    def init_tokens(self):
        return self.httpx_client.get(url=self.init_auth_url)

    @__post_process_tokens
    def refresh_tokens(self):
        print()
        print('#'*8, 'refreshing tokens', '#'*8)
        print()
        return self.httpx_client.post(
            self.refresh_token_url,
            headers=self.auth_headers,
            data=json.dumps({'refreshToken': self.refresh_token}),
        )

    def refresh_request_requisites(self):
        print()
        print('#'*8, 'refreshing requisites', '#'*8)
        print()
        response = self.httpx_client.get(
            url=self.abs_url(self.NEPSE_OPEN_URL),
            headers=self.auth_headers,
        )

        try:
            self.request_requisites = response.json()
        except json.JSONDecodeError:
            raise NepseNetworkError

        today = date.today().day

        for_scrips = (
            self.DUMMY_DATA[self.init_id] +
            self.init_id + 2 * (today)
        )

        self.request_requisites['scrips'] = for_scrips
        self.request_requisites['basic'] = (
            for_scrips
            + self.salts[3 if for_scrips % 10 < 5 else 1] * today
            - self.salts[(3 if for_scrips % 10 < 5 else 1) - 1]
        )
        self.request_requisites['floorsheet'] = (
            for_scrips
            + self.salts[1 if for_scrips % 10 < 4 else 3] * today
            - self.salts[(1 if for_scrips % 10 < 4 else 3) - 1]
        )

        return self.request_requisites


class TokenParser:
    def __init__(self):
        self.runtime = pywasm.core.Runtime()
        self.wasm_module = self.runtime.instance_from_file(NepseSettings.CSS_WASM_PATH)

    def parse_token_response(self, token_response):
        func_and_salts = {
            'accessToken': [
                ('cdx', [1, 2, 3, 4, 5]),
                ('rdx', [1, 2, 4, 3, 5]),
                ('bdx', [1, 2, 4, 3, 5]),
                ('ndx', [1, 2, 4, 3, 5]),
                ('mdx', [1, 2, 4, 3, 5]),
            ],
            'refreshToken': [
                ('cdx', [2, 1, 3, 5, 4]),
                ('rdx', [2, 1, 3, 4, 5]),
                ('bdx', [2, 1, 4, 3, 5]),
                ('ndx', [2, 1, 4, 3, 5]),
                ('mdx', [2, 1, 4, 3, 5]),
            ]
        }

        for token_type in ('accessToken', 'refreshToken'):
            unparsed_token = token_response.get(token_type)
            token_settings = func_and_salts.get(token_type)

            parsed_token = ''
            lidx = 0
            ridx = 0

            for func_alias, salt_index in token_settings:
                ridx = self.runtime.invocate(
                    self.wasm_module, func_alias,
                    [token_response[f'salt{idx}'] for idx in salt_index],
                )[0]
                parsed_token += unparsed_token[lidx:ridx]
                lidx = ridx + 1

            parsed_token += unparsed_token[lidx:]
            token_response[token_type] = parsed_token

        return token_response
