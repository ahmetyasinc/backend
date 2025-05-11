from app.routes.profile.indicator.indicator_library.input_collector import InputCollector

def extract_user_inputs(user_code: str):
    collector = InputCollector()

    # Sadece input'lara izin verilecek çalışma ortamı
    allowed_globals = {
        "__builtins__": {},
        "input": collector
    }

    try:
        # Yalnızca input ile başlayan satırları çalıştır
        lines = user_code.splitlines()
        input_lines = [line for line in lines if "input." in line]
        input_code = "\n".join(input_lines)

        exec(input_code, allowed_globals)
        return {"status": "ok", "inputs": collector.inputs}
    except Exception as e:
        return {"status": "error", "message": str(e)}

