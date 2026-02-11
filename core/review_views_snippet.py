
from django.db.models import Avg

def add_review(request, daycare_id):
    daycare = get_object_or_404(Daycare, id=daycare_id)
    if request.method == 'POST':
        parent = request.user.profile.parent
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        
        # Check if review already exists
        existing_review = DaycareReview.objects.filter(daycare=daycare, parent=parent).first()
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, "Review updated successfully!")
        else:
            DaycareReview.objects.create(
                daycare=daycare,
                parent=parent,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Review submitted successfully!")
            
        return redirect('my_children')
        
    return render(request, 'add_review.html', {'daycare': daycare})

def daycare_reviews(request, daycare_id):
    daycare = get_object_or_404(Daycare, id=daycare_id)
    reviews = DaycareReview.objects.filter(daycare=daycare).order_by('-created_on')
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'daycare': daycare,
        'reviews': reviews,
        'average_rating': average_rating
    }
    return render(request, 'daycare_reviews.html', context)
