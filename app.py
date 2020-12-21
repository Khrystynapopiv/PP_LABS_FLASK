from flask import Flask, request, jsonify, abort
from schemas import *
from wtforms import ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
session = Session()
bcrypt = Bcrypt(app)


@app.route('/product', methods=['POST'])
def create_product():
    if len(session.query(Product).all()) > 7:
        return jsonify({'message': 'Too much products were add!'})
    data = request.get_json()
    new_product = Product(product_id=data["product_id"], name=data["name"], product_number=data["product_number"],
                          status=data["status"])
    session.add(new_product)
    session.commit()
    return jsonify({'message': 'New product added!'})


@app.route('/product/<product_id>', methods=['PUT'])
def update_product(product_id):
    product = session.query(Product).filter_by(product_id=product_id).first()
    if product is None:
        raise ValidationError(message="Invalid ID supplied")
    data = request.get_json()

    product.name = data['name'] if 'name' in data else product.name
    product.product_number = data['product_number'] if 'product_number' in data else product.product_number
    product.status = data['status'] if 'status' in data else product.status

    session.commit()
    product_schema = ProductSchema()
    result = product_schema.dump(product)
    return result


@app.route('/product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = session.query(Product).filter_by(product_id=product_id).first()
    if product is None:
        return jsonify({'message': "Invalid ID supplied"})
    session.delete(product)
    session.commit()
    return jsonify({'message': 'Product is deleted!'})


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    orders = []
    if 'order_id' in data:
        for i in data['order_id']:
            orders.append(session.query(Order).filter_by(order_id=i).first())
    new_user = User(uid=data['uid'], username=data['username'], first_name=data['first_name'],
                    last_name=data['last_name'], email=data['email'], orders=orders,
                    password=bcrypt.generate_password_hash(data['password']).decode('utf-8'))
    session.add(new_user)
    session.commit()
    return jsonify({'message': 'New user created!'})


@app.route('/user/<uid>', methods=['GET'])
def get_user(uid):
    user = session.query(User).filter(User.uid == uid).one_or_none()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    user_schema = UserSchema()
    result = user_schema.dump(user)
    return result


@app.route('/user/<uid>', methods=['PUT'])
def update_user(uid):
    user = session.query(User).filter_by(uid=uid).first()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    data = request.get_json()

    user.first_name = data['first_name'] if 'first_name' in data else user.first_name
    user.last_name = data['last_name'] if 'last_name' in data else user.last_name
    user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8') if 'password' in data else user.password
    user.email = data['email'] if 'email' in data else user.email

    session.commit()
    user_schema = UserSchema()
    result = user_schema.dump(user)
    return result


@app.route('/user/<uid>', methods=['DELETE'])
def delete_user(uid):
    user = session.query(User).filter_by(uid=uid).first()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    session.delete(user)
    session.commit()
    return jsonify({'message': 'User is deleted!'})


@app.route('/store/order', methods=['POST'])
def create_order():
    data = request.get_json()
    products = []
    for i in data['products']:
        product = session.query(Product).filter_by(product_id=i).first()
        if product.product_number <= 0:
            return jsonify({'message': "Product with id {} isn`t available!".format(i)})
        products.append(product)
        product.product_number -= 1

    new_order = Order(order_id=data['order_id'], status=data['status'], products=products)

    user = session.query(User).filter_by(uid=data['uid']).first()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    user.orders.append(new_order)

    session.add(new_order)
    session.commit()
    return jsonify({'message': 'New order created!'})


@app.route('/store/order/<order_id>', methods=['GET'])
def get_order(order_id):
    order = session.query(Order).filter_by(order_id=order_id).first()
    if order is None:
        return jsonify({'message': "Order is not found", "code": 404}), 404
    order_schema = OrderSchema()
    result = order_schema.dump(order)
    return result


@app.route('/store/order/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = session.query(Order).filter_by(order_id=order_id).first()
    if order is None:
        return jsonify({'message': "Order is not found", "code": 404}), 404
    session.delete(order)
    session.commit()
    return jsonify({'message': 'Order is deleted!'})


if __name__ == '__main__':
    app.run()
