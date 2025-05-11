class InputCollector:
    def __init__(self):
        self.inputs = []

    def _add_input(self, input_type: str, name: str, default, **kwargs):
        self.inputs.append({
            "type": input_type,
            "name": name,
            "default": default,
            "options": kwargs.get("options"),
            "min": kwargs.get("minval"),
            "max": kwargs.get("maxval"),
            "step": kwargs.get("step"),
        })
        return default  # Kullanıcının kodu hata vermeden devam etsin diye

    def int(self, default, title="", **kwargs):
        return self._add_input("int", title, default, **kwargs)

    def float(self, default, title="", **kwargs):
        return self._add_input("float", title, default, **kwargs)

    def bool(self, default, title="", **kwargs):
        return self._add_input("bool", title, default, **kwargs)

    def string(self, default, title="", options=None, **kwargs):
        return self._add_input("string", title, default, options=options)

    def color(self, default, title="", **kwargs):
        return self._add_input("color", title, default, **kwargs)
