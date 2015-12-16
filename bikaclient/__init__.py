import os
import urllib
import urllib2
import json


class BikaClient():
    def __init__(self, host='http://localhost:8080/Plone', username='admin', password='secret'):
        self.__url = host
        self.__opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        self.__error = False
        try:
            self.__login(username, password)
        except:
            self.__set_error()

    def __login(self, username, password):
        params = {
            "form.submitted": 1,
            "pwd_empty": 0,
            "__ac_name": username,
            "__ac_password": password,
            "submit": "Log in"
        }
        api_service = 'login_form'
        url = self._make_bika_url(service=api_service, is_login_service=True)
        self._make_bika_request(url=url, params=params)

    def is_error(self):
        return self.__error

    def get_clients(self, params=None):
        return self._read(portal_type='Client', query_params=params)

    def get_samples(self, params=None):
        return self._read(portal_type='Sample', query_params=params)

    def get_analysis_requests(self, params=None):
        return self._read(portal_type='AnalysisRequest', query_params=params)

    def get_arimports(self, params=None):
        return self._read(portal_type='ARImport', query_params=params)

    def get_batches(self, params=None):
        return self._read(portal_type='Batch', query_params=params)

    def get_worksheets(self, params=None):
        return self._read(portal_type='Worksheet', query_params=params)

    def get_invoices(self, params=None):
        return self._read(portal_type='Invoice', query_params=params)

    def get_price_list(self, params=None):
        return self._read(portal_type='PriceList', query_params=params)

    def get_supply_order(self, params=None):
        return self._read(portal_type='SupplyOrder', query_params=params)

    # BIKA SETUP

    def get_artemplates(self, params=None):
        return self._read(portal_type='ARTemplate', query_params=params)

    def get_analysis_profiles(self, params=None):
        return self._read(portal_type='AnalysisProfile', query_params=params)

    def get_analysis_services(self, params=None):
        return self._read(portal_type='AnalysisService', query_params=params)

    def get_sample_types(self, params=None):
        return self._read(portal_type='SampleType', query_params=params)

    def _read(self, portal_type, query_params=None):
        api_service = 'read'
        url = self._make_bika_url(service=api_service)

        params = dict(
                portal_type=portal_type,
                page_size=0)
        if query_params:
            params.update(query_params)

        resp = self._make_bika_request(url=url, params=params)
        return json.loads(resp)

    def _make_bika_url(self, service, is_login_service=False):
        prefix = '@@API' if not is_login_service else ''
        return os.path.join(self.__url, prefix, service)

    def _make_bika_request(self, url, params=dict()):
        self.__reset_error()
        try:
            f = self.__opener.open(url, urllib.urlencode(params))
            data = f.read()
            f.close()
        except:
            self.__set_error()
            data = json.dumps(dict(error=self.is_error()))
        return data

    def __reset_error(self):
        self.__error = False

    def __set_error(self):
        self.__error = True

        return data
