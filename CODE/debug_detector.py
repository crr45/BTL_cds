"""
Script debug để test detector trực tiếp
"""

import cv2
import numpy as np
from license_plate_detector import LicensePlateDetector

def test_detector():
    """Test detector với ảnh đơn giản"""
    
    # Tạo ảnh test với biển số rõ ràng
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Vẽ biển số "28A-175.37" rõ ràng
    cv2.putText(img, '28A-175.37', (200, 240), 
               cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    # Vẽ thêm text khác để test
    cv2.putText(img, 'Test Text', (50, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    print("=== Test Detector ===")
    print("Ảnh test được tạo với biển số: 28A-175.37")
    
    # Khởi tạo detector
    detector = LicensePlateDetector()
    
    # Test detection
    print("\nBắt đầu nhận diện...")
    results = detector.detect_license_plate(img)
    
    print(f"\nKết quả: {len(results)} biển số được tìm thấy")
    for i, result in enumerate(results):
        print(f"  {i+1}. Text: '{result['text']}'")
        print(f"     Confidence: {result['confidence']:.3f}")
        print(f"     BBox: {result['bbox']}")
    
    # Lưu ảnh test
    cv2.imwrite('test_image.jpg', img)
    print("\nẢnh test đã được lưu: test_image.jpg")

if __name__ == "__main__":
    test_detector()

