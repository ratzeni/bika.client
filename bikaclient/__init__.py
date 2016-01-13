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

    def get_contacts(self, params=None):
        return self._read(portal_type='Contact', query_params=params)

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

    # CREATING
    def create_batch(self, params=None):
        obj_path = self._make_obj_path('batches')
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='Batch', query_params=query_params)

    def create_analysis_request(self, params=None):
        obj_path=None
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='AnalysisRequest', query_params=query_params)

    def _create(self, obj_path, obj_type, query_params=None):
        api_service = 'create'
        url = self._make_bika_url(service=api_service)

        if obj_path:
            params = dict(
                    obj_path=obj_path,
                    obj_type=obj_type)
        else:
             params = dict(obj_type=obj_type)

        if query_params:
            params.update(query_params)

        resp = self._make_bika_request(url=url, params=params)
        return json.loads(resp)

    # REVIEW STATE

    def close_batch(self, params=None):
        query_params = self._make_query_params(params)
        return self._do_action_for(portal_type='Batch', action='close', query_params=query_params)

    def open_batch(self, params=None):
        query_params = self._make_query_params(params)
        return self._do_action_for(portal_type='Batch', action='open', query_params=query_params)

    def cancel_batch(self, params=None):
        query_params = self._make_query_params(params)
        return self._do_action_for(portal_type='Batch', action='cancel', query_params=query_params)

    def cancel_analysis_request(self, params=None):
        query_params = self._make_query_params(params)
        return self._do_action_for(portal_type='AnalysisRequest', action='cancel', query_params=query_params)

    def reinstate_batch(self, params=None):
        query_params = self._make_query_params(params)
        return self._do_action_for(portal_type='Batch', action='reinstate', query_params=query_params)

    def reinstate_analysis_request(self, params=None):
        query_params = self._make_query_params(params)
        return self._do_action_for(portal_type='AnalysisRequest', action='reinstate', query_params=query_params)

    def receive_sample(self, params=None):
        query_params = self._make_query_params(params)
        return self._do_action_for(portal_type='AnalysisRequest', action='receive', query_params=query_params)

    def submit(self, params=None):
        return self._do_action_for_many(action='submit', query_params=params)

    def verify(self, params=None):
        return self._do_action_for_many(action='verify', query_params=params)

    def publish(self, params=None):
        return self._do_action_for_many(action='publish', query_params=params)

    def update(self, params=None):
        return self._update(query_params=params)

    def update_many(self, params=None):
        return self._update_many(query_params=params)

    # low level methods
    def _do_action_for(self, portal_type, action, query_params):
        api_service = 'doActionFor'
        url = self._make_bika_url(service=api_service)

        params = dict(
                portal_type=portal_type,
                action=action)

        if query_params:
            params.update(query_params)

        resp = self._make_bika_request(url=url, params=params)
        return json.loads(resp)

    def _do_action_for_many(self, action, query_params):
        api_service = 'doActionFor_many'
        url = self._make_bika_url(service=api_service)

        params = dict(action=action)

        if query_params:
            params.update(query_params)

        resp = self._make_bika_request(url=url, params=params)
        return json.loads(resp)

    def _update(self, query_params):
        api_service = 'update'
        url = self._make_bika_url(service=api_service)

        params = dict()

        if query_params:
            params.update(query_params)

        resp = self._make_bika_request(url=url, params=params)
        return json.loads(resp)

    def _update_many(self, query_params):
        api_service = 'update_many'
        url = self._make_bika_url(service=api_service)

        params = dict()

        if query_params:
            params.update(query_params)

        resp = self._make_bika_request(url=url, params=params)
        return json.loads(resp)

    def _make_query_params(self, params):
        keywords_2_retrieve = ['Client', 'Service', 'SampleType', 'Contact','ContainerType', 'Batch']
        for k in keywords_2_retrieve:
            if k in params:
                portal_type = 'AnalysisService' if k in ['Service'] else k
                params[k] = "portal_type:{}|id:{}".format(portal_type, params[k])

        keywords_2_retrieve = ['Services', 'CCContact']
        for k in keywords_2_retrieve:
            if k in params:
                values = params[k].split('|')
                params[k] = list()
                for v in values:
                    portal_type = 'AnalysisService' if k in ['Services'] else k
                    portal_type = 'Contact' if portal_type in ['CCContact'] else portal_type
                    value = {"{}:list".format(k): "portal_type:{}|id:{}".format(portal_type, v)}
                    params[k].append(value)

        keywords_2_retrieve = ['ids']
        for k in keywords_2_retrieve:
            if k in params:
                values = params[k].split('|')
                key = k[:-1]
                params[key] = list()
                for v in values:
                    value = {"{}".format(key): "{}".format(v)}
                    params[key].append(value)
                del params[k]
        return params

    def _make_obj_path(self, folder):
        return '/{}'.format(os.path.join(os.path.split(self.__url)[1], folder))

    def _make_bika_url(self, service, is_login_service=False):
        prefix = '@@API' if not is_login_service else ''
        return os.path.join(self.__url, prefix, service)

    def _make_bika_request(self, url, params=dict()):
        self.__reset_error()
        try:
            f = self.__opener.open(url, self._make_bika_urlencode(params))
            data = f.read()
            f.close()
        except:
            self.__set_error()
            data = json.dumps(dict(error=self.is_error()))
        return data

    def _make_bika_urlencode(self, params):
        params_list = list()
        keys = list()
        for key, value in params.iteritems():
            if isinstance(value, list):
                for v in value:
                    params_list.append({key: v})
                keys.append(key)

        for k in keys:
            del params[k]

        url = urllib.urlencode(params)

        for p in params_list:
            for k,v in p.iteritems():
                url = "{}&{}".format(url,urllib.urlencode(v))

        return url

    def __reset_error(self):
        self.__error = False

    def __set_error(self):
        self.__error = True


