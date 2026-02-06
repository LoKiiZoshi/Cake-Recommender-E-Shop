from django import forms
from shop.models import Product, Category
from django.utils.text import slugify

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'image', 'description', 'price', 'available', 
                  'ingredients', 'flavor_profile', 'occasion']
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if not self.instance.pk:  # Only for new products
            # Check if a product with this slug already exists
            slug = slugify(name)
            if Product.objects.filter(slug=slug).exists():
                raise forms.ValidationError('A product with this name already exists.')
        return name
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if not self.instance.pk:  # Only for new categories
            # Check if a category with this slug already exists
            slug = slugify(name)
            if Category.objects.filter(slug=slug).exists():
                raise forms.ValidationError('A category with this name already exists.')
        return name
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance
