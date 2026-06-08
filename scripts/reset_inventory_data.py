# -*- coding: utf-8 -*-
"""Reset SQLite database về dữ liệu mẫu chuẩn, dùng cột Mã kho."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import db


if __name__ == "__main__":
    db.reset_sample_data()
    print(f"SQLite reset complete: {len(db.SAMPLE_PRODUCTS)} products and {len(db.SAMPLE_TRANSACTIONS)} transactions.")
