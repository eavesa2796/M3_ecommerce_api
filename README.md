Description--
A fully functional e-commerce API using Flask, Flask-SQLAlchemy, Flask-Marshmallow, and MySQL. The API will manage Users, Orders, and Products with proper relationships, including One-to-Many and Many-to-Many associations.

Learning Objectives--
Database Design: Create models with relationships in SQLAlchemy and MySQL.
API Development: Build a RESTful API with CRUD operations using Flask.
Serialization: Implement Marshmallow schemas for input validation and data serialization.
Testing: Use tools like Postman and MySQL Workbench to validate API functionality.

Relationships--
One-to-Many: A User can have multiple Orders.
Many-to-Many: An Order can include multiple Products, and a Product can belong to multiple Orders. (Implemented using an association table.)
