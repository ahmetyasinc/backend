class InputShim:
    def __init__(self, input_values: dict):
        self.input_values = input_values or {}

    def _log(self, requested_type, name, title, default, resolved_value):
        print(f"[InputShim] {requested_type} input resolved:")
        print(f"  ↳ name: {name}, title: {title}")
        print(f"  ↳ default: {default}")
        print(f"  ↳ resolved value: {resolved_value}\n")

    def _get(self, requested_type, name=None, title=None, default=None):
        resolved_value = None

        if name and name in self.input_values:
            resolved_value = self.input_values[name]
        elif title and title in self.input_values:
            resolved_value = self.input_values[title]
        else:
            resolved_value = default

        self._log(requested_type, name, title, default, resolved_value)
        return resolved_value

    def int(self, default=0, name=None, title=None, **kwargs):
        return int(self._get("int", name, title, default))

    def float(self, default=0.0, name=None, title=None, **kwargs):
        return float(self._get("float", name, title, default))

    def bool(self, default=False, name=None, title=None, **kwargs):
        return bool(self._get("bool", name, title, default))

    def string(self, default="", name=None, title=None, **kwargs):
        return str(self._get("string", name, title, default))

    def color(self, default="", name=None, title=None, **kwargs):
        return str(self._get("color", name, title, default))
