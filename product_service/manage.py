#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
<<<<<<< HEAD
=======

>>>>>>> 18dbb88a9362a033dc4c676fef71847f9aab5159
import os
import sys


def main():
    """Run administrative tasks."""
<<<<<<< HEAD
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_service.settings')
=======
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "product_service.settings")
>>>>>>> 18dbb88a9362a033dc4c676fef71847f9aab5159
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


<<<<<<< HEAD
if __name__ == '__main__':
=======
if __name__ == "__main__":
>>>>>>> 18dbb88a9362a033dc4c676fef71847f9aab5159
    main()
