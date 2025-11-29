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
   
   

    if method == 'collaborative':
        return collaborative_filtering(user, limit)
    elif method == 'content':
        return content_based_filtering(product, limit)
    elif method == 'clustering':
        return clustering_recommendations(user, limit)
    elif method == 'clean':
        return clean_recommendations(user, limit)
    else:  # hybrid (default)
        collab_recs = collaborative_filtering(user, limit)
        
        # If we have a specific product, get content-based recommendations too
        
        if product:
            content_recs = content_based_filtering(product, limit)
            
            # Combine and deduplicate recommendations
            
            hybrid_recs = list(collab_recs)
            for rec in content_recs:
                if rec not in hybrid_recs:
                    hybrid_recs.append(rec)
            return hybrid_recs[:limit]
        
        return collab_recs
    
    