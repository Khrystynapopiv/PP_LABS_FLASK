from flask import json
import pytest
from .app import app

def get_admin_auth_token(client):
    req = client.post('/users/login', data=json.dumps({"username" : "admin", "password" : "admin"}),
                        content_type = 'application/json').get_json()
    token = req['access_token']
    return token


def get_customer_auth_token(client):
    req = client.post('/users/login', data=json.dumps({"username" : "test1", "password" : "test"}),
                        content_type = 'application/json').get_json()
    token = req['access_token']
    return token


def create_users(client):
    client.post('/user', data=json.dumps({"username" : "admin", "first_name" : "admin", "last_name" : "1", 
                "password" : "admin", "email" : "admin@gmail", "id" : "1"}),
                content_type='application/json')

    client.post('/user', data=json.dumps({"username" : "test1", "first_name" : "test", "last_name" : "1", 
                "password" : "test", "email" : "test1@gmail", "id" : "2"}),
                content_type='application/json')

    client.post('/user', data=json.dumps({"username" : "test2", "first_name" : "test", "last_name" : "2", 
                "password" : "test", "email" : "test2@gmail", "id" : "3"}),
                content_type='application/json')


@pytest.fixture
def client():
    client = app.test_client()
    create_users(client)
    return client
    
def test_post_products(client):
    customer_token = get_customer_auth_token(client)
    response2 = client.post('/product', data=json.dumps({"product_id" : "2", "name" : "laptop", "product_number" : "2",
                            "status" : "available"}), content_type='application/json',
                            headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response2 == 401

    admin_token = get_admin_auth_token(client)
    response1 = client.post('/product', data=json.dumps({"product_id" : "1", "name" : "adapter", "product_number" : "5",
                            "status" : "available"}), content_type='application/json',
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response1 == 200


def test_post_more_products(client):
    admin_token = get_admin_auth_token(client)
    response = client.post('/product', data=json.dumps({"product_id" : "2", "name" : "laptop", "product_number" : "0",
                            "status" : "sold"}), content_type='application/json',
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    response = client.post('/product', data=json.dumps({"product_id" : "3", "name" : "headphones", "product_number" : "5",
                            "status" : "available"}), content_type='application/json',
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    response = client.post('/product', data=json.dumps({"product_id" : "4", "name" : "iphone", "product_number" : "0",
                            "status" : "pending"}), content_type='application/json',
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    response = client.post('/product', data=json.dumps({"product_id" : "5", "name" : "smartphone", "product_number" : "10",
                            "status" : "available"}), content_type='application/json',
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    response = client.post('/product', data=json.dumps({"product_id" : "6", "name" : "smart watch", "product_number" : "6",
                            "status" : "available"}), content_type='application/json',
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    response = client.post('/product', data=json.dumps({"product_id" : "7", "name" : "graphic panel", "product_number" : "5",
                            "status" : "available"}), content_type='application/json',
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    response = client.post('/product', data=json.dumps({"product_id" : "8", "name" : "pen", "product_number" : "4",
                            "status" : "available"}), content_type='application/json',
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response == 400


def test_post_order(client):
    customer_token = get_customer_auth_token(client)
    response1 = client.post('/store/order/2', data=json.dumps({"order_id" : "1", "status" : "placed", 
                            "products" : ["1"]}), content_type='application/json',
                            headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response1 == 200
    admin_token = get_admin_auth_token(client)
    response2 = client.post('/store/order/2', data=json.dumps({"order_id" : "2", "status" : "placed", 
                            "products" : ["1"]}), content_type='application/json',
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response2 == 403
    response3 = client.post('/store/order/2', data=json.dumps({"order_id" : "1", "status" : "placed", 
                            "products" : ["4"]}), content_type='application/json',
                            headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response3 == 400
    response4 = client.post('/store/order/10', data=json.dumps({"order_id" : "1", "status" : "placed", 
                            "products" : ["4"]}), content_type='application/json',
                            headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response4 == 404


def test_get_order_by_id(client):
    customer_token = get_customer_auth_token(client)
    admin_token = get_admin_auth_token(client)
    response1 = client.get('/store/order/1', headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response1 == 200
    response2 = client.get('/store/order/1', headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response2 == 403
    response3 = client.get('/store/order/5', headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response3 == 404

def test_delete_order(client):
    admin_token = get_admin_auth_token(client)
    customer_token = get_customer_auth_token(client)    
    response1 = client.delete('/store/order/1', 
                headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response1 == 403
    response2 = client.delete('/store/order/2', 
                headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response2 == 404
    response3 = client.delete('/store/order/1', 
                headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response3 == 200


def test_put_product(client):
    admin_token = get_admin_auth_token(client)
    product_id1 = 2
    response1 = client.put(f'/product/{product_id1}', data=json.dumps(
                            {"product_id" : "2","product_number" : "11", }), 
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response1 == 500

    product_id2 = 10
    response2 = client.put(f'/product/{product_id2}', data=json.dumps(
                            {"product_id" : "10", "name" : "adapter", "product_number" : "10", 
                            "status" : "available"}), headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response2 == 404

    customer_token = get_customer_auth_token(client)
    product_id3 = 1
    response3 = client.put(f'/product/{product_id3}', data=json.dumps(
                            {"product_id" : "1", "name" : "adapter", "product_number" : "10", 
                            "status" : "available"}), headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response3 == 401


def test_delete_product(client):
    admin_token = get_admin_auth_token(client)
    customer_token = get_customer_auth_token(client)    
    response1 = client.delete(f'/product/10', 
                headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response1 == 404
    response2 = client.delete(f'/product/2', 
                headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response2 == 401
    response3 = client.delete(f'/product/2', 
                headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response3 == 200

def test_put_user(client):
    admin_token = get_admin_auth_token(client)
    customer_token = get_customer_auth_token(client)
    response1 = client.put('/user/1', data=json.dumps(
                            {"last_name" : "adddmin"}), 
                            headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response1 == 403
    response2 = client.put('/user/10', data=json.dumps(
                            {"last_name" : "adddmin"}), 
                            headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response2 == 404
    response3 = client.put('/user/1', data=json.dumps(
                            {"last_name" : "adddmin"}), 
                            headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response3 == 500

def test_delete_user(client):
    admin_token = get_admin_auth_token(client)
    customer_token = get_customer_auth_token(client)  
    response1 = client.delete(f'/user/2', 
                headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response1 == 200
    response2 = client.delete(f'/user/10', 
                headers={'Authorization': f'JWT {admin_token}'}).status_code
    assert response2 == 404
    response3 = client.delete(f'/user/1', 
                headers={'Authorization': f'JWT {customer_token}'}).status_code
    assert response3 == 401


def test_get_user_info(client):
    data1 = {'username' : 'admin'}
    username = data1['username']
    response1 = client.get(f'/user/{username}').status_code
    assert response1 == 200
    data2 = {'username' : 'admin9'}
    username = data2['username']
    response2 = client.get(f'/user/{username}').status_code
    assert response2 == 404


def test_post_user(client):
    response1 = client.post(f'/user', content_type='application/json', 
                            data=json.dumps({"username" : "test101", "first_name" : "test", "last_name" : "1", 
                            "password" : "test", "email" : "test1@gmail", "id" : "101"})).status_code

    assert response1 == 200
    response2 = client.post(f'/user', content_type='application/json', 
                            data=json.dumps({"username" : "test1", "first_name" : "test", "last_name" : "2", 
                            "password" : "test", "email" : "test2@gmail", "id" : "102"})).status_code
    assert response2 == 400


def test_get_product(client):
    response1 = client.get('/store/inventory/3').status_code
    assert response1 == 200
    response2 = client.get('/store/inventory/100').status_code
    assert response2 == 404