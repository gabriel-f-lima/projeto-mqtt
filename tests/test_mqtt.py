
import pytest
import json
import mqtt_listener

class MockMensagemMQTT:
    """Classe auxiliar para simular uma mensagem vinda do Broker MQTT."""
    def __init__(self, payload_dict):
        # Converte o dicionário para string e depois para bytes (como o MQTT faz)
        self.payload = json.dumps(payload_dict).encode('utf-8')

def test_ao_receber_mensagem_valida(mocker):
    """Testa se uma mensagem JSON válida chama a inserção no banco."""
    # Evita que a mensagem seja gravada no banco de dados real
    mock_inserir = mocker.patch('mqtt_listener.inserir_leitura_sensor')
    
    msg_falsa = MockMensagemMQTT({
        "device_id": "ESP_01",
        "distance_cm": 18.5,
        "is_detected": True
    })

    mqtt_listener.ao_receber_mensagem(None, None, msg_falsa)

    # Verifica se a função de banco foi chamada com os dados do JSON
    mock_inserir.assert_called_once_with("ESP_01", 18.5, True)

def test_ao_receber_mensagem_invalida(capfd):
    """Testa o comportamento se receber um JSON quebrado ou malformado."""
    class MockMensagemQuebrada:
        payload = b"{isso_nao_e_um_json_valido}"

    msg_quebrada = MockMensagemQuebrada()

    # Chama a função e captura o que foi impresso no console (print)
    mqtt_listener.ao_receber_mensagem(None, None, msg_quebrada)
    
    saida_console, err = capfd.readouterr()
    assert "não está em formato JSON válido" in saida_console

def test_ao_receber_mensagem_sem_distancia(mocker, capfd):
    """Testa se o sistema ignora mensagens que não tenham o campo distance_cm."""
    mock_inserir = mocker.patch('mqtt_listener.inserir_leitura_sensor')
    
    msg_incompleta = MockMensagemMQTT({
        "device_id": "ESP_01"
        # Sem distance_cm
    })

    mqtt_listener.ao_receber_mensagem(None, None, msg_incompleta)

    # Verifica se o sistema impediu a inserção no banco
    mock_inserir.assert_not_called()
    
    saida_console, err = capfd.readouterr()
    assert "Mensagem recebida sem o campo" in saida_console