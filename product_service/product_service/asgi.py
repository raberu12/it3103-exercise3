"""
ASGI config for product_service project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

<<<<<<< HEAD
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_service.settings')
=======
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "product_service.settings")
>>>>>>> 18dbb88a9362a033dc4c676fef71847f9aab5159

application = get_asgi_application()
