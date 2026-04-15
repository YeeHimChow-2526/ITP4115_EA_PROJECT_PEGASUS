# add_cooler_products.py
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

def add_cooler_products():
    with app.app_context():
        cooler_category = Category.query.filter_by(slug='cooler').first()
        if not cooler_category:
            print("❌ 未找到 '散热器' 分类，尝试创建...")
            cooler_category = Category(name='散热器', slug='cooler', sort_order=8, is_active=True)
            db.session.add(cooler_category)
            db.session.commit()
            print("✅ 已创建 散热器 分类")

        products = [
            {
                "name": "NZXT Kraken Elite 360 RGB",
                "brand": "NZXT",
                "price": 1899.00,
                "original_price": 2099.00,
                "stock": 12,
                "sku": "NZXT-KRAKEN-360",
                "short_description": "360mm一体水冷，2.36英寸LCD屏幕，RGB风扇",
                "description": "高性能一体水冷，可自定义LCD显示屏，显示温度/系统信息，高效散热。",
                "specifications": '{"类型":"360mm一体水冷","风扇":"3x120mm RGB","转速":"500-1800 RPM","水泵":"Asetek 7代","支持平台":"Intel LGA1700/1200, AMD AM5/AM4"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "Noctua NH-D15 chromax.black",
                "brand": "Noctua",
                "price": 799.00,
                "original_price": 899.00,
                "stock": 25,
                "sku": "NOCTUA-NHD15",
                "short_description": "双塔风冷，6热管，静音风扇",
                "description": "旗舰风冷，双塔设计，双NF-A15风扇，顶级散热性能，六年质保。",
                "specifications": '{"类型":"双塔风冷","热管":"6根","风扇":"2x140mm","高度":"165mm","TDP":"220W+","支持平台":"Intel/AMD主流"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "Thermalright Peerless Assassin 120 SE",
                "brand": "Thermalright",
                "price": 299.00,
                "original_price": 399.00,
                "stock": 50,
                "sku": "TL-PA120-SE",
                "short_description": "双塔风冷，6热管，性价比之王",
                "description": "入门级双塔风冷，逆重力热管，TL-C12C风扇，压制i5/R5无压力。",
                "specifications": '{"类型":"双塔风冷","热管":"6根","风扇":"2x120mm","高度":"155mm","TDP":"245W","支持平台":"Intel LGA1700/1200, AMD AM5/AM4"}',
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
                category_id=cooler_category.id,
                is_featured=p["is_featured"],
                is_new=p["is_new"],
                is_active=True
            )
            db.session.add(product)
            added += 1
            print(f"✅ 已添加散热器: {p['name']}")

        db.session.commit()
        print(f"\n🎉 成功添加 {added} 个散热器商品！")

if __name__ == "__main__":
    add_cooler_products()