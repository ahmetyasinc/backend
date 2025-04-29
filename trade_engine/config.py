from sqlalchemy import create_engine

DB_CONFIG = {
    'dbname': 'balina_db',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

# SQLAlchemy için bağlantı URI'si
DATABASE_URL = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

# SQLAlchemy Engine oluştur
engine = create_engine(DATABASE_URL)
