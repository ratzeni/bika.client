import datetime
import json
import os

from bikaclient.__version__ import __version__

from six import iteritems
from six.moves.urllib.request import Request, build_opener, HTTPCookieProcessor
from six.moves.urllib.parse import urlencode
from six.moves.urllib.error import URLError
from distutils.util import strtobool


class BikaClient:
    def __init__(self, host='http://localhost:8080/Plone', username='admin', password='secret'):
        self.__url = host
        self.__opener = build_opener(HTTPCookieProcessor())
        self.__error = False
        self.__msg = ''
        self.__is_authenticated = False
        try:
            resp = self.__login(username, password)
            if isinstance(resp, (bytes, bytearray)):
                if resp.find(b"login_failed") > 0:
                    self.__set_error('Login Failed')
                else:
                    self.__is_authenticated = True
            elif isinstance(resp, dict):
                if 'error' in resp and strtobool(resp.get('error')):
                    self.__set_error(resp.get('msg'))
        except Exception as e:
            self.__set_error(str(e))

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
        return self._make_bika_request(url=url, params=params)

    def is_error(self):
        return self.__error

    def is_authenticated(self):
        return self.__is_authenticated

    def get_error_msg(self):
        return self.__msg

    @property
    def version(self):
        return "bikaclient version {v}".format(v=__version__)

    # QUERYING
    def get_clients(self, params=dict()):
        return self._read(portal_type='Client', query_params=params)

    def get_contacts(self, params=dict()):
        return self._read(portal_type='Contact', query_params=params)

    def get_samples(self, params=dict()):
        return self._read(portal_type='Sample', query_params=params)

    def get_analysis_requests(self, params=dict()):
        query_params = self._make_query_params(params)
        return self._read(portal_type='AnalysisRequest', query_params=query_params)

    def get_arimports(self, params=dict()):
        return self._read(portal_type='ARImport', query_params=params)

    def get_batches(self, params=dict()):
        query_params = self._make_query_params(params)
        return self._read(portal_type='Batch', query_params=query_params)

    def get_worksheets(self, params=dict()):
        query_params = self._make_query_params(params)
        return self._read(portal_type='Worksheet', query_params=query_params)

    def get_invoices(self, params=dict()):
        return self._read(portal_type='Invoice', query_params=params)

    def get_price_list(self, params=dict()):
        return self._read(portal_type='PriceList', query_params=params)

    def get_supply_orders(self, params=dict()):
        return self._read(portal_type='SupplyOrder', query_params=params)

    def get_lab_products(self, params=dict()):
        if 'path' not in params:
            params.update(dict(path=self._make_obj_path(obj_type='LabProduct')))
        return self._read(portal_type=None, query_params=params)

    def get_storage_locations(self, params=dict()):
        if 'path' not in params:
            params.update(dict(path=self._make_obj_path(obj_type='StorageLocation')))
        return self._read(portal_type=None, query_params=params)

    def get_suppliers(self, params=dict()):
        if 'path' not in params:
            params.update(dict(path=self._make_obj_path(obj_type='Supplier')))
        return self._read(portal_type=None, query_params=params)

    def get_manufacturers(self, params=dict()):
        if 'path' not in params:
            params.update(dict(path=self._make_obj_path(obj_type='Manufacturer')))
        return self._read(portal_type=None, query_params=params)

    def get_artemplates(self, params=dict()):
        return self._read(portal_type='ARTemplate', query_params=params)

    def get_analysis_profiles(self, params=dict()):
        return self._read(portal_type='AnalysisProfile', query_params=params)

    def get_analysis_services(self, params=dict()):
        return self._read(portal_type='AnalysisService', query_params=params)

    def get_sample_types(self, params=dict()):
        return self._read(portal_type='SampleType', query_params=params)

    def _read(self, portal_type=None, query_params=dict()):
        api_service = 'read'
        url = self._make_bika_url(service=api_service)

        params = dict()

        if portal_type:
            params.update(dict(portal_type=portal_type))

        if 'page_size' not in params:
            params.update(dict(page_size=0))

        if query_params:
            params.update(query_params)

        resp = self._make_bika_request(url=url, params=params)
        return json.loads(resp)

    # HIGH LEVEL QUERYING
    def query_analysis_request(self, params=dict(id=None,
                                                 client_sample_id=None,
                                                 review_state=None,
                                                 batch_id=None,
                                                 analysis_service_id=None,
                                                 run=None)):

        if 'review_state' in params and params['review_state']:
            if 'active' in [params['review_state']]:
                params.update(dict(Subjects='sample_due|sample_received|to_be_verified|verified|published'))
                del params['review_state']
            elif 'published' in [params['review_state']]:
                pass
            else:
                params.update(dict(Subject=params['review_state']))
                del params['review_state']

        if 'batch_id' in params and params['batch_id']:
            params.update(dict(title=params['batch_id']))
            del params['batch_id']

        if 'id' in params and params['id'] and isinstance(params['id'], list) and len(params['id']) > 0:
            params.update(dict(ids="|".join(params['id'])))
            del params['id']

        analysis_requests = self.get_analysis_requests(params)

        result = self._format_result(analysis_requests)

        if 'client_sample_id' in params and params['client_sample_id']:
            result = [ar for ar in result if
                      'ClientSampleID' in ar and params['client_sample_id'] == ar['ClientSampleID']]

        if 'analysis_service_id' in params and params['analysis_service_id']:
            result = [ar for ar in result if
                      'Analyses' in ar and params['analysis_service_id'] in [a['id'] for a in ar['Analyses']]]

        if 'run' in params and params['run']:
            result = [ar for ar in result if
                      'Sampler' in ar and params['run'] in ar['Sampler']]

        return result

    def query_batches(self, params=dict(id=None, client_id=None, review_state=None)):

        if 'review_state' in params and params['review_state']:
            if 'all' in [params['review_state']]:
                params.update(dict(Subjects='open|closed|cancelled'))
                del params['review_state']
            else:
                params.update(dict(Subject=params['review_state']))
                del params['review_state']

        if 'id' in params and params['id'] and isinstance(params['id'], list) and len(params['id']) > 0:
            params.update(dict(ids="|".join(params['id'])))
            del params['id']

        result = self.get_batches(params)

        if 'client_id' in params and params['client_id']:
            clients = self.get_clients(dict(id=params['client_id']))
            clients = self._format_result(clients)

            client = clients.pop() if len(clients) > 0 else list()

            return [b for b in self._format_result(result) if
                    'Client' in b and client['Name'] == b['Client']]

        return self._format_result(result)

    def query_worksheets(self, params=dict(id=None, review_state=None)):

        if 'review_state' in params and params['review_state']:
            if 'all' in [params['review_state']]:
                params.update(dict(Subjects='open|closed|cancelled'))
                del params['review_state']
            else:
                params.update(dict(Subject=params['review_state']))
                del params['review_state']

        if 'id' in params and params['id'] and isinstance(params['id'], list) and len(params['id']) > 0:
            params.update(dict(ids="|".join(params['id'])))
            del params['id']

        result = self.get_worksheets(params)
        return self._format_result(result)

    def query_deliveries(self, params=dict(id=None, review_state=None)):

        if 'review_state' in params and params['review_state']:
            if 'all' in [params['review_state']]:
                params.update(dict(Subjects='draft|ready|processing|dispatched|delivered|deleted'))
                del params['review_state']
            else:
                params.update(dict(Subject=params['review_state']))
                del params['review_state']

        if 'id' in params and params['id'] and isinstance(params['id'], list) and len(params['id']) > 0:
            params.update(dict(ids="|".join(params['id'])))
            del params['id']

        result = self.get_worksheets(params)
        return self._format_result(result)

    @staticmethod
    def _format_result(result=dict()):
        if 'objects' in result:
            return result['objects']
        return list()

    # CREATING
    def create_client(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='Client')
        query_params = self._make_query_params(params, remove_client_id=False)
        return self._create(obj_path=obj_path, obj_type='Client', query_params=query_params)

    def create_contact(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='Contact',  params=params)
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='Contact', query_params=query_params)

    def create_batch(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='Batch')
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='Batch', query_params=query_params)

    def create_analysis_request(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='AnalysisRequest')
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='AnalysisRequest', query_params=query_params)

    def create_worksheet(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='Worksheet')
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='Worksheet', query_params=query_params)

    def create_supply_order(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='SupplyOrder', params=params)
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='SupplyOrder', query_params=query_params)

    def create_lab_product(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='LabProduct', params=params)
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='LabProduct', query_params=query_params)

    def create_container_type(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='ContainerType', params=params)
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='ContainerType', query_params=query_params)

    def create_sample_type(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='SampleType', params=params)
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='SampleType', query_params=query_params)

    def create_instrument_type(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='InstrumentType', params=params)
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='InstrumentType', query_params=query_params)

    def create_analysis_category(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='AnalysisCategory', params=params)
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='AnalysisCategory', query_params=query_params)

    def create_analysis_service(self, params=dict()):
        obj_path = self._make_obj_path(obj_type='AnalysisService', params=params)
        query_params = self._make_query_params(params)
        return self._create(obj_path=obj_path, obj_type='AnalysisService', query_params=query_params)

    def _create(self, obj_path, obj_type, query_params=dict()):
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

    # REMOVING
    def remove(self, params=dict()):
        return self._remove(params=params)

    def _remove(self, params=dict()):
        api_service = 'remove'
        url = self._make_bika_url(service=api_service)

        resp = self._make_bika_request(url=url, params=params)
        return json.loads(resp)

    # USERS HANDLING
    def get_manager_users(self):
        params = dict(roles='LabManager')
        query_params = self._make_query_params(params)
        return self._get_users(query_params)

    def get_analyst_users(self):
        params = dict(roles='Analyst')
        query_params = self._make_query_params(params)
        return self._get_users(query_params)

    def get_clerk_users(self):
        params = dict(roles='LabClerk')
        query_params = self._make_query_params(params)
        return self._get_users(query_params)

    def get_client_users(self):
        params = dict(roles='Client')
        query_params = self._make_query_params(params)
        return self._get_users(query_params)

    def get_admin_users(self):
        params = dict(roles='Site Administrator')
        query_params = self._make_query_params(params)
        return self._get_users(query_params)

    def get_users(self, params):
        query_params = self._make_query_params(params)
        return self._get_users(query_params)

    def _get_users(self, query_params=dict()):
        api_service = 'getusers'
        url = self._make_bika_url(service=api_service)

        params = dict()

        if query_params:
            params.update(query_params)

        resp = self._make_bika_request(url=url, params=params)
        return json.loads(resp)

    # REVIEW STATE
    def close_batch(self, params=dict()):
        return self._do_action_for_many(action='close', query_params=params)

    def close_worksheet(self, params=dict()):
        return self._do_action_for_many(action='close', query_params=params)

    def open_batch(self, params=dict()):
        return self._do_action_for_many(action='open', query_params=params)

    def open_worksheet(self, params=dict()):
        return self._do_action_for_many(action='open', query_params=params)

    def cancel_batch(self, params=dict()):
        return self._do_action_for_many(action='cancel', query_params=params)

    def cancel_worksheet(self, params=dict()):
        return self._do_action_for_many(action='cancel', query_params=params)

    def cancel_analysis_request(self, params=dict()):
        return self._do_action_for_many(action='cancel', query_params=params)

    def reinstate_batch(self, params=dict()):
        return self._do_action_for_many(action='reinstate', query_params=params)

    def reinstate_worksheet(self, params=dict()):
        return self._do_action_for_many(action='reinstate', query_params=params)

    def reinstate_analysis_request(self, params=dict()):
        return self._do_action_for_many(action='reinstate', query_params=params)

    def receive_sample(self, params=dict()):
        return self._do_action_for_many(action='receive', query_params=params)

    def activate_supply_order(self, params=dict()):
        return self._do_action_for_many(action='activate', query_params=params)

    def deactivate_supply_order(self, params=dict()):
        return self._do_action_for_many(action='deactivate', query_params=params)

    def dispatch_supply_order(self, params=dict()):
        return self._do_action_for_many(action='dispatch', query_params=params)

    def activate_lab_product(self, params=dict()):
        return self._do_action_for_many(action='activate', query_params=params)

    def deactivate_lab_product(self, params=dict()):
        return self._do_action_for_many(action='deactivate', query_params=params)

    def activate_client(self, params=dict()):
        return self._do_action_for_many(action='activate', query_params=params)

    def deactivate_client(self, params=dict()):
        return self._do_action_for_many(action='deactivate', query_params=params)

    def submit(self, params=dict()):
        return self._do_action_for_many(action='submit', query_params=params)

    def verify(self, params=dict()):
        return self._do_action_for_many(action='verify', query_params=params)

    def publish(self, params=dict()):
        return self._do_action_for_many(action='publish', query_params=params)

    def republish(self, params=dict()):
        return self._do_action_for_many(action='republish', query_params=params)

    def update(self, params=dict()):
        return self._update(query_params=params)

    def update_many(self, params=dict()):
        return self._update_many(query_params=params)

    # HIGH LEVEL REVIEW STATE
    def submit_analyses(self, paths, result=1):

        def _make_params(_paths=list(), _result=1):
            input_values = dict()
            for path in _paths:
                input_values["{}".format(path)] = dict(Result=str(_result))
            return dict(input_values=json.dumps(input_values))

        params = _make_params(_paths=paths, _result=result)
        update = self.update_many(params=params)

        if 'message' in update:
            return update

        params = self._make_action_params(paths)
        return self.submit(params=params)

    def verify_analyses(self, paths):
        params = self._make_action_params(paths)
        return self.verify(params=params)

    def publish_analyses(self, paths):
        params = self._make_action_params(paths)
        return self.publish(params=params)

    def publish_analysis_requests(self, paths=list()):
        def _make_params(_paths=list()):
            input_values = dict()
            for path in _paths:
                input_values["{}".format(path)] = dict(subject='published', DatePublished=datetime.date.today().strftime("%y-%m-%d"))
            return dict(input_values=json.dumps(input_values))

        params = self._make_action_params(paths)
        publish = self.publish(params=params)

        if 'message' in publish:
            return publish

        params = _make_params(_paths=paths)
        update = self.update_many(params=params)

        return update

    def close_batches(self, paths):
        def _make_params(_paths=list()):
            input_values = dict()
            for path in _paths:
                input_values["{}".format(path)] = dict(subject='closed')
            return dict(input_values=json.dumps(input_values))

        params = self._make_action_params(paths)
        close = self.close_batch(params=params)

        if 'message' in close:
            return close

        params = _make_params(_paths=paths)
        update = self.update_many(params=params)

        return update

    def close_worksheets(self, paths):
        def _make_params(_paths=list()):
            input_values = dict()
            for path in _paths:
                input_values["{}".format(path)] = dict(subject='closed')
            return dict(input_values=json.dumps(input_values))

        params = _make_params(_paths=paths)
        update = self.update_many(params=params)

        params = self._make_action_params(paths)
        close = self.close_worksheet(params=params)

        return update

    def set_delivery_started(self, path):
        params = dict(obj_path=path, subject='processing')
        update = self.update(params=params)

        return update

    def set_delivery_completed(self, path):
        params = dict(obj_path=path, subject='dispatched')
        update = self.update(params=params)

        return update

    def update_delivery_details(self, path, details):
        params = dict(obj_path=path, location=json.dumps(details))
        update = self.update(params=params)

        return update

    # low level methods
    def _do_action_for(self, portal_type=None, action=None, query_params=dict()):
        api_service = 'doActionFor'
        url = self._make_bika_url(service=api_service)

        params = dict()

        if portal_type:
            params.update(dict(portal_type=portal_type))

        params.update(dict(action=action))

        if query_params:
            params.update(query_params)

        resp = self._make_bika_request(url=url, params=params)
        return json.loads(resp)

    def _do_action_for_many(self, action=None, query_params=dict()):
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

    @staticmethod
    def _make_query_params(params, remove_client_id=True):
        if remove_client_id and 'ClientID' in params:
            del params['ClientID']

        keywords_2_retrieve = ['Client', 'Service', 'SampleType', 'Contact', 'ContainerType','Category','Batch']
        for k in keywords_2_retrieve:
            if k in params:
                portal_type = 'AnalysisService' if k in ['Service'] else k
                portal_type = 'AnalysisCategory' if k in ['Category'] else k
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

        keywords_2_retrieve = ['roles']
        for k in keywords_2_retrieve:
            if k in params:
                values = params[k].split('|')
                params[k] = list()
                for v in values:
                    value = {"{}:list".format(k): "{}".format(v)}
                    params[k].append(value)

        keywords_2_retrieve = ['ids', 'Subjects', 'titles', 'paths']
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

    @staticmethod
    def _make_action_params(paths=list()):
        f = [path for path in paths]
        return dict(f=json.dumps(f))

    def _make_obj_path(self, obj_type=None, params=dict()):
        folder = None
        if obj_type in ["Client"]:
            folder = 'clients'
        if obj_type in ["Batch"]:
            folder = 'batches'
        if obj_type in ['Worksheet']:
            folder = 'worksheets'
        if obj_type in ['Contact']:
            folder = os.path.join('clients', params.get('ClientID', ''))
        if obj_type in ['SupplyOrder']:
            folder = os.path.join('clients', params.get('ClientID', ''))
        if obj_type in ['LabProduct']:
            folder = os.path.join('bika_setup', 'bika_labproducts')
        if obj_type in ['Supplier']:
            folder = os.path.join('bika_setup', 'bika_suppliers')
        if obj_type in ['Manufacturer']:
            folder = os.path.join('bika_setup', 'bika_manufacturers')
        if obj_type in ['StorageLocation']:
            folder = os.path.join('bika_setup', 'bika_storagelocations')
        if obj_type in ['ContainerType']:
            folder = os.path.join('bika_setup', 'bika_containertypes')
        if obj_type in ['InstrumentType']:
            folder = os.path.join('bika_setup', 'bika_instrumenttypes')
        if obj_type in ['SampleType']:
            folder = os.path.join('bika_setup', 'bika_sampletypes')
        if obj_type in ['AnalysisCategory']:
            folder = os.path.join('bika_setup', 'bika_analysiscategories')
        if obj_type in ['AnalysisService']:
            folder = os.path.join('bika_setup', 'bika_analysisservices')
        if folder:
            return '/{}'.format(os.path.join(os.path.split(self.__url)[1],
                                             folder))
        return None

    def _make_bika_url(self, service, is_login_service=False):
        prefix = '@@API' if not is_login_service else ''
        return os.path.join(self.__url, prefix, service)

    def _make_bika_request(self, url, params=dict()):
        self.__reset_error()
        try:
            data = self._make_bika_urlencode(params)
            req = Request(url, data)
            f = self.__opener.open(req)
            data = f.read()
            f.close()
        except Exception as e:
            self.__set_error(str(e))
            data = json.dumps(dict(error=self.is_error(), msg=str(e)))
        return data

    @staticmethod
    def _make_bika_urlencode(params):
        params_list = list()
        keys = list()
        for key, value in iteritems(params):
            if isinstance(value, list):
                for v in value:
                    params_list.append({key: v})
                keys.append(key)

        for k in keys:
            del params[k]

        url = urlencode(params)
        for p in params_list:
            for k, v in iteritems(p):
                url = "{}&{}".format(url, urlencode(v))

        return url.encode('utf-8')

    def __reset_error(self):
        self.__error = False
        self.__msg = ''

    def __set_error(self, msg = None):
        self.__error = True
        self.__msg = msg if msg else ''

