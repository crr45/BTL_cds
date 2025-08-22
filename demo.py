"""
Demo đơn giản để test các chức năng cơ bản
"""

import cv2
import numpy as np
from database import db
from toll_system import toll_system

def test_database():
    """Test cơ sở dữ liệu"""
    print("🧪 Test cơ sở dữ liệu...")
    
    # Thêm xe mẫu
    db.add_vehicle("30A-12345", "car", 1500)
    db.add_vehicle("51F-67890", "truck", 8000)
    
    print("✅ Đã thêm 2 xe mẫu vào cơ sở dữ liệu")
    
    # Thêm giao dịch mẫu
    db.add_transaction("30A-12345", 50000)
    db.add_transaction("51F-67890", 80000)
    
    print("✅ Đã thêm 2 giao dịch mẫu")

def test_toll_system():
    """Test hệ thống thu phí"""
    print("\n🧪 Test hệ thống thu phí...")
    
    # Test tính phí
    fee1 = toll_system.calculate_toll_fee("car", 1500, 50)
    fee2 = toll_system.calculate_toll_fee("truck", 8000, 100)
    
    print(f"✅ Xe ô tô: {fee1:,} VNĐ")
    print(f"✅ Xe tải: {fee2:,} VNĐ")
    
    # Test xử lý xe vào trạm
    result1 = toll_system.process_vehicle_entry("30A-12345", "car", 1500, 50)
    result2 = toll_system.process_vehicle_entry("51F-67890", "truck", 8000, 100)
    
    if result1['success']:
        print(f"✅ Xử lý xe {result1['license_plate']}: {result1['message']}")
    
    if result2['success']:
        print(f"✅ Xử lý xe {result2['license_plate']}: {result2['message']}")

def test_license_plate_detection():
    """Test nhận diện biển số (giả lập)"""
    print("\n🧪 Test nhận diện biển số...")
    
    # Tạo ảnh mẫu đơn giản
    img = np.zeros((300, 600, 3), dtype=np.uint8)
    img[:] = (255, 255, 255)  # Nền trắng
    
    # Vẽ khung giả biển số
    cv2.rectangle(img, (100, 100), (500, 200), (0, 0, 0), 2)
    
    # Thêm text giả
    cv2.putText(img, "30A-12345", (150, 150), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Lưu ảnh mẫu
    cv2.imwrite("sample_plate.jpg", img)
    print("✅ Đã tạo ảnh mẫu: sample_plate.jpg")
    print("ℹ️  Đây là ảnh giả để demo. Trong thực tế sẽ dùng camera thật.")

def main():
    """Hàm chính demo"""
    print("=" * 60)
    print("🧪 DEMO - AI Nhận diện Biển số Xe và Thu phí")
    print("=" * 60)
    
    try:
        # Test các chức năng
        test_database()
        test_toll_system()
        test_license_plate_detection()
        
        print("\n" + "=" * 60)
        print("🎉 Demo hoàn thành thành công!")
        print("📁 Đã tạo file: sample_plate.jpg")
        print("🗄️  Cơ sở dữ liệu: toll_system.db")
        print("🌐 Chạy 'python main.py' để khởi động ứng dụng web")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Lỗi trong demo: {e}")
        print("🔧 Vui lòng kiểm tra cài đặt dependencies")

if __name__ == "__main__":
    main() 