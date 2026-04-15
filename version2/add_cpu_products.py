# add_cpu_products.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Category, Product

def slugify(name):
    import re
    slug = name.lower()
    slug = re.sub(r'[^\w\-]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug

def add_cpu_products():
    with app.app_context():
        cpu_category = Category.query.filter_by(slug='cpu').first()
        if not cpu_category:
            print("❌ 未找到 'CPU处理器' 分类，尝试创建...")
            cpu_category = Category(name='CPU处理器', slug='cpu', sort_order=1, is_active=True)
            db.session.add(cpu_category)
            db.session.commit()
            print("✅ 已创建 CPU处理器 分类")

        products = [
            {
                "name": "Intel Core i9-13900K",
                "brand": "Intel",
                "price": 4299.00,
                "original_price": 4899.00,
                "stock": 25,
                "sku": "INTEL-13900K",
                "short_description": "24核心32线程，最高5.8GHz",
                "description": "Intel第13代旗舰处理器，8个性能核+16个能效核，总计24核32线程。",
                "specifications": '{"核心":"24","线程":"32","频率":"5.8GHz"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "AMD Ryzen 9 7950X",
                "brand": "AMD",
                "price": 3899.00,
                "original_price": 4299.00,
                "stock": 18,
                "sku": "AMD-7950X",
                "short_description": "16核心32线程，5nm制程",
                "description": "AMD Ryzen 7000系列旗舰，16核32线程，Zen4架构。",
                "specifications": '{"核心":"16","线程":"32","频率":"5.7GHz"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "Intel Core i5-13600K",
                "brand": "Intel",
                "price": 2499.00,
                "original_price": 2799.00,
                "stock": 42,
                "sku": "INTEL-13600K",
                "short_description": "14核心20线程，高性价比",
                "description": "6性能核+8能效核，适合游戏与日常使用。",
                "specifications": '{"核心":"14","线程":"20","频率":"5.1GHz"}',
                "is_featured": False,
                "is_new": True
            }
        ]

        added = 0
        for p in products:
            existing = Product.query.filter_by(sku=p["sku"]).first()
            if existing:
                print(f"⏭️ 已存在: {p['name']}")
                continue
            product = Product(
                name=p["name"],
                slug=slugify(p["name"]),
                brand=p["brand"],
                price=p["price"],
                original_price=p["original_price"],
                stock=p["stock"],
                sku=p["sku"],
                short_description=p["short_description"],
                description=p["description"],
                specifications=p["specifications"],
                category_id=cpu_category.id,
                is_featured=p["is_featured"],
                is_new=p["is_new"],
                is_active=True
            )
            db.session.add(product)
            added += 1
            print(f"✅ 已添加 CPU: {p['name']}")

        db.session.commit()
        print(f"\n🎉 成功添加 {added} 个 CPU 商品！")

if __name__ == "__main__":
    add_cpu_products()