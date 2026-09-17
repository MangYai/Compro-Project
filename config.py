"""
ค่าคงที่และการตั้งค่าที่ใช้ร่วมกันทั้งระบบ
M&N Rental Shop
"""
import os
import struct
 
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
 
BOOKS_FILE = os.path.join(DATA_DIR, "books.dat")
MEMBERS_FILE = os.path.join(DATA_DIR, "members.dat")
RENTALS_FILE = os.path.join(DATA_DIR, "rentals.dat")
REPORT_FILE = os.path.join(DATA_DIR, "report.txt")
 
BOOK_FORMAT = "<I45s35s15sfIII"
MEMBER_FORMAT = "<I30s15sII"
RENTAL_FORMAT = "<IIIIIIfI"
 
BOOK_SIZE = struct.calcsize(BOOK_FORMAT)      # 115
MEMBER_SIZE = struct.calcsize(MEMBER_FORMAT)  # 57
RENTAL_SIZE = struct.calcsize(RENTAL_FORMAT)  # 32
 
STATUS_DELETED = 0
STATUS_ACTIVE = 1
STATUS_BORROWING = 1
STATUS_RETURNED = 2
 
DEFAULT_RENT_DAYS = 7
FINE_PER_DAY = 5.0  # บาท/วันที่คืนช้า
 
GENRE_PRICE = {
    "Comic": 3.0,
    "Manga": 5.0,
    "Novel": 15.0,
}
 
APP_VERSION = "1.0"
APP_NAME = "M&N Rental Shop"
 