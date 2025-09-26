// Global variables
let currentExercise = null;
let metricsUpdateInterval = null;
let recording = false;
let sessionData = {
    exercises: {}
};
let progressChart = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateDateTime();
    setInterval(updateDateTime, 1000);
    initProgressChart();
});

// Update date and time
function updateDateTime() {
    const now = new Date();
    const dateTimeStr = now.toLocaleDateString('en-IN', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    document.getElementById('dateTime').textContent = dateTimeStr;
}

// Exercise selection
function selectExercise(exercise) {
    // Update UI
    document.querySelectorAll('.exercise-card').forEach(card => {
        card.classList.remove('active');
    });
    event.target.closest('.exercise-card').classList.add('active');
    
    // Set current exercise
    currentExercise = exercise;
    
    // Update server
    fetch('/api/set_exercise', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ exercise: exercise })
    });
    
    // Update display
    updateExerciseDisplay(exercise);
    
    // Start metrics update
    if (metricsUpdateInterval) {
        clearInterval(metricsUpdateInterval);
    }
    metricsUpdateInterval = setInterval(updateMetrics, 500);
}

// Update exercise display
function updateExerciseDisplay(exercise) {
    const exercises = {
        'jumping_jacks': {
            name: 'Jumping Jacks',
            description: 'Full body cardio exercise',
            instructions: [
                'Stand with feet together, arms at sides',
                'Jump feet apart while raising arms overhead',
                'Jump back to starting position',
                'Maintain steady rhythm'
            ]
        },
        'push_ups': {
            name: 'Push Ups',
            description: 'Upper body strength exercise',
            instructions: [
                'Start in plank position',
                'Lower body until chest nearly touches floor',
                'Push back up to starting position',
                'Keep body straight throughout'
            ]
        },
        'sit_ups': {
            name: 'Sit Ups',
            description: 'Core strengthening exercise',
            instructions: [
                'Lie on back with knees bent',
                'Place hands behind head',
                'Lift torso towards knees',
                'Lower back down with control'
            ]
        },
        'plank': {
            name: 'Plank Hold',
            description: 'Core endurance exercise',
            instructions: [
                'Start in forearm plank position',
                'Keep body straight from head to heels',
                'Engage core muscles',
                'Hold position as long as possible'
            ]
        },
        'vertical_jump': {
            name: 'Vertical Jump',
            description: 'Explosive power test',
            instructions: [
                'Stand with feet shoulder-width apart',
                'Bend knees slightly',
                'Jump as high as possible',
                'Land softly and repeat'
            ]
        }
    };
    
    const exerciseInfo = exercises[exercise];
    
    // Update current exercise display
    document.getElementById('currentExercise').innerHTML = `
        <h2>${exerciseInfo.name}</h2>
        <p>${exerciseInfo.description}</p>
    `;
    
    // Update instructions
    const instructionsHtml = exerciseInfo.instructions.map((instruction, index) => `
        <div class="instruction-item">
            <i class="fas fa-check-circle"></i>
            <span>${index + 1}. ${instruction}</span>
        </div>
    `).join('');
    
    document.getElementById('instructionsDisplay').innerHTML = instructionsHtml;
}

// Update metrics
function updateMetrics() {
    if (!currentExercise) return;
    
    fetch('/api/get_metrics')
        .then(response => response.json())
        .then(data => {
            if (data.metrics) {
                // Update display based on exercise type
                const metricsContainer = document.getElementById('metricsDisplay');
                
                switch(currentExercise) {
                    case 'jumping_jacks':
                        metricsContainer.innerHTML = `
                            <div class="metric-card">
                                <i class="fas fa-hashtag"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Count</span>
                                    <span class="metric-value">${data.metrics.count || 0}</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-check-circle"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Form Score</span>
                                    <span class="metric-value">${data.metrics.form_score || 0}%</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-info-circle"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Status</span>
                                    <span class="metric-value">${data.metrics.status || 'Ready'}</span>
                                </div>
                            </div>
                        `;
                        break;
                        
                    case 'push_ups':
                        metricsContainer.innerHTML = `
                            <div class="metric-card">
                                <i class="fas fa-hashtag"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Count</span>
                                    <span class="metric-value">${data.metrics.count || 0}</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-angle-down"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Arm Angle</span>
                                    <span class="metric-value">${data.metrics.arm_angle || 0}°</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-ruler"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Body Angle</span>
                                    <span class="metric-value">${data.metrics.body_angle || 0}°</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-check-circle"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Form Score</span>
                                    <span class="metric-value">${data.metrics.form_score || 0}%</span>
                                </div>
                            </div>
                        `;
                        break;
                        
                    case 'sit_ups':
                        metricsContainer.innerHTML = `
                            <div class="metric-card">
                                <i class="fas fa-hashtag"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Count</span>
                                    <span class="metric-value">${data.metrics.count || 0}</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-angle-up"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Angle</span>
                                    <span class="metric-value">${data.metrics.angle || 0}°</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-info-circle"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Status</span>
                                    <span class="metric-value">${data.metrics.status || 'Ready'}</span>
                                </div>
                            </div>
                        `;
                        break;
                        
                    case 'plank':
                        metricsContainer.innerHTML = `
                            <div class="metric-card">
                                <i class="fas fa-clock"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Current Hold</span>
                                    <span class="metric-value">${data.metrics.current_hold || 0}s</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-hourglass-half"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Total Time</span>
                                    <span class="metric-value">${data.metrics.total_time || 0}s</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-ruler"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Body Angle</span>
                                    <span class="metric-value">${data.metrics.body_angle || 0}°</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-${data.metrics.in_position ? 'check' : 'times'}-circle"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Position</span>
                                    <span class="metric-value">${data.metrics.in_position ? 'Correct' : 'Adjust'}</span>
                                </div>
                            </div>
                        `;
                        break;
                        
                    case 'vertical_jump':
                        metricsContainer.innerHTML = `
                            <div class="metric-card">
                                <i class="fas fa-arrow-up"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Current Height</span>
                                    <span class="metric-value">${data.metrics.current_height || 0}px</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-trophy"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Max Height</span>
                                    <span class="metric-value">${data.metrics.max_height || 0}px</span>
                                </div>
                            </div>
                            <div class="metric-card">
                                <i class="fas fa-hashtag"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Jump Count</span>
                                    <span class="metric-value">${data.metrics.jump_count || 0}</span>
                                </div>
                            </div>
                        `;
                        break;
                }
                
                // Store session data
                if (!sessionData.exercises[currentExercise]) {
                    sessionData.exercises[currentExercise] = [];
                }
                sessionData.exercises[currentExercise].push({
                    timestamp: new Date(),
                    metrics: data.metrics
                });
                
                // Update chart
                updateProgressChart();
            }
        });
}

// Initialize progress chart
function initProgressChart() {
    const ctx = document.getElementById('progressChart').getContext('2d');
    progressChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Performance',
                data: [],
                borderColor: '#FF6B35',
                backgroundColor: 'rgba(255, 107, 53, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#b0b0b0'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#b0b0b0',
                        maxTicksLimit: 10
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

// Update progress chart
function updateProgressChart() {
    if (!currentExercise || !sessionData.exercises[currentExercise]) return;
    
    const exerciseData = sessionData.exercises[currentExercise];
    const lastData = exerciseData[exerciseData.length - 1];
    
    // Determine which metric to plot
    let metricValue = 0;
    switch(currentExercise) {
        case 'jumping_jacks':
        case 'push_ups':
        case 'sit_ups':
            metricValue = lastData.metrics.count || 0;
            break;
        case 'plank':
            metricValue = lastData.metrics.current_hold || 0;
            break;
        case 'vertical_jump':
            metricValue = lastData.metrics.max_height || 0;
            break;
    }
    
    // Update chart
    progressChart.data.labels.push(new Date().toLocaleTimeString());
    progressChart.data.datasets[0].data.push(metricValue);
    
    // Keep only last 20 points
    if (progressChart.data.labels.length > 20) {
        progressChart.data.labels.shift();
        progressChart.data.datasets[0].data.shift();
    }
    
    progressChart.update();
}

// Recording functions
function startRecording() {
    recording = !recording;
    const indicator = document.getElementById('recordingIndicator');
    const button = event.target;
    
    if (recording) {
        indicator.classList.add('active');
        button.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
        button.classList.remove('btn-success');
        button.classList.add('btn-danger');
    } else {
        indicator.classList.remove('active');
        button.innerHTML = '<i class="fas fa-video"></i> Start Recording';
        button.classList.remove('btn-danger');
        button.classList.add('btn-success');
    }
}

// Reset exercise
function resetExercise() {
    if (!currentExercise) return;
    
    fetch('/api/reset')
        .then(response => response.json())
        .then(data => {
            // Clear session data for current exercise
            sessionData.exercises[currentExercise] = [];
            
            // Reset chart
            progressChart.data.labels = [];
            progressChart.data.datasets[0].data = [];
            progressChart.update();
            
            console.log('Exercise reset');
        });
}

// Save session
function saveSession() {
    const athleteInfo = {
        name: document.getElementById('athleteName')?.value || 'Anonymous',
        age: document.getElementById('athleteAge')?.value || '',
        sport: document.getElementById('athleteSport')?.value || '',
        location: document.getElementById('athleteLocation')?.value || ''
    };
    
    fetch('/api/save_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            athlete_info: athleteInfo,
            session_data: sessionData
        })
    })
    .then(response => response.json())
    .then(data => {
        alert('Session saved successfully!');
        // Reset session data
        sessionData = { exercises: {} };
        progressChart.data.labels = [];
        progressChart.data.datasets[0].data = [];
        progressChart.update();
    });
}

// Modal functions
function showAthleteModal() {
    document.getElementById('athleteModal').classList.add('active');
}

function closeModal() {
    document.getElementById('athleteModal').classList.remove('active');
}

// Handle athlete form submission
document.getElementById('athleteForm').addEventListener('submit', function(e) {
    e.preventDefault();
    closeModal();
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    switch(e.key) {
        case '1':
            selectExercise('jumping_jacks');
            break;
        case '2':
            selectExercise('push_ups');
            break;
        case '3':
            selectExercise('sit_ups');
            break;
        case '4':
            selectExercise('plank');
            break;
        case '5':
            selectExercise('vertical_jump');
            break;
        case 'r':
        case 'R':
            document.querySelector('.btn-success').click();
            break;
        case 'c':
        case 'C':
            resetExercise();
            break;
        case 's':
        case 'S':
            saveSession();
            break;
    }
});
