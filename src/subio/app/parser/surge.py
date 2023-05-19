from configparser import ConfigParser
from functools import reduce
from .common import common_transform_list

surge_anonymous_keys = ['type', 'server', 'port', 'username', 'password']

def parse(sub_text):
    config = ConfigParser()
    config.optionxform=str
    config.read_string(sub_text)
    all_proxies = []
    for k, v in config['Proxy'].items():
        proxy = {
            "name": k,
        }
        all_comps = v.split(',')
        # remove space
        all_comps = list(map(lambda x: x.strip(), all_comps))
        first_5_keys = surge_anonymous_keys
        for i in range(len(all_comps)):
            if '=' in all_comps[i]:
                # split by first '='
                k, v = all_comps[i].split('=', 1)
                if v == 'true':
                    v = True
                elif v == 'false':
                    v = False

                proxy[k] = v
            else:
                if i < len(first_5_keys):
                    proxy[first_5_keys[i]] = all_comps[i]
                else:
                    print(f"Warning: {k} has too many components")
        all_proxies.append(proxy)
        if proxy['type'] == 'https':
            proxy['type'] = 'http'
            proxy['tls'] = True
        if proxy['type'] == 'socks5-tls':
            proxy['type'] = 'socks5'
            proxy['tls'] = True
        if proxy['type'] in ['vmess', 'trojan']:
            if proxy['ws']:
                proxy['network'] = 'ws'
                def parse_headers(header_str):
                    # ws-headers=X-Header-1:value|X-Header-2:value
                    headers = {}
                    for header in header_str.split('|'):
                        k, v = header.split(':', 1)
                        headers[k] = v
                    return headers

                proxy['ws-headers'] = parse_headers(proxy['ws-headers']) if 'ws-headers' in proxy else {}
                proxy.pop('ws', None)
                print()

    return all_proxies

def transform_list(lst, unify_map):
    common_trans =  common_transform_list(lst, unify_map)
    def fix(node):
        if node['type'] == 'ss':
            if 'plugin_opts_mode' in node:
                node['plugin'] = 'obfs'
        return node
    return list(map(fix, common_trans))
