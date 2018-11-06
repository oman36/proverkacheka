import os
from datetime import datetime, timedelta
from decimal import Decimal
from urllib.parse import parse_qs

import requests

from . import exceptions


class API:
    endpoint = 'https://proverkacheka.nalog.ru:9999/'
    headers = {
        "Device-Id": "63343",
        "Device-OS": "Android 5.5",
        "Version": "2",
    }
    required_query_string_keys = {'i', 'fn', 't', 'fp', 's'}

    def __init__(self, username=None, password=None, params=None):
        self.username = os.environ.get('PROVERKACHEKA_USER') if username is None else username
        self.password = os.environ.get('PROVERKACHEKA_PASS') if password is None else password
        self.params = {
            'request_retries': 5,
            'request_retry_timeout': 0.5,
        }
        self.params.update(**(params or {}))

    def get_ticket_json_text(self, query_str: str) -> str:
        query = self.__parse_query(query_str)

        uri = 'v1/inns/*/kkts/*/fss/{fn}/tickets/{fd}'.format(fn=query['fn'], fd=query['i'])
        params = {
            'fiscalSign': query['fp'],
            'sendToEmail': "no",
        }
        url = self.__build_url(uri)

        response = None
        tries = 0

        while tries < self.params['request_retries']:
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    auth=(self.username, self.password),
                    timeout=self.params['request_retry_timeout'],
                )
            except requests.ReadTimeout:
                pass
            else:
                if response.status_code != 202:
                    break
            tries += 1

        if response is None:
            raise exceptions.RequestTimeoutException(self.params['request_retry_timeout'] * tries, url)

        if response.status_code == 202:
            raise exceptions.TicketDataNotExistsException(
                f'{url}?' + '&'.join(f'{k}={v}' for k, v in params.items()),
            )

        if response.status_code != 200:
            raise exceptions.InvalidStatusCodeException(
                response.status_code,
                f'{url}?' + '&'.join(f'{k}={v}' for k, v in params.items()),
            )

        return response.text

    def check_ticket(self, query_str):
        query = self.__parse_query(query_str)
        if None is query:
            return False

        uri = 'v1/ofds/*/inns/*/fss/{fn}/operations/{n}/tickets/{fd}'.format(fd=query['i'], **query)
        params = {
            'fiscalSign': query['fp'],
            'sum': int(Decimal(query['s']) * 100),
        }

        original_date = datetime.strptime(query['t'][:13], '%Y%m%dT%H%M')

        # hack. Because provider may save wrong time.
        dates_list = (
            original_date,
            original_date - timedelta(minutes=1),
            original_date + timedelta(minutes=1)
        )

        for next_date in dates_list:
            params['date'] = next_date.strftime('%Y-%m-%dT%H:%M:00')
            try:
                response = requests.get(
                    self.__build_url(uri),
                    params=params,
                    headers=self.headers,
                    auth=(self.username, self.password),
                    timeout=self.params['request_retry_timeout'],
                )
            except requests.ReadTimeout:
                return None

            if response.status_code == 204:
                return True

        return False

    def __parse_query(self, query_str):
        query = {k: v[0] for k, v in parse_qs(query_str).items()}

        diff = self.required_query_string_keys - set(query.keys())
        if diff:
            raise exceptions.InvalidQueryStringException(query, diff)

        return query

    def is_valid_query_string(self, query_str: str, silent=True):
        try:
            self.__parse_query(query_str)
        except exceptions.InvalidQueryStringException:
            if silent:
                return False
            raise

        return True

    def __build_url(self, uri):
        return self.endpoint + (uri[1:] if uri[:1] == '/' else uri)
