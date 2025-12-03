import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from .models import Product,UserProductInteraction

def get_recommendations(user, method = 'hybrid', product = None,limit = 5):
   """  
   Get product recommendations based on specified method 
   
   Args: 
   
   user : User object
   method : 'collaborative','content','hybrid','clustering',or 'clean'
   product : Product object (for content-based recommendations)
   limit: number of recommendations to return
   
   Returns:
   List of recommended Product objects
    
   """
   
        
        return collab_recs
    
    