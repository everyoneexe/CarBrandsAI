#!/usr/bin/env python3
"""
Car Brand Logo Detection Training Script
Gerçek dataset (12k+ images) için optimize edilmiş YOLOv11 training
"""

import torch
import os
from pathlib import Path
from ultralytics import YOLO
import time

def main():
    print("🚗 Car Brand Logo Detection Training")
    print("=" * 50)
    
    # GPU kontrolü
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Count: {torch.cuda.device_count()}")
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    else:
        print("⚠️  CPU mode will be used")
    
    # Dataset konfigürasyonu
    dataset_path = "/home/fukushima/Desktop/car_logo_dataset"
    data_config = f"{dataset_path}/data.yaml"
    
    print(f"\n📂 Dataset Path: {dataset_path}")
    print(f"📄 Data Config: {data_config}")
    
    # Dataset varlığını kontrol et
    if not os.path.exists(data_config):
        print(f"❌ Error: {data_config} not found!")
        return
    
    # Dataset boyutunu kontrol et
    train_dir = f"{dataset_path}/train/images"
    valid_dir = f"{dataset_path}/valid/images"
    test_dir = f"{dataset_path}/test/images"
    
    train_count = len([f for f in os.listdir(train_dir) if f.endswith('.jpg')])
    valid_count = len([f for f in os.listdir(valid_dir) if f.endswith('.jpg')])
    test_count = len([f for f in os.listdir(test_dir) if f.endswith('.jpg')])
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Train: {train_count:,} images")
    print(f"   Valid: {valid_count:,} images") 
    print(f"   Test:  {test_count:,} images")
    print(f"   Total: {train_count + valid_count + test_count:,} images")
    
    # Model yükleme
    print(f"\n🤖 Loading YOLOv11 model...")
    model = YOLO('yolo11n.pt')  # Nano model - hızlı ve etkili
    print("✅ Model loaded successfully!")
    
    # Training parametreleri (GPU modunda NMS problemini bypass etmeye çalışıyoruz)
    training_config = {
        'data': data_config,
        'epochs': 100,           # GPU için geri yükseltildi
        'batch': 8,              # GPU için geri yükseltildi
        'imgsz': 640,            # Standard YOLO resolution
        'device': 0,             # GPU zorla kullan
        'lr0': 0.001,            # Initial learning rate
        'optimizer': 'AdamW',    # Modern optimizer
        'patience': 30,          # Early stopping patience
        'save': True,            # Save checkpoints
        'save_period': 5,        # Save every 5 epochs
        'cache': True,           # Cache images for speed
        'workers': 4,            # Azaltıldı - CUDA uyumluluk için
        'project': 'car_brand_detection',
        'name': 'no_validation_v1',
        'exist_ok': True,        # Allow overwriting
        'amp': False,            # AMP kapatıldı - CUDA uyumluluk için
        'verbose': True,         # Detailed output
        'plots': True,           # Generate training plots
        'half': False,           # Half precision kapatıldı
        'val': False,            # VALİDATİON KAPALI - NMS CUDA problemini bypass et
    }
    
    print(f"\n⚙️  Training Configuration:")
    for key, value in training_config.items():
        print(f"   {key}: {value}")
    
    # Training başlat
    print(f"\n🚀 Starting training...")
    print(f"📅 Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        results = model.train(**training_config)
        
        training_time = time.time() - start_time
        print(f"\n✅ Training completed!")
        print(f"⏱️  Training time: {training_time/3600:.2f} hours")
        
        # En iyi model yolu
        best_model = f"{training_config['project']}/{training_config['name']}/weights/best.pt"
        print(f"🏆 Best model saved at: {best_model}")
        
        # Validation kapatıldı - CUDA NMS problemi nedeniyle
        print(f"\n⚠️  Validation skipped (CUDA NMS issue)")
        print(f"📊 Training completed without validation")
        
        print(f"\n🎉 Training process completed successfully!")
        print(f"📁 Check results in: {training_config['project']}/{training_config['name']}/")
        
        return best_model
        
    except Exception as e:
        print(f"\n❌ Training failed with error: {str(e)}")
        return None

if __name__ == "__main__":
    main()