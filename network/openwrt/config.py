DEFAULT_SESSION_ID = '0' * 32
TIMEOUT = 10

UBUS_METHODS = {
    'LOGIN': ['session', 'login'],
    'SYSTEM_INFO': ['system', 'board'],
    'NETWORK_STATUS': lambda interface: [f'network.interface.{interface}', 'status'],
    'RESTART_NETWORK': ['network', 'restart'],
}
