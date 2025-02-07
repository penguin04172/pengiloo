DEFAULT_SESSION_ID = '0' * 32
TIMEOUT = 10

UBUS_METHODS = {
    'LOGIN': ['session', 'login'],
    'WIFI_ASSOCLIST': lambda device: ['iwinfo', 'assoclist', {'device': device}],
    'WIFI_INFO': lambda device: ['iwinfo', 'info', {'device': device}],
    'WIFI_CLIENTS': lambda device: [f'hostapd.{device}', 'get_clients'],
    'WIFI_CHANNEL': lambda channel: [
        'uci',
        'set',
        {'config': 'wireless', 'section': '@wifi-device[1]', 'values': {'channel': channel}},
    ],
    'WIFI_DISABLE': lambda index, disable: [
        'uci',
        'set',
        {
            'config': 'wireless',
            'type': f'@wifi-iface[{index + 1}]',
            'values': {'disabled': f'{disable}'},
        },
    ],
    'WIFI_SSID': lambda index, ssid: [
        'uci',
        'set',
        {'config': 'wireless', 'section': f'@wifi-iface[{index + 1}]', 'values': {'ssid': ssid}},
    ],
    'WIFI_WPAPSK': lambda index, wpakey: [
        'uci',
        'set',
        {'config': 'wireless', 'section': f'@wifi-iface[{index + 1}]', 'values': {'key': wpakey}},
    ],
    'WIFI_WPASAE': lambda index, sae: [
        'uci',
        'set',
        {'config': 'wireless', 'section': f'@wifi-iface[{index + 1}]', 'values': {'sae': sae}},
    ],
    'RELOAD_NETWORK': ['network', 'reload'],
    'UCI_COMMIT_WIFI': ['uci', 'commit', {'config': 'wireless'}],
}
