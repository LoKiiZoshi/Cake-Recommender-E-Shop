from .cart import Cart

def cart(request):
    cart = Cart(request)
    total_items = sum(item['quantity'] for item in cart)
    return {'cart': cart, 'total_items': total_items}   