import sys
import os
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import Inventory
from app.redis_client import set_stock_to_cache

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    sample_products = [
        {"product_id": "PROD001", "product_name": "iPhone 15 Pro", "stock": 100},
        {"product_id": "PROD002", "product_name": "MacBook Pro 14", "stock": 50},
        {"product_id": "PROD003", "product_name": "AirPods Pro", "stock": 200},
    ]

    for p in sample_products:
        existing = db.query(Inventory).filter(Inventory.product_id == p["product_id"]).first()
        if existing:
            print(f"商品 {p['product_id']} 已存在，库存: {existing.stock}")
        else:
            inventory = Inventory(**p)
            db.add(inventory)
            print(f"创建商品 {p['product_id']} ({p['product_name']})，库存: {p['stock']}")

    db.commit()

    for p in sample_products:
        try:
            existing = db.query(Inventory).filter(Inventory.product_id == p["product_id"]).first()
            if existing:
                set_stock_to_cache(p["product_id"], existing.stock)
                print(f"缓存商品 {p['product_id']} 库存: {existing.stock}")
            else:
                set_stock_to_cache(p["product_id"], p["stock"])
                print(f"缓存商品 {p['product_id']} 库存: {p['stock']}")
        except Exception as e:
            print(f"缓存商品 {p['product_id']} 失败 (Redis未启动): {e}")

    print("\n初始化数据完成！")
    print("测试商品列表:")
    for p in sample_products:
        existing = db.query(Inventory).filter(Inventory.product_id == p["product_id"]).first()
        actual_stock = existing.stock if existing else p["stock"]
        print(f"  - {p['product_id']}: {p['product_name']} (库存: {actual_stock})")

finally:
    db.close()
