from models import Session, User, Product, Order

session = Session()

product1 = Product(product_id = 1, name = 'phone', product_number =  26, status = 'AVAILABLE')
product2 = Product(product_id = 2, name = 'camera', product_number = 0, status = 'PENDING')
product3 = Product(product_id = 3, name = 'laptop', product_number = 0, status = 'SOLD')
product4 = Product(product_id = 4, name = 'headphone', product_number = 32, status = 'AVAILABLE')

session.add(product1)
session.add(product2)
session.add(product3)
session.add(product4)

order1 = Order(order_id = 1, products =[product1, product4], status = 'approved')
order2 = Order(order_id = 2, products =[product1, product4], status = 'delivered')
order3 = Order(order_id = 3, products =[product1, product4], status = 'delivered')

session.add(order1)
session.add(order2)
session.add(order3)

user1 = User(uid = 1, username = 'Victoria1', first_name = 'Victoria', last_name = 'H',
        password = 'qwerty', email = 'qwerty@gmail', orders = [order1, order2])
user2 = User(uid = 2, username = 'Victoria2', first_name = 'Victoria', last_name = 'H',
        password = 'asdfg', email = 'asdfg@gmail', orders = [order1, order3])
user3 = User(uid = 3, username = 'Victoria3', first_name = 'Victoria', last_name = 'H',
         password = 'zxcvb', email = 'zxcvb@gmail', orders = [order2, order3])


session.add(user1)
session.add(user2)
session.add(user3)


session.commit()
