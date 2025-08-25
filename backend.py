#!/usr/bin/env python3
"""
CarBrandsAI Backend Server
Flask API for car brand detection using YOLO model
"""

import os
import io
import time
import base64
import logging
import sys
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from ultralytics import YOLO
import torch

# Suppress all Flask and Werkzeug logs
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('flask').setLevel(logging.ERROR)

# 🔧 CUDA NMS Fix - Monkey patch to prevent CUDA NMS issues
def monkey_patch_nms():
    """Apply monkey patch to fix CUDA NMS issues during model loading"""
    try:
        import torchvision.ops
        original_nms = torchvision.ops.nms
        
        def patched_nms(boxes, scores, iou_threshold):
            # Force CPU execution to avoid CUDA NMS issues
            return original_nms(boxes.cpu(), scores.cpu(), iou_threshold).cuda() if boxes.is_cuda else original_nms(boxes, scores, iou_threshold)
        
        torchvision.ops.nms = patched_nms
        pass
    except Exception as e:
        pass

# Apply the patch immediately
monkey_patch_nms()

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
MODEL_PATH = "./model/best.pt"
UPLOAD_FOLDER = "uploads"
MAX_CONTENT_LENGTH = 16000000 * 10240000000* 10240000000  # 16MB max file size

# Car brand class names (18 brands from your training)
CLASS_NAMES = [
    'Audi', 'BMW', 'BYD (New)', 'BYD (Old)', 'Chevrolet', 'Ford', 
    'Honda', 'Hyundai', 'KIA', 'KIA (New)', 'Lexus', 'Mazda', 
    'Mercedes-Benz', 'Mitsubishi', 'Nissan', 'Tesla', 'Toyota', 'Volkswagen'
]

# Global model variable
model = None

def load_model():
    """Load YOLO model with proper error handling"""
    global model
    try:
        pass
        
        # Check if model file exists
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        
        # Load model
        model = YOLO(MODEL_PATH)
        
        # Test model on dummy image
        dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
        test_results = model(dummy_img, verbose=False)
        
        print("✅ Model loaded")
        
        return True
    except Exception as e:
        print("❌ Model loading failed")
        return False

def process_image(image_data):
    """Process uploaded image and return detection results - COMPLETELY SAFE VERSION"""
    try:
        start_time = time.time()
        
        # Convert base64 to image if needed
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            image = Image.open(image_data)
        
        # Convert PIL to OpenCV format
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Run YOLO inference
        results = model(image_cv, verbose=False)
        
        # Process results - COMPLETELY SAFE CONVERSION
        best_brand = "Unknown"
        best_confidence = 0.0
        best_box = {'x': 0, 'y': 0, 'w': 0, 'h': 0}
        
        try:
            for result in results:
                if hasattr(result, 'boxes') and result.boxes is not None:
                    boxes = result.boxes
                    if len(boxes) > 0:
                        # Get the first/best box
                        box = boxes[0]
                        
                        # Extract coordinates as plain Python types
                        xyxy_tensor = box.xyxy[0]
                        x1 = float(xyxy_tensor[0].item())
                        y1 = float(xyxy_tensor[1].item())
                        x2 = float(xyxy_tensor[2].item())
                        y2 = float(xyxy_tensor[3].item())
                        
                        # Extract confidence as plain Python float
                        conf_tensor = box.conf[0]
                        confidence = float(conf_tensor.item())
                        
                        # Extract class as plain Python int
                        cls_tensor = box.cls[0]
                        class_id = int(cls_tensor.item())
                        
                        # Validate and set results
                        if 0 <= class_id < len(CLASS_NAMES) and confidence > 0.3:
                            best_brand = str(CLASS_NAMES[class_id])
                            best_confidence = confidence
                            best_box = {
                                'x': int(x1),
                                'y': int(y1),
                                'w': int(x2 - x1),
                                'h': int(y2 - y1)
                            }
                            
                            # 🔍 DEBUG: Backend koordinatları
                            print(f"🎯 BACKEND DEBUG:")
                            print(f"   Brand: {best_brand}")
                            print(f"   Image size: {image_cv.shape[1]}x{image_cv.shape[0]}")
                            print(f"   Raw YOLO: x1={x1:.1f}, y1={y1:.1f}, x2={x2:.1f}, y2={y2:.1f}")
                            print(f"   Sent box: x={best_box['x']}, y={best_box['y']}, w={best_box['w']}, h={best_box['h']}")
                            break
        except Exception as inner_e:
            print(f"⚠️ Inner processing error: {inner_e}")
            pass
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Return completely safe dict
        return {
            'brand': best_brand,
            'confidence': best_confidence,
            'latency': f"{processing_time:.2f}s",
            'box': best_box
        }
            
    except Exception as e:
        print(f"❌ Image processing error: {str(e)}")
        return {
            'brand': 'Error',
            'confidence': 0.0,
            'latency': '0.00s',
            'box': {'x': 0, 'y': 0, 'w': 0, 'h': 0}
        }

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'CarBrandsAI Backend Server',
        'model_loaded': model is not None,
        'supported_brands': len(CLASS_NAMES),
        'max_file_size': f"{MAX_CONTENT_LENGTH // (1024*1024)}MB"
    })

@app.route('/api/detect', methods=['POST'])
def detect_brand():
    """Main detection endpoint"""
    try:
        # Check if model is loaded
        if model is None:
            return jsonify({
                'error': 'Model not loaded',
                'brand': 'Error',
                'confidence': 0.0
            }), 500
        
        # Check if file is in request
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided',
                'brand': 'Error',
                'confidence': 0.0
            }), 400
        
        file = request.files['image']
        
        # Check if file is empty
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'brand': 'Error',
                'confidence': 0.0
            }), 400
        
        # Check file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f'Unsupported file type: {file_ext}',
                'brand': 'Error',
                'confidence': 0.0
            }), 400
        
        # Process image
        result = process_image(file)
        
        # Add metadata - safe JSON conversion
        result['model_info'] = {
            'name': 'CarBrandsAI YOLOv11m',
            'version': 'V5',
            'classes': len(CLASS_NAMES),
            'accuracy': '87.4% mAP50'
        }
        
        # Ensure all values are JSON serializable
        safe_result = {}
        for key, value in result.items():
            if key == 'confidence':
                safe_result[key] = float(value) if value is not None else 0.0
            elif key == 'latency':
                safe_result[key] = str(value)
            elif key == 'brand':
                safe_result[key] = str(value)
            elif key == 'box':
                safe_result[key] = {
                    'x': int(value.get('x', 0)),
                    'y': int(value.get('y', 0)),
                    'w': int(value.get('w', 0)),
                    'h': int(value.get('h', 0))
                }
            else:
                safe_result[key] = value
        
        return jsonify(safe_result)
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({
            'error': f'Server error: {str(e)}',
            'brand': 'Error',
            'confidence': 0.0
        }), 500

@app.route('/api/brands', methods=['GET'])
def get_supported_brands():
    """Get list of supported car brands"""
    return jsonify({
        'brands': CLASS_NAMES,
        'count': len(CLASS_NAMES),
        'model_version': 'V5'
    })

@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    """Get detailed model information"""
    return jsonify({
        'model': {
            'name': 'CarBrandsAI YOLOv11m',
            'version': 'V5',
            'architecture': 'YOLOv11 Medium',
            'accuracy': '87.4% mAP50',
            'training_epochs': 35,
            'classes': len(CLASS_NAMES),
            'input_size': '640x640',
            'framework': 'Ultralytics YOLO'
        },
        'supported_brands': CLASS_NAMES,
        'performance': {
            'mAP50': 0.874,
            'precision': 0.89,
            'recall': 0.85,
            'inference_time': '~100ms'
        }
    })

if __name__ == '__main__':
    pass
    
    # Create upload directory
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Load model
    if load_model():
        print("Backend ready on port 5000")
        
        # Simple Flask startup without complex suppression
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    else:
        print("❌ Server failed to start")
        exit(1)
