import builtins
import collections
import errno
import inflection
import json
import keyword
import os
import requests
import sys

BASE_PATH = '../build/cloudcheckr_api_client/controllers/'

IMPORTS = '''import requests
from ._utils import get_non_blank_parameters, from_str_to_obj\n\n'''

UTILS_FILE = '_utils.py'

UTILS_SOURCE_CODE = '''import collections
import inflection
import json\n\n
def from_str_to_obj(response=''): 
    return json.loads(response, object_hook=lambda r: collections.namedtuple(
        'response', 
        [inflection.underscore(key) for key in r.keys()])(*r.values()))\n\n 
def get_non_blank_parameters(all_parameters, normalized_parameters=None):
    if all_parameters:
        return {denormalize(k, normalized_parameters): v for k, v in all_parameters.items()
                if v and v.strip() and k != 'access_key' and k != 'normalized_parameters' and k != 'env'}
    return {}\n\n
def denormalize(key, normalized_parameters=None):
    return normalized_parameters[key] if normalized_parameters and key in normalized_parameters.keys() \
        else key.rstrip('_')\n\n'''

PARAMETER_NAME_EXCEPTIONS = {'thirdpartyaccountids': 'third_party_account_ids'}

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
    cleaned_name = parameter_name.replace('(required)', '').replace('(admin level)', '')
    return cleaned_name + '_' if keyword.iskeyword(cleaned_name) or cleaned_name in dir(builtins) else cleaned_name


def is_not_normalized(parameter_name):
    return inflection.camelize(parameter_name) == parameter_name


def normalize(string):
    return inflection.underscore(string)


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

            # saved already processed methods to avoid duplicates
            seen_api_calls.append(call.method_name)

            required_parameters = []
            optional_parameters = []
            normalized_parameters = {}

            for name in call.param_names:

                if name in PARAMETER_NAME_EXCEPTIONS.keys():
                    clean_name = PARAMETER_NAME_EXCEPTIONS[name]
                    normalized_clean_name = PARAMETER_NAME_EXCEPTIONS[name]
                    normalized_parameters[normalized_clean_name] = name
                else:
                    clean_name = clean_parameter_name(name)
                    normalized_clean_name = clean_parameter_name(normalize(name))
                if '(required)' in name:
                    required_parameters.append(normalized_clean_name)
                else:
                    if normalized_clean_name not in required_parameters \
                            and normalized_clean_name not in optional_parameters:
                        optional_parameters.append(normalized_clean_name)

                if is_not_normalized(clean_name):
                    normalized_parameters[normalized_clean_name] = clean_name

            source_code += 'def ' + normalize(call.method_name) + '(\n'

            if required_parameters:
                source_code += ',\n'.join(required_parameters) + ',\n'
            if optional_parameters:
                source_code += ',\n'.join([p + '=None' for p in optional_parameters]) + ',\n'
            source_code += "env='https://api.cloudcheckr.com/api/'):\n"
            if normalized_parameters:
                source_code += '    normalized_parameters = ' + json.dumps(normalized_parameters) + '\n'

            source_code += '    response = requests.' + (
                'get' if + call.method_name.startswith('get') else 'post') + '(\n'
            source_code += 'env + CONTROLLER_NAME + \'' + call.method_name + '\',\n'
            source_code += 'params=get_non_blank_parameters(locals()' + \
                           (', normalized_parameters' if normalized_parameters else '') + '),\n'
            source_code += 'headers={\'access_key\': access_key})\n'
            source_code += '    response.raise_for_status()\n'
            source_code += '    return from_str_to_obj(response.text)\n\n\n'

    with open(BASE_PATH + c.controller_name + '.py', 'w') as file:
        file.write(IMPORTS + source_code)
