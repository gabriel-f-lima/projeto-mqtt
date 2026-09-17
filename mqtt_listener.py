import json
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from database import inserir_leitura_sensor

load_dotenv()

BROKER_MQTT = os.getenv("MQTT_BROKER")
PORTA_MQTT = int(os.getenv("MQTT_PORT"))
TOPICO_MQTT = os.getenv("MQTT_TOPIC")

def ao_conectar(cliente, userdata, flags, rc, properties=None):
    """Callback executada quando o cliente conecta ao Broker MQTT."""
    if rc == 0:
        print(f"Conectado com sucesso ao Broker MQTT! Inscrito no tópico: {TOPICO_MQTT}")
        cliente.subscribe(TOPICO_MQTT)
    else:
        print(f"Falha ao conectar no Broker MQTT. Código de retorno: {rc}")

def ao_receber_mensagem(cliente, userdata, msg):
    """Callback executada sempre que uma nova mensagem chega no tópico."""
    try:
        dados = json.loads(msg.payload.decode('utf-8'))
        
        id_dispositivo = dados.get("device_id", "ESP32_DESCONHECIDO")
        distancia_cm = dados.get("distance_cm")
        esta_detectado = dados.get("is_detected", False)

        if distancia_cm is not None:
            # Chama a função importada do database.py
            inserir_leitura_sensor(id_dispositivo, distancia_cm, esta_detectado)
            print(f"[MQTT] Gravado no banco: Sensor={id_dispositivo} | Distância={distancia_cm}cm")
        else:
            print("[MQTT Aviso] Mensagem recebida sem o campo 'distance_cm'.")

    except json.JSONDecodeError:
        print("[MQTT Erro] Mensagem recebida não está em formato JSON válido.")
    except Exception as erro:
        print(f"[MQTT Erro] Erro ao processar mensagem: {erro}")

def iniciar_escuta():
    """Inicializa o cliente MQTT e inicia o loop de escuta."""
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.on_connect = ao_conectar
    cliente.on_message = ao_receber_mensagem

    print(f"Iniciando conexão MQTT com {BROKER_MQTT}:{PORTA_MQTT}...")
    cliente.connect(BROKER_MQTT, PORTA_MQTT, 60)
    
    # Mantém o script rodando e escutando as mensagens
    cliente.loop_forever()

if __name__ == '__main__':
    iniciar_escuta()