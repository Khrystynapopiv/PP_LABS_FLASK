import enum

from sqlalchemy import create_engine, Integer, Column, String, ForeignKey, Enum
from sqlalchemy import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import TINYTEXT
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import backref


engine = create_engine
engine = create_engine('postgresql+psycopg2://victoriapp:victoriapp@localhost/dbpp')
Base = declarative_base()
Session = sessionmaker(bind=engine)


users_orders = Table("users_orders",
                       Base.metadata,
                       Column("uid", Integer(), ForeignKey("users.uid")),
                       Column("order_id", Integer(), ForeignKey("orders.order_id")))

order_products = Table("order_products",
                       Base.metadata,
                       Column("order_id", Integer(), ForeignKey("orders.order_id")),
                       Column("product_id", Integer(), ForeignKey("products.product_id")))

class product_status(enum.Enum):
    AVAILABLE ="available"
    PENDING = "pending"
    SOLD = "sold"

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key = True)
    name = Column(String)
    product_number = Column(Integer)
    status = Column(Enum(product_status))

class order_status(enum.Enum):
    PLACED = 'placed'
    APPROVED = 'approved'
    DELIVERED = 'delivered'

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key = True)
    products = relationship(Product, secondary=order_products, lazy="subquery",
                            backref=backref("Product", lazy=True))
    status = Column(Enum(order_status))

class User(Base):
    __tablename__ = "users"

    uid = Column(Integer, primary_key = True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    email = Column(String)
    orders = relationship(Order, secondary=users_orders, lazy="subquery",
                            backref=backref("Order", lazy=True))
