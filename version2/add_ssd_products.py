# add_ssd_products.py
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

def add_ssd_products():
    with app.app_context():
        ssd_category = Category.query.filter_by(slug='ssd').first()
        if not ssd_category:
            print("❌ 未找到 '固态硬盘' 分类，尝试创建...")
            ssd_category = Category(name='固态硬盘', slug='ssd', sort_order=5, is_active=True)
            db.session.add(ssd_category)
            db.session.commit()
            print("✅ 已创建 固态硬盘 分类")

        products = [
            {
                "name": "Samsung 990 Pro 1TB NVMe PCIe 4.0",
                "brand": "Samsung",
                "price": 899.00,
                "original_price": 999.00,
                "stock": 30,
                "sku": "SAMSUNG-990PRO-1TB",
                "short_description": "1TB NVMe PCIe 4.0，读取7450MB/s",
                "description": "顶级PCIe 4.0固态，顺序读取高达7450MB/s，写入6900MB/s，适合游戏和专业应用。",
                "specifications": '{"容量":"1TB","接口":"NVMe PCIe 4.0","读取速度":"7450MB/s","写入速度":"6900MB/s","缓存":"1GB DRAM"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "WD Black SN850X 2TB NVMe PCIe 4.0",
                "brand": "Western Digital",
                "price": 1299.00,
                "original_price": 1499.00,
                "stock": 25,
                "sku": "WD-SN850X-2TB",
                "short_description": "2TB NVMe PCIe 4.0，读取7300MB/s",
                "description": "高性能游戏固态，顺序读取7300MB/s，支持游戏模式2.0。",
                "specifications": '{"容量":"2TB","接口":"NVMe PCIe 4.0","读取速度":"7300MB/s","写入速度":"6600MB/s","缓存":"2GB DRAM"}',
                "is_featured": True,
                "is_new": True
            },
            {
                "name": "Kingston KC3000 512GB NVMe PCIe 4.0",
                "brand": "Kingston",
                "price": 499.00,
                "original_price": 599.00,
                "stock": 50,
                "sku": "KING-KC3000-512G",
                "short_description": "512GB NVMe PCIe 4.0，读取7000MB/s",
                "description": "入门级PCIe 4.0固态，性价比高，适合系统盘。",
                "specifications": '{"容量":"512GB","接口":"NVMe PCIe 4.0","读取速度":"7000MB/s","写入速度":"3900MB/s","缓存":"无DRAM（HMB）"}',
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
                category_id=ssd_category.id,
                is_featured=p["is_featured"],
                is_new=p["is_new"],
                is_active=True
            )
            db.session.add(product)
            added += 1
            print(f"✅ 已添加固态硬盘: {p['name']}")

        db.session.commit()
        print(f"\n🎉 成功添加 {added} 个固态硬盘商品！")

if __name__ == "__main__":
    add_ssd_products()