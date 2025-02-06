class UbusError(Exception):
    """通用 UBUS 錯誤"""

    def __init__(self, message='UBUS 錯誤', error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(f'{message} (錯誤代碼: {error_code})' if error_code else message)


class UbusLoginError(UbusError):
    """登入失敗錯誤"""

    def __init__(self, message='UBUS 登入失敗'):
        super().__init__(message)


class UbusRequestError(UbusError):
    """API 請求錯誤"""

    def __init__(self, message='UBUS API 請求錯誤', error_code=None):
        super().__init__(message, error_code)


class UbusTimeoutError(UbusError):
    """請求超時錯誤"""

    def __init__(self, message='UBUS API 請求超時'):
        super().__init__(message)


class UbusUnauthorizedError(UbusError):
    """未授權錯誤 (Session 過期或無效)"""

    def __init__(self, message='未授權的 UBUS 請求，請重新登入'):
        super().__init__(message)
