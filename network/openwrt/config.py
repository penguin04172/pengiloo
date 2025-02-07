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
    'RELOAD_NETWORK': ['network', 'reload'],
    'UCI_COMMIT_WIFI': ['uci', 'commit', {'config': 'wireless'}],
}
