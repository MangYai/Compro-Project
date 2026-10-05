"""
pack/unpack และ CRUD สำหรับ books.dat
"""
import storage
from config import (
    BOOKS_FILE,
    BOOK_FORMAT,
    BOOK_SIZE,
    STATUS_ACTIVE,
    STATUS_DELETED,
    GENRE_PRICE,
)

import struct


def pack_book(book_id, title, author, genre, price, stock_total, stock_available, status):
    title_size, author_size, genre_size = _string_field_sizes()
    return struct.pack(
        BOOK_FORMAT,
        book_id,
        storage.encode_str(title, title_size),
        storage.encode_str(author, author_size),
        storage.encode_str(genre, genre_size),
        float(price),
        int(stock_total),
        int(stock_available),
        int(status),
    )


def unpack_book(raw):
    (book_id, title_raw, author_raw, genre_raw, price_per_day,
     stock_total, stock_available, status) = struct.unpack(BOOK_FORMAT, raw)
    return {
        "book_id": book_id,
        "title": storage.decode_str(title_raw),
        "author": storage.decode_str(author_raw),
        "genre": storage.decode_str(genre_raw),
        "price_per_day": price_per_day,
        "stock_total": stock_total,
        "stock_available": stock_available,
        "status": status,
    }


def _string_field_sizes():
    import re
    sizes = [int(n) for n in re.findall(r"(\d+)s", BOOK_FORMAT)]
    return sizes[0], sizes[1], sizes[2]


def add(title, author, genre, stock_total):
    if genre not in GENRE_PRICE:
        raise ValueError(f"genre ไม่ถูกต้อง: '{genre}' ต้องเป็นหนึ่งใน {list(GENRE_PRICE.keys())}")
    storage.ensure_file(BOOKS_FILE)
    new_id = storage.next_id(BOOKS_FILE, BOOK_SIZE, unpack_book, "book_id")
    stock_total = int(stock_total)
    price_per_day = GENRE_PRICE[genre]
    raw = pack_book(new_id, title, author, genre, price_per_day, stock_total, stock_total, STATUS_ACTIVE)
    storage.append_record(BOOKS_FILE, raw)
    return new_id


def get(book_id):
    storage.ensure_file(BOOKS_FILE)
    _, record = storage.find_index_by_id(BOOKS_FILE, BOOK_SIZE, unpack_book, "book_id", book_id)
    if record is None or record["status"] == STATUS_DELETED:
        return None
    return record


def update(book_id, title=None, author=None, genre=None, stock_total=None):
    storage.ensure_file(BOOKS_FILE)
    index, record = storage.find_index_by_id(BOOKS_FILE, BOOK_SIZE, unpack_book, "book_id", book_id)
    if record is None or record["status"] == STATUS_DELETED:
        return False
    if genre is not None and genre not in GENRE_PRICE:
        raise ValueError(f"genre ไม่ถูกต้อง: '{genre}' ต้องเป็นหนึ่งใน {list(GENRE_PRICE.keys())}")
    new_title = title if title is not None else record["title"]
    new_author = author if author is not None else record["author"]
    new_genre = genre if genre is not None else record["genre"]
    new_price = GENRE_PRICE[new_genre] if genre is not None else record["price_per_day"]
    new_stock_total = record["stock_total"]
    new_stock_available = record["stock_available"]
    if stock_total is not None:
        stock_total = int(stock_total)
        rented = record["stock_total"] - record["stock_available"]
        new_stock_total = stock_total
        new_stock_available = max(0, new_stock_total - rented)
    raw = pack_book(book_id, new_title, new_author, new_genre, new_price, new_stock_total, new_stock_available, record["status"])
    storage.overwrite_record_at_index(BOOKS_FILE, BOOK_SIZE, index, raw)
    return True


def delete(book_id):
    storage.ensure_file(BOOKS_FILE)
    index, record = storage.find_index_by_id(BOOKS_FILE, BOOK_SIZE, unpack_book, "book_id", book_id)
    if record is None or record["status"] == STATUS_DELETED:
        return False
    raw = pack_book(record["book_id"], record["title"], record["author"], record["genre"], record["price_per_day"],
                     record["stock_total"], record["stock_available"], STATUS_DELETED)
    storage.overwrite_record_at_index(BOOKS_FILE, BOOK_SIZE, index, raw)
    return True


def decrement_stock(book_id):
    storage.ensure_file(BOOKS_FILE)
    index, record = storage.find_index_by_id(BOOKS_FILE, BOOK_SIZE, unpack_book, "book_id", book_id)
    if record is None or record["status"] == STATUS_DELETED:
        return False
    if record["stock_available"] <= 0:
        return False
    raw = pack_book(record["book_id"], record["title"], record["author"], record["genre"], record["price_per_day"],
                     record["stock_total"], record["stock_available"] - 1, record["status"])
    storage.overwrite_record_at_index(BOOKS_FILE, BOOK_SIZE, index, raw)
    return True


def increment_stock(book_id):
    storage.ensure_file(BOOKS_FILE)
    index, record = storage.find_index_by_id(BOOKS_FILE, BOOK_SIZE, unpack_book, "book_id", book_id)
    if record is None:
        return False
    new_available = min(record["stock_total"], record["stock_available"] + 1)
    raw = pack_book(record["book_id"], record["title"], record["author"], record["genre"], record["price_per_day"],
                     record["stock_total"], new_available, record["status"])
    storage.overwrite_record_at_index(BOOKS_FILE, BOOK_SIZE, index, raw)
    return True


def list_all(active_only=True):
    storage.ensure_file(BOOKS_FILE)
    records = storage.read_all(BOOKS_FILE, BOOK_SIZE, unpack_book)
    if active_only:
        return [r for r in records if r["status"] != STATUS_DELETED]
    return records


def filter_books(genre=None, available_only=False):
    records = list_all(active_only=True)
    if genre is not None:
        genre_lower = genre.strip().lower()
        records = [r for r in records if r["genre"].strip().lower() == genre_lower]
    if available_only:
        records = [r for r in records if r["stock_available"] > 0]
    return records


def stats():
    all_records = list_all(active_only=False)
    active_records = [r for r in all_records if r["status"] != STATUS_DELETED]
    deleted_records = [r for r in all_records if r["status"] == STATUS_DELETED]
    total_copies = sum(r["stock_total"] for r in active_records)
    available_now = sum(r["stock_available"] for r in active_records)
    currently_borrowed = total_copies - available_now
    prices = [r["price_per_day"] for r in active_records]
    price_min = min(prices) if prices else 0.0
    price_max = max(prices) if prices else 0.0
    price_avg = (sum(prices) / len(prices)) if prices else 0.0
    genre_count = {}
    for r in active_records:
        genre_count[r["genre"]] = genre_count.get(r["genre"], 0) + 1
    return {
        "total_titles": len(all_records),
        "active_titles": len(active_records),
        "deleted_titles": len(deleted_records),
        "total_copies": total_copies,
        "currently_borrowed": currently_borrowed,
        "available_now": available_now,
        "price_min": price_min,
        "price_max": price_max,
        "price_avg": price_avg,
        "genre_count": genre_count,
    }
