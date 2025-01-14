from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped
from sqlalchemy import select, ForeignKey, Table, Column
from typing import List
from datetime import datetime, timezone

# Initialize the Flask application
app = Flask(__name__)

# Configure the database URI for MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Summer12321@localhost/ecommerce_api'
# Disable SQLAlchemy's modification tracking to save resources
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Define a base class for models using SQLAlchemy's DeclarativeBase
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the custom base model
db = SQLAlchemy(model_class=Base)
# Bind SQLAlchemy to the Flask app
db.init_app(app)
# Initialize Marshmallow for serialization and validation
ma = Marshmallow(app)

# Define an association table for linking orders and products
order_product = Table(
    "order_product", 
    Base.metadata,  
    Column("order_id", ForeignKey("orders.id"), primary_key=True), 
    Column("product_id", ForeignKey("products.id"), primary_key=True)  
)

class User(Base):
    __tablename__ = "users"  
    id: Mapped[int] = db.mapped_column(primary_key=True)  
    name: Mapped[str] = db.mapped_column(db.String(100), nullable=False)  
    address: Mapped[str] = db.mapped_column(db.String(200))  
    email: Mapped[str] = db.mapped_column(db.String(100), unique=True, nullable=False)
     
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")  

class Order(Base):
    __tablename__ = "orders" 
    id: Mapped[int] = db.mapped_column(primary_key=True)
    order_date: Mapped[datetime] = db.mapped_column(db.DateTime, default=datetime.now(timezone.utc))
    user_id: Mapped[int] = db.mapped_column(ForeignKey("users.id"), nullable=False) 

    user: Mapped["User"] = relationship("User", back_populates="orders") 
    products: Mapped[List["Product"]] = relationship("Product", secondary=order_product, back_populates="orders")  

class Product(Base):
    __tablename__ = "products"  
    id: Mapped[int] = db.mapped_column(primary_key=True)  
    product_name: Mapped[str] = db.mapped_column(db.String(100), nullable=False)  
    price: Mapped[float] = db.mapped_column(db.Float, nullable=False) 

    orders: Mapped[List["Order"]] = relationship("Order", secondary=order_product, back_populates="products")  

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User  

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order  

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product  

# Create instances for single and multiple records
user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# CRUD Endpoints
# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.jsonify(users), 200  # Return as JSON

# Get a user by ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)  # Fetch the user by ID
    if not user:
        return jsonify({"message": "User not found"}), 404  # Error if not found
    return user_schema.jsonify(user), 200  # Return as JSON

# Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json) 
    except ValidationError as e:
        return jsonify(e.messages), 400 

    new_user = User(name=user_data['name'], address=user_data['address'], email=user_data['email'])
    db.session.add(new_user) 
    db.session.commit()  
    return user_schema.jsonify(new_user), 201 

# Update a user
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': 'Invalid user id'}), 400

    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Update user fields
    user.name = user_data['name']
    user.address = user_data['address']
    user.email = user_data['email']
    db.session.commit()  
    return user_schema.jsonify(user), 200  

# Delete a user
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': 'Invalid user id'}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'Successfully deleted user {id}'}), 200

# Get all products
@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products), 200  

# Get product by id
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    return product_schema.jsonify(product), 200  

# Create a product
@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_product = Product(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)  
    db.session.commit()  
    return product_schema.jsonify(new_product), 201  

# Update a product
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({'message': 'Invalid product id'}), 400

    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.product_name = product_data['product_name']
    product.price = product_data['price']
    db.session.commit()  
    return product_schema.jsonify(product), 200  

# Delete a product
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({'message': 'Invalid product id'}), 400

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': f'Successfully deleted product {id}'}), 200

# Create an order
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Order(order_date=order_schema['order_date'], user_id=order_schema['user_id'])
    db.session.add(new_order)
    db.session.commit()

    return order_schema.jsonify(new_order), 201

# Add a product to an order
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['GET'])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if not order or not product:
        return jsonify({"message": "Order or Product not found"}), 404
    
    if product in order.products:
        return jsonify({"message": "Product already in order"}), 400
    
    order.products.appenct(product)
    db.session.commit()
    return jsonify({"message": f"Product {product.product_name} added to order {order.id}"}), 200

# Remove a product from an order
@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def remove_product_from_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if not order or not product:
        return jsonify({"message": "Order or Product not found"}), 404

    if product not in order.products:
        return jsonify({"message": "Product not in order"}), 400

    order.products.remove(product)
    db.session.commit() 
    return jsonify({"message": f"Product {product.product_name} removed from order {order.id}"}), 200

# Get all orders for a user
@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return orders_schema.jsonify(user.orders), 200

# Get all products for an order
@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_order_products(order_id):
    order = db.session.get(Order, order_id)

    if not order: 
        return jsonify({'message': 'Order not found'}), 404
    
    return products_schema.jsonify(order.products), 200

# Main Function
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)