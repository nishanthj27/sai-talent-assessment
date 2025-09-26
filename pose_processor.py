import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
import time

class PoseProcessor:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Exercise counters
        self.counters = {
            'jumping_jacks': {'count': 0, 'direction': 0},
            'push_ups': {'count': 0, 'direction': 0},
            'sit_ups': {'count': 0, 'direction': 0},
            'plank': {'start_time': None, 'elapsed': 0, 'total': 0},
            'vertical_jump': {'baseline': None, 'max_height': 0, 'jumps': 0}
        }
        
    def process_frame(self, frame, exercise):
        """Process frame based on exercise type"""
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        # Draw pose
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                self.mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2)
            )
            
            # Process based on exercise
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape
            
            if exercise == 'jumping_jacks':
                return self.process_jumping_jacks(frame, landmarks, w, h)
            elif exercise == 'push_ups':
                return self.process_push_ups(frame, landmarks, w, h)
            elif exercise == 'sit_ups':
                return self.process_sit_ups(frame, landmarks, w, h)
            elif exercise == 'plank':
                return self.process_plank(frame, landmarks, w, h)
            elif exercise == 'vertical_jump':
                return self.process_vertical_jump(frame, landmarks, w, h)
        
        return frame, {}
    
    def process_jumping_jacks(self, frame, landmarks, w, h):
        """Process jumping jacks"""
        counter = self.counters['jumping_jacks']
        
        # Get key points
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        
        # Check if arms are raised
        arms_up = (left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y)
        
        # Check if legs are spread (using hip distance)
        hip_distance = abs(right_hip.x - left_hip.x) * w
        legs_spread = hip_distance > 100  # pixels
        
        # Count logic
        if arms_up and legs_spread:
            if counter['direction'] == 0:
                counter['count'] += 0.5
                counter['direction'] = 1
        else:
            if counter['direction'] == 1:
                counter['count'] += 0.5
                counter['direction'] = 0
        
        metrics = {
            'count': int(counter['count']),
            'form_score': 95 if arms_up and legs_spread else 70,
            'status': 'Up' if arms_up else 'Down'
        }
        
        return frame, metrics
    
    def process_push_ups(self, frame, landmarks, w, h):
        """Process push-ups"""
        counter = self.counters['push_ups']
        
        # Calculate arm angle
        shoulder = [landmarks[11].x * w, landmarks[11].y * h]
        elbow = [landmarks[13].x * w, landmarks[13].y * h]
        wrist = [landmarks[15].x * w, landmarks[15].y * h]
        
        arm_angle = self.calculate_angle(shoulder, elbow, wrist)
        
        # Calculate body alignment
        hip = [landmarks[23].x * w, landmarks[23].y * h]
        knee = [landmarks[25].x * w, landmarks[25].y * h]
        
        body_angle = self.calculate_angle(shoulder, hip, knee)
        
        # Count logic
        if arm_angle < 90:
            if counter['direction'] == 0:
                counter['count'] += 0.5
                counter['direction'] = 1
        elif arm_angle > 160:
            if counter['direction'] == 1:
                counter['count'] += 0.5
                counter['direction'] = 0
        
        metrics = {
            'count': int(counter['count']),
            'arm_angle': int(arm_angle),
            'body_angle': int(body_angle),
            'form_score': 100 if 160 < body_angle < 190 else 70
        }
        
        return frame, metrics
    
    def process_sit_ups(self, frame, landmarks, w, h):
        """Process sit-ups"""
        counter = self.counters['sit_ups']
        
        # Calculate torso angle
        shoulder = [landmarks[11].x * w, landmarks[11].y * h]
        hip = [landmarks[23].x * w, landmarks[23].y * h]
        knee = [landmarks[25].x * w, landmarks[25].y * h]
        
        angle = self.calculate_angle(shoulder, hip, knee)
        
        # Count logic
        if angle < 90:
            if counter['direction'] == 0:
                counter['count'] += 0.5
                counter['direction'] = 1
        elif angle > 150:
            if counter['direction'] == 1:
                counter['count'] += 0.5
                counter['direction'] = 0
        
        metrics = {
            'count': int(counter['count']),
            'angle': int(angle),
            'status': 'Up' if angle < 90 else 'Down'
        }
        
        return frame, metrics
    
    def process_plank(self, frame, landmarks, w, h):
        """Process plank hold"""
        counter = self.counters['plank']
        
        # Calculate body alignment
        shoulder = [landmarks[11].x * w, landmarks[11].y * h]
        hip = [landmarks[23].x * w, landmarks[23].y * h]
        ankle = [landmarks[27].x * w, landmarks[27].y * h]
        
        body_angle = self.calculate_angle(shoulder, hip, ankle)
        
        # Check if in plank position
        in_plank = 160 < body_angle < 190
        
        if in_plank:
            if counter['start_time'] is None:
                counter['start_time'] = time.time()
            counter['elapsed'] = time.time() - counter['start_time']
        else:
            if counter['start_time'] is not None:
                counter['total'] += counter['elapsed']
                counter['start_time'] = None
                counter['elapsed'] = 0
        
        current_hold = counter['elapsed'] if in_plank else 0
        
        metrics = {
            'current_hold': int(current_hold),
            'total_time': int(counter['total']),
            'body_angle': int(body_angle),
            'in_position': in_plank
        }
        
        return frame, metrics
    
    def process_vertical_jump(self, frame, landmarks, w, h):
        """Process vertical jump"""
        counter = self.counters['vertical_jump']
        
        # Get hip position
        hip_y = (landmarks[23].y + landmarks[24].y) / 2 * h
        
        # Set baseline
        if counter['baseline'] is None:
            counter['baseline'] = hip_y
        
        # Calculate jump height
        jump_height = counter['baseline'] - hip_y
        
        # Detect jump
        if jump_height > 20:  # pixels
            if counter['max_height'] < jump_height:
                counter['max_height'] = jump_height
        elif jump_height < 10 and counter['max_height'] > 20:
            # Landed
            counter['jumps'] += 1
            counter['max_height'] = 0
        
        metrics = {
            'current_height': int(jump_height),
            'max_height': int(counter['max_height']),
            'jump_count': counter['jumps']
        }
        
        return frame, metrics
    
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
                  np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        
        return angle
    
    def reset_counter(self, exercise):
        """Reset exercise counter"""
        if exercise == 'jumping_jacks':
            self.counters['jumping_jacks'] = {'count': 0, 'direction': 0}
        elif exercise == 'push_ups':
            self.counters['push_ups'] = {'count': 0, 'direction': 0}
        elif exercise == 'sit_ups':
            self.counters['sit_ups'] = {'count': 0, 'direction': 0}
        elif exercise == 'plank':
            self.counters['plank'] = {'start_time': None, 'elapsed': 0, 'total': 0}
        elif exercise == 'vertical_jump':
            self.counters['vertical_jump'] = {'baseline': None, 'max_height': 0, 'jumps': 0}
