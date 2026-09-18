// Função para formatar a data (Ex: 18/09/2026 14:30:00)
function formatarData(dataString) {
    const data = new Date(dataString);
    return data.toLocaleString('pt-BR');
}

// Função principal para buscar dados da API
async function atualizarDashboard() {
    try {
        const resposta = await fetch('/api/sensor');
        if (!resposta.ok) throw new Error('Erro ao buscar dados');
        
        const leituras = await resposta.json();
        
        if (leituras.length > 0) {
            // 1. Atualizar o Card de Status Atual (pegando o primeiro item da lista)
            const maisRecente = leituras[0];
            
            document.getElementById('distancia-atual').innerText = `${maisRecente.distance_cm} cm`;
            
            const badgeEstado = document.getElementById('estado-atual');
            if (maisRecente.is_detected) {
                badgeEstado.innerText = 'Detectado (Cancela Aberta)';
                badgeEstado.className = 'badge detectado';
            } else {
                badgeEstado.innerText = 'Livre (Cancela Fechada)';
                badgeEstado.className = 'badge livre';
            }

            document.getElementById('hora-atualizacao').innerText = formatarData(maisRecente.measured_at);

            // 2. Atualizar a Tabela de Histórico
            const corpoTabela = document.getElementById('tabela-corpo');
            corpoTabela.innerHTML = ''; // Limpa a tabela atual

            leituras.forEach(leitura => {
                const tr = document.createElement('tr');
                
                const tdData = document.createElement('td');
                tdData.innerText = formatarData(leitura.measured_at);
                
                const tdDispositivo = document.createElement('td');
                tdDispositivo.innerText = leitura.device_id;
                
                const tdDistancia = document.createElement('td');
                tdDistancia.innerText = `${leitura.distance_cm} cm`;
                
                const tdStatus = document.createElement('td');
                tdStatus.innerText = leitura.is_detected ? 'Detectado' : 'Livre';
                tdStatus.style.color = leitura.is_detected ? '#e74c3c' : '#2ecc71';
                tdStatus.style.fontWeight = 'bold';

                tr.appendChild(tdData);
                tr.appendChild(tdDispositivo);
                tr.appendChild(tdDistancia);
                tr.appendChild(tdStatus);
                
                corpoTabela.appendChild(tr);
            });
        }
    } catch (erro) {
        console.error('Erro ao atualizar dashboard:', erro);
    }
}

// Atualiza imediatamente ao carregar a página
atualizarDashboard();

// Configura para atualizar automaticamente a cada 3 segundos (3000 ms)
setInterval(atualizarDashboard, 3000);
