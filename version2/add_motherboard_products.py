# add_motherboard_products.py
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

def add_motherboard_products():
    with app.app_context():
        # 查找主板分类 (slug='motherboard')
        mb_category = Category.query.filter_by(slug='motherboard').first()
        if not mb_category:
            print("❌ 未找到 '主板' 分类，尝试创建...")
            mb_category = Category(name='主板', slug='motherboard', sort_order=3, is_active=True)
            db.session.add(mb_category)
            db.session.commit()
            print("✅ 已创建 主板 分类")

        products = [
            {
                "name": "ASUS ROG MAXIMUS Z790 HERO",
                "brand": "ASUS",
                "price": 4599.00,
                "original_price": 4999.00,
                "stock": 12,
                "sku": "ASUS-Z790-HERO",
                "short_description": "Z790芯片组，支持Intel第13/14代，DDR5",
                "description": "旗舰级Z790主板，20+1相供电，PCIe 5.0，WiFi 6E，雷电4接口。",
                "specifications": '{"芯片组":"Z790","CPU插槽":"LGA1700","内存类型":"DDR5","内存插槽":"4","M.2插槽":"5","供电相数":"20+1"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "MSI B760 TOMAHAWK",
                "brand": "MSI",
                "price": 1499.00,
                "original_price": 1699.00,
                "stock": 35,
                "sku": "MSI-B760-TOMAHAWK",
                "short_description": "B760芯片组，高性价比，DDR5",
                "description": "中端B760主板，12+1+1相供电，支持PCIe 4.0，2.5G网卡，适合搭配i5处理器。",
                "specifications": '{"芯片组":"B760","CPU插槽":"LGA1700","内存类型":"DDR5","内存插槽":"4","M.2插槽":"3","供电相数":"12+1+1"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "Gigabyte X670 AORUS ELITE AX",
                "brand": "Gigabyte",
                "price": 2799.00,
                "original_price": 2999.00,
                "stock": 18,
                "sku": "GB-X670-AORUS",
                "short_description": "X670芯片组，支持AMD Ryzen 7000系列",
                "description": "16+2+2相供电，PCIe 5.0显卡和M.2，WiFi 6E，适合高端锐龙处理器。",
                "specifications": '{"芯片组":"X670","CPU插槽":"AM5","内存类型":"DDR5","内存插槽":"4","M.2插槽":"4","供电相数":"16+2+2"}',
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
                category_id=mb_category.id,
                is_featured=p["is_featured"],
                is_new=p["is_new"],
                is_active=True
            )
            db.session.add(product)
            added += 1
            print(f"✅ 已添加主板: {p['name']}")

        db.session.commit()
        print(f"\n🎉 成功添加 {added} 个主板商品！")

if __name__ == "__main__":
    add_motherboard_products()