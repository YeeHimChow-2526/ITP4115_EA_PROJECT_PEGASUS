# add_ram_products.py
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

def add_ram_products():
    with app.app_context():
        # 查找内存分类 (slug='ram')
        ram_category = Category.query.filter_by(slug='ram').first()
        if not ram_category:
            print("❌ 未找到 '内存' 分类，尝试创建...")
            ram_category = Category(name='内存', slug='ram', sort_order=4, is_active=True)
            db.session.add(ram_category)
            db.session.commit()
            print("✅ 已创建 内存 分类")

        products = [
            {
                "name": "Corsair Vengeance DDR5 32GB (16GBx2) 6000MHz",
                "brand": "Corsair",
                "price": 1099.00,
                "original_price": 1299.00,
                "stock": 45,
                "sku": "COR-DDR5-32G-6000",
                "short_description": "32GB DDR5 6000MHz，CL36，RGB灯效",
                "description": "高品质DDR5内存，支持Intel XMP 3.0，铝制散热片，动态RGB灯效。",
                "specifications": '{"容量":"32GB (2x16GB)","频率":"6000MHz","时序":"CL36","电压":"1.35V","类型":"DDR5"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "Kingston Fury Beast DDR4 32GB (16GBx2) 3200MHz",
                "brand": "Kingston",
                "price": 699.00,
                "original_price": 799.00,
                "stock": 60,
                "sku": "KING-DDR4-32G-3200",
                "short_description": "32GB DDR4 3200MHz，CL16，高性价比",
                "description": "经典DDR4内存，兼容Intel和AMD平台，即插即用，稳定性出色。",
                "specifications": '{"容量":"32GB (2x16GB)","频率":"3200MHz","时序":"CL16","电压":"1.35V","类型":"DDR4"}',
                "is_featured": True,
                "is_new": False
            },
            {
                "name": "G.Skill Trident Z5 RGB DDR5 64GB (32GBx2) 6400MHz",
                "brand": "G.Skill",
                "price": 2199.00,
                "original_price": 2499.00,
                "stock": 20,
                "sku": "GS-DDR5-64G-6400",
                "short_description": "64GB DDR5 6400MHz，CL32，旗舰级",
                "description": "顶级DDR5内存，支持Intel XMP 3.0，绚丽RGB灯条，适合内容创作和高端游戏。",
                "specifications": '{"容量":"64GB (2x32GB)","频率":"6400MHz","时序":"CL32","电压":"1.40V","类型":"DDR5"}',
                "is_featured": True,
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
                category_id=ram_category.id,
                is_featured=p["is_featured"],
                is_new=p["is_new"],
                is_active=True
            )
            db.session.add(product)
            added += 1
            print(f"✅ 已添加内存: {p['name']}")

        db.session.commit()
        print(f"\n🎉 成功添加 {added} 个内存商品！")

if __name__ == "__main__":
    add_ram_products()