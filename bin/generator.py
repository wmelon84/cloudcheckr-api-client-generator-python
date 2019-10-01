import collections
import errno
import inflection
import json
import os
import requests
import sys

BASE_PATH = 'cloudcheckr_api_client_python/controllers/'
IMPORTS = '''
import collections
import inflection
import json
import requests


def from_str_to_obj(response=''):
    return json.loads(response, object_hook=lambda resp: collections.namedtuple('response', [inflection.underscore(key) for key in resp.keys()])(*resp.values()))


'''


def make_dirs(directory):
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


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
print('There are #' + str(len(controllers)) + ' controllers' + str([c.controller_name for c in controllers]))

# make_dirs(BASE_PATH)

for c in controllers:
    # try:
    #     os.mknod(BASE_PATH + c.controller_name + '.py')
    # except OSError as e:
    #     if e.errno != errno.EEXIST:
    #         raise
    source_code = ''
    if c.controller_name == 'account':
        source_code = ''
        print('Controller: ' + c.controller_name)
        for call in c.api_calls:
            if call.method_name == 'test_key':
                source_code = IMPORTS

                source_code += 'def ' + call.method_name + '('
                for param in call.param_names:
                    if '(required)' in param:
                        source_code += param.replace('(required)', '').replace('(admin level)', '')
                    else:
                        source_code += param.replace('(admin level)', '') + '=None'
                    source_code += ', '
                    source_code += "env='https://api.cloudcheckr.com/api/'"
                    source_code += '):\n'
                    source_code += '    response = requests.get(env + \'' + c.controller_name + '.json/' + call.method_name + '\', headers={\'access_key\': access_key})\n'
                    source_code += '    response.raise_for_status()\n'
                    source_code += '    return from_str_to_obj(response.text)\n'

        with open(c.controller_name + '.py', 'w') as file:  # Use file to refer to the file object
            file.write(source_code)


def from_str_to_obj(response=''):
    return json.loads(response, object_hook=lambda resp: collections.namedtuple('response',
                                                                                [inflection.underscore(key) for key in
                                                                                 resp.keys()])(*resp.values()))


def test_key(access_key, env='https://api.cloudcheckr.com/api/'):
    # env + controller_name + format_suffix + method_name

    response = requests.get('https://api.cloudcheckr.com/api/' + 'account' + '.json' + '/' + 'test_key',
                            headers={'access_key': access_key})
    response.raise_for_status()
    return from_str_to_obj(response.text)
