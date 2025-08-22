"""
Module hệ thống thu phí tự động
"""

import datetime
from typing import Dict, Optional
from database import db

class TollSystem:
    def __init__(self):
        """Khởi tạo hệ thống thu phí"""
        self.base_fees = {
            'car': 50000,      # Xe ô tô con
            'truck': 80000,    # Xe tải
            'bus': 70000,      # Xe buýt
            'motorcycle': 30000, # Xe máy
            'default': 50000   # Mặc định
        }
        
        self.weight_multipliers = {
            'car': 1.0,
            'truck': 1.5,
            'bus': 1.3,
            'motorcycle': 0.5,
            'default': 1.0
        }
    
    def calculate_toll_fee(self, vehicle_type: str, weight: float = None, 
                          distance: float = None) -> float:
        """Tính toán phí thu phí"""
        # Lấy phí cơ bản
        base_fee = self.base_fees.get(vehicle_type, self.base_fees['default'])
        
        # Tính phí theo trọng lượng
        weight_fee = 0
        if weight and weight > 0:
            weight_multiplier = self.weight_multipliers.get(vehicle_type, 1.0)
            weight_fee = weight * weight_multiplier * 1000  # 1000 VNĐ/kg
        
        # Tính phí theo khoảng cách
        distance_fee = 0
        if distance and distance > 0:
            distance_fee = distance * 100  # 100 VNĐ/km
        
        # Tổng phí
        total_fee = base_fee + weight_fee + distance_fee
        
        return round(total_fee, -3)  # Làm tròn đến nghìn
    
    def process_vehicle_entry(self, license_plate: str, vehicle_type: str = 'car',
                            weight: float = None, distance: float = None) -> Dict:
        """Xử lý xe vào trạm thu phí"""
        try:
            # Tính phí
            toll_fee = self.calculate_toll_fee(vehicle_type, weight, distance)
            
            # Thêm xe vào cơ sở dữ liệu
            db.add_vehicle(license_plate, vehicle_type, weight)
            
            # Thêm giao dịch thu phí
            db.add_transaction(license_plate, toll_fee)
            
            # Tạo thông báo
            message = f"Xe {license_plate} đã được xử lý. Phí: {toll_fee:,} VNĐ"
            
            return {
                'success': True,
                'license_plate': license_plate,
                'vehicle_type': vehicle_type,
                'toll_fee': toll_fee,
                'message': message,
                'timestamp': datetime.datetime.now()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.datetime.now()
            }
    
    def get_vehicle_info(self, license_plate: str) -> Optional[Dict]:
        """Lấy thông tin xe"""
        return db.get_vehicle(license_plate)
    
    def get_toll_history(self, license_plate: str = None) -> list:
        """Lấy lịch sử thu phí"""
        # Giả lập dữ liệu lịch sử
        if license_plate:
            return [
                {
                    'license_plate': license_plate,
                    'toll_fee': 50000,
                    'timestamp': datetime.datetime.now() - datetime.timedelta(days=1)
                }
            ]
        else:
            return [
                {
                    'license_plate': '30A-12345',
                    'toll_fee': 50000,
                    'timestamp': datetime.datetime.now() - datetime.timedelta(hours=2)
                },
                {
                    'license_plate': '51F-67890',
                    'toll_fee': 80000,
                    'timestamp': datetime.datetime.now() - datetime.timedelta(hours=1)
                }
            ]
    
    def generate_receipt(self, license_plate: str, toll_fee: float) -> str:
        """Tạo hóa đơn thu phí"""
        receipt = f"""
        ========================================
                    HÓA ĐƠN THU PHÍ
        ========================================
        
        Biển số xe: {license_plate}
        Thời gian: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        Số tiền: {toll_fee:,} VNĐ
        
        Cảm ơn quý khách!
        ========================================
        """
        return receipt
    
    def get_daily_statistics(self) -> Dict:
        """Lấy thống kê hàng ngày"""
        today = datetime.datetime.now().date()
        
        # Giả lập dữ liệu thống kê
        return {
            'date': today.strftime('%d/%m/%Y'),
            'total_vehicles': 45,
            'total_revenue': 2500000,
            'vehicle_types': {
                'car': 30,
                'truck': 10,
                'bus': 3,
                'motorcycle': 2
            }
        }

# Khởi tạo hệ thống thu phí
toll_system = TollSystem() 