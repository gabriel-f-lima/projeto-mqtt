import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

URL_BANCO_DADOS = os.getenv("DATABASE_URL")

def obter_conexao_bd():
    """Cria e retorna a conexão ativa com o banco de dados Neon."""
    return psycopg2.connect(URL_BANCO_DADOS)

def inserir_leitura_sensor(id_dispositivo, distancia_cm, esta_detectado=False):
    """Insere o registro de uma leitura no banco de dados."""
    conexao = obter_conexao_bd()
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
    conexao.close()

def buscar_leituras_sensor(limite=50):
    """Busca as leituras mais recentes do banco formatadas como dicionário."""
    conexao = obter_conexao_bd()
    cursor = conexao.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(
        "SELECT * FROM sensor_readings ORDER BY measured_at DESC LIMIT %s;", 
        (limite,)
    )
    leituras = cursor.fetchall()
    
    cursor.close()
    conexao.close()
    return leituras