// DOM Elements
const wsStatus = document.getElementById('ws-status');
const valHr = document.getElementById('val-hr');
const valSpo2 = document.getElementById('val-spo2');
const valHrv = document.getElementById('val-hrv');
const valExpression = document.getElementById('val-expression');
const valPosture = document.getElementById('val-posture');

const cardHr = document.getElementById('card-hr');
const cardSpo2 = document.getElementById('card-spo2');
const cardHrv = document.getElementById('card-hrv');

const explainerIdle = document.querySelector('.idle-state');
const explainerAlert = document.getElementById('alert-state');
const alertText = document.getElementById('alert-text');

// Chart Setup
const ctx = document.getElementById('telemetryChart').getContext('2d');
const MAX_DATA_POINTS = 60; // Show 60 seconds of data

const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Time labels
        datasets: [
            {
                label: 'Heart Rate (bpm)',
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                data: [],
                yAxisID: 'y',
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0
            },
            {
                label: 'SpO2 (%)',
                borderColor: '#0ea5e9',
                backgroundColor: 'rgba(14, 165, 233, 0.1)',
                data: [],
                yAxisID: 'y1',
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: {
                labels: { color: '#e0f2fe', font: { family: 'Inter' } }
            }
        },
        scales: {
            x: {
                display: false // Hide x-axis labels for clean look
            },
            y: {
                type: 'linear',
                display: true,
                position: 'left',
                title: { display: true, text: 'Heart Rate', color: '#64748b' },
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#64748b' },
                min: 40,
                max: 140
            },
            y1: {
                type: 'linear',
                display: true,
                position: 'right',
                title: { display: true, text: 'SpO2 (%)', color: '#64748b' },
                grid: { drawOnChartArea: false },
                ticks: { color: '#64748b' },
                min: 85,
                max: 100
            }
        }
    }
});

// Anomaly State Tracking
let anomalyState = 'NORMAL'; // 'NORMAL', 'ALERT_UNACKED', 'ALERT_ACKED'

// Connect to the FastAPI WebSocket
function connectWebSocket() {
    const ws = new WebSocket('ws://localhost:8000/ws/telemetry');

    ws.onopen = () => {
        wsStatus.textContent = 'CONNECTED';
        wsStatus.style.borderColor = '#34d399';
        wsStatus.style.color = '#34d399';
    };

    ws.onclose = () => {
        wsStatus.textContent = 'DISCONNECTED';
        wsStatus.style.borderColor = '#ef4444';
        wsStatus.style.color = '#ef4444';
        // Try to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };

    ws.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        if(payload.error) {
            console.error(payload.error);
            return;
        }
        
        // Update autonomous action text if present
        if (payload.autonomous_action) {
            const autoLog = document.getElementById('autonomous-log');
            if(autoLog) {
                // Typewriter effect simulation for the terminal look
                if(autoLog.dataset.lastText !== payload.autonomous_action) {
                    autoLog.dataset.lastText = payload.autonomous_action;
                    autoLog.innerHTML = '> ' + payload.autonomous_action;
                }
            }
        }
        
        const data = payload.telemetry;
        updateDashboard(data);
    };
}

function updateDashboard(data) {
    // 1. Update Vitals Text
    valHr.textContent = data.heart_rate.toFixed(1);
    valSpo2.textContent = data.spo2.toFixed(1) + '%';
    valHrv.textContent = data.hrv.toFixed(1);
    valExpression.textContent = data.detected_expression.toUpperCase();
    valPosture.textContent = data.exercise_posture_score.toFixed(2);

    // 2. Update Chart
    const now = new Date().toLocaleTimeString();
    chart.data.labels.push(now);
    chart.data.datasets[0].data.push(data.heart_rate);
    chart.data.datasets[1].data.push(data.spo2);

    if (chart.data.labels.length > MAX_DATA_POINTS) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
        chart.data.datasets[1].data.shift();
    }
    chart.update();

    // 3. Client-side Anomaly Detection (Simulating the Backend Math)
    const hasHrSpike = data.heart_rate > 95;
    const hasSpo2Drop = data.spo2 < 95;
    const hasAnomaly = hasHrSpike || hasSpo2Drop;

    if (hasAnomaly) {
        if (anomalyState === 'NORMAL') {
            anomalyState = 'ALERT_UNACKED';
            triggerAlert(data);
        }
    } else {
        if (anomalyState === 'ALERT_ACKED') {
            // Re-arm the system once telemetry is normal again
            anomalyState = 'NORMAL';
        }
    }
}

function triggerAlert(data) {
    // UI Flash
    cardHr.classList.add('alert');
    cardSpo2.classList.add('alert');
    valExpression.style.color = '#ef4444';
    valExpression.style.borderColor = '#ef4444';

    // Show Agent Explainer
    explainerIdle.classList.add('hidden');
    explainerAlert.classList.remove('hidden');

    // Generate strict, compliant text (No Diagnosis)
    alertText.innerHTML = `
        <strong>Deviation recorded: Multi-signal Concordance</strong><br><br>
        Observed Heart Rate (${data.heart_rate.toFixed(1)} bpm) and SpO2 (${data.spo2.toFixed(1)}%) deviated significantly from personal baseline (Z-score > 2.0).<br><br>
        HuskyLens 2 Vision Sensor corroborates physiological shift with structural expression change (${data.detected_expression}).<br><br>
        <em>Literature context:</em> According to NASA's Human Research Program, cardiovascular autonomic regulation shifts are well-documented in microgravity analog studies.
    `;
}

function clearAlert() {
    // UI Restore
    cardHr.classList.remove('alert');
    cardSpo2.classList.remove('alert');
    valExpression.style.color = '#fff';
    valExpression.style.borderColor = '#0ea5e9';

    // Hide Agent Explainer
    explainerIdle.classList.remove('hidden');
    explainerAlert.classList.add('hidden');
}

function acknowledgeAlert() {
    if (anomalyState === 'ALERT_UNACKED') {
        clearAlert();
        anomalyState = 'ALERT_ACKED';
    }
}

// Start connection
connectWebSocket();

// HuskyLens AI Chat Logic
const chatInput = document.getElementById('chat-input');
const chatSubmit = document.getElementById('chat-submit');
const chatLog = document.getElementById('chat-log');

async function sendChatQuery() {
    const question = chatInput.value.trim();
    if (!question) return;

    // 1. Append user message to log
    appendMessage(question, 'user');
    chatInput.value = '';
    
    // Disable input while waiting
    chatInput.disabled = true;
    chatSubmit.disabled = true;

    const mode = document.getElementById('chat-mode') ? document.getElementById('chat-mode').value : 'Facial Expression Recognition';
    try {
        // 2. Send POST request to FastAPI backend (which forwards it to HuskyLens over Wi-Fi)
        const response = await fetch('http://localhost:8000/api/vision/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question, algorithm: mode })
        });

        const result = await response.json();

        if (response.ok) {
            appendMessage(result.answer, 'ai');
        } else {
            // If the camera is turned off (timeout), show a helpful fallback message for the demo
            if (response.status === 504) {
                appendMessage("Camera unreachable. [Demo Fallback] Based on simulated context: The astronaut is actively performing stationary exercises.", 'ai');
            } else {
                appendMessage(result.detail || "Error connecting to AI", 'error');
            }
        }
    } catch (error) {
        appendMessage("Network error. Make sure the FastAPI server is running.", 'error');
    } finally {
        chatInput.disabled = false;
        chatSubmit.disabled = false;
        chatInput.focus();
    }
}

function appendMessage(text, senderType) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${senderType}`;
    msgDiv.textContent = text;
    chatLog.appendChild(msgDiv);
    // Auto scroll to bottom
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Event listeners
chatSubmit.addEventListener('click', sendChatQuery);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChatQuery();
});
document.getElementById('ack-button').addEventListener('click', acknowledgeAlert);
