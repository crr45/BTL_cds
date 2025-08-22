"""
Cấu hình cho ứng dụng AI Nhận diện Biển số Xe và Thu phí Không dừng
"""

import os
from pathlib import Path

# Đường dẫn cơ bản
BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
DATABASE_PATH = BASE_DIR / "toll_system.db"

# Cấu hình camera
CAMERA_INDEX = 0  # Index của camera (0 là camera mặc định)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# Cấu hình nhận diện biển số
LICENSE_PLATE_MIN_AREA = 1000  # Diện tích tối thiểu của biển số
LICENSE_PLATE_ASPECT_RATIO = 2.0  # Tỷ lệ khung hình biển số
CONFIDENCE_THRESHOLD = 0.7  # Ngưỡng tin cậy cho OCR

# Cấu hình thu phí (VNĐ)
BASE_TOLL_FEE = 50000  # Phí cơ bản
WEIGHT_MULTIPLIER = 1000  # Hệ số nhân theo trọng lượng
DISTANCE_MULTIPLIER = 100  # Hệ số nhân theo khoảng cách

# Cấu hình Flask
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
SECRET_KEY = "your-secret-key-here"

# Cấu hình cơ sở dữ liệu
DATABASE_CONFIG = {
    "database": str(DATABASE_PATH),
    "echo": False
}

# Tạo thư mục uploads nếu chưa tồn tại
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Cấu hình logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 