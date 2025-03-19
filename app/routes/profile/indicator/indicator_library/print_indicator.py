import numpy as np
import pandas as pd

def custom_print(print_outputs, *args, **kwargs):
    """
    Kullanıcının print() fonksiyonunu yakalar ve print_outputs listesine ekler.
    - `print_outputs`: Print edilen mesajların saklanacağı liste
    """
    output_list = []
    
    for arg in args:
        if isinstance(arg, pd.DataFrame):
            # DataFrame'leri tam formatında göster
            output_list.append("\n" + arg.to_string())  
        elif isinstance(arg, pd.Series):
            # Series objesini düzgün biçimde göstermek için
            output_list.append("\n" + arg.to_string(index=True))  
        else:
            output_list.append(str(arg))  

    output = " ".join(output_list)  
    print_outputs.append(output)
