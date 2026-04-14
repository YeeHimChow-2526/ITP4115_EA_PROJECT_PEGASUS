from app import db, app
from app.models import User, Post, ProductType, SaleType, Product, CartItem, Order, OrderItem
from datetime import datetime, timedelta

app_context = app.app_context()
app_context.push()
db.drop_all()
db.create_all()

# ===== PRODUCT TYPES =====
cpu_type = ProductType(name='CPU', description='Processors for your system')
gpu_type = ProductType(name='GPU', description='Graphics cards for gaming and rendering')
motherboard_type = ProductType(name='Motherboard', description='Main boards for your PC')
ram_type = ProductType(name='RAM', description='Memory modules')

db.session.add_all([cpu_type, gpu_type, motherboard_type, ram_type])
db.session.commit()

# ===== SALE TYPES =====
regular_sale = SaleType(name='None', discount_percent=0, label='Regular Price')
clearance_sale = SaleType(name='Clearance', discount_percent=20, label='Clearance Sale')
limited_sale = SaleType(name='Limited', discount_percent=10, label='Limited Offer')

db.session.add_all([regular_sale, clearance_sale, limited_sale])
db.session.commit()

# ===== PRODUCTS =====
# CPU Products
cpu_product_1 = Product(
    name='Intel Core i7-13700K',
    description='High-performance desktop processor with 16 cores and 24 threads',
    price=589.99,
    stock=10,
    type_id=cpu_type.id,
    sale_type_id=regular_sale.id,
    image_url='/static/images/cpu.jpg'
)

cpu_product_2 = Product(
    name='AMD Ryzen 9 7950X',
    description='Ultra-high-performance 16-core processor for enthusiasts',
    price=699.99,
    stock=7,
    is_on_sale=True,
    type_id=cpu_type.id,
    sale_type_id=limited_sale.id,
    image_url='/static/images/cpu2.jpg'
)

# GPU Products
gpu_product_1 = Product(
    name='NVIDIA RTX 4070 Ti',
    description='Powerful graphics card for gaming and content creation',
    price=799.99,
    stock=5,
    type_id=gpu_type.id,
    sale_type_id=limited_sale.id,
    image_url='/static/images/gpu.jpg'
)

gpu_product_2 = Product(
    name='AMD Radeon RX 7900 XTX',
    description='High-end gaming GPU with excellent ray tracing performance',
    price=849.99,
    stock=3,
    is_on_sale=True,
    type_id=gpu_type.id,
    sale_type_id=clearance_sale.id,
    image_url='/static/images/gpu2.jpg'
)

# Motherboard Products
motherboard_product_1 = Product(
    name='ASUS ROG Strix Z690-E',
    description='Gaming motherboard with WiFi 6E and extensive connectivity',
    price=329.99,
    stock=8,
    type_id=motherboard_type.id,
    sale_type_id=regular_sale.id,
    image_url='/static/images/motherboard.jpg'
)

motherboard_product_2 = Product(
    name='MSI MEG X870E-E GODLIKE',
    description='Premium AM5 motherboard with superior power delivery',
    price=799.99,
    stock=2,
    type_id=motherboard_type.id,
    sale_type_id=regular_sale.id,
    image_url='/static/images/motherboard2.jpg'
)

# RAM Products
ram_product_1 = Product(
    name='Corsair Vengeance DDR5 32GB',
    description='High-speed DDR5 memory kit for optimal performance',
    price=149.99,
    stock=15,
    is_on_sale=True,
    type_id=ram_type.id,
    sale_type_id=clearance_sale.id,
    image_url='/static/images/ram.jpg'
)

ram_product_2 = Product(
    name='G.SKILL Trident Z5 64GB (2x32GB)',
    description='Extreme performance DDR5 memory with RGB lighting',
    price=299.99,
    stock=6,
    type_id=ram_type.id,
    sale_type_id=regular_sale.id,
    image_url='/static/images/ram2.jpg'
)

db.session.add_all([cpu_product_1, cpu_product_2, gpu_product_1, gpu_product_2, 
                    motherboard_product_1, motherboard_product_2, ram_product_1, ram_product_2])
db.session.commit()

# ===== USERS =====
admin_user = User(username='admin', email='admin@example.com', is_admin=True, about_me='System administrator')
admin_user.set_password('admin')

normal_user = User(username='user', email='user@example.com', is_admin=False, about_me='Regular user')
normal_user.set_password('user')

john_user = User(username='john', email='john@example.com', is_admin=False, about_me='PC gaming enthusiast')
john_user.set_password('P@ssw0rd')

susan_user = User(username='susan', email='susan@example.com', is_admin=False, about_me='Content creator')
susan_user.set_password('P@ssw0rd')

alice_user = User(username='alice', email='alice@example.com', is_admin=False, about_me='Hardware tinkerer')
alice_user.set_password('P@ssw0rd')

db.session.add_all([admin_user, normal_user, john_user, susan_user, alice_user])
db.session.commit()

# ===== FOLLOWER RELATIONSHIPS =====
john_user.follow(susan_user)
susan_user.follow(john_user)
alice_user.follow(susan_user)

db.session.commit()

# ===== POSTS =====
post_1 = Post(body='Just built my new gaming PC! Excited to test it!', author=john_user)
post_2 = Post(body='Working on a new video production setup', author=susan_user)
post_3 = Post(body='Overclocking my GPU for better performance', author=alice_user)

db.session.add_all([post_1, post_2, post_3])
db.session.commit()

# ===== CART ITEMS =====
# John's cart
cart_item_1 = CartItem(user=john_user, product=cpu_product_1, quantity=1)
cart_item_2 = CartItem(user=john_user, product=ram_product_1, quantity=2)

# Susan's cart
cart_item_3 = CartItem(user=susan_user, product=gpu_product_1, quantity=1)

# Alice's cart
cart_item_4 = CartItem(user=alice_user, product=motherboard_product_1, quantity=1)

db.session.add_all([cart_item_1, cart_item_2, cart_item_3, cart_item_4])
db.session.commit()

# ===== ORDERS =====
# Order 1: John's completed order
order_1 = Order(
    user=john_user,
    total_amount=1489.97,
    shipping_address='123 Main St, New York, NY 10001',
    status='Completed',
    created_at=datetime.utcnow() - timedelta(days=30)
)
db.session.add(order_1)
db.session.commit()

# Order Items for Order 1
order_item_1_1 = OrderItem(order=order_1, product=cpu_product_1, quantity=1, price=589.99)
order_item_1_2 = OrderItem(order=order_1, product=ram_product_1, quantity=2, price=149.99)
db.session.add_all([order_item_1_1, order_item_1_2])
db.session.commit()

# Order 2: Susan's pending order
order_2 = Order(
    user=susan_user,
    total_amount=799.99,
    shipping_address='456 Studio Ave, Los Angeles, CA 90001',
    status='Pending',
    created_at=datetime.utcnow() - timedelta(days=2)
)
db.session.add(order_2)
db.session.commit()

# Order Items for Order 2
order_item_2_1 = OrderItem(order=order_2, product=gpu_product_1, quantity=1, price=799.99)
db.session.add(order_item_2_1)
db.session.commit()

# Order 3: Alice's completed order
order_3 = Order(
    user=alice_user,
    total_amount=1179.97,
    shipping_address='789 Tech St, San Francisco, CA 94102',
    status='Completed',
    created_at=datetime.utcnow() - timedelta(days=15)
)
db.session.add(order_3)
db.session.commit()

# Order Items for Order 3
order_item_3_1 = OrderItem(order=order_3, product=motherboard_product_1, quantity=1, price=329.99)
order_item_3_2 = OrderItem(order=order_3, product=cpu_product_2, quantity=1, price=699.99)
order_item_3_3 = OrderItem(order=order_3, product=ram_product_2, quantity=1, price=299.99)
db.session.add_all([order_item_3_1, order_item_3_2, order_item_3_3])

db.session.commit()

print("✅ Test data created successfully!")
print(f"  - 4 users created (1 admin, 3 regular)")
print(f"  - 4 product types created")
print(f"  - 3 sale types created")
print(f"  - 8 products created")
print(f"  - 4 cart items created")
print(f"  - 3 orders created (2 completed, 1 pending)")
print(f"  - 6 order items created")
