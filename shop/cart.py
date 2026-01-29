from decimal import Decimal
from django.conf import settings
from .models import Product



class Cart:
    def __init__(self, request):
        """Initialize the cart."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # Debug: Log cart contents on initialization
        print(f"Cart contents: {self.cart}")
        
        

    def add(self, product, quantity=1, override_quantity=False):
        """Add a product to the cart or update its quantity."""
        # Validate that product has a valid integer ID
        try:
            product_id = str(int(product.id))  # Ensure ID is numeric
        except (ValueError, AttributeError):
            print(f"Invalid product ID: {product.id if hasattr(product, 'id') else product}")
            return  # Skip adding invalid product

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()



    def save(self):
        # Mark the session as "modified" to make sure it gets saved
        self.session.modified = True



    def remove(self, product):
        """Remove a product from the cart."""
        try:
            product_id = str(int(product.id))  # Validate ID
            if product_id in self.cart:
                del self.cart[product_id]
                self.save()
        except (ValueError, AttributeError):
            print(f"Invalid product ID for removal: {product.id if hasattr(product, 'id') else product}")



    def __iter__(self):
        """Iterate over the items in the cart and get the products from the database."""
        product_ids = self.cart.keys()
        # Filter out non-integer product IDs
        valid_product_ids = []
        for pid in product_ids:
            try:
                valid_product_ids.append(int(pid))
            except ValueError:
                print(f"Invalid product ID in cart: {pid}")  # Log invalid IDs
                continue

        # Get the product objects and add them to the cart
        products = Product.objects.filter(id__in=valid_product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            if 'product' in item:  # Only yield items with valid products
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        """Count all items in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()