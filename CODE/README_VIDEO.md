# Hướng dẫn sử dụng chức năng Nhận diện Biển số từ Video

## Tính năng mới

Web app đã được cập nhật để hỗ trợ nhận diện biển số xe từ video files, bên cạnh các tính năng hiện có:
- Camera real-time
- Upload ảnh
- **Upload video (MỚI)**

## Cách sử dụng

### 1. Khởi động ứng dụng
```bash
python web_app.py
```
Ứng dụng sẽ chạy tại: http://localhost:5000

### 2. Truy cập trang nhận diện
- Vào tab "Video" trên trang detection
- Hoặc truy cập trực tiếp: http://localhost:5000/detection

### 3. Upload video
- Click vào vùng upload hoặc kéo thả file video
- Hỗ trợ các định dạng: MP4, AVI, MOV, MKV, WEBM
- Kích thước tối đa: 100MB

### 4. Xử lý video
- Sau khi upload, video sẽ hiển thị với controls
- Click "Bắt đầu Nhận diện Video" để xử lý
- Quá trình xử lý sẽ hiển thị progress bar

### 5. Kết quả
- Hiển thị biển số xe được nhận diện
- Độ tin cậy của kết quả
- Thống kê: tổng số detections, biển số duy nhất, thời gian xử lý
- Thông tin frame và timestamp (nếu có)

## Cấu trúc API

### Endpoint mới: `/api/detect_plate_video`
- **Method**: POST
- **Input**: FormData với key 'video'
- **Output**: JSON response với kết quả nhận diện

### Response format:
```json
{
  "success": true,
  "license_plate": "30A-12345",
  "confidence": 0.85,
  "total_detections": 10,
  "all_results": [
    {
      "text": "30A-12345",
      "confidence": 0.85,
      "bbox": [x1, y1, x2, y2],
      "frame_number": 15,
      "timestamp": 1.5
    }
  ]
}
```

## Cải tiến kỹ thuật

### 1. Video Processing
- Xử lý frame-by-frame với sample rate có thể điều chỉnh
- Giới hạn số frame xử lý để tối ưu hiệu suất
- Loại bỏ kết quả trùng lặp

### 2. Memory Management
- Lưu file tạm thời trong thư mục uploads/
- Tự động xóa file sau khi xử lý
- Giới hạn kích thước file upload

### 3. Error Handling
- Kiểm tra định dạng file
- Xử lý lỗi video corruption
- Fallback cho các trường hợp lỗi

## Test

### Tạo video test
```bash
python test_video_detection.py
```

### Test API trực tiếp
```bash
curl -X POST -F "video=@test_video.mp4" http://localhost:5000/api/detect_plate_video
```

## Troubleshooting

### Lỗi thường gặp:
1. **File quá lớn**: Giảm kích thước video hoặc tăng giới hạn trong code
2. **Định dạng không hỗ trợ**: Chuyển đổi sang MP4 hoặc AVI
3. **Video corruption**: Kiểm tra file video có bị hỏng không

### Tối ưu hiệu suất:
1. Giảm sample_rate trong `detect_from_video_file()` để xử lý ít frame hơn
2. Giảm giới hạn frame xử lý (hiện tại là 100)
3. Sử dụng GPU nếu có (EasyOCR hỗ trợ GPU)

## Cấu hình

### Thay đổi giới hạn file size:
```python
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB
```

### Thay đổi sample rate:
```python
results = detector.detect_from_video_file(video_path, sample_rate=10)  # Xử lý mỗi 10 frame
```

### Thay đổi giới hạn frame:
```python
if processed_frames > 200:  # Tăng lên 200 frames
    break
```

## Tương lai

Các tính năng có thể phát triển thêm:
- Real-time video streaming
- Batch processing nhiều video
- Export kết quả dưới dạng CSV/JSON
- Integration với camera IP
- Multi-threading cho xử lý video
