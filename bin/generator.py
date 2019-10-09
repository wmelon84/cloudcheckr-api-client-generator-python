import builtins
import collections
import errno
import inflection
import json
import keyword
import os
import requests
import sys

BASE_PATH = '../_build/cloudcheckr_api_client/controllers/'
IMPORTS = '''import requests
from ._utils import get_non_blank_parameters, from_str_to_obj\n\n'''
UTILS_FILE = '_utils.py'
UTILS_SOURCE_CODE = '''import collections
import inflection
import json\n\n
def from_str_to_obj(response=''): 
    return json.loads(response, object_hook=lambda r: collections.namedtuple(
        'r', 
        [inflection.underscore(key) for key in r.keys()])(*r.values()))\n\n 
def get_non_blank_parameters(all_parameters=None):
    if all_parameters:
        return {k.rstrip('_'): v for k, v in all_parameters.items() if v and v.strip() and k != 'access_key'}
    return {}\n\n'''

all_api_endpoints = ''
if len(sys.argv) > 1:
    script, access_key = sys.argv
    if access_key:
        print('ONLINE mode, getting api description...')
        all_api_endpoints = requests.get('https://api.cloudcheckr.com/api/help.json/get_all_api_endpoints',
                                         headers={'access_key': access_key}).text
else:
    print('OFFLINE mode, loading local api description...')
    with open('../res/get_all_api_endpoints.json') as json_file:
        all_api_endpoints = json_file.read()
if not all_api_endpoints:
    sys.exit(1)
controllers = json.loads(all_api_endpoints,
                         object_hook=lambda d: collections.namedtuple('controller', d.keys())(*d.values()))


def clean_parameter_name(parameter_name):
    clean_name = parameter_name.replace('(required)', '').replace('(admin level)', '')
    return clean_name + '_' if keyword.iskeyword(clean_name) or clean_name in dir(builtins) else clean_name


def is_camel_case(parameter_name):
    return inflection.camelize(parameter_name, uppercase_first_letter=False) == parameter_name \
           or inflection.camelize(parameter_name) == parameter_name


def to_snake_case(parameter_name):
    return inflection.underscore(parameter_name)


#  create base directory
try:
    os.makedirs(BASE_PATH)
    os.mknod(BASE_PATH + '__init__.py')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

#  create _utils.py file
with open(BASE_PATH + UTILS_FILE, 'w') as file:
    file.write(UTILS_SOURCE_CODE)

for c in controllers:
    source_code = 'CONTROLLER_NAME = \'' + c.controller_name + '.json/\'\n\n\n'
    seen_api_calls = []
    for call in c.api_calls:
        if call.method_name not in seen_api_calls and not call.method_warning:
            seen_api_calls.append(call.method_name)
            source_code += 'def ' + inflection.underscore(call.method_name) + '(\n'
            required_list = list(
                map(lambda p: clean_parameter_name(p),
                    filter(lambda p: '(required)' in p, call.param_names)))
            optional_list = list(
                map(lambda p: clean_parameter_name(p) + '=None',
                    filter(lambda p: '(required)' not in p, call.param_names)))
            source_code += ',\n'.join(required_list) if required_list else ''
            source_code += ',\n' + ',\n'.join(optional_list) if optional_list else ''
            source_code += ",\nenv='https://api.cloudcheckr.com/api/'):\n"
            # HTTP method works also for GET methods
            source_code += '    response = requests.post(\n'
            source_code += 'env + CONTROLLER_NAME + \'' + call.method_name + '\',\n'
            source_code += 'params=get_non_blank_parameters(locals()),\n'
            source_code += 'headers={\'access_key\': access_key})\n'
            source_code += '    response.raise_for_status()\n'
            source_code += '    return from_str_to_obj(response.text)\n\n\n'

    with open(BASE_PATH + c.controller_name + '.py', 'w') as file:
        file.write(IMPORTS + source_code)
