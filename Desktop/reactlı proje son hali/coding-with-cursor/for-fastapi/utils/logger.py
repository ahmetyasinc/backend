import logging

# Logging yapılandırması
logging.basicConfig(
    filename="app.log",  # Log dosyası adı
    level=logging.INFO,  # Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log formatı
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Logger nesnesi oluştur
logger = logging.getLogger(__name__)
