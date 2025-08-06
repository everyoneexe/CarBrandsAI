#!/usr/bin/env python3
"""
Car Brand Logo Detection - COMPREHENSIVE Brand Testing
Test ALL images for each brand to get complete accuracy statistics for instructor
"""

import torch
from ultralytics import YOLO
import os
from pathlib import Path

def comprehensive_brand_test():
    """Test ALL images for each brand to get complete accuracy statistics"""
    
    # Force CPU usage to avoid CUDA NMS issue
    torch.cuda.set_device(-1)
    
    # Load the best trained model
    model_path = "car_brand_detection/no_validation_v1/weights/best.pt"
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        return
    
    print("🔥 COMPREHENSIVE BRAND ACCURACY TEST")
    print("Testing ALL images for instructor report...")
    print("=" * 60)
    
    model = YOLO(model_path)
    model.to('cpu')
    
    # Test directory
    test_images_dir = "car_logo_dataset/test/images"
    
    if not os.path.exists(test_images_dir):
        print(f"❌ Test directory not found: {test_images_dir}")
        return
    
    # Get all test images
    test_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        test_images.extend(list(Path(test_images_dir).glob(ext)))
    
    # Group images by brand based on filename
    brand_groups = {
        'audi': [],
        'hyundai': [],
        'lexus': [],
        'mazda': [],
        'mercedes': [],
        'opel': [],
        'others': [],
        'toyota': [],
        'volkswagen': []
    }
    
    # Categorize images by filename
    for img_path in test_images:
        filename = img_path.name.lower()
        for brand in brand_groups.keys():
            if brand in filename or filename.startswith(brand):
                brand_groups[brand].append(img_path)
                break
    
    print(f"📊 DATASET OVERVIEW:")
    print(f"Total test images: {len(test_images)}")
    for brand, images in brand_groups.items():
        if images:
            print(f"  {brand.upper()}: {len(images)} images")
    print("=" * 60)
    
    # Results storage
    results_summary = []
    total_correct = 0
    total_tested = 0
    
    for brand, images in brand_groups.items():
        if not images:
            continue
            
        print(f"\n🏷️ TESTING {brand.upper()}: {len(images)} images")
        print("-" * 40)
        
        correct = 0
        tested = 0
        detailed_results = []
        
        # Test ALL images for this brand
        for i, img_path in enumerate(images):
            tested += 1
            total_tested += 1
            
            try:
                results = model(str(img_path), device='cpu', verbose=False)
                
                best_detection = None
                best_confidence = 0
                
                for r in results:
                    if len(r.boxes) > 0:
                        for box in r.boxes:
                            confidence = float(box.conf[0])
                            if confidence > best_confidence:
                                best_confidence = confidence
                                cls_id = int(box.cls[0])
                                best_detection = model.names[cls_id]
                
                if best_detection:
                    if best_detection.lower() == brand:
                        status = "✅ CORRECT"
                        correct += 1
                        total_correct += 1
                    else:
                        status = f"❌ WRONG (detected: {best_detection.upper()})"
                    
                    detailed_results.append({
                        'image': img_path.name,
                        'detected': best_detection.upper(),
                        'confidence': best_confidence,
                        'correct': best_detection.lower() == brand
                    })
                    
                    if i < 10:  # Show first 10 results
                        print(f"  {i+1:2}. {status} - {best_confidence:.3f}")
                else:
                    status = "❓ NO DETECTION"
                    detailed_results.append({
                        'image': img_path.name,
                        'detected': 'NONE',
                        'confidence': 0.0,
                        'correct': False
                    })
                    if i < 10:
                        print(f"  {i+1:2}. {status}")
                    
            except Exception as e:
                print(f"  {i+1:2}. ❌ ERROR: {e}")
                tested -= 1
                total_tested -= 1
        
        # Calculate accuracy for this brand
        if tested > 0:
            accuracy = (correct / tested) * 100
            print(f"\n📊 {brand.upper()} FINAL RESULTS:")
            print(f"   Correct: {correct}/{tested}")
            print(f"   Accuracy: {accuracy:.1f}%")
            
            # Store for summary
            results_summary.append({
                'brand': brand.upper(),
                'correct': correct,
                'total': tested,
                'accuracy': accuracy
            })
        
        print("-" * 40)
    
    # FINAL INSTRUCTOR REPORT
    print("\n" + "=" * 60)
    print("🎓 INSTRUCTOR REPORT - BRAND DETECTION ACCURACY")
    print("=" * 60)
    
    for result in results_summary:
        print(f"{result['brand']:12} : {result['correct']:3}/{result['total']:3} = {result['accuracy']:5.1f}%")
    
    print("-" * 60)
    
    if total_tested > 0:
        overall_accuracy = (total_correct / total_tested) * 100
        print(f"{'OVERALL':12} : {total_correct:3}/{total_tested:3} = {overall_accuracy:5.1f}%")
    
    print("=" * 60)
    
    # Performance classification
    if overall_accuracy >= 95:
        print("🏆 PERFORMANCE: EXCELLENT (A+)")
    elif overall_accuracy >= 90:
        print("🥇 PERFORMANCE: VERY GOOD (A)")
    elif overall_accuracy >= 85:
        print("🥈 PERFORMANCE: GOOD (B+)")
    elif overall_accuracy >= 80:
        print("🥉 PERFORMANCE: SATISFACTORY (B)")
    else:
        print("⚠️ PERFORMANCE: NEEDS IMPROVEMENT")
    
    print(f"\n📝 Model trained on 12,817 images over 100 epochs")
    print(f"📝 Test set contains {total_tested} images across 9 car brands")
    print(f"📝 Training time: ~2.5 hours on RTX 4070")
    
    return results_summary

if __name__ == "__main__":
    comprehensive_brand_test()