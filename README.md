
# Ứng dụng AI Nhận diện Biển số Xe và Thu phí Không dừng

## Mô tả
Ứng dụng Python sử dụng AI để tự động nhận diện biển số xe từ camera và thực hiện thu phí không dừng. Hệ thống bao gồm:

- **Nhận diện biển số xe**: Sử dụng OpenCV và EasyOCR
- **Xử lý ảnh/video**: Tiền xử lý và tối ưu hóa ảnh
- **Hệ thống thu phí**: Tính toán và lưu trữ thông tin thu phí
- **Giao diện web**: Dashboard quản lý và theo dõi
- **Cơ sở dữ liệu**: SQLite để lưu trữ dữ liệu

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd BTL-CDS
```

2. Tạo môi trường ảo:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# hoặc
source venv/bin/activate  # Linux/Mac
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

## Sử dụng

1. Chạy ứng dụng chính:
```bash
python main.py
```

2. Mở trình duyệt và truy cập: `http://localhost:5000`

3. Sử dụng camera để nhận diện biển số xe

## Cấu trúc dự án

```
BTL-CDS/
├── main.py                 # Ứng dụng chính
├── license_plate_detector.py  # Module nhận diện biển số
├── toll_system.py          # Hệ thống thu phí
├── database.py             # Quản lý cơ sở dữ liệu
├── web_app.py              # Giao diện web Flask
├── utils.py                # Tiện ích hỗ trợ
├── config.py               # Cấu hình
├── requirements.txt         # Dependencies
└── README.md               # Hướng dẫn này
```

## Tính năng

- ✅ Nhận diện biển số xe từ camera
- ✅ Xử lý ảnh và video real-time
- ✅ Hệ thống thu phí tự động
- ✅ Giao diện web quản lý
- ✅ Lưu trữ dữ liệu SQLite
- ✅ Báo cáo và thống kê

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

