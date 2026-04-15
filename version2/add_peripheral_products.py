# add_peripheral_products.py
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

def add_peripheral_products():
    with app.app_context():
        peripheral_category = Category.query.filter_by(slug='peripheral').first()
        if not peripheral_category:
            print("❌ 未找到 '外设' 分类，尝试创建...")
            peripheral_category = Category(name='外设', slug='peripheral', sort_order=9, is_active=True)
            db.session.add(peripheral_category)
            db.session.commit()
            print("✅ 已创建 外设 分类")

        products = [
            {
                "name": "Logitech G Pro X Superlight 2 无线鼠标",
                "brand": "Logitech",
                "price": 1099.00,
                "original_price": 1299.00,
                "stock": 30,
                "sku": "LOG-GPROX-SL2",
                "short_description": "60g超轻量，无线，HERO 2传感器",
                "description": "电竞级无线鼠标，约60g重量，32000 DPI，最长95小时续航。",
                "specifications": '{"重量":"60g","连接":"无线2.4GHz","DPI":"32000","按键":"5个","续航":"95小时"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "Keychron K2 Pro 机械键盘",
                "brand": "Keychron",
                "price": 699.00,
                "original_price": 799.00,
                "stock": 25,
                "sku": "KEY-K2-PRO",
                "short_description": "75%布局，蓝牙/有线，热插拔，Gasket结构",
                "description": "Mac/Win双系统适配，RGB背光，K Pro轴体，QMK/VIA开源改键。",
                "specifications": '{"布局":"75%","连接":"蓝牙5.1+有线","轴体":"热插拔","电池":"4000mAh","键帽":"PBT双色"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "HyperX Cloud II 电竞耳机",
                "brand": "HyperX",
                "price": 599.00,
                "original_price": 699.00,
                "stock": 40,
                "sku": "HX-CLOUD-II",
                "short_description": "7.1虚拟环绕声，53mm驱动单元",
                "description": "虚拟7.1环绕声，53mm驱动单元，记忆海绵耳罩，可拆卸麦克风。",
                "specifications": '{"类型":"头戴式","连接":"USB/3.5mm","驱动单元":"53mm","频率":"15Hz-25kHz","重量":"320g"}',
                "is_featured": True,
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
                category_id=peripheral_category.id,
                is_featured=p["is_featured"],
                is_new=p["is_new"],
                is_active=True
            )
            db.session.add(product)
            added += 1
            print(f"✅ 已添加外设: {p['name']}")

        db.session.commit()
        print(f"\n🎉 成功添加 {added} 个外设商品！")

if __name__ == "__main__":
    add_peripheral_products()