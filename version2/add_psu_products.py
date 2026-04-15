# add_psu_products.py
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

def add_psu_products():
    with app.app_context():
        psu_category = Category.query.filter_by(slug='psu').first()
        if not psu_category:
            print("❌ 未找到 '电源' 分类，尝试创建...")
            psu_category = Category(name='电源', slug='psu', sort_order=6, is_active=True)
            db.session.add(psu_category)
            db.session.commit()
            print("✅ 已创建 电源 分类")

        products = [
            {
                "name": "Corsair RM850e 850W 80Plus Gold",
                "brand": "Corsair",
                "price": 999.00,
                "original_price": 1199.00,
                "stock": 25,
                "sku": "COR-RM850E",
                "short_description": "850W 80Plus金牌，全模组，静音风扇",
                "description": "高品质电源，全模组设计，120mm静音风扇，支持现代显卡，七年质保。",
                "specifications": '{"功率":"850W","效率":"80Plus Gold","模组化":"全模组","风扇":"120mm","保护":"OVP/UVP/SCP/OPP/OTP"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "Seasonic Focus GX-750 750W 80Plus Gold",
                "brand": "Seasonic",
                "price": 899.00,
                "original_price": 999.00,
                "stock": 30,
                "sku": "SEA-FOCUS-750",
                "short_description": "750W 80Plus金牌，全模组，全日系电容",
                "description": "稳定高效的电源，全日系电容，智能温控风扇，十年质保。",
                "specifications": '{"功率":"750W","效率":"80Plus Gold","模组化":"全模组","风扇":"120mm","保护":"OPP/OVP/UVP/SCP/OCP/OTP"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "Cooler Master MWE 550 Bronze 550W",
                "brand": "Cooler Master",
                "price": 399.00,
                "original_price": 499.00,
                "stock": 50,
                "sku": "CM-MWE550",
                "short_description": "550W 80Plus铜牌，入门级性价比",
                "description": "经济型电源，适合办公和入门游戏主机，三年质保。",
                "specifications": '{"功率":"550W","效率":"80Plus Bronze","模组化":"非模组","风扇":"120mm","保护":"OVP/UVP/OPP/SCP"}',
                "is_featured": False,
                "is_new": False
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
                category_id=psu_category.id,
                is_featured=p["is_featured"],
                is_new=p["is_new"],
                is_active=True
            )
            db.session.add(product)
            added += 1
            print(f"✅ 已添加电源: {p['name']}")

        db.session.commit()
        print(f"\n🎉 成功添加 {added} 个电源商品！")

if __name__ == "__main__":
    add_psu_products()