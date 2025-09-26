from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json
from datetime import datetime, timedelta
import hashlib
import io
import base64
from scipy import signal
from scipy.stats import zscore
import random
import os

app = Flask(__name__)

# Mock Data Generation Functions
def generate_time_series_data(duration=10, fps=30):
    """Generate mock biomechanical time series data"""
    t = np.linspace(0, duration, duration * fps)
    
    # Displacement (jump motion)
    displacement = np.where(
        (t > 2) & (t < 8), 
        0.5 * np.sin(2 * np.pi * (t - 2) / 2) ** 2 + np.random.normal(0, 0.02, len(t)),
        np.random.normal(0, 0.01, len(t))
    )
    
    # Velocity and acceleration
    velocity = np.gradient(displacement, t)
    acceleration = np.gradient(velocity, t)
    
    # Joint angles (knee, hip, ankle)
    knee_angle = 160 + 20 * np.sin(2 * np.pi * t / 1.5) + np.random.normal(0, 2, len(t))
    hip_angle = 170 + 15 * np.cos(2 * np.pi * t / 1.8) + np.random.normal(0, 2, len(t))
    ankle_angle = 90 + 10 * np.sin(2 * np.pi * t / 1.2) + np.random.normal(0, 1.5, len(t))
    
    return {
        'time': t,
        'displacement': displacement,
        'velocity': velocity,
        'acceleration': acceleration,
        'knee_angle': knee_angle,
        'hip_angle': hip_angle,
        'ankle_angle': ankle_angle
    }

def generate_pose_coordinates():
    """Generate mock pose coordinate data"""
    keypoints = ['head', 'neck', 'left_shoulder', 'right_shoulder', 'left_elbow', 
                'right_elbow', 'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
                'left_knee', 'right_knee', 'left_ankle', 'right_ankle']
    
    poses = []
    for frame in range(300):  # 10 seconds at 30fps
        pose_data = {}
        for kp in keypoints:
            pose_data[kp] = {
                'x': random.uniform(100, 500),
                'y': random.uniform(100, 400),
                'confidence': random.uniform(0.7, 1.0)
            }
        poses.append(pose_data)
    
    return poses

def generate_athlete_data():
    """Generate mock athlete performance data"""
    return {
        'athlete_id': 'ATH001',
        'name': 'John Doe',
        'age': 25,
        'gender': 'male',
        'height': 175,  # cm
        'weight': 70,   # kg
        'test_history': [
            {
                'date': '2024-09-01',
                'jump_height': 45.2,
                'push_ups': 28,
                'speed': 8.5,
                'overall_score': 87
            },
            {
                'date': '2024-09-08',
                'jump_height': 47.1,
                'push_ups': 30,
                'speed': 8.7,
                'overall_score': 89
            },
            {
                'date': '2024-09-15',
                'jump_height': 48.5,
                'push_ups': 32,
                'speed': 8.9,
                'overall_score': 92
            }
        ]
    }

def calculate_jump_height(displacement_data):
    """Calculate vertical jump height from displacement data"""
    max_displacement = np.max(displacement_data)
    return max_displacement * 100  # Convert to cm

def count_repetitions(joint_angle_data, threshold=120):
    """Count repetitions using threshold crossing"""
    peaks, _ = signal.find_peaks(-joint_angle_data, height=-threshold)
    return len(peaks)

def detect_cheating(data):
    """Mock cheat detection algorithm"""
    # Simulate various cheat detection metrics
    repeated_frames = random.uniform(0, 0.1)
    unnatural_motion = random.uniform(0, 0.2)
    metadata_inconsistency = random.uniform(0, 0.05)
    
    overall_score = (repeated_frames + unnatural_motion + metadata_inconsistency) / 3
    
    return {
        'repeated_frames': repeated_frames,
        'unnatural_motion': unnatural_motion,
        'metadata_inconsistency': metadata_inconsistency,
        'overall_cheat_score': overall_score,
        'is_suspicious': overall_score > 0.1
    }

# Routes
@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template('dashboard.html')

@app.route('/api/performance_metrics')
def performance_metrics():
    """API endpoint for performance metrics data"""
    data = generate_time_series_data()
    
    # Create Plotly figures
    fig_displacement = go.Figure()
    fig_displacement.add_trace(go.Scatter(
        x=data['time'], 
        y=data['displacement'],
        mode='lines',
        name='Displacement'
    ))
    fig_displacement.update_layout(
        title='Displacement Over Time',
        xaxis_title='Time (s)',
        yaxis_title='Displacement (m)'
    )
    
    fig_angles = go.Figure()
    fig_angles.add_trace(go.Scatter(x=data['time'], y=data['knee_angle'], name='Knee'))
    fig_angles.add_trace(go.Scatter(x=data['time'], y=data['hip_angle'], name='Hip'))
    fig_angles.add_trace(go.Scatter(x=data['time'], y=data['ankle_angle'], name='Ankle'))
    fig_angles.update_layout(
        title='Joint Angles Over Time',
        xaxis_title='Time (s)',
        yaxis_title='Angle (degrees)'
    )
    
    return jsonify({
        'displacement_plot': json.dumps(fig_displacement, cls=plotly.utils.PlotlyJSONEncoder),
        'angles_plot': json.dumps(fig_angles, cls=plotly.utils.PlotlyJSONEncoder),
        'raw_data': {
            'time': data['time'].tolist(),
            'displacement': data['displacement'].tolist(),
            'velocity': data['velocity'].tolist(),
            'acceleration': data['acceleration'].tolist(),
            'knee_angle': data['knee_angle'].tolist(),
            'hip_angle': data['hip_angle'].tolist(),
            'ankle_angle': data['ankle_angle'].tolist()
        }
    })

@app.route('/api/computed_metrics')
def computed_metrics():
    """API endpoint for computed physical quantities"""
    data = generate_time_series_data()
    
    # Calculate metrics
    jump_height = calculate_jump_height(data['displacement'])
    repetitions = count_repetitions(data['knee_angle'])
    
    # Kinematic statistics
    stats = {
        'velocity': {
            'mean': np.mean(data['velocity']),
            'max': np.max(data['velocity']),
            'min': np.min(data['velocity']),
            'std': np.std(data['velocity'])
        },
        'acceleration': {
            'mean': np.mean(data['acceleration']),
            'max': np.max(data['acceleration']),
            'min': np.min(data['acceleration']),
            'std': np.std(data['acceleration'])
        },
        'joint_angles': {
            'knee': {
                'mean': np.mean(data['knee_angle']),
                'max': np.max(data['knee_angle']),
                'min': np.min(data['knee_angle']),
                'range': np.max(data['knee_angle']) - np.min(data['knee_angle'])
            },
            'hip': {
                'mean': np.mean(data['hip_angle']),
                'max': np.max(data['hip_angle']),
                'min': np.min(data['hip_angle']),
                'range': np.max(data['hip_angle']) - np.min(data['hip_angle'])
            },
            'ankle': {
                'mean': np.mean(data['ankle_angle']),
                'max': np.max(data['ankle_angle']),
                'min': np.min(data['ankle_angle']),
                'range': np.max(data['ankle_angle']) - np.min(data['ankle_angle'])
            }
        }
    }
    
    return jsonify({
        'jump_height': round(jump_height, 2),
        'repetitions': repetitions,
        'kinematic_stats': stats
    })

@app.route('/api/cheat_detection')
def cheat_detection():
    """API endpoint for cheat detection results"""
    cheat_data = detect_cheating(None)
    
    # Create confidence score visualization
    fig = go.Figure(data=[
        go.Bar(
            x=['Repeated Frames', 'Unnatural Motion', 'Metadata Issues'],
            y=[cheat_data['repeated_frames'], cheat_data['unnatural_motion'], 
               cheat_data['metadata_inconsistency']],
            marker_color=['red' if x > 0.1 else 'green' for x in [
                cheat_data['repeated_frames'], cheat_data['unnatural_motion'],
                cheat_data['metadata_inconsistency']
            ]]
        )
    ])
    fig.update_layout(
        title='Cheat Detection Scores',
        yaxis_title='Confidence Score',
        yaxis_range=[0, 1]
    )
    
    return jsonify({
        'cheat_scores': cheat_data,
        'cheat_plot': json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    })

@app.route('/api/benchmarking')
def benchmarking():
    """API endpoint for benchmarking and normative comparisons"""
    athlete_data = generate_athlete_data()
    
    # Mock normative data for 25-year-old males
    normative_data = {
        'jump_height': {'mean': 42.5, 'std': 5.2},
        'push_ups': {'mean': 25, 'std': 4},
        'speed': {'mean': 8.2, 'std': 0.8}
    }
    
    # Calculate percentiles and z-scores
    current_performance = athlete_data['test_history'][-1]
    
    benchmarks = {}
    for metric in ['jump_height', 'push_ups', 'speed']:
        value = current_performance[metric]
        norm_mean = normative_data[metric]['mean']
        norm_std = normative_data[metric]['std']
        
        z_score = (value - norm_mean) / norm_std
        percentile = 50 + 50 * np.tanh(z_score / 2)  # Approximate percentile
        
        benchmarks[metric] = {
            'value': value,
            'z_score': round(z_score, 2),
            'percentile': round(percentile, 1),
            'grade': 'A' if percentile > 85 else 'B' if percentile > 70 else 'C' if percentile > 50 else 'D'
        }
    
    # Progress over time
    dates = [test['date'] for test in athlete_data['test_history']]
    scores = [test['overall_score'] for test in athlete_data['test_history']]
    
    fig_progress = go.Figure()
    fig_progress.add_trace(go.Scatter(
        x=dates, 
        y=scores,
        mode='lines+markers',
        name='Progress'
    ))
    fig_progress.update_layout(
        title='Performance Progress Over Time',
        xaxis_title='Date',
        yaxis_title='Overall Score'
    )
    
    return jsonify({
        'benchmarks': benchmarks,
        'athlete_data': athlete_data,
        'progress_plot': json.dumps(fig_progress, cls=plotly.utils.PlotlyJSONEncoder)
    })

@app.route('/api/ai_validation')
def ai_validation():
    """API endpoint for AI model validation scores"""
    # Mock AI validation scores
    validation_scores = {
        'pose_accuracy': random.uniform(0.85, 0.98),
        'kinematic_consistency': random.uniform(0.80, 0.95),
        'heuristic_validation': random.uniform(0.75, 0.92),
        'cheat_detection_confidence': random.uniform(0.88, 0.99),
        'overall_validation': random.uniform(0.82, 0.96)
    }
    
    # Feature importance
    feature_importance = {
        'joint_angles': 0.35,
        'velocity_profile': 0.28,
        'pose_consistency': 0.22,
        'temporal_alignment': 0.15
    }
    
    # Create validation score chart
    fig_validation = go.Figure(data=[
        go.Bar(
            x=list(validation_scores.keys()),
            y=list(validation_scores.values()),
            marker_color='lightblue'
        )
    ])
    fig_validation.update_layout(
        title='AI Validation Scores',
        yaxis_title='Confidence Score',
        yaxis_range=[0, 1]
    )
    
    # Feature importance chart
    fig_importance = go.Figure(data=[
        go.Pie(
            labels=list(feature_importance.keys()),
            values=list(feature_importance.values())
        )
    ])
    fig_importance.update_layout(title='Feature Importance')
    
    return jsonify({
        'validation_scores': validation_scores,
        'feature_importance': feature_importance,
        'validation_plot': json.dumps(fig_validation, cls=plotly.utils.PlotlyJSONEncoder),
        'importance_plot': json.dumps(fig_importance, cls=plotly.utils.PlotlyJSONEncoder)
    })

@app.route('/api/gamification')
def gamification():
    """API endpoint for gamification and progress tracking"""
    athlete_data = generate_athlete_data()
    
    # Mock gamification data
    gamification_data = {
        'total_points': 2450,
        'level': 12,
        'badges': [
            {'name': 'Jump Master', 'description': 'Achieved 45cm+ vertical jump', 'earned': True},
            {'name': 'Consistency King', 'description': '10 consecutive tests', 'earned': True},
            {'name': 'Speed Demon', 'description': 'Sub 8.5s sprint time', 'earned': False},
            {'name': 'Strength Hero', 'description': '50+ push-ups', 'earned': False}
        ],
        'leaderboard_position': 15,
        'total_participants': 150,
        'streak_days': 12
    }
    
    # Points over time
    dates = pd.date_range(start='2024-08-01', periods=30, freq='D')
    points = np.cumsum(np.random.randint(10, 100, 30))
    
    fig_points = go.Figure()
    fig_points.add_trace(go.Scatter(
        x=dates,
        y=points,
        mode='lines+markers',
        name='Points'
    ))
    fig_points.update_layout(
        title='Points Accumulation Over Time',
        xaxis_title='Date',
        yaxis_title='Total Points'
    )
    
    return jsonify({
        'gamification_data': gamification_data,
        'points_plot': json.dumps(fig_points, cls=plotly.utils.PlotlyJSONEncoder)
    })

@app.route('/api/audit_logs')
def audit_logs():
    """API endpoint for data integrity and audit logs"""
    # Mock audit log data
    audit_logs = [
        {
            'timestamp': '2024-09-16 10:30:25',
            'action': 'Video Upload',
            'video_hash': hashlib.md5(b'mock_video_data').hexdigest(),
            'model_version': 'v2.1.4',
            'reviewer': 'AI System',
            'status': 'Validated'
        },
        {
            'timestamp': '2024-09-16 10:31:12',
            'action': 'Pose Estimation',
            'video_hash': hashlib.md5(b'mock_video_data').hexdigest(),
            'model_version': 'PoseNet v1.8.2',
            'reviewer': 'AI System',
            'status': 'Completed'
        },
        {
            'timestamp': '2024-09-16 10:32:45',
            'action': 'Cheat Detection',
            'video_hash': hashlib.md5(b'mock_video_data').hexdigest(),
            'model_version': 'CheatDetector v3.0.1',
            'reviewer': 'AI System',
            'status': 'No Issues Detected'
        },
        {
            'timestamp': '2024-09-16 10:33:20',
            'action': 'Human Review',
            'video_hash': hashlib.md5(b'mock_video_data').hexdigest(),
            'model_version': 'N/A',
            'reviewer': 'Dr. Smith',
            'status': 'Approved'
        }
    ]
    
    # Data integrity summary
    integrity_summary = {
        'total_tests': 156,
        'validated_tests': 152,
        'flagged_tests': 4,
        'integrity_score': 97.4,
        'last_audit': '2024-09-15 18:00:00'
    }
    
    return jsonify({
        'audit_logs': audit_logs,
        'integrity_summary': integrity_summary
    })

@app.route('/api/export_data')
def export_data():
    """Export metrics and graphs for offline use"""
    # Generate comprehensive data export
    data = generate_time_series_data()
    athlete_data = generate_athlete_data()
    
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'athlete_info': athlete_data,
        'time_series_data': {
            'time': data['time'].tolist(),
            'displacement': data['displacement'].tolist(),
            'velocity': data['velocity'].tolist(),
            'acceleration': data['acceleration'].tolist(),
            'knee_angle': data['knee_angle'].tolist(),
            'hip_angle': data['hip_angle'].tolist(),
            'ankle_angle': data['ankle_angle'].tolist()
        },
        'computed_metrics': {
            'jump_height': calculate_jump_height(data['displacement']),
            'repetitions': count_repetitions(data['knee_angle'])
        },
        'cheat_detection': detect_cheating(None)
    }
    
    return jsonify(export_data)

# HTML Template (embedded for single-file solution)
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biomechanics Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        .plot-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            margin: 20px 0;
        }
        .badge-earned {
            background-color: #28a745;
        }
        .badge-not-earned {
            background-color: #6c757d;
        }
        .navbar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        .loading {
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="#">Biomechanics Dashboard</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#performance">Performance</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#validation">Validation</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#benchmarks">Benchmarks</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#gamification">Gamification</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Performance Metrics Section -->
        <section id="performance">
            <h2>Performance Metrics</h2>
            <div class="row">
                <div class="col-md-6">
                    <div class="plot-container">
                        <div id="displacement-plot" class="loading">Loading displacement data...</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="plot-container">
                        <div id="angles-plot" class="loading">Loading joint angles...</div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-4">
                    <div class="metric-card">
                        <h4>Jump Height</h4>
                        <h2 id="jump-height">--</h2>
                        <small>centimeters</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-card">
                        <h4>Repetitions</h4>
                        <h2 id="repetitions">--</h2>
                        <small>count</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-card">
                        <h4>Max Velocity</h4>
                        <h2 id="max-velocity">--</h2>
                        <small>m/s</small>
                    </div>
                </div>
            </div>
        </section>

        <!-- Validation Section -->
        <section id="validation" class="mt-5">
            <h2>Validation & Cheat Detection</h2>
            <div class="row">
                <div class="col-md-6">
                    <div class="plot-container">
                        <div id="cheat-detection-plot" class="loading">Loading cheat detection...</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="plot-container">
                        <div id="ai-validation-plot" class="loading">Loading AI validation...</div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-12">
                    <div class="alert alert-info">
                        <h5>Cheat Detection Status</h5>
                        <p id="cheat-status">Analyzing...</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Benchmarking Section -->
        <section id="benchmarks" class="mt-5">
            <h2>Benchmarking & Normative Comparisons</h2>
            <div class="row">
                <div class="col-md-8">
                    <div class="plot-container">
                        <div id="progress-plot" class="loading">Loading progress data...</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>Performance Grades</h5>
                        </div>
                        <div class="card-body" id="grades-container">
                            Loading grades...
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Gamification Section -->
        <section id="gamification" class="mt-5">
            <h2>Gamification & Progress</h2>
            <div class="row">
                <div class="col-md-8">
                    <div class="plot-container">
                        <div id="points-plot" class="loading">Loading points data...</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>Achievements</h5>
                        </div>
                        <div class="card-body" id="badges-container">
                            Loading badges...
                        </div>
                    </div>
                    <div class="card mt-3">
                        <div class="card-header">
                            <h5>Statistics</h5>
                        </div>
                        <div class="card-body" id="stats-container">
                            Loading statistics...
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Data Integrity Section -->
        <section id="audit" class="mt-5">
            <h2>Data Integrity & Audit Logs</h2>
            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>Recent Audit Logs</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped" id="audit-table">
                                    <thead>
                                        <tr>
                                            <th>Timestamp</th>
                                            <th>Action</th>
                                            <th>Model Version</th>
                                            <th>Reviewer</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr><td colspan="5">Loading audit logs...</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Export Section -->
        <section class="mt-5">
            <div class="row">
                <div class="col-md-12 text-center">
                    <button class="btn btn-primary btn-lg" onclick="exportData()">
                        Export Data & Graphs
                    </button>
                </div>
            </div>
        </section>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js"></script>
    <script>
        // Load all dashboard data
        async function loadDashboard() {
            try {
                // Load performance metrics
                const performanceResponse = await fetch('/api/performance_metrics');
                const performanceData = await performanceResponse.json();
                
                // Plot displacement
                Plotly.newPlot('displacement-plot', 
                    JSON.parse(performanceData.displacement_plot).data,
                    JSON.parse(performanceData.displacement_plot).layout
                );
                
                // Plot joint angles
                Plotly.newPlot('angles-plot',
                    JSON.parse(performanceData.angles_plot).data,
                    JSON.parse(performanceData.angles_plot).layout
                );

                // Load computed metrics
                const computedResponse = await fetch('/api/computed_metrics');
                const computedData = await computedResponse.json();
                
                document.getElementById('jump-height').textContent = computedData.jump_height + ' cm';
                document.getElementById('repetitions').textContent = computedData.repetitions;
                document.getElementById('max-velocity').textContent = 
                    computedData.kinematic_stats.velocity.max.toFixed(2);

                // Load cheat detection
                const cheatResponse = await fetch('/api/cheat_detection');
                const cheatData = await cheatResponse.json();
                
                Plotly.newPlot('cheat-detection-plot',
                    JSON.parse(cheatData.cheat_plot).data,
                    JSON.parse(cheatData.cheat_plot).layout
                );
                
                const cheatStatus = cheatData.cheat_scores.is_suspicious ? 
                    'SUSPICIOUS ACTIVITY DETECTED' : 'No suspicious activity detected';
                document.getElementById('cheat-status').textContent = cheatStatus;
                document.getElementById('cheat-status').parentElement.className = 
                    cheatData.cheat_scores.is_suspicious ? 'alert alert-warning' : 'alert alert-success';

                // Load AI validation
                const aiResponse = await fetch('/api/ai_validation');
                const aiData = await aiResponse.json();
                
                Plotly.newPlot('ai-validation-plot',
                    JSON.parse(aiData.validation_plot).data,
                    JSON.parse(aiData.validation_plot).layout
                );

                // Load benchmarking
                const benchmarkResponse = await fetch('/api/benchmarking');
                const benchmarkData = await benchmarkResponse.json();
                
                Plotly.newPlot('progress-plot',
                    JSON.parse(benchmarkData.progress_plot).data,
                    JSON.parse(benchmarkData.progress_plot).layout
                );
                
                // Display grades
                const gradesHtml = Object.entries(benchmarkData.benchmarks).map(([metric, data]) => `
                    <div class="mb-2">
                        <strong>${metric.replace('_', ' ').toUpperCase()}</strong>
                        <div class="d-flex justify-content-between">
                            <span>Grade: ${data.grade}</span>
                            <span>${data.percentile}th percentile</span>
                        </div>
                        <div class="progress">
                            <div class="progress-bar" style="width: ${data.percentile}%"></div>
                        </div>
                    </div>
                `).join('');
                document.getElementById('grades-container').innerHTML = gradesHtml;

                // Load gamification
                const gamificationResponse = await fetch('/api/gamification');
                const gamificationData = await gamificationResponse.json();
                
                Plotly.newPlot('points-plot',
                    JSON.parse(gamificationData.points_plot).data,
                    JSON.parse(gamificationData.points_plot).layout
                );
                
                // Display badges
                const badgesHtml = gamificationData.gamification_data.badges.map(badge => `
                    <div class="badge ${badge.earned ? 'badge-earned' : 'badge-not-earned'} mb-2 p-2">
                        <div><strong>${badge.name}</strong></div>
                        <small>${badge.description}</small>
                    </div>
                `).join('');
                document.getElementById('badges-container').innerHTML = badgesHtml;
                
                // Display statistics
                const statsData = gamificationData.gamification_data;
                const statsHtml = `
                    <p><strong>Total Points:</strong> ${statsData.total_points}</p>
                    <p><strong>Level:</strong> ${statsData.level}</p>
                    <p><strong>Leaderboard:</strong> #${statsData.leaderboard_position} of ${statsData.total_participants}</p>
                    <p><strong>Streak:</strong> ${statsData.streak_days} days</p>
                `;
                document.getElementById('stats-container').innerHTML = statsHtml;

                // Load audit logs
                const auditResponse = await fetch('/api/audit_logs');
                const auditData = await auditResponse.json();
                
                const auditTableHtml = auditData.audit_logs.map(log => `
                    <tr>
                        <td>${log.timestamp}</td>
                        <td>${log.action}</td>
                        <td>${log.model_version}</td>
                        <td>${log.reviewer}</td>
                        <td><span class="badge bg-success">${log.status}</span></td>
                    </tr>
                `).join('');
                document.querySelector('#audit-table tbody').innerHTML = auditTableHtml;

            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }

        // Export data function
        async function exportData() {
            try {
                const response = await fetch('/api/export_data');
                const data = await response.json();
                
                const dataStr = JSON.stringify(data, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                
                const link = document.createElement('a');
                link.href = URL.createObjectURL(dataBlob);
                link.download = `biomechanics_export_${new Date().toISOString().slice(0,10)}.json`;
                link.click();
            } catch (error) {
                console.error('Error exporting data:', error);
                alert('Error exporting data. Please try again.');
            }
        }

        // Load dashboard on page load
        document.addEventListener('DOMContentLoaded', loadDashboard);

        // Auto-refresh every 30 seconds for real-time updates
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
"""

# Flask app configuration
app.template_folder = 'templates'

# Create templates directory and save HTML template
if not os.path.exists('templates'):
    os.makedirs('templates')

with open('templates/dashboard.html', 'w') as f:
    f.write(html_template)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
