from flask import Flask, jsonify, request
from database import inserir_leitura_sensor, buscar_leituras_sensor

app = Flask(__name__)

@app.route('/api/sensor', methods=['POST'])
def salvar_dados_sensor():
    """Rota para receber leituras do sensor via requisição HTTP POST."""
    dados = request.get_json() or {}
    
    id_dispositivo = dados.get('device_id')
    distancia_cm = dados.get('distance_cm')
    esta_detectado = dados.get('is_detected', False)

    if not id_dispositivo or distancia_cm is None:
        return jsonify({"erro": "Dados incompletos fornecidos"}), 400

    try:
        inserir_leitura_sensor(id_dispositivo, distancia_cm, esta_detectado)
        return jsonify({"mensagem": "Leitura gravada com sucesso!"}), 201
    except Exception as erro:
        return jsonify({"erro": str(erro)}), 500


@app.route('/api/sensor', methods=['GET'])
def obter_dados_sensor():
    """Rota para consultar o histórico de leituras em formato JSON."""
    try:
        leituras = buscar_leituras_sensor()
        return jsonify(leituras), 200
    except Exception as erro:
        return jsonify({"erro": str(erro)}), 500


if __name__ == '__main__':
    app.run(debug=True)