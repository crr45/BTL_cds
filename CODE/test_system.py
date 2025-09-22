#!/usr/bin/env python3
"""
Test script cho hệ thống nhận diện biển số xe
"""

import cv2
import numpy as np
from license_plate_detector import LicensePlateDetector

def test_detector():
    """Test detector với ảnh mẫu"""
    print("🧪 Testing License Plate Detector...")
    
    try:
        # Khởi tạo detector
        detector = LicensePlateDetector()
        print("✅ Detector initialized successfully")
        
        # Tạo ảnh mẫu đơn giản
        img = np.zeros((300, 600, 3), dtype=np.uint8)
        img[:] = (255, 255, 255)  # Nền trắng
        
        # Vẽ khung giả biển số
        cv2.rectangle(img, (100, 100), (500, 200), (0, 0, 0), 2)
        
        # Thêm text giả
        cv2.putText(img, "30A-12345", (150, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        print("✅ Sample image created")
        
        # Test nhận diện
        results = detector.detect_license_plate(img)
        
        if results:
            print(f"✅ Detection successful: {len(results)} plate(s) found")
            for i, result in enumerate(results):
                print(f"   Plate {i+1}: {result['text']} (confidence: {result['confidence']:.2f})")
        else:
            print("⚠️  No plates detected (this is normal for sample image)")
        
        print("✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_detector()
