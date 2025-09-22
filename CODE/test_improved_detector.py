"""
Script test để kiểm tra cải tiến detector biển số
"""

import cv2
import numpy as np
from license_plate_detector import LicensePlateDetector
import os

def test_detector():
    """Test detector với ảnh mẫu"""
    try:
        detector = LicensePlateDetector()
        
        # Test với ảnh có sẵn
        test_image_path = "test_image.jpg"
        if os.path.exists(test_image_path):
            print(f"Testing with image: {test_image_path}")
            image = cv2.imread(test_image_path)
            
            if image is not None:
                print("Image loaded successfully")
                print(f"Image shape: {image.shape}")
                
                # Nhận diện biển số
                results = detector.detect_license_plate(image)
                
                if results:
                    print(f"\nFound {len(results)} license plate(s):")
                    for i, result in enumerate(results):
                        print(f"  {i+1}. Text: '{result['text']}'")
                        print(f"     Confidence: {result['confidence']:.3f}")
                        print(f"     BBox: {result['bbox']}")
                else:
                    print("No license plates detected")
            else:
                print("Failed to load image")
        else:
            print(f"Test image not found: {test_image_path}")
            
            # Test với camera
            print("\nTesting with camera...")
            print("Press 'q' to quit")
            detector.detect_from_video()
            
    except Exception as e:
        print(f"Error in test: {e}")

if __name__ == "__main__":
    test_detector()

