
import pytest  
from app import app

@pytest.fixture
def cliente_teste():
    """Cria um cliente de teste do Flask."""
    app.config['TESTING'] = True
    with app.test_client() as cliente:
        yield cliente

def test_rota_get_sensor(cliente_teste, mocker):
    """Testa se a rota GET retorna as leituras corretamente."""
    # Simulamos o banco de dados retornando uma lista fictícia
    dados_simulados = [{"device_id": "ESP32_TESTE", "distance_cm": 15.5, "is_detected": True}]
    mocker.patch('app.buscar_leituras_sensor', return_value=dados_simulados)

    resposta = cliente_teste.get('/api/sensor')
    
    assert resposta.status_code == 200
    assert resposta.json == dados_simulados

def test_rota_post_sensor_sucesso(cliente_teste, mocker):
    """Testa o envio de dados válidos via POST."""
    # Simulamos a função de inserir para não gravar no banco real
    mocker.patch('app.inserir_leitura_sensor', return_value=None)

    dados_envio = {
        "device_id": "ESP32_01",
        "distance_cm": 12.0,
        "is_detected": True
    }
    resposta = cliente_teste.post('/api/sensor', json=dados_envio)
    
    assert resposta.status_code == 201
    assert resposta.json["mensagem"] == "Leitura gravada com sucesso!"

def test_rota_post_sensor_dados_incompletos(cliente_teste):
    """Testa o envio de dados incompletos (faltando distance_cm) via POST."""
    dados_envio = {"device_id": "ESP32_01"} # Faltando a distância
    
    resposta = cliente_teste.post('/api/sensor', json=dados_envio)
    
    assert resposta.status_code == 400
    assert "erro" in resposta.json