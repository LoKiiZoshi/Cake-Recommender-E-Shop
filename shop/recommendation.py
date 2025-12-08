import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from .models import Product, UserProductInteraction 



def get_recommendations(user, method='hybrid', product=None, limit=5):
    
    """
    Get product recommendations based on specified method
    
    Args:
        user: User object
        method: 'collaborative', 'content', 'hybrid', 'clustering', or 'clean'
        product: Product object (for content-based recommendations)
        limit: Number of recommendations to return
        
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
    
    
    
    
    

def collaborative_filtering(user, limit=5):
    """User-based collaborative filtering"""
    # Get all user interactions
    interactions = UserProductInteraction.objects.all()
    
    
    # Create user-item matrix
    user_item_matrix = defaultdict(dict)
    
    
    # Weight different interaction types
    weights = {
        'view': 1,
        'cart': 3,
        'purchase': 5,
        'rating': 2  # Base weight, will be multiplied by rating value
    }
    
    
    
    
    
    
    # Fill the matrix with weighted interaction scores
    for interaction in interactions:
        score = weights[interaction.interaction_type]
        if interaction.interaction_type == 'rating' and interaction.rating:
            score *= interaction.rating
        
        if interaction.user.id in user_item_matrix:
            if interaction.product.id in user_item_matrix[interaction.user.id]:
                user_item_matrix[interaction.user.id][interaction.product.id] += score
            else:
                user_item_matrix[interaction.user.id][interaction.product.id] = score
        else:
            user_item_matrix[interaction.user.id] = {interaction.product.id: score}
    
    
    
    
    
    # Find similar users
    target_user_id = user.id
    if target_user_id not in user_item_matrix:
        # If user has no interactions, return popular products
        return get_popular_products(limit)
    
    user_similarities = {}
    target_user_items = user_item_matrix[target_user_id]
    
    for other_user_id, other_user_items in user_item_matrix.items():
        if other_user_id == target_user_id:
            continue
        
        # Calculate Jaccard similarity
        common_items = set(target_user_items.keys()) & set(other_user_items.keys())
        all_items = set(target_user_items.keys()) | set(other_user_items.keys())
        
        if not all_items:
            continue
            
        similarity = len(common_items) / len(all_items)
        user_similarities[other_user_id] = similarity
        
    
    
    
    # Get top similar users
    similar_users = sorted(user_similarities.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Get items from similar users that target user hasn't interacted with
    target_user_items_set = set(target_user_items.keys())
    candidate_items = {}
    
    for similar_user_id, similarity in similar_users:
        for item_id, score in user_item_matrix[similar_user_id].items():
            if item_id not in target_user_items_set:
                if item_id in candidate_items:
                    candidate_items[item_id] += score * similarity
                else:
                    candidate_items[item_id] = score * similarity
                    
     
     
                    
    
    # Get top recommended items
    recommended_items = sorted(candidate_items.items(), key=lambda x: x[1], reverse=True)[:limit]
    recommended_item_ids = [item_id for item_id, _ in recommended_items]
    
    # If we don't have enough recommendations, add popular products
    if len(recommended_item_ids) < limit:
        popular_products = get_popular_products(limit - len(recommended_item_ids))
        for product in popular_products:
            if product.id not in recommended_item_ids and product.id not in target_user_items_set:
                recommended_item_ids.append(product.id)
                if len(recommended_item_ids) >= limit:
                    break
                
    
    
                
    
    # Get product objects
    recommended_products = list(Product.objects.filter(id__in=recommended_item_ids, available=True))
    
    # Sort products in the same order as recommended_item_ids
    recommended_products.sort(key=lambda x: recommended_item_ids.index(x.id))
    
    return recommended_products
 







def content_based_filtering(product, limit=5):
    """Content-based filtering"""
    if not product:
        return get_popular_products(limit)
    
    # Get all products
    all_products = Product.objects.filter(available=True).exclude(id=product.id)
    
    
    
    # Create feature vectors
    
    
    # For simplicity, we'll use text similarity of ingredients, flavor_profile, and occasion
    
    
    target_features = f"{product.ingredients} {product.flavor_profile} {product.occasion} {product.category.name}"
    
    
    similarities = []
    for other_product in all_products:
        other_features = f"{other_product.ingredients} {other_product.flavor_profile} {other_product.occasion} {other_product.category.name}"
        
        # Calculate simple text similarity (Jaccard similarity)
        target_words = set(target_features.lower().split())
        other_words = set(other_features.lower().split())
        
        if not target_words or not other_words:
            similarity = 0
        else:
            intersection = len(target_words & other_words)
            union = len(target_words | other_words)
            similarity = intersection / union if union > 0 else 0
        
        similarities.append((other_product, similarity))
        
        
    
    # Sort by similarity and get top recommendations
    similarities.sort(key=lambda x: x[1], reverse=True)
    recommended_products = [p for p, _ in similarities[:limit]]
    
    return recommended_products





def clustering_recommendations(user, limit=5):
    """K-means clustering based recommendations"""
    # Get all products
    all_products = list(Product.objects.filter(available=True))
    
    
    
    if len(all_products) < 10:  # Not enough products for meaningful clustering
        return get_popular_products(limit)
    
    
    
    # Create feature vectors (simplified for demonstration)
    # In a real system, you'd use more sophisticated feature engineering
    
    features = []
    for product in all_products:
        # Extract numeric features
        
        price = float(product.price)
        
        # Create a simple feature vector
        # In a real system, you'd include more features and use techniques like one-hot encoding
        
        feature_vector = [price]
        features.append(feature_vector)
        
        
    
    # Convert to numpy array
    features = np.array(features)
    
    
    # Normalize features
    features_mean = np.mean(features, axis=0)
    features_std = np.std(features, axis=0)
    features_normalized = (features - features_mean) / features_std
    
    
    
    # Apply K-means clustering
    
    n_clusters = min(5, len(all_products) // 2)                    # Adjust number of clusters based on data size
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(features_normalized)
    
    
    
    # Find user's preferred cluster
    user_interactions = UserProductInteraction.objects.filter(user=user)
    
    if not user_interactions:
        return get_popular_products(limit)
    
    
    
    
    # Count interactions by cluster
    cluster_interactions = defaultdict(int)
    for interaction in user_interactions:
        try:
            product_index = next(i for i, p in enumerate(all_products) if p.id == interaction.product.id)
            product_cluster = clusters[product_index]
            
            # Weight by interaction type
            weight = 1
            if interaction.interaction_type == 'cart':
                weight = 3
            elif interaction.interaction_type == 'purchase':
                weight = 5
            elif interaction.interaction_type == 'rating' and interaction.rating:
                weight = interaction.rating
                
            cluster_interactions[product_cluster] += weight
        except StopIteration:
            continue
        
        
    
    # Find preferred cluster
    if not cluster_interactions:
        preferred_cluster = 0  # Default to first cluster
    else:
        preferred_cluster = max(cluster_interactions.items(), key=lambda x: x[1])[0]
        
        
    
    # Get products from preferred cluster that user hasn't interacted with
    user_product_ids = {interaction.product.id for interaction in user_interactions}
    recommended_products = []
    
    for i, product in enumerate(all_products):
        if clusters[i] == preferred_cluster and product.id not in user_product_ids:
            recommended_products.append(product)
            if len(recommended_products) >= limit:
                break
            
            
            
    
    # If we don't have enough recommendations, add products from other clusters
    if len(recommended_products) < limit:
        for product in all_products:
            if product not in recommended_products and product.id not in user_product_ids:
                recommended_products.append(product)
                if len(recommended_products) >= limit:
                    break
    
    return recommended_products[:limit]










def clean_recommendations(user, limit=5):
    
    
    """
    Clean Algorithm for recommendations
    
    This algorithm provides unbiased recommendations by:
    1. Removing outliers in user interaction data
    2. Normalizing user behavior data
    3. Addressing popularity bias
    4. Ensuring diversity in recommendations
    """
    
    
    # Get 
    # 
    # all user interactions
    interactions = UserProductInteraction.objects.all()
    
    # Get all products
    all_products = Product.objects.filter(available=True)
    
    if not interactions or not all_products:
        return get_popular_products(limit)
    
    
    
    
    
    
    # Step 1: Calculate interaction statistics for outlier detection
    product_interaction_counts = defaultdict(int)
    user_interaction_counts = defaultdict(int)
    
    for interaction in interactions:
        product_interaction_counts[interaction.product.id] += 1
        user_interaction_counts[interaction.user.id] += 1
        
        
        
        
         
    
    # Calculate mean and standard deviation for product interactions
    product_counts = list(product_interaction_counts.values())
    product_mean = sum(product_counts) / len(product_counts) if product_counts else 0
    product_std = (sum((x - product_mean) ** 2 for x in product_counts) / len(product_counts)) ** 0.5 if product_counts else 0
    
    
    # Identify outlier products (products with abnormally high interaction counts)
    outlier_threshold = product_mean + 2 * product_std
    outlier_products = {pid for pid, count in product_interaction_counts.items() if count > outlier_threshold}
    
    
    
    # Step 2: Create normalized user-item interaction matrix
    user_item_matrix = defaultdict(dict)
    
    # Weight different interaction types
    weights = {
        'view': 1,
        'cart': 3,
        'purchase': 5,
        'rating': 2  # Base weight, will be multiplied by rating value
    }
    
    
    
    
    # Fill the matrix with weighted interaction scores
    for interaction in interactions:
        # Skip outlier products for cleaner recommendations
        if interaction.product.id in outlier_products:
            continue
            
        score = weights[interaction.interaction_type]
        if interaction.interaction_type == 'rating' and interaction.rating:
            score *= interaction.rating
        
        if interaction.user.id in user_item_matrix:
            if interaction.product.id in user_item_matrix[interaction.user.id]:
                user_item_matrix[interaction.user.id][interaction.product.id] += score
            else:
                user_item_matrix[interaction.user.id][interaction.product.id] = score
        else:
            user_item_matrix[interaction.user.id] = {interaction.product.id: score}
            
            
            
    
    # Step 3: Normalize scores per user to address different user activity levels
    for user_id in user_item_matrix:
        user_scores = user_item_matrix[user_id]
        max_score = max(user_scores.values()) if user_scores else 1
        for product_id in user_scores:
            user_item_matrix[user_id][product_id] /= max_score
            
            
            
    
    # Step 4: Find similar users with normalized data
    target_user_id = user.id
    if target_user_id not in user_item_matrix:
        # If user has no interactions, return popular products
        return get_popular_products(limit)
    
    user_similarities = {}
    target_user_items = user_item_matrix[target_user_id]
    
    for other_user_id, other_user_items in user_item_matrix.items():
        if other_user_id == target_user_id:
            continue
        
        
        
        # Calculate cosine similarity
        common_items = set(target_user_items.keys()) & set(other_user_items.keys())
        if not common_items:
            continue
            
        numerator = sum(target_user_items[item] * other_user_items[item] for item in common_items)
        sum1 = sum(target_user_items[item] ** 2 for item in target_user_items)
        sum2 = sum(other_user_items[item] ** 2 for item in other_user_items)
        
        denominator = (sum1 ** 0.5) * (sum2 ** 0.5)
        
        if denominator == 0:
            continue
            
        similarity = numerator / denominator
        user_similarities[other_user_id] = similarity
        
        
        
    
    # Get top similar users
    similar_users = sorted(user_similarities.items(), key=lambda x: x[1], reverse=True)[:10]
    
    
    
    # Step 5: Get items from similar users that target user hasn't interacted with
    target_user_items_set = set(target_user_items.keys())
    candidate_items = {}
    
    for similar_user_id, similarity in similar_users:
        for item_id, score in user_item_matrix[similar_user_id].items():
            if item_id not in target_user_items_set:
                if item_id in candidate_items:
                    candidate_items[item_id] += score * similarity
                else:
                    candidate_items[item_id] = score * similarity
                    
                    
                    
    
    # Step 6: Apply diversity enhancement - ensure we don't just recommend from one category
    recommended_items = sorted(candidate_items.items(), key=lambda x: x[1], reverse=True)
    
    
    
    # Get product objects for the top recommendations
    top_product_ids = [item_id for item_id, _ in recommended_items[:limit*2]]  # Get more than needed for diversity
    top_products = list(Product.objects.filter(id__in=top_product_ids, available=True))
    
    
    
    # Group by category
    category_products = defaultdict(list)
    for product in top_products:
        category_products[product.category.id].append(product)
        
        
    
    # Select products ensuring category diversity
    diverse_products = []
    categories = list(category_products.keys())
    
    
    
    # Round-robin selection from different categories
    
    while len(diverse_products) < limit and categories:
        for category_id in categories[:]:
            if category_products[category_id]:
                diverse_products.append(category_products[category_id].pop(0))
                if len(diverse_products) >= limit:
                    break
            else:
                categories.remove(category_id)
                
                
                
    
    # If we still need more products, add from the top recommendations
    if len(diverse_products) < limit:
        remaining_products = [p for p in top_products if p not in diverse_products]
        diverse_products.extend(remaining_products[:limit-len(diverse_products)])
    
    return diverse_products[:limit]








def get_popular_products(limit=5):
    """Get popular products based on interaction count"""
    # Count interactions for each product
    product_interactions = defaultdict(int)
    
    for interaction in UserProductInteraction.objects.all():
        weight = 1
        if interaction.interaction_type == 'cart':
            weight = 3
        elif interaction.interaction_type == 'purchase':
            weight = 5
        elif interaction.interaction_type == 'rating' and interaction.rating:
            weight = interaction.rating
            
        product_interactions[interaction.product.id] += weight
    
    
    
    
    
    # Sort products by interaction count
    popular_product_ids = sorted(product_interactions.items(), key=lambda x: x[1], reverse=True)
    popular_product_ids = [p_id for p_id, _ in popular_product_ids]
    
    
    # Get product objects
    popular_products = list(Product.objects.filter(id__in=popular_product_ids, available=True)[:limit])
    
    
    # If we don't have enough popular products, add some recent ones
    if len(popular_products) < limit:
        recent_products = Product.objects.filter(available=True).order_by('-created')
        for product in recent_products:
            if product not in popular_products:
                popular_products.append(product)
                if len(popular_products) >= limit:
                    break
                
    
    return popular_products[:limit]
