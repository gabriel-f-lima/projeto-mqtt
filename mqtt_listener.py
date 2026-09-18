import json
import os

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from database import inserir_leitura_sensor

load_dotenv()

BROKER_MQTT = os.getenv("MQTT_BROKER")
PORTA_MQTT = os.getenv("MQTT_PORT")
TOPICO_MQTT = os.getenv("MQTT_TOPIC")

if not BROKER_MQTT:
    raise RuntimeError("MQTT_BROKER não foi configurado no arquivo .env")

if not PORTA_MQTT:
    raise RuntimeError("MQTT_PORT não foi configurado no arquivo .env")

if not TOPICO_MQTT:
    raise RuntimeError("MQTT_TOPIC não foi configurado no arquivo .env")

try:
    PORTA_MQTT = int(PORTA_MQTT)
except ValueError as erro:
    raise RuntimeError("MQTT_PORT precisa ser um número inteiro") from erro
