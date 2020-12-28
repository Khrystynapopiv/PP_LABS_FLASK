from flask import Flask, request, jsonify, abort

from PP_LABS_FLASK.schemas import *
from PP_LABS_FLASK.models import *
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
import os, sys
from flask_jwt import JWT, jwt_required, current_identity

parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(parent_dir)
sys.path.append(".")

app = Flask(__name__)
session = Session()
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = '06Oh72gc65dF4WIZzi8oOSIob9LRFegYbgYXs2GdBdOIylIEMS'
app.config['JWT_AUTH_URL_RULE'] = '/users/login'

def authenticate(username, password):
    user = session.query(User).filter(User.username == username).first()
    if user is None:
        return

    check_password = bcrypt.check_password_hash(user.password, password)
    if not check_password:
        return

    return user

def identity(payload):
    user_id = payload['identity']
    return session.query(User).filter(User.id == user_id).one_or_none()

JWT = JWT(app, authenticate, identity)


@app.route('/product', methods=['POST'])
@jwt_required()
def create_product():
    admin = UserSchema().dump(current_identity)
    if admin['username'] != 'admin' : return("This method not allowed")
    else:
        if len(session.query(Product).all()) > 7:
            return jsonify({'message': 'Too much products were add!'})
        data = request.get_json()
        new_product = Product(product_id=data["product_id"], name=data["name"], product_number=data["product_number"],
                              status=data["status"])
        session.add(new_product)
        session.commit()
        return jsonify({'message': 'New product added!'})



@app.route('/product/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    admin = UserSchema().dump(current_identity)
    if admin['username'] != 'admin':
        return ("This method not allowed")
    else:
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
@jwt_required()
def delete_product(product_id):
    admin = UserSchema().dump(current_identity)
    if admin['username'] != 'admin':
        return ("This method not allowed")
    else:
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
    new_user = User(id=data['id'], username=data['username'], first_name=data['first_name'],
                    last_name=data['last_name'], email=data['email'], orders=orders,
                    password=bcrypt.generate_password_hash(data['password']).decode('utf-8'))
    schema = UserSchema()
    if not session.query(User).filter(User.username == data['username']).first() is None:
        return "This username already exists"
    session.add(new_user)
    session.commit()
    return jsonify({'message': 'New user created!'})


@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    user = session.query(User).filter(User.username == username).one_or_none()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    user_schema = UserSchema()
    result = user_schema.dump(user)
    return result


@app.route('/user/<uid>', methods=['PUT'])
@jwt_required()
def update_user(uid):

    user = session.query(User).filter_by(id=uid).first()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    if user.id != current_identity.id:
        return 'It is not your acount', 403

    data = request.get_json()

    user.first_name = data['first_name'] if 'first_name' in data else user.first_name
    user.last_name = data['last_name'] if 'last_name' in data else user.last_name
    user.password = bcrypt.generate_password_hash(data['password']).decode(
        'utf-8') if 'password' in data else user.password
    user.email = data['email'] if 'email' in data else user.email

    session.commit()
    user_schema = UserSchema()
    result = user_schema.dump(user)
    return result


@app.route('/user/<uid>', methods=['DELETE'])
@jwt_required()
def delete_user(uid):
    user = session.query(User).filter_by(id=uid).first()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    if user.id != current_identity.id:
        return 'It is not your acount', 403
    session.delete(user)
    session.commit()
    return jsonify({'message': 'User is deleted!'})


@app.route('/store/order/<id>', methods=['POST'])
@jwt_required()
def create_order(id):
    data = request.get_json()
    user = session.query(User).filter_by(id=id).first()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404

    if user.id != current_identity.id:
        return 'It is not your acount', 403

    products = []
    new_order = Order(order_id=data['order_id'], status=data['status'], products=products)

    for i in data['products']:
        product = session.query(Product).filter_by(product_id=i).first()

        if product.product_number <= 0:
            return jsonify({'message': "Product with id {} isn`t available!".format(i)})
        products.append(product)
        product.product_number -= 1
        new_order.products.append(product)

    user.orders.append(new_order)
    session.add(new_order)
    session.commit()
    return jsonify({'message': 'New order created!'})


@app.route('/store/order/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    order2 = session.query(users_orders).filter_by(order_id=order_id).first()
    if order2.id != current_identity.id: return 'It is not your order', 403
    order = session.query(Order).filter_by(order_id=order_id).first()

    if order is None:
        return jsonify({'message': "Order is not found", "code": 404}), 404
    order_schema = OrderSchema()
    result = order_schema.dump(order)
    return result


@app.route('/store/order/<order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    order2 = session.query(users_orders).filter_by(order_id=order_id).first()
    if order2.id != current_identity.id :return 'It is not your order', 403
    order = session.query(Order).filter_by(order_id=order_id).first()
    if order is None:
        return jsonify({'message': "Order is not found", "code": 404}), 404
    session.delete(order)
    session.commit()
    return jsonify({'message': 'Order is deleted!'})


@app.route('/store/inventory/<product_id>', methods=['GET'])
def get_product(product_id):
    product = session.query(Product).filter_by(product_id=product_id).first()

    if product is None:
        return jsonify({'message': "product is not found", "code": 404}), 404
    product_schema = ProductSchema()
    result = product_schema.dump(product)
    return result

if __name__ == '__main__':
    app.run()

# DB
# psql -h localhost -d postgres -U postgres -p 5433 -a -q -f create_tables.sql

# USER
# curl -X POST http://127.0.0.1:5000/user -H "Content-Type: application/json" --data "{\"username\" : \"kh\", \"first_name\" : \"Khrystyna\", \"last_name\" : \"P\", \"password\" : \"qwerty\", \"email\" : \"kh@gmail\", \"id\" : \"4\"}"
# curl -X PUT http://127.0.0.1:5000/user/4 -H "Content-Type: application/json" -H "Authorization: JWT " --data "{\"last_name\" : \"Popiv\"}"
# curl -X DELETE http://127.0.0.1:5000/user/4 -H "Content-Type: application/json" -H "Authorization: JWT
# curl -X GET http://127.0.0.1:5000/user/4


# LOG
#  curl -X POST http://127.0.0.1:5000/users/login -H "Content-Type:application/json" --data "{\"username\" : \"kh\",  \"password\" : \"qwerty\"}

# PRODUCT
# curl -X POST http://127.0.0.1:5000/product -H "Content-Type: application/json" -H "Authorization: JWT" --data "{\"product_id\" : \"2\", \"name\" : \"adapter\", \"product_number\" : \"60\", \"status\" : \"available\"}"
# curl -X DELETE http://127.0.0.1:5000/product/2 -H "Content-Type: application/json" -H "Authorization: JWT"
# curl -X PUT http://127.0.0.1:5000/product/2 -H "Content-Type: application/json" -H "Authorization: JWT" --data "{\"product_number\" : \"46\"}"

# ORDER
# curl -X POST http://127.0.0.1:5000/store/order/2 -H "Content-Type: application/json" -H "Authorization: JWT"  --data "{\"order_id\" : \"1\", \"status\" : \"placed\", \"products\" : [\"1\"]}"
# curl -X GET http://127.0.0.1:5000/store/order/1 -H "Content-Type: application/json" -H "Authorization: JWT"