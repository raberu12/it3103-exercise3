# IT 3103 - EXERCISE 3: MICROSERVICES API
## API STRUCTURE:
1. **API Gateway**
    - *GET* `/products`: Get all products.
    - *GET* `/users`: Get all users.
    - *GET* `/orders`: Get all orders.
2. **Product Service**
    - *POST* `/products`: Add a new product.
    - *GET* `/products/`:productId: Get product details by ID.
    - *PUT* `/products/`:productId: Update a product.
    - *DELETE* `/products/`:productId: Delete a product.
3. **Customer Service**
    - *POST* `/users`: Add a new user.
    - *GET* `/users/`:userId: Get user details by ID.
    - *PUT* `/users/`:userId: Update user information.
    - *DELETE* `/users/`:userId: Delete a user.
4. **Order Service**
    - *POST* `/orders`: Create a new order. This service will:
        - *Verify*  that the user exists by communicating with the Customer Service.
        - *Verify* that the product exists by communicating with the Product Service.
        - *Create* the order only if the user and product are valid.
    - *GET* `/orders/:orderId`: Get order details.
    - *PUT* `/orders/:orderId`: Update an order.
    - *DELETE* `/orders/:orderId`: Delete an order.
## TECHNOLOGIES USED AND INSTALLATION
- [Python](https://www.python.org/downloads/)
- **Django**
- **Django Rest Framework**
- **Requests**
- **Django Cors Headers**
- **Django Rest Framework Simple JWT**
- **Django SSL Server**
```
pip install django
pip install djangorestframework
pip install requests
pip install django-cors-headers
pip install djangorestframework-simplejwt
pip install django-sslserver
```
## RUNNING THE SERVICES
1. Navigate to the correct directories; for example:
```
cd user
cd it3103-3
cd order_service
```
2. Run the API Gateway as an SSL Server to route to HTTPS instead of HTTP:
```
cd api_gateway
python manage.py runsslserver 127.0.0.1:8000
```
3. Run the runserver command for each of the services with the specific **PORTS IN THEIR SPECIFIC DIRECTORIES**:
- `python manage.py runserver 3001` for **product_service**
- `python manage.py runserver 3002` for **user_service**
- `python manage.py runserver 3003` for **order_service**
4. Open up 3 separate ***localhost:PORT*** in your preferred browser.

## Example request for POST on ORDERS:
```
{
    "id": order_id,
    "user_id": user_id,
    "product_id": product_id,
    "quantity": quantity
}
```
## Written by:
- Matt Vincent E. Magdadaro
- Julz Kaupper O. Cortes


