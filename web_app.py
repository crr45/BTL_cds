"""
Giao diện web Flask cho hệ thống thu phí
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import datetime
from toll_system import toll_system
from license_plate_detector import LicensePlateDetector
import cv2
import base64
import numpy as np
import os
import tempfile
import uuid
import re

# web_app.py (đầu file)
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)
app.secret_key = 'your-secret-key-here'


# Giới hạn kích thước ảnh xử lý để tránh lỗi bộ nhớ
MAX_SERVER_DIM = 1024

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-here'

# Khởi tạo detector
_detector_singleton = None

def get_detector():
	global _detector_singleton
	if _detector_singleton is None:
		_detector_singleton = LicensePlateDetector()
	return _detector_singleton

# Hàm kiểm tra/chuẩn hóa biển số VN
VN_STRICT_REGEX = re.compile(r'^\d{1,2}[A-Z]{1,2}-\d{2,3}\.\d{2}$')

def is_strict_vn_plate(text: str) -> bool:
	return bool(VN_STRICT_REGEX.match(text))

def normalize_vn_plate(text: str) -> str:
	if not text:
		return text
	s = re.sub(r'[^A-Z0-9\-\.]', '', text.upper())
	# Đúng chuẩn rồi
	if is_strict_vn_plate(s):
		return s
	# 28A-17537 -> 28A-175.37
	m = re.match(r'^(\d{1,2}[A-Z]{1,2})-(\d{3})(\d{2})$', s)
	if m:
		return f"{m.group(1)}-{m.group(2)}.{m.group(3)}"
	# 28A175.37 -> 28A-175.37
	m = re.match(r'^(\d{1,2}[A-Z]{1,2})(\d{3})\.(\d{2})$', s)
	if m:
		return f"{m.group(1)}-{m.group(2)}.{m.group(3)}"
	# 28A17537 -> 28A-175.37
	m = re.match(r'^(\d{1,2}[A-Z]{1,2})(\d{3})(\d{2})$', s)
	if m:
		return f"{m.group(1)}-{m.group(2)}.{m.group(3)}"
	return s

# Cấu hình upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'jpg', 'jpeg', 'png', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
	os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/favicon.ico')
def favicon():
	"""Serve favicon"""
	return send_from_directory(os.path.join(app.root_path, 'static'),
							   'favicon.svg', mimetype='image/svg+xml')

@app.route('/')
def index():
	"""Trang chủ"""
	return render_template('index.html')

@app.route('/detection')
def detection():
	"""Trang nhận diện biển số"""
	return render_template('detection.html')

@app.route('/toll_system')
def toll_system_page():
	"""Trang hệ thống thu phí"""
	return render_template('toll_system.html')

@app.route('/statistics')
def statistics():
	"""Trang thống kê"""
	stats = toll_system.get_daily_statistics()
	return render_template('statistics.html', stats=stats)

@app.route('/api/detect_plate', methods=['POST'])
def api_detect_plate():
	"""API nhận diện biển số từ ảnh"""
	try:
		data = request.get_json(silent=True) or {}
		image_data = data.get('image')
		if not image_data:
			print('api_detect_plate: missing image in request')
			return jsonify({'error': 'Không có ảnh'}), 400
		
		print(f"api_detect_plate: received image string length={len(image_data)}")
		if isinstance(image_data, str) and ',' in image_data:
			image_data = image_data.split(',', 1)[1]
			print('api_detect_plate: data URL detected, stripped header')
		image_data = re.sub(r'\s+', '', image_data)
		
		try:
			image_bytes = base64.b64decode(image_data, validate=True)
		except Exception as e:
			print(f"api_detect_plate: base64 decode error: {e}")
			return jsonify({'error': f'Decode base64 thất bại: {str(e)}'}), 400
		
		nparr = np.frombuffer(image_bytes, np.uint8)
		image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
		if image is None:
			print('api_detect_plate: cv2.imdecode returned None')
			return jsonify({'error': 'Không thể đọc ảnh (imdecode lỗi).'}), 400
		
		# Downscale ảnh quá lớn để giảm lag/bộ nhớ
		h, w = image.shape[:2]
		max_dim = max(h, w)
		if max_dim > MAX_SERVER_DIM:
			scale = MAX_SERVER_DIM / max_dim
			new_w, new_h = int(w * scale), int(h * scale)
			image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
			print(f"api_detect_plate: resized on server to {new_w}x{new_h}")
		
		print(f"api_detect_plate: image shape={image.shape}")
		detector = get_detector()
		results = detector.detect_license_plate(image)
		
		# Chuẩn hóa tất cả kết quả rồi lọc chặt
		normalized = []
		for r in results:
			text_norm = normalize_vn_plate(r['text'])
			normalized.append({**r, 'text': text_norm})
		strict_results = [r for r in normalized if is_strict_vn_plate(r['text'])]
		chosen_list = strict_results if strict_results else normalized
		
		# Fallback mạnh: nếu vẫn rỗng, đọc OCR trực tiếp nhiều biến thể + paragraph và suy diễn
		if not chosen_list:
			try:
				variants = []
				# dựng biến thể tương tự trong detector
				variants.extend(detector._generate_variants(image))
				variants.append(image)
				cands = []
				for var in variants:
					ocr1 = detector.reader.readtext(var)
					for _, txt, conf in ocr1:
						n = normalize_vn_plate(txt)
						# Ưu tiên biến thể hợp lệ hoặc có đủ 5 chữ số
						if is_strict_vn_plate(n) or sum(1 for c in n if c.isdigit()) >= 5:
							cands.append({'text': n, 'confidence': conf, 'score': conf})
					# paragraph
					try:
						ocr2 = detector.reader.readtext(var, paragraph=True)
						for _, txt, conf in ocr2:
							n = normalize_vn_plate(txt)
							if is_strict_vn_plate(n) or sum(1 for c in n if c.isdigit()) >= 5:
								cands.append({'text': n, 'confidence': conf, 'score': conf})
					except Exception:
						pass
				# chọn ứng viên tốt nhất nếu có
				if cands:
					cands.sort(key=lambda x: x['score'], reverse=True)
					best = cands[0]
					return jsonify({'success': True, 'license_plate': best['text'], 'confidence': best['confidence']})
			except Exception as e:
				print(f"api_detect_plate fallback error: {e}")
		
		if chosen_list:
			best = sorted(chosen_list, key=lambda x: x.get('score', x['confidence']), reverse=True)[0]
			return jsonify({'success': True, 'license_plate': best['text'], 'confidence': best['confidence']})
		else:
			return jsonify({'success': False, 'message': 'Không tìm thấy biển số xe'})
			
	except Exception as e:
		print(f"api_detect_plate: unexpected error: {e}")
		return jsonify({'error': str(e)}), 500

@app.route('/api/detect_plate_video', methods=['POST'])
def api_detect_plate_video():
	"""API nhận diện biển số từ video"""
	try:
		# Kiểm tra file upload
		if 'video' not in request.files:
			return jsonify({'error': 'Không có file video'}), 400
		
		file = request.files['video']
		if file.filename == '':
			return jsonify({'error': 'Không có file được chọn'}), 400
		
		if not allowed_file(file.filename):
			return jsonify({'error': 'Định dạng file không được hỗ trợ'}), 400
		
		# Kiểm tra kích thước file
		if file.content_length and file.content_length > app.config['MAX_CONTENT_LENGTH']:
			return jsonify({'error': 'File video quá lớn'}), 400
		
		# Lưu file tạm thời
		temp_filename = f"{uuid.uuid4()}_{file.filename}"
		temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
		file.save(temp_path)
		
		try:
			# Xử lý video
			print(f"Bắt đầu xử lý video: {file.filename}")
			results = get_detector().detect_from_video_file(temp_path)
			print(f"Kết quả xử lý: {len(results) if results else 0} detections")
			
			# Xóa file tạm
			os.remove(temp_path)
			
			if results:
				# Trả về kết quả tốt nhất
				best_result = max(results, key=lambda x: x['confidence'])
				return jsonify({
					'success': True,
					'license_plate': best_result['text'],
					'confidence': best_result['confidence'],
					'total_detections': len(results),
					'all_results': results
				})
			else:
				return jsonify({
					'success': False,
					'message': 'Không tìm thấy biển số xe trong video'
				})
				
		except Exception as e:
			# Xóa file tạm nếu có lỗi
			if os.path.exists(temp_path):
				os.remove(temp_path)
			print(f"Lỗi xử lý video: {str(e)}")
			raise e
			
	except Exception as e:
		print(f"Lỗi API video: {str(e)}")
		return jsonify({'error': str(e)}), 500

@app.route('/api/process_toll', methods=['POST'])
def api_process_toll():
	"""API xử lý thu phí"""
	try:
		data = request.json
		license_plate = data.get('license_plate')
		vehicle_type = data.get('vehicle_type', 'car')
		weight = data.get('weight')
		distance = data.get('distance')
		
		if not license_plate:
			return jsonify({'error': 'Thiếu biển số xe'}), 400
		
		# Xử lý xe vào trạm
		result = toll_system.process_vehicle_entry(
			license_plate, vehicle_type, weight, distance
		)
		
		if result['success']:
			# Tạo hóa đơn
			receipt = toll_system.generate_receipt(
				result['license_plate'], result['toll_fee']
			)
			result['receipt'] = receipt
		
		return jsonify(result)
		
	except Exception as e:
		return jsonify({'error': str(e)}), 500

@app.route('/api/vehicle_info/<license_plate>')
def api_vehicle_info(license_plate):
	"""API lấy thông tin xe"""
	try:
		vehicle_info = toll_system.get_vehicle_info(license_plate)
		if vehicle_info:
			return jsonify({'success': True, 'vehicle': vehicle_info})
		else:
			return jsonify({'success': False, 'message': 'Không tìm thấy xe'})
	except Exception as e:
		return jsonify({'error': str(e)}), 500

@app.route('/api/toll_history')
def api_toll_history():
	"""API lấy lịch sử thu phí"""
	try:
		license_plate = request.args.get('license_plate')
		history = toll_system.get_toll_history(license_plate)
		return jsonify({'success': True, 'history': history})
	except Exception as e:
		return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def api_statistics():
	"""API lấy thống kê"""
	try:
		stats = toll_system.get_daily_statistics()
		return jsonify({'success': True, 'statistics': stats})
	except Exception as e:
		return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000) 