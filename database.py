import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

URL_BANCO_DADOS = os.getenv("DATABASE_URL")

db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, URL_BANCO_DADOS)

def inserir_leitura_sensor(id_dispositivo, distancia_cm, esta_detectado=False):
    conexao = db_pool.getconn()
    try:
        cursor = conexao.cursor()
        cursor.execute(
            """
            INSERT INTO sensor_readings (device_id, distance_cm, is_detected)
            VALUES (%s, %s, %s);
            """,
            (id_dispositivo, distancia_cm, esta_detectado)
        )
        conexao.commit()
        cursor.close()
    finally:
        # Return connection to the pool instead of closing it entirely
        db_pool.putconn(conexao)
