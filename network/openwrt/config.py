DEFAULT_SESSION_ID = '0' * 32
TIMEOUT = 10

UBUS_METHODS = {
    'LOGIN': ['session', 'login'],
    'WIFI_ASSOCLIST': lambda device: ['iwinfo', 'assoclist', {'device': device}],
    'WIFI_INFO': lambda device: ['iwinfo', 'info', {'device': device}],
    'WIFI_CLIENTS': lambda device: [f'hostapd.{device}', 'get_clients'],
    'WIFI_CHANNEL': lambda radio, channel: [
        'uci',
        'set',
        {'config': 'wireless', 'section': f'radio{radio}', 'values': {'channel': channel}},
    ],
    'RELOAD_NETWORK': ['network', 'reload'],
    'RECONF_WIFI': ['network.wireless', 'reconf'],
    'UCI_SET': lambda config, section, values: [
        'uci',
        'set',
        {'config': config, 'section': section, 'values': values},
    ],
    'UCI_COMMIT': lambda config: ['uci', 'commit', {'config': config}],
}
