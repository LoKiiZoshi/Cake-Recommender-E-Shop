from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from shop.models import Product, Category, Order, OrderItem, EsewaPayment
from accounts.models import UserProfile
from .forms import ProductForm, CategoryForm
from django.contrib.auth.models import User

@login_required
def dashboard(request):
    # Check if user is admin
    try:
        if not request.user.profile.is_admin:
            messages.error(request, "You don't have permission to access the admin dashboard.")
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    # Dashboard statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.count()
    total_customers = User.objects.filter(profile__is_admin=False).count()
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created')[:5]
    
    # Top selling products
    top_products = OrderItem.objects.values('product__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    # Pending eSewa payments
    # Temporary fix until migrations are applied
    try:
        # Try the original query
        pending_esewa_payments = Order.objects.filter(
            payment_method='esewa', 
            payment_status='completed',
            status='pending'
        ).count()
    except Exception:
        # If it fails, set to 0
        pending_esewa_payments = 0
    
    return render(request, 'admin_dashboard/dashboard.html', {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'pending_esewa_payments': pending_esewa_payments
    })

@login_required
def product_list(request):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    products = Product.objects.all()
    return render(request, 'admin_dashboard/products.html', {'products': products})

@login_required
def product_create(request):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('admin_dashboard:products')
    else:
        form = ProductForm()
    
    return render(request, 'admin_dashboard/product_form.html', {'form': form})

@login_required
def product_edit(request, pk):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('admin_dashboard:products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'admin_dashboard/product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('admin_dashboard:products')
    
    return render(request, 'admin_dashboard/product_confirm_delete.html', {'product': product})

@login_required
def category_list(request):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    categories = Category.objects.all()
    return render(request, 'admin_dashboard/categories.html', {'categories': categories})

@login_required
def category_create(request):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('admin_dashboard:categories')
    else:
        form = CategoryForm()
    
    return render(request, 'admin_dashboard/category_form.html', {'form': form})

@login_required
def category_edit(request, pk):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('admin_dashboard:categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'admin_dashboard/category_form.html', {'form': form})

@login_required
def category_delete(request, pk):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('admin_dashboard:categories')
    
    return render(request, 'admin_dashboard/category_confirm_delete.html', {'category': category})

@login_required
def order_list(request):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    orders = Order.objects.all().order_by('-created')
    return render(request, 'admin_dashboard/orders.html', {'orders': orders})

@login_required
def order_detail(request, pk):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    order = get_object_or_404(Order, pk=pk)
    
    # Check if this order has an eSewa payment
    esewa_payment = None
    try:
        esewa_payment = order.esewa_payment
    except:
        pass
    
    return render(request, 'admin_dashboard/order_detail.html', {
        'order': order,
        'esewa_payment': esewa_payment
    })

@login_required
def order_status_update(request, pk):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES).keys():
            order.status = status
            order.save()
            messages.success(request, f'Order status updated to {status}.')
        else:
            messages.error(request, 'Invalid status.')
        
        return redirect('admin_dashboard:order_detail', pk=pk)
    
    return redirect('admin_dashboard:orders')

@login_required
def customer_list(request):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    customers = User.objects.filter(profile__is_admin=False)
    return render(request, 'admin_dashboard/customers.html', {'customers': customers})

@login_required
def customer_detail(request, pk):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    customer = get_object_or_404(User, pk=pk)
    orders = Order.objects.filter(user=customer).order_by('-created')
    
    return render(request, 'admin_dashboard/customer_detail.html', {
        'customer': customer,
        'orders': orders
    })

@login_required
def esewa_payments(request):
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    # Get all eSewa payments
    payments = Order.objects.filter(payment_method='esewa').order_by('-created')
    
    return render(request, 'admin_dashboard/esewa_payments.html', {
        'payments': payments
    })

@login_required
def process_esewa_payment(request, pk):  
    # Check if user is admin
    if not request.user.profile.is_admin:
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('home')
    
    order = get_object_or_404(Order, pk=pk, payment_method='esewa')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            # Update order status
            if order.payment_status == 'completed':
                order.status = 'processing'
                order.save()
                messages.success(request, f'Order #{order.order_ref} has been approved and is now being processed.')
            else:
                messages.warning(request, f'Order #{order.order_ref} cannot be approved because payment is not completed.')
        
        elif action == 'reject':
            # Cancel the order
            order.status = 'cancelled'
            order.save()
            messages.warning(request, f'Order #{order.order_ref} has been rejected.')
        
        return redirect('admin_dashboard:esewa_payments')
    
    return render(request, 'admin_dashboard/process_payment.html', {
        'order': order
    })
