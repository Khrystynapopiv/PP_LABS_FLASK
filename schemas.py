from marshmallow import Schema, fields, validate, post_load
from PP_LABS_FLASK.models import *


class ProductSchema(Schema):
    product_id = fields.Int()
    name = fields.Str()
    product_number = fields.Int()
    status = fields.Str(validate=validate.OneOf(["available", "pending", "sold"]))

    @post_load
    def create_product(self, data, **kwargs):
        return Product(**data)


class OrderSchema(Schema):
    order_id = fields.Int()
    status = fields.Str(validate=validate.OneOf(["placed", "approved", "delivered"]))
    products = fields.List(fields.Nested(ProductSchema(only=('product_id', ))))

    @post_load
    def create_order(self, data, **kwargs):
        return Order(**data)


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    password = fields.Str()
    orders = fields.List(fields.Nested(OrderSchema(only=('order_id', ))))

    @post_load
    def create_user(self, data, **kwargs):
        return User(**data)
