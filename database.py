"""
Module quản lý cơ sở dữ liệu cho hệ thống thu phí
"""

import sqlite3
import datetime

class TollDatabase:
    def __init__(self, db_path="toll_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY,
                    license_plate TEXT UNIQUE,
                    vehicle_type TEXT,
                    weight REAL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS toll_transactions (
                    id INTEGER PRIMARY KEY,
                    license_plate TEXT,
                    toll_fee REAL,
                    timestamp TIMESTAMP
                )
            ''')
            conn.commit()
    
    def add_vehicle(self, license_plate, vehicle_type, weight=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO vehicles VALUES (?, ?, ?, ?)',
                         (None, license_plate, vehicle_type, weight))
            conn.commit()
    
    def add_transaction(self, license_plate, toll_fee):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO toll_transactions VALUES (?, ?, ?, ?)',
                         (None, license_plate, toll_fee, datetime.datetime.now()))
            conn.commit()

db = TollDatabase() 