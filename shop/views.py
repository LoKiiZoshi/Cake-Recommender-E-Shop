from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime
import uuid
import hmac
import hashlib
import base64
import json
import logging
import requests

from .models import Category, Product, Order, OrderItem, UserProductInteraction, EsewaPayment
from .forms import OrderCreateForm
from .recommendation import get_recommendations
from .cart import Cart




# Configure logging for debugging
logger = logging.getLogger(__name__)





# eSewa API settings - Testing credentials
ESEWA_MERCHANT_ID = "EPAYTEST"
ESEWA_SECRET_KEY = "8gBm/:&EnhH.1/q"
ESEWA_API_URL = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
ESEWA_STATUS_URL = "https://rc-epay.esewa.com.np/api/epay/main/v2/status"




def generate_esewa_signature(data, secret_key):
    """
    Generate HMAC-SHA256 signature for eSewa payment based on signed_field_names.
    """
    
    signed_field_names = data.get('signed_field_names', 'total_amount,transaction_uuid,product_code')
    fields = signed_field_names.split(',')
    message = ','.join(f"{field}={data.get(field, '')}" for field in fields)
    logger.debug(f"Signature message: {message}")
    
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    logger.debug(f"Generated signature: {signature_b64}")
    return signature_b64





def verify_esewa_transaction(transaction_uuid, total_amount, product_code):
    """
    Verify transaction status with eSewa's API.
    """
    
    
    url = f"{ESEWA_STATUS_URL}?product_code={product_code}&total_amount={total_amount}&transaction_uuid={transaction_uuid}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Transaction status response: {data}")
            return data.get('status') == 'COMPLETE'
        logger.error(f"Transaction status check failed: {response.status_code} - {response.text}")
        return False
    except requests.RequestException as e:
        logger.error(f"Transaction status check error: {str(e)}")
        return False






def home(request): 
    products = Product.objects.filter(available=True)[:16]
    categories = Category.objects.all()  # Get all categories

    recommended_products = []
    clean_recommended_products = []
    if request.user.is_authenticated:
        recommended_products = get_recommendations(request.user, 'collaborative', limit=4)
        clean_recommended_products = get_recommendations(request.user, 'clean', limit=4)
        
    return render(request, 'shop/home.html', {
        'products': products,
        'categories': categories,  # Pass to template
        'recommended_products': recommended_products,
        'clean_recommended_products': clean_recommended_products
    })
 
    
    
    
    
    

def product_list(request, category_slug=None):   
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })
    
    
    
    
    
    

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    
    if request.user.is_authenticated:
        UserProductInteraction.objects.create(
            user=request.user,
            product=product,
            interaction_type='view'
        )
    
    similar_products = get_recommendations(request.user, 'content', product=product, limit=4)
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'similar_products': similar_products
    })






@login_required
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product, quantity=quantity)
    
    if request.user.is_authenticated:
        UserProductInteraction.objects.create(
            user=request.user,
            product=product,
            interaction_type='cart'
        )
    
    return redirect('shop:cart_detail')





def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('shop:cart_detail')




def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})





@login_required
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Your cart is empty. Please add some products before checkout.")
        return redirect('shop:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            payment_method = request.POST.get('payment_method', 'cod')
            payment_status = 'pending'
            
            order.payment_method = payment_method
            order.payment_status = payment_status
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
                
                if request.user.is_authenticated:
                    UserProductInteraction.objects.create(
                        user=request.user,
                        product=item['product'],
                        interaction_type='purchase'
                    )
            
            if payment_method == 'esewa':
                return redirect('shop:esewa_payment', order_id=order.id)
            
            cart.clear()
            
            return render(request, 'shop/order_created.html', {'order': order})
    else:
        form = OrderCreateForm()
    
    return render(request, 'shop/checkout.html', {'cart': cart, 'form': form})








@login_required
def esewa_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    amount = "{:.2f}".format(float(order.get_total_cost()))
    tax_amount = "{:.2f}".format(float(order.get_total_cost()) * 0.13)
    service_charge = "0.00"
    delivery_charge = "0.00"
    total_amount = "{:.2f}".format(float(amount) + float(tax_amount) + float(service_charge) + float(delivery_charge))
    
    transaction_uuid = str(uuid.uuid4())
    
    success_url = request.build_absolute_uri(reverse('shop:esewa_success'))
    failure_url = request.build_absolute_uri(reverse('shop:esewa_failure'))
    
    # Prepare data for signature
    signature_data = {
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': ESEWA_MERCHANT_ID,
        'signed_field_names': 'total_amount,transaction_uuid,product_code'
    }
    signature = generate_esewa_signature(signature_data, ESEWA_SECRET_KEY)
    
    try:
        esewa_payment = EsewaPayment.objects.get(order=order)
        esewa_payment.amount = amount
        esewa_payment.tax_amount = tax_amount
        esewa_payment.service_charge = service_charge
        esewa_payment.delivery_charge = delivery_charge
        esewa_payment.total_amount = total_amount
        esewa_payment.transaction_uuid = transaction_uuid
        esewa_payment.product_code = ESEWA_MERCHANT_ID
        esewa_payment.signature = signature
        esewa_payment.save()
    except EsewaPayment.DoesNotExist:
        esewa_payment = EsewaPayment.objects.create(
            order=order,
            amount=amount,
            tax_amount=tax_amount,
            service_charge=service_charge,
            delivery_charge=delivery_charge,
            total_amount=total_amount,
            transaction_uuid=transaction_uuid,
            product_code=ESEWA_MERCHANT_ID,
            signature=signature
        )
    
    context = {
        'order': order,
        'esewa_api_url': ESEWA_API_URL,
        'amount': amount,
        'tax_amount': tax_amount,
        'service_charge': service_charge,
        'delivery_charge': delivery_charge,
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': ESEWA_MERCHANT_ID,
        'success_url': success_url,
        'failure_url': failure_url,
        'signature': signature,
        'signed_field_names': "total_amount,transaction_uuid,product_code"
    }
    
    return render(request, 'shop/esewa_payment.html', context)







@csrf_exempt
def esewa_success(request):
    if request.method == 'GET':
        data = request.GET.get('data')
        if data:
            try:
                decoded_data = base64.b64decode(data).decode('utf-8')
                transaction_data = json.loads(decoded_data)
                logger.debug(f"Received transaction data: {transaction_data}")
                
                transaction_uuid = transaction_data.get('transaction_uuid')
                if not transaction_uuid:
                    logger.error("Missing transaction_uuid in response")
                    messages.error(request, "Invalid payment response: Missing transaction UUID.")
                    return redirect('shop:esewa_failure')
                
                payment = get_object_or_404(EsewaPayment, transaction_uuid=transaction_uuid)
                order = payment.order
                
                # Format total_amount to match eSewa's response
                total_amount = transaction_data.get('total_amount').replace(',', '')
                if '.' not in total_amount:
                    total_amount = f"{total_amount}.0"
                
                # Prepare data for signature verification
                signature_data = {
                    'transaction_code': transaction_data.get('transaction_code', ''),
                    'status': transaction_data.get('status', ''),
                    'total_amount': total_amount,
                    'transaction_uuid': transaction_uuid,
                    'product_code': transaction_data.get('product_code', ''),
                    'signed_field_names': transaction_data.get('signed_field_names', 'total_amount,transaction_uuid,product_code')
                }
                
                # Log received signature for debugging
                received_signature = transaction_data.get('signature')
                logger.debug(f"Received signature: {received_signature}")
                
                # Regenerate signature for verification
                expected_signature = generate_esewa_signature(signature_data, ESEWA_SECRET_KEY)
                logger.debug(f"Expected signature: {expected_signature}")
                
                if received_signature != expected_signature:
                    logger.error(f"Signature mismatch. Received: {received_signature}, Expected: {expected_signature}")
                    messages.error(request, "Invalid signature in payment response.")
                    return redirect('shop:esewa_failure')
                
                
                
                payment.status = 'completed'
                payment.save()
                order.payment_status = 'completed'
                order.paid = True
                order.status = 'processing'
                order.payment_date = timezone.now()
                order.transaction_id = transaction_uuid
                order.save()
                
                cart = Cart(request)
                cart.clear()
                
                messages.success(request, "Your payment was successful! Your order is being processed.")
                return redirect('shop:order_history')
            except (base64.binascii.Error, json.JSONDecodeError, ValueError) as e:
                logger.error(f"Payment verification failed: Invalid data format - {str(e)}")
                messages.error(request, "Payment verification failed: Invalid data format.")
                return redirect('shop:esewa_failure')
            except Exception as e:
                logger.error(f"Payment verification failed: {str(e)}")
                messages.error(request, f"Payment verification failed: {str(e)}")
                return redirect('shop:esewa_failure')
        else:
            logger.error("No payment data received")
            messages.error(request, "No payment data received.")
            return redirect('shop:esewa_failure')
    
    return HttpResponse(status=400)







@csrf_exempt
def esewa_failure(request):  
    if request.method == 'GET':
        messages.error(request, "Your payment was not successful. Please try again or choose a different payment method.")
        return redirect('shop:checkout')
    
    return HttpResponse(status=400)  



@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'shop/order_history.html', {'orders': orders})



@login_required
def order_detail(request, order_id): 
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})





def shop_list(request):
    """Enhanced shop list view with working filters, search, and sorting"""
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    # Get filter parameters from GET request
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', '')
    price_range = request.GET.get('price', '5000')
    
    # Apply category filter
    if category_slug and category_slug != 'all':
        try:
            category = Category.objects.get(slug=category_slug)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            category = None
    else:
        category = None

    # Apply search filter
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(flavor_profile__icontains=search_query)
        )

    # Apply price range filter
    try:
        max_price = float(price_range)
        products = products.filter(price__lte=max_price)
    except ValueError:
        logger.warning(f"Invalid price range value: {price_range}")

    # Apply sorting
    if sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'name-desc':
        products = products.order_by('-name')
    elif sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == 'price-desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    else:
        products = products.order_by('name')  # Default sorting

    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # AJAX request for filtering
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_data = []
        for product in page_obj:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image_url': product.image.url if product.image else '/static/images/placeholder.jpg',
                'description': product.description[:60] + '...' if len(product.description) > 60 else product.description,
                'url': product.get_absolute_url(),
                'category': product.category.name if product.category else '',
            })
        
        return JsonResponse({
            'products': products_data,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })

    context = {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'result_count': paginator.count,
        'search_query': search_query,
        'sort_by': sort_by,
        'price_range': price_range,
        'page_obj': page_obj,
    }

    return render(request, 'shop/shop.html', context)

def quick_view(request, product_id):
    """AJAX view for quick product preview"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            product = get_object_or_404(Product, id=product_id, available=True)
            
            # Track view interaction  
            if request.user.is_authenticated:
                UserProductInteraction.objects.create(
                    user=request.user,
                    product=product,
                    interaction_type='view'
                )
            
            data = {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'description': product.description,
                'image_url': product.image.url if product.image else '/static/images/placeholder.jpg',
                'category': product.category.name if product.category else '',
                'url': product.get_absolute_url(),
                'ingredients': product.ingredients,
                'flavor_profile': product.flavor_profile,
                'occasion': product.occasion,
            }
            
            return JsonResponse({'success': True, 'product': data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})






def categories_view(request):
    """Enhanced categories view with search and statistics"""
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'name')
    
    # Get all categories with product counts and statistics
    categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__available=True)),
        total_orders=Count('products__order_items'),
        avg_price=Avg('products__price', filter=Q(products__available=True))
    ).filter(product_count__gt=0)  # Only show categories with products
    
    # Apply search filter
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply sorting
    if sort_by == 'name':
        categories = categories.order_by('name')
    elif sort_by == 'products':
        categories = categories.order_by('-product_count')
    elif sort_by == 'popular':
        categories = categories.order_by('-total_orders')
    elif sort_by == 'price':
        categories = categories.order_by('avg_price')
    else:
        categories = categories.order_by('name')
    
    # Get popular categories (top 3 by orders)
    popular_categories = Category.objects.annotate(
        total_orders=Count('products__order_items')
    ).order_by('-total_orders')[:3]
    
    # Get category statistics
    total_categories = categories.count()
    total_products = Product.objects.filter(available=True).count()
    
    # AJAX request for search
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'product_count': category.product_count,
                'avg_price': float(category.avg_price) if category.avg_price else 0,
                'url': category.get_absolute_url(),
            })
        
        return JsonResponse({
            'categories': categories_data,
            'total_count': len(categories_data),
        })
    
    context = {
        'categories': categories,
        'popular_categories': popular_categories,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_categories': total_categories,
        'total_products': total_products,
    }
    
    return render(request, 'shop/categories.html', context)



def about_view(request):
    """
    Display about us page
    """
    return render(request, 'shop/about.html')






def contact_view(request):
    """
    Display contact us page and handle form submissions
    """
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        newsletter = request.POST.get('newsletter') == 'on'

        # Basic validation
        errors = []
        if not first_name:
            errors.append('First name is required')
        if not last_name:
            errors.append('Last name is required')
        if not email:
            errors.append('Email is required')
        if not subject:
            errors.append('Subject is required')
        if not message:
            errors.append('Message is required')

        if errors:
            # Preserve form data for re-rendering
            context = {
                'form_data': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'subject': subject,
                    'message': message,
                    'newsletter': newsletter,
                }
            }
            for error in errors:
                messages.error(request, error)
            return render(request, 'shop/contact.html', context)

        try:
            # Send email to admin
            admin_subject = f"New Contact Form Submission: {subject}"
            admin_message = f"""
New contact form submission received:

Name: {first_name} {last_name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Subject: {subject}
Newsletter Subscription: {'Yes' if newsletter else 'No'}

Message:
{message}

Submitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """

            send_mail(
                subject=admin_subject,
                message=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )

            # Send confirmation email to user
            user_subject = "Thank you for contacting Smart Cake Shop!"
            user_message = f"""
Dear {first_name} {last_name},

Thank you for reaching out to Smart Cake Shop! We have received your message and will get back to you within 24 hours.

Your message details:
Subject: {subject}
Message: {message}

If you have any urgent inquiries, please call us at +977 1-234-5678.

Best regards,
Smart Cake Shop Team
            """

            send_mail(
                subject=user_subject,
                message=user_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            # Handle newsletter subscription if checked
            if newsletter:
                # Add newsletter subscription logic here (e.g., save to a model or external service)
                pass

            messages.success(request, 'Thank you for your message! We\'ll get back to you within 24 hours.')
            return redirect('shop:contact')  # Redirect to prevent form resubmission

        except Exception as e:
            messages.error(request, 'Sorry, there was an error sending your message. Please try again or contact us directly.')
            print(f"Email sending error: {e}")  # Log the error for debugging

    return render(request, 'shop/contact.html')

@require_http_methods(["POST"])
def contact_ajax_view(request):
    """
    Handle AJAX contact form submissions
    """
    try:
        # Get form data from POST (not expecting JSON)
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        newsletter = request.POST.get('newsletter') == 'on'

        # Validation
        if not all([first_name, last_name, email, subject, message]):
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields.'
            }, status=400)

        # Send email to admin
        admin_subject = f"New Contact Form Submission: {subject}"
        admin_message = f"""
New contact form submission received:

Name: {first_name} {last_name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Subject: {subject}
Newsletter Subscription: {'Yes' if newsletter else 'No'}

Message:
{message}

Submitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        send_mail(
            subject=admin_subject,
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL, 
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )

        # Send confirmation to user
        user_subject = "Thank you for contacting Smart Cake Shop!"
        user_message = f"""
Dear {first_name} {last_name},

Thank you for reaching out to Smart Cake Shop! We have received your message and will get back to you within 24 hours.

Your message details:
Subject: {subject}
Message: {message}

If you have any urgent inquiries, please call us at +977 1-234-5678.

Best regards,
Smart Cake Shop Team
        """

        send_mail(
            subject=user_subject,
            message=user_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        # Handle newsletter subscription if checked
        if newsletter:
            # Add newsletter subscription logic here
            pass

        return JsonResponse({
            'success': True,
            'message': 'Thank you for your message! We\'ll get back to you within 24 hours.'
        })

    except Exception as e:
        print(f"Email sending error: {e}")  # Log the error for debugging
        return JsonResponse({
            'success': False,
            'message': 'Sorry, there was an error sending your message. Please try again.'
        }, status=500)
 


