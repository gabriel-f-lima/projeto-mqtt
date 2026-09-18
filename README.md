Codigos externos:


conexao.h
#ifndef CONEXAO_H
#define CONEXAO_H

#include <WiFi.h>
#include <PubSubClient.h>

// Credenciais de Rede Wi-Fi
inline const char* WIFI_SSID = "";
inline const char* WIFI_PASSWORD = "";

// Configurações do Broker MQTT
inline const char* MQTT_BROKER = "";
inline const int MQTT_PORT = ;
inline const char* MQTT_TOPIC = "";
inline const char* DEVICE_ID = "";

extern WiFiClient espClient;
extern PubSubClient mqttClient;

void gerenciarConexoes();

#endif



conexao.cpp
#include "conexao.h"

WiFiClient espClient;
PubSubClient mqttClient(espClient);

unsigned long ultimaTentativaWiFi = 0;
unsigned long ultimaTentativaMQTT = 0;

void gerenciarConexoes() {
    // Tenta conectar ao Wi-Fi a cada 10 segundos sem travar o processador
    if (WiFi.status() != WL_CONNECTED) {
        if (millis() - ultimaTentativaWiFi > 10000) {
            ultimaTentativaWiFi = millis();
            Serial.println("Tentando conectar ao Wi-Fi...");
            WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        }
        return; // Enquanto não conectar, retorna e deixa o sensor continuar rodando
    }

    // Se o Wi-Fi conectar, gerencia o MQTT
    if (!mqttClient.connected()) {
        if (millis() - ultimaTentativaMQTT > 5000) {
            ultimaTentativaMQTT = millis();
            Serial.print("Tentando conectar ao Broker MQTT...");
            if (mqttClient.connect(DEVICE_ID)) {
                Serial.println(" Conectado ao MQTT com sucesso!");
            } else {
                Serial.print(" Falha no MQTT. Código de erro: ");
                Serial.println(mqttClient.state());
            }
        }
    } else {
        mqttClient.loop();
    }
}



main.cpp
#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include "conexao.h"

// Mapeamento dos Pinos
const int TRIG_PIN  = 5;
const int ECHO_PIN  = 18;
const int SERVO_PIN = 13;
const int LED_PIN   = 4;

// Parâmetros de Controle
const float LIMITE_DETECCAO_CM = 20.0;
const int ANGULO_INICIAL = 0;
const int ANGULO_ACIONADO = 90;
const unsigned long TEMPO_ESPERA_MS = 5000;

Servo meuServo;

float medirDistancia() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duracao = pulseIn(ECHO_PIN, HIGH, 30000);
    if (duracao == 0) return -1.0;

    return duracao * 0.0343 / 2.0;
}

void acionarAtuadores(float distancia) {
    Serial.print("Aproximação detectada (");
    Serial.print(distancia);
    Serial.println(" cm)! Ligando LED e girando Servo para 90°...");

    // Envia a mensagem MQTT apenas se estiver conectado no momento
    if (mqttClient.connected()) {
        StaticJsonDocument<200> doc;
        doc["device_id"] = DEVICE_ID;
        doc["distance_cm"] = distancia;
        doc["is_detected"] = true;

        char bufferJSON[200];
        serializeJson(doc, bufferJSON);
        mqttClient.publish(MQTT_TOPIC, bufferJSON);
        Serial.println("Dados enviados ao broker MQTT com sucesso!");
    } else {
        Serial.println("Aviso: Dados não enviados ao MQTT (Sem conexão no momento).");
    }

    // Executa a movimentação física normalmente
    meuServo.write(ANGULO_ACIONADO);
    digitalWrite(LED_PIN, HIGH);

    delay(TEMPO_ESPERA_MS);

    meuServo.write(ANGULO_INICIAL);
    digitalWrite(LED_PIN, LOW);

    Serial.println("5 segundos finalizados. Servo retornado para 0° e LED desligado.");
}

void setup() {
    Serial.begin(115200);

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    ESP32PWM::allocateTimer(0);
    meuServo.setPeriodHertz(50);
    meuServo.attach(SERVO_PIN, 500, 2400);
    meuServo.write(ANGULO_INICIAL);

    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void loop() {
    // Processa tentativa de conexao sem bloquear a leitura dos sensores
    gerenciarConexoes();

    float distancia = medirDistancia();
    
    Serial.print("Distância lida: ");
    Serial.print(distancia);
    Serial.println(" cm");

    if (distancia >= 0 && distancia <= LIMITE_DETECCAO_CM) {
        acionarAtuadores(distancia);
    }

    delay(300);
}


libraries
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
lib_deps = 
    knolleary/PubSubClient@^2.8
    bblanchon/ArduinoJson@^6.21.3
    madhephaestus/ESP32Servo@^1.2.1
