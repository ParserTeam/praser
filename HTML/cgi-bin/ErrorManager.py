import traceback


class ErrorManager:
    _instance = None
    _error = False
    _error_messages = []

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ErrorManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def has_error(self):
        return self._error

    def add_error_message(self, message=None):
        self._error = True
        self._error_messages += [message or "" + "\n" + traceback.format_exc()]

    def get_error_messages_as_string(self):
        self._error = False
        return ("\n" * 2 + ("#" * 20)).join(self._error_messages)

