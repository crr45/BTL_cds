"""
Ứng dụng chính - AI Nhận diện Biển số Xe và Thu phí Không dừng
"""

import os
import sys
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Hàm chính để chạy ứng dụng"""
    print("=" * 60)
    print("🚗 AI Nhận diện Biển số Xe và Thu phí Không dừng")
    print("=" * 60)
    
    try:
        # Kiểm tra các module cần thiết
        print("📋 Kiểm tra dependencies...")
        
        required_modules = [
            'cv2',
            'numpy',
            'flask',
            'easyocr'
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                missing_modules.append(module)
                print(f"❌ {module} - Chưa cài đặt")
        
        if missing_modules:
            print(f"\n⚠️  Thiếu các module: {', '.join(missing_modules)}")
            print("📥 Vui lòng cài đặt: pip install -r requirements.txt")
            return
        
        print("\n✅ Tất cả dependencies đã sẵn sàng!")
        
        # Khởi tạo cơ sở dữ liệu
        print("\n🗄️  Khởi tạo cơ sở dữ liệu...")
        from database import db
        print("✅ Cơ sở dữ liệu đã sẵn sàng!")
        
        # Khởi tạo hệ thống thu phí
        print("\n💰 Khởi tạo hệ thống thu phí...")
        from toll_system import toll_system
        print("✅ Hệ thống thu phí đã sẵn sàng!")
        
        # Khởi tạo detector
        print("\n🔍 Khởi tạo AI detector...")
        from license_plate_detector import LicensePlateDetector
        detector = LicensePlateDetector()
        print("✅ AI detector đã sẵn sàng!")
        
        # Chạy ứng dụng web
        print("\n🌐 Khởi động ứng dụng web...")
        from web_app import app
        
        print("\n" + "=" * 60)
        print("🎉 Ứng dụng đã sẵn sàng!")
        print("🌐 Mở trình duyệt và truy cập: http://localhost:5000")
        print("📱 Sử dụng camera để nhận diện biển số xe")
        print("💰 Hệ thống thu phí tự động")
        print("📊 Dashboard thống kê và báo cáo")
        print("=" * 60)
        print("⏹️  Nhấn Ctrl+C để dừng ứng dụng")
        print("=" * 60)
        
        # Chạy Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Ứng dụng đã được dừng bởi người dùng")
        print("👋 Tạm biệt!")
        
    except Exception as e:
        print(f"\n❌ Lỗi khởi động ứng dụng: {e}")
        print("🔧 Vui lòng kiểm tra cài đặt và thử lại")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 