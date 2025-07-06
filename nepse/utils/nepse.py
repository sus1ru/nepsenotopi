import functools
import time
import httpx
import json
from httpx import RemoteProtocolError, ReadError, ConnectError
import tqdm

from nepse.utils.nepse_errors import (
    NepseInvalidServerResponse,
    NepseInvalidClientRequest,
    NepseNetworkError,
)
from nepse.utils.nepse_settings import NepseSettings
from nepse.utils.request_manager import RequestManager


class Nepse(NepseSettings):
    def __init__(self, tls_verify=False):
        # explicitly set value to True, can be disabled by user using setTLSVerification method
        self.client = httpx.Client(verify=tls_verify, http2=True, timeout=100)
        self.request_manager = RequestManager(httpx_client=self.client)

    def _request_handler(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                response = func(self, *args, **kwargs)
                status_code = response.status_code

                if status_code == 400:
                    raise NepseInvalidClientRequest()

                elif status_code == 401:
                    self.request_manager.refresh_tokens()
                    response = func(self, *args, **kwargs)

                elif status_code == 502:
                    raise NepseInvalidServerResponse()

                elif not (status_code >= 200 and status_code < 300):
                    raise NepseNetworkError()

                return response.json()
        
            except (RemoteProtocolError, ReadError, ConnectError):
                return func(self, *args, **kwargs)

            except json.JSONDecodeError:
                return {
                    'result': False,
                    'code': 400,
                    'error': response.text
                }

        return wrapper

    @_request_handler
    def get(self, url, with_auth_headers=True):
        return self.client.get(
            self.abs_url(url),
            headers=(
                self.request_manager.auth_headers
                if with_auth_headers
                else self.HEADERS
            ),
        )

    @_request_handler
    def post(self, url, payload):
        return self.client.post(
            self.abs_url(url),
            headers=self.request_manager.auth_headers,
            data=payload,
        )

    def fetch_data(self, url_alias, params={}):
        method, url, id_type = self.get_url_data(url_alias, params)

        if method == 'get':
            result = self.get(url)

        elif method == 'post':
            id_value = (
                self
                .request_manager
                .fetch_request_id(id_type=id_type)
            )
            result = self.post(url, payload=json.dumps({'id': id_value}))

        else:
            result = {}

        return result
