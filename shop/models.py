from django.db import models 
from django.contrib.auth.models import User 
from django.urls import reverse
from django.utils import timezone
from django.utils import timezone
import uuid



class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100,unique=True)
    description = models.TextField(blank=True)
    
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        
    def __str__(self):
        return self.name
    
    
    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',args=[self.slug])
    
    