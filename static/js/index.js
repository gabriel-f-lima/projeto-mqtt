const readingsBody = document.querySelector('#readings-body');
const readingCount = document.querySelector('#reading-count');
const latestDistance = document.querySelector('#latest-distance');
const connectionStatus = document.querySelector('#connection-status');
const lastUpdated = document.querySelector('#last-updated');
const feedback = document.querySelector('#feedback');
const refreshButton = document.querySelector('#refresh-button');

function escapeHtml(value) {
	return String(value ?? '')
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;')
		.replaceAll("'", '&#039;');
}

function formatDistance(value) {
	const distance = Number(value);
	return Number.isFinite(distance) ? `${distance.toFixed(1)} cm` : '-';
}

function formatDate(value) {
	if (!value) return '-';

	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return escapeHtml(value);

	return date.toLocaleString('pt-BR', {
		dateStyle: 'short',
		timeStyle: 'medium'
	});
}

function setStatus(label, statusClass) {
	connectionStatus.textContent = label;
	connectionStatus.className = `status ${statusClass}`;
}

function renderReadings(readings) {
	readingCount.textContent = readings.length;

	if (readings.length === 0) {
		latestDistance.textContent = '-';
		readingsBody.innerHTML = '<tr><td colspan="4" class="empty-state">Nenhuma leitura encontrada.</td></tr>';
		return;
	}

	latestDistance.textContent = formatDistance(readings[0].distance_cm);
	readingsBody.innerHTML = readings.map((reading) => `
		<tr>
			<td><strong>${escapeHtml(reading.device_id || 'Desconhecido')}</strong></td>
			<td>${formatDistance(reading.distance_cm)}</td>
			<td><span class="badge ${reading.is_detected ? 'badge-alert' : 'badge-normal'}">
				${reading.is_detected ? 'Sim' : 'Nao'}
			</span></td>
			<td>${formatDate(reading.measured_at)}</td>
		</tr>
	`).join('');
}

async function loadReadings() {
	refreshButton.disabled = true;
	feedback.textContent = '';

	try {
		const response = await fetch('/api/sensor', { headers: { Accept: 'application/json' } });
		const data = await response.json();

		if (!response.ok || !Array.isArray(data)) {
			throw new Error(data.erro || 'A API retornou uma resposta invalida.');
		}

		renderReadings(data);
		setStatus('Conectado', 'status-online');
		lastUpdated.textContent = `Atualizado as ${new Date().toLocaleTimeString('pt-BR')}`;
	} catch (error) {
		setStatus('Erro', 'status-error');
		feedback.textContent = `Nao foi possivel carregar os dados: ${error.message}`;
		readingsBody.innerHTML = '<tr><td colspan="4" class="empty-state">Verifique se o Flask e o banco estao disponiveis.</td></tr>';
	} finally {
		refreshButton.disabled = false;
	}
}

refreshButton.addEventListener('click', loadReadings);
loadReadings();
setInterval(loadReadings, 10000);
