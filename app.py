from flask import Flask, render_template, Response, jsonify, request
import cv2
import json
import time
from datetime import datetime
from pose_processor import PoseProcessor
import os

app = Flask(__name__)

# Global variables
pose_processor = PoseProcessor()
current_exercise = None
session_data = {
    'start_time': datetime.now().isoformat(),
    'exercises': {},
    'athlete_info': {}
}

def generate_frames():
    """Generate video frames for streaming"""
    camera = cv2.VideoCapture(0)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Process frame
            frame = cv2.flip(frame, 1)
            
            if current_exercise:
                frame, metrics = pose_processor.process_frame(frame, current_exercise)
                
                # Update session data
                session_data['exercises'][current_exercise] = {
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    camera.release()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/set_exercise', methods=['POST'])
def set_exercise():
    """Set current exercise"""
    global current_exercise
    data = request.json
    current_exercise = data.get('exercise')
    pose_processor.reset_counter(current_exercise)
    return jsonify({'status': 'success', 'exercise': current_exercise})

@app.route('/api/get_metrics')
def get_metrics():
    """Get current exercise metrics"""
    if current_exercise and current_exercise in session_data['exercises']:
        return jsonify({
            'exercise': current_exercise,
            'metrics': session_data['exercises'][current_exercise]['metrics'],
            'timestamp': datetime.now().isoformat()
        })
    return jsonify({'exercise': None, 'metrics': {}})

@app.route('/api/save_session', methods=['POST'])
def save_session():
    """Save session data"""
    session_data['end_time'] = datetime.now().isoformat()
    session_data['athlete_info'] = request.json.get('athlete_info', {})
    
    # Save to file
    filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(f"sessions/{filename}", 'w') as f:
        json.dump(session_data, f, indent=4)
    
    return jsonify({'status': 'success', 'filename': filename})

@app.route('/api/reset')
def reset_exercise():
    """Reset current exercise counter"""
    if current_exercise:
        pose_processor.reset_counter(current_exercise)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Create sessions directory
    os.makedirs('sessions', exist_ok=True)
    
    # Run app
    app.run(debug=True, host='0.0.0.0', port=3000)
