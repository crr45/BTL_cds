"""
Module nhận diện biển số xe sử dụng OpenCV và EasyOCR
"""

import cv2
import numpy as np
import easyocr
import re
import os

class LicensePlateDetector:
	def __init__(self):
		try:
			# Sử dụng cả tiếng Anh và tiếng Việt để cải thiện độ chính xác
			self.reader = easyocr.Reader(['en', 'vi'], gpu=False)
		except Exception as e:
			print(f"Warning: Could not initialize EasyOCR: {e}")
			self.reader = None

	def preprocess_image(self, image):
		"""Tiền xử lý ảnh để cải thiện OCR"""
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
		enhanced = clahe.apply(gray)
		denoised = cv2.fastNlMeansDenoising(enhanced)
		kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
		sharpened = cv2.filter2D(denoised, -1, kernel)
		return sharpened

	def _generate_variants(self, image):
		"""Sinh nhiều biến thể ảnh để thử OCR."""
		variants = []
		processed = self.preprocess_image(image)
		variants.append(processed)
		# Ngưỡng hóa thích nghi
		thr = cv2.adaptiveThreshold(processed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 5)
		variants.append(thr)
		thr_inv = cv2.bitwise_not(thr)
		variants.append(thr_inv)
		# Đóng mở hình thái học để gộp ký tự mảnh
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
		morph = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel, iterations=1)
		variants.append(morph)
		return variants

	def _normalize_vn_plate(self, text: str) -> str:
		"""Chuẩn hóa các biến thể về định dạng 28A-175.37 khi có thể."""
		t = text
		if re.match(r'^\d{1,2}[A-Z]{1,2}-\d{2,3}\.\d{2}$', t):
			return t
		m = re.match(r'^(\d{1,2}[A-Z]{1,2})-(\d{3})(\d{2})$', t)
		if m:
			return f"{m.group(1)}-{m.group(2)}.{m.group(3)}"
		m = re.match(r'^(\d{1,2}[A-Z]{1,2})(\d{3})(\d{2})$', t)
		if m:
			return f"{m.group(1)}-{m.group(2)}.{m.group(3)}"
		m = re.match(r'^(\d{1,2}[A-Z]{1,2})(\d{3})\.(\d{2})$', t)
		if m:
			return f"{m.group(1)}-{m.group(2)}.{m.group(3)}"
		return t

	def _infer_plate_from_text(self, text: str) -> str | None:
		"""Suy diễn biển số từ chuỗi chưa đúng định dạng."""
		candidate = None
		m = re.search(r'(\d{1,2}[A-Z]{1,2})(\d{5,6})', text)
		if m:
			left, digits = m.group(1), m.group(2)
			if len(digits) >= 5:
				main = digits[:3]
				last = digits[3:5]
				candidate = f"{left}-{main}.{last}"
		return candidate

	def _char_postfix_fixes(self, text: str) -> str:
		"""Sửa nhầm lẫn giữa chữ và số thường gặp."""
		replacements = {
			'S':'5','Z':'2','I':'1','O':'0','Q':'0','B':'8','G':'6','D':'0',
			'T':'7','L':'1','J':'3','R':'8'
		}
		return ''.join(replacements.get(c, c) for c in text)

	def clean_plate_text(self, text):
		"""Làm sạch text biển số xe với cải tiến cho biển số Việt Nam"""
		text = text.upper()
		text = re.sub(r'[^A-Z0-9\-\.]', '', text)
		text = self._char_postfix_fixes(text)
		patterns = [
			r'(\d{1,2}[A-Z]{1,2}-\d{2,3}\.\d{2})',
			r'(\d{1,2}[A-Z]{1,2}-\d{5})',
			r'(\d{1,2}[A-Z]{1,2}\d{3}\.\d{2})',
			r'(\d{1,2}[A-Z]{1,2}\d{5})',
		]
		for pattern in patterns:
			match = re.search(pattern, text)
			if match:
				candidate = match.group(1)
				return self._normalize_vn_plate(candidate)
		# Không match -> thử suy diễn
		inferred = self._infer_plate_from_text(text)
		return inferred or text

	def validate_plate_format(self, text):
		"""Kiểm tra format biển số có hợp lệ không"""
		if not text:
			return False
		digits = sum(1 for c in text if c.isdigit())
		if digits < 5 or len(text) < 7:
			return False
		if not any(c.isalpha() for c in text) or not any(c.isdigit() for c in text):
			return False
		acceptable = [
			r'^\d{1,2}[A-Z]{1,2}-\d{2,3}\.\d{2}$',
			r'^\d{1,2}[A-Z]{1,2}-\d{5}$',
			r'^\d{1,2}[A-Z]{1,2}\d{3}\.\d{2}$',
			r'^\d{1,2}[A-Z]{1,2}\d{5}$',
		]
		return any(re.match(p, text) for p in acceptable)

	def _quality_score(self, text: str, conf: float) -> float:
		score = conf
		if '-' in text and '.' in text:
			score += 0.2
		digits = sum(1 for c in text if c.isdigit())
		score += min(digits, 7) * 0.01
		return score

	def detect_license_plate(self, image: np.ndarray):
		"""Nhận diện biển số xe từ ảnh với cải tiến"""
		try:
			if self.reader is None:
				print("Warning: EasyOCR not available, skipping detection")
				return []
			all_results = []
			# 1) OCR trên nhiều biến thể ảnh
			for variant in self._generate_variants(image) + [image]:
				ocr_results = self.reader.readtext(variant)
				for _, text, conf in ocr_results:
					cleaned = self.clean_plate_text(text)
					if self.validate_plate_format(cleaned) and conf > 0.12:
						all_results.append({'text': cleaned,'confidence': conf,'bbox': [0,0,image.shape[1],image.shape[0]],'score': self._quality_score(cleaned, conf)})
			# 2) Contours crop
			processed = self.preprocess_image(image)
			edges = cv2.Canny(processed, 50, 150)
			contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			for c in contours:
				area = cv2.contourArea(c)
				if area > 800:
					x, y, w, h = cv2.boundingRect(c)
					ar = w / max(h, 1)
					if 1.3 <= ar <= 5.0:
						crop = image[y:y+h, x:x+w]
						for variant in self._generate_variants(crop) + [crop]:
							ocr_results = self.reader.readtext(variant)
							for _, text, conf in ocr_results:
								cleaned = self.clean_plate_text(text)
								if self.validate_plate_format(cleaned) and conf > 0.12:
									all_results.append({'text': cleaned,'confidence': conf,'bbox': [x,y,x+w,y+h],'score': self._quality_score(cleaned, conf)})
			# 3) Paragraph mode (gộp đoạn)
			if not all_results:
				for variant in self._generate_variants(image) + [image]:
					try:
						text_blocks = self.reader.readtext(variant, paragraph=True)
						for _, text, conf in text_blocks:
							clean = re.sub(r'[^A-Z0-9]', '', text.upper())
							clean = self._char_postfix_fixes(clean)
							infer = self._infer_plate_from_text(clean)
							if infer:
								all_results.append({'text': infer,'confidence': conf,'bbox': [0,0,image.shape[1],image.shape[0]],'score': self._quality_score(infer, conf)})
					except Exception:
						pass
			# Hợp nhất theo score
			unique = {}
			for r in all_results:
				key = r['text']
				if key not in unique or r['score'] > unique[key]['score']:
					unique[key] = r
			results = sorted(unique.values(), key=lambda x: x['score'], reverse=True)
			return results
		except Exception as e:
			print(f"Error in license plate detection: {e}")
			return []

	def detect_from_video_file(self, video_path: str, sample_rate: int = 5):
		"""Nhận diện biển số từ video file"""
		try:
			if not os.path.exists(video_path):
				raise FileNotFoundError(f"Video file không tồn tại: {video_path}")
			
			cap = cv2.VideoCapture(video_path)
			if not cap.isOpened():
				raise ValueError(f"Không thể mở video file: {video_path}")
			
			total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
			fps = cap.get(cv2.CAP_PROP_FPS)
			duration = total_frames / fps if fps > 0 else 0
			
			print(f"Video info: {total_frames} frames, {fps:.2f} fps, {duration:.2f}s")
			
			all_results = []
			frame_count = 0
			processed_frames = 0
			
			while True:
				ret, frame = cap.read()
				if not ret:
					break
				
				frame_count += 1
				
				# Chỉ xử lý mỗi N frame để tăng tốc độ
				if frame_count % sample_rate != 0:
					continue
				
				processed_frames += 1
				print(f"Đang xử lý frame {frame_count}/{total_frames} ({processed_frames} processed)")
				
				# Nhận diện biển số
				results = self.detect_license_plate(frame)
				
				if results:
					for result in results:
						# Thêm thông tin frame
						result['frame_number'] = frame_count
						result['timestamp'] = frame_count / fps if fps > 0 else 0
						all_results.append(result)
						print(f"Frame {frame_count}: Tìm thấy biển số {result['text']} (confidence: {result['confidence']:.2f})")
				
				# Giới hạn số frame xử lý để tránh quá tải
				if processed_frames > 100:  # Tối đa 100 frames
					print("Đã đạt giới hạn frame xử lý")
					break
			
			cap.release()
			
			# Loại bỏ kết quả trùng lặp và sắp xếp theo confidence
			unique_results = self._remove_duplicate_plates(all_results)
			unique_results.sort(key=lambda x: x['confidence'], reverse=True)
			
			print(f"Tổng cộng tìm thấy {len(unique_results)} biển số duy nhất từ {len(all_results)} detections")
			
			return unique_results
			
		except Exception as e:
			print(f"Error in video file detection: {e}")
			return []

	def _remove_duplicate_plates(self, results):
		"""Loại bỏ các biển số trùng lặp, giữ lại kết quả có confidence cao nhất"""
		if not results:
			return []
		
		# Nhóm theo text
		plate_groups = {}
		for result in results:
			text = result['text']
			if text not in plate_groups:
				plate_groups[text] = []
			plate_groups[text].append(result)
		
		# Chọn kết quả tốt nhất cho mỗi biển số
		unique_results = []
		for text, group in plate_groups.items():
			best_result = max(group, key=lambda x: x['confidence'])
			unique_results.append(best_result)
		
		return unique_results

	def detect_from_video(self, video_path: str = 0, output_path: str = None):
		"""Nhận diện biển số từ video/camera"""
		try:
			cap = cv2.VideoCapture(video_path)
			
			if output_path:
				fourcc = cv2.VideoWriter_fourcc(*'XVID')
				out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
			
			while True:
				ret, frame = cap.read()
				if not ret:
					break
				
				# Nhận diện biển số
				results = self.detect_license_plate(frame)
				
				# Hiển thị kết quả
				for result in results:
					print(f"Biển số: {result['text']} (Độ tin cậy: {result['confidence']:.2f})")
					
					# Vẽ bounding box
					x1, y1, x2, y2 = result['bbox']
					cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
					cv2.putText(frame, result['text'], (x1, y1-10), 
							   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
				
				# Hiển thị frame
				cv2.imshow('License Plate Detection', frame)
				
				if output_path:
					out.write(frame)
				
				# Nhấn 'q' để thoát
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
			
			cap.release()
			if output_path:
				out.release()
			cv2.destroyAllWindows()
			
		except Exception as e:
			print(f"Error in video detection: {e}")

# Hàm tiện ích để test
def test_detector():
	"""Test detector với ảnh mẫu"""
	try:
		detector = LicensePlateDetector()
		
		# Test với camera
		print("Bắt đầu nhận diện từ camera...")
		print("Nhấn 'q' để thoát")
		detector.detect_from_video()
		
	except Exception as e:
		print(f"Error in test: {e}")

if __name__ == "__main__":
	test_detector() 