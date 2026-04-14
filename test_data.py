from app import db, app
from app.models import User, Post, ProductType, SaleType, Product

app_context = app.app_context()
app_context.push()
db.drop_all()
db.create_all()

# Create Product Types (Categories)
cpu_type = ProductType(name='CPU', description='Processors for your system')
gpu_type = ProductType(name='GPU', description='Graphics cards for gaming and rendering')
motherboard_type = ProductType(name='Motherboard', description='Main boards for your PC')
ram_type = ProductType(name='RAM', description='Memory modules')

db.session.add_all([cpu_type, gpu_type, motherboard_type, ram_type])
db.session.commit()

# Create Sale Types
regular_sale = SaleType(name='None', discount_percent=0, label='Regular Price')
clearance_sale = SaleType(name='Clearance', discount_percent=20, label='Clearance Sale')
limited_sale = SaleType(name='Limited', discount_percent=10, label='Limited Offer')

db.session.add_all([regular_sale, clearance_sale, limited_sale])
db.session.commit()

# Create Products - one for each category
cpu_product = Product(
    name='Intel Core i7-13700K',
    description='High-performance desktop processor with 16 cores and 24 threads',
    price=589.99,
    stock=10,
    type_id=cpu_type.id,
    sale_type_id=regular_sale.id,
    image_url='/static/images/cpu.jpg'
)

gpu_product = Product(
    name='NVIDIA RTX 4070 Ti',
    description='Powerful graphics card for gaming and content creation',
    price=799.99,
    stock=5,
    type_id=gpu_type.id,
    sale_type_id=limited_sale.id,
    image_url='/static/images/gpu.jpg'
)

motherboard_product = Product(
    name='ASUS ROG Strix Z690-E',
    description='Gaming motherboard with WiFi 6E and extensive connectivity',
    price=329.99,
    stock=8,
    type_id=motherboard_type.id,
    sale_type_id=regular_sale.id,
    image_url='/static/images/motherboard.jpg'
)

ram_product = Product(
    name='Corsair Vengeance DDR5 32GB',
    description='High-speed DDR5 memory kit for optimal performance',
    price=149.99,
    stock=15,
    type_id=ram_type.id,
    sale_type_id=clearance_sale.id,
    image_url='/static/images/ram.jpg'
)

db.session.add_all([cpu_product, gpu_product, motherboard_product, ram_product])
db.session.commit()

# Create users
normal_user = User(username='user', email='user@example.com', is_admin=False)
normal_user.set_password('user')

admin_user = User(username='admin', email='admin@example.com', is_admin=True)
admin_user.set_password('admin')

# Keep some existing users for testing
u1 = User(username='john', email='john@example.com')
u2 = User(username='susan', email='susan@example.com')
u1.set_password("P@ssw0rd")
u2.set_password("P@ssw0rd")

db.session.add_all([normal_user, admin_user, u1, u2])
db.session.commit()

# Create some follower relationships
u1.follow(u2)
u2.follow(u1)

# Create some posts
p1 = Post(body='my first post!', author=u1)
p2 = Post(body='my first post!', author=u2)
db.session.add(p1)
db.session.add(p2)

db.session.commit()
