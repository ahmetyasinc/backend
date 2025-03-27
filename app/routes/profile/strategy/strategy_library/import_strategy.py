def indicator(user_globals, **kwargs):
    """
    Değişkenleri user_globals içerisine ekler.
    """
    try:
        user_globals.update(kwargs)
        return user_globals

    except Exception as e:
        raise ImportError(f"İndikatör çalıştırılırken hata oluştu: {str(e)}")

