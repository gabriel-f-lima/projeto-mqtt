
import pytest
import database

def test_buscar_leituras_sensor(mocker):
    """Testa se a busca ao banco chama os métodos corretos."""
    # Simulamos a conexão e o cursor do psycopg2
    mock_conexao = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    mock_conexao.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"distance_cm": 10}]
    
    # Forçamos a função obter_conexao_bd a retornar nossa conexão falsa
    mocker.patch('database.obter_conexao_bd', return_value=mock_conexao)

    resultado = database.buscar_leituras_sensor(limite=5)

    # Verifica se a query SQL foi executada corretamente
    mock_cursor.execute.assert_called_once()
    assert "SELECT * FROM sensor_readings" in mock_cursor.execute.call_args[0][0]
    assert resultado == [{"distance_cm": 10}]

def test_inserir_leitura_sensor(mocker):
    """Testa a inserção de dados."""
    mock_conexao = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conexao.cursor.return_value = mock_cursor
    
    mocker.patch('database.obter_conexao_bd', return_value=mock_conexao)

    database.inserir_leitura_sensor("ESP_TESTE", 15.5, True)

    # Verifica se o INSERT foi chamado com os valores corretos
    mock_cursor.execute.assert_called_once()
    assert "INSERT INTO sensor_readings" in mock_cursor.execute.call_args[0][0]
    assert mock_cursor.execute.call_args[0][1] == ("ESP_TESTE", 15.5, True)
    
    # Garante que o commit() foi chamado para salvar os dados
    mock_conexao.commit.assert_called_once()