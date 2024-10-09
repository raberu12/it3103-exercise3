# IT 3103 - EXERCISE 3: MICROSERVICES API
## Written by:
- Matt Vincent E. Magdadaro
- Julz Kaupper O. Cortes
## API STRUCTURE:
1. **Product Service**
    - *POST* `/products`: Add a new product.
    - *GET* `/products/`:productId: Get product details by ID.
    - *PUT* `/products/`:productId: Update a product.
    - *DELETE* `/products/`:productId: Delete a product.
2. **Customer Service**
    - *POST* `/customers`: Add a new customer.
    - *GET* `/customers/`:customerId: Get customer details by ID.
    - *PUT* `/customers/`:customerId: Update customer information.
    - *DELETE* `/customers/`:customerId: Delete a customer.
3. **Order Service**
    - *POST* `/orders`: Create a new order. This service will:
        - *Verify*  that the customer exists by communicating with the Customer Service.
        - *Verify* that the product exists by communicating with the Product Service.
        - *Create* the order only if the customer and product are valid.
    - *GET* `/orders/:orderId`: Get order details.
    - *PUT* `/orders/:orderId`: Update an order.
    - *DELETE* `/orders/:orderId`: Delete an order.
## TECHNOLOGIES USED AND INSTALLATION
- [Python](https://www.python.org/downloads/)
- **Django**:
- **Django Rest Framework**:
- **Requests**
- **Django Cors Headers**
- **Django Rest Framework Simple JWT**
- **Django SSLify**
```
pip install django
pip install djangorestframework
pip install requests
pip install django-cors-headers
pip install djangorestframework-simplejwt
pip install django-sslify
```
## RUNNING THE SERVICES
1. Navigate to the correct directories; for example:
```
cd user
cd it3103-3
cd order_service
```
2. Run the runserver command for each of the services with the specific **PORTS IN THEIR SPECIFIC DIRECTORIES**:
- `python manage.py runserver 3001` for **product_service**
- `python manage.py runserver 3002` for **customer_service**
- `python manage.py runserver 3003` for **order_service**
3. Open up 3 separate ***localhost:PORT*** in your preferred browser.

## Example request for POST on ORDERS:
```
{
    "id": order_id,
    "customer_id": customer_id,
    "product_id": product_id,
    "quantity": quantity
}
```


