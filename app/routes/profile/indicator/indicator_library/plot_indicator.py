import numpy as np
import pandas as pd
# Kullanıcının çizim için çağıracağı fonksiyon
def plot(indicator_results, indicator_name: str, plot_type: str, on_graph: bool, indicator_data: list[tuple], **kwargs):
    """
    Kullanıcının çizdirmek istediği indikatör verilerini kaydeden fonksiyon.
    
    - `indicator_name`: İndikatörün adı
    - `plot_type`: "line", "histogram", "fill"
    - `on_graph`: Ana fiyat grafiğinin üzerine mi çizilecek? (True/False)
    - `indicator_data`: [(timestamp, value), (timestamp, value), ...]
    
    **Opsiyonel Ayarlar (kwargs)**:
    - **Çizgi Grafiği (`line`)**: `line_width`, `color`
    - **Histogram (`histogram`)**: `bar_color`, `bar_width`
    - **Alan Doldurma (`fill`)**: `fill_color`, `opacity`
    """

    if not isinstance(indicator_data, list) or not all(isinstance(i, tuple) and len(i) == 2 for i in indicator_data):
        raise ValueError("Indicator data must be a list of tuples (date, value).")

    # NaN ve sonsuz değerleri temizle
    cleaned_data = [
        (date, value) for date, value in indicator_data
        if not (pd.isna(value) or np.isinf(value))  # NaN veya inf olanları sil
    ]

    # Varsayılan ayarlar (Kullanıcı belirtmezse bunlar kullanılacak)
    plot_settings = {}

    if plot_type == "line":
        plot_settings["line_width"] = kwargs.get("line_width", 2)  # Varsayılan kalınlık: 2
        plot_settings["color"] = kwargs.get("color", "#FF0000")  # Varsayılan renk: Kırmızı

    elif plot_type == "histogram":
        plot_settings["bar_color"] = kwargs.get("bar_color", "#0000FF")  # Varsayılan çubuk rengi: Mavi
        plot_settings["bar_width"] = kwargs.get("bar_width", 1.5)  # Varsayılan çubuk genişliği: 1.5

    elif plot_type == "fill":
        plot_settings["fill_color"] = kwargs.get("fill_color", "#00FF00")  # Varsayılan doldurma rengi: Yeşil
        plot_settings["opacity"] = kwargs.get("opacity", 0.5)  # Varsayılan opaklık: %50

    # Yeni ayarları ekleyerek JSON'a dönüştürüyoruz
    indicator_results.append({
        "name": indicator_name,
        "type": plot_type,
        "on_graph": on_graph,
        "settings": plot_settings,
        "data": cleaned_data,
    })