from django.utils import timezone  # ✅ Django's timezone
from pyexpat.errors import messages
import uuid
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import requests

from core.utils import generate_ai_suggestion
from core.forms import ActivityReportForm
from .models import Child, ChildEnrollmentRequest, DaycareRequest, DaycareReview, Milestone, Notification, Profile, Daycare, Parent ,ActivityReport, ChildMilestone, GeminiSuggestion, ChatMessage
from .utils import calculate_age_in_months
from django.db.models import Q
def home_view(request):
    return render(request,'home.html')


# ----------------------------------------------
# REGISTER
# ----------------------------------------------
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists.'})

        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user, role=role)
        return redirect('login')

    return render(request, 'register.html')


# ----------------------------------------------
# LOGIN
# ----------------------------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            role = user.profile.role
            if role == 'admin':
                return redirect('admin_dashboard')
            elif role == 'daycare':
                return redirect('daycare_dashboard')
            elif role == 'parent':
                return redirect('parent_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


# ----------------------------------------------
# LOGOUT
# ----------------------------------------------
def logout_view(request):
    logout(request)
    return redirect('login')


# ----------------------------------------------
# DASHBOARDS
# ----------------------------------------------
@login_required


@login_required
def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.profile.role != 'admin':
        return redirect('login')

    pending_daycares = Daycare.objects.filter(verified=False)
    verified_daycares = Daycare.objects.filter(verified=True)
    parents = Parent.objects.all()
    children = Child.objects.select_related('parent', 'daycare').all()
    


    return render(request, 'admin_dashboard.html', {
        'pending_daycares': pending_daycares,
        'verified_daycares': verified_daycares,
        'parents': parents,
        'children': children
    })




@login_required
def approve_daycare(request, daycare_id):
    if request.user.profile.role != 'admin':
        return redirect('login')

    daycare = get_object_or_404(Daycare, id=daycare_id)
    daycare.verified = True
    daycare.save()
    return redirect('admin_dashboard')


@login_required
def reject_daycare(request, daycare_id):
    if request.user.profile.role != 'admin':
        return redirect('login')

    daycare = get_object_or_404(Daycare, id=daycare_id)
    daycare.delete()
    return redirect('admin_dashboard')

@login_required




@login_required
def daycare_dashboard(request):
    profile = request.user.profile
    if profile.role != 'daycare':
        return redirect('home')

    # Get daycare linked to this profile
    try:
        daycare = profile.daycare
    except Daycare.DoesNotExist:
        return redirect('daycare_complete_profile')  # First login

    # If daycare is not verified, show pending verification page
    if not daycare.verified:
        return render(request, 'daycare_pending_verification.html', {'daycare': daycare})

    # Fetch stats for verified daycare
    children = Child.objects.filter(daycare=daycare)
    enrolled_count = children.count()
    pending_requests = ChildEnrollmentRequest.objects.filter(daycare=daycare, status="pending").count()
    notifications = Notification.objects.filter(
        recipient=daycare.profile.user
    ).order_by('-created_on')

    today = timezone.localdate()
    todays_activities = ActivityReport.objects.filter(child__in=children, date=today).count()
    total_reports = ActivityReport.objects.filter(child__in=children).count()

    # Optional: fetch daily thought
    import requests
    try:
        response = requests.get("https://zenquotes.io/api/today")
        if response.status_code == 200:
            data = response.json()
            thought = f"{data[0]['q']} — {data[0]['a']}"
        else:
            thought = "Have a wonderful day! 🌞"
    except Exception:
        thought = "Have a wonderful day! 🌞"

    context = {
        'daycare': daycare,
        'enrolled_count': enrolled_count,
        'pending_requests': pending_requests,
        'todays_activities': todays_activities,
        'total_reports': total_reports,
        'thought': thought,
        'children': children,
        'notifications': notifications
    }
    return render(request, 'daycare_dashboard.html', context)

    

from django.shortcuts import redirect

def redirect_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    profile = request.user.profile
    if profile.role == 'admin':
        return redirect('admin_dashboard')
    elif profile.role == 'daycare':
        return redirect('daycare_dashboard')
    elif profile.role == 'parent':
        return redirect('parent_dashboard')
    else:
        return redirect('home')


@login_required
def parent_dashboard(request):
    profile = request.user.profile
    if profile.role != 'parent':
        return redirect('home')

    try:
        parent = profile.parent
    except Parent.DoesNotExist:
        return redirect('parent_complete_profile')

    children = Child.objects.filter(parent=parent)
    children_count = children.count()  # My Family

    enrolled_count = children.filter(daycare__verified=True).count()  # Children actually enrolled in verified daycares

    # Today's activities for all children of this parent
    today = timezone.localdate()
    todays_activities = ActivityReport.objects.filter(child__in=children, date=today).count()
    notifications = Notification.objects.filter(
        recipient=parent.profile.user
    ).order_by('-created_on')
    context = {
        'parent': parent,
        'children_count': children_count,
        'enrolled_count': enrolled_count,
        'todays_activities': todays_activities,
        'notifications':notifications
    }

    return render(request, 'parent_dashboard.html', context)


# ----------------------------------------------
# COMPLETE PROFILE FORMS
# ----------------------------------------------
@login_required
def daycare_complete_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        contact = request.POST['contact']
        doc = request.FILES['document']
        Daycare.objects.create(profile=profile, name=name, address=address, contact_number=contact, license_document=doc)
        return redirect('daycare_dashboard')
    
    return render(request, 'daycare_complete_profile.html')


@login_required
def parent_complete_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        mother = request.POST['mother']
        father = request.POST['father']
        phone = request.POST['phone']
        email = request.POST['email']
        Parent.objects.create(profile=profile, mother_name=mother, father_name=father, phone=phone,email=email)
        return redirect('parent_dashboard')
    return render(request, 'parent_complete_profile.html')

@login_required
def ban_daycare(request, daycare_id):
    if request.user.profile.role != 'admin':
        return redirect('login')

    daycare = get_object_or_404(Daycare, id=daycare_id)
    
    # Delete all children of this daycare
    Child.objects.filter(daycare=daycare).delete()
    
    # Delete the daycare profile (Profile + User if needed)
    daycare_profile = daycare.profile
    user = daycare_profile.user
    daycare.delete()
    daycare_profile.delete()
    user.delete()
    
    return redirect('admin_dashboard')


# Ban/Remove a parent
@login_required
def ban_parent(request, parent_id):
    if request.user.profile.role != 'admin':
        return redirect('login')

    parent = get_object_or_404(Parent, id=parent_id)
    
    # Delete all children of this parent
    Child.objects.filter(parent=parent).delete()
    
    # Delete parent profile + user
    parent_profile = parent.profile
    user = parent_profile.user
    parent.delete()
    parent_profile.delete()
    user.delete()
    
    return redirect('admin_dashboard')



def my_children(request):
    parent = request.user.profile.parent
    children = Child.objects.filter(parent=parent)
    
    # Optionally, gather reports and milestones for each child
    child_data = []
    for child in children:
        reports = ActivityReport.objects.filter(child=child).order_by('-date')
        milestones = ChildMilestone.objects.filter(child=child)
        suggestions = GeminiSuggestion.objects.filter(child=child).order_by('-created_on')
        child_data.append({
            'child': child,
            'reports': reports,
            'milestones': milestones,
            'suggestions': suggestions,
        })
    
    return render(request, 'my_child.html', {'child_data': child_data})

@login_required
def daycares_list(request):
    # Only show verified daycares
    daycares = Daycare.objects.filter(verified=True)

    # Search functionality
    query = request.GET.get('q')
    if query:
        daycares = daycares.filter(name__icontains=query)

    context = {
        'daycares': daycares,
    }
    return render(request, 'daycares.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Daycare, Parent, ChildEnrollmentRequest

@login_required
def enroll_child(request, daycare_id):
    daycare = get_object_or_404(Daycare, id=daycare_id)
    parent = request.user.profile.parent  # Get Parent object linked to this user

    if request.method == 'POST':
        child_name = request.POST.get('child_name')
        date_of_birth = request.POST.get('date_of_birth')
        birth_certificate = request.FILES.get('birth_certificate')
        medical_history = request.POST.get('medical_history', '')

        # Create enrollment request
        ChildEnrollmentRequest.objects.create(
            parent=parent,
            daycare=daycare,
            child_name=child_name,
            date_of_birth=date_of_birth,
            birth_certificate=birth_certificate,
            medical_history=medical_history,
        )

        # ✅ Use Django’s messages framework
        messages.success(request, f"Enrollment request for {child_name} sent to {daycare.name}!")
        return redirect('parent_dashboard')

    context = {
        'daycare': daycare
    }
    return render(request, 'enroll_child.html', context)

def enrollment_requests(request):
    # Only show requests for the daycare that is logged in
    daycare = getattr(request.user.profile, "daycare", None)
    if not daycare:
        return redirect("daycare_dashboard")

    pending_requests = ChildEnrollmentRequest.objects.filter(
        daycare=daycare, status="pending"
    ).order_by("-id")
    approved_requests = ChildEnrollmentRequest.objects.filter(
        daycare=daycare, status="approved"
    ).order_by("-id")

    return render(request, "enrollment_requests.html", {
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
    })


def approve_request(request, pk):
    req = get_object_or_404(ChildEnrollmentRequest, pk=pk)
    req.status = 'approved'
    req.save()

    # Create the Child entry only if it doesn't already exist
    if not Child.objects.filter(child_name=req.child_name, parent=req.parent).exists():
        Child.objects.create(
            daycare=req.daycare,
            parent=req.parent,
            child_name=req.child_name,
            date_of_birth=req.date_of_birth,
            birth_certificate=req.birth_certificate,
            medical_history=req.medical_history,
            unique_id = f"CHILD-{uuid.uuid4().hex[:8].upper()}"  # You can replace this with UUID if you want
        )


    return redirect('enrollment_requests')


def reject_request(request, pk):
    req = get_object_or_404(ChildEnrollmentRequest, pk=pk)
    req.status = "rejected"
    req.save()
    return redirect("enrollment_requests")

@login_required
def add_activity_report(request):
    profile = request.user.profile

    # Only daycare staff can add reports
    if profile.role != 'daycare':
        return redirect('home')

    # Get children of this daycare
    children = Child.objects.filter(daycare__profile=profile)

    if request.method == 'POST':
        # Include request.FILES to handle image upload
        form = ActivityReportForm(request.POST, request.FILES)
        form.fields['child'].queryset = children  # Limit dropdown to daycare’s children

        if form.is_valid():
            form.save()
            return redirect('daycare_dashboard')
    else:
        form = ActivityReportForm()
        form.fields['child'].queryset = children

    return render(request, 'add_activity_report.html', {'form': form})

@login_required
def update_milestones(request):
    profile = request.user.profile
    if profile.role != 'daycare':
        return redirect('home')

    # Fetch all children of this daycare
    children = Child.objects.filter(daycare__profile=profile)
    selected_child = None
    milestones = []
    age_in_months = None  # initialize

    # Get child_id from POST (update) or GET (dropdown selection)
    child_id = request.POST.get('child_id') or request.GET.get('child_id')

    if child_id:
        selected_child = get_object_or_404(
            Child,
            id=child_id,
            daycare__profile=profile
        )

        # Fetch all existing ChildMilestone objects for this child
        milestones = ChildMilestone.objects.filter(child=selected_child)

        # Calculate age only if child is selected
        age_in_months = calculate_age_in_months(selected_child.date_of_birth)

    # Handle POST update
    if request.method == 'POST' and selected_child:
        for milestone in milestones:
            status = request.POST.get(f'status_{milestone.id}')
            if status:
                milestone.status = status
                milestone.save()
        return redirect('update_milestones')  # reload page

    return render(request, 'update_milestones.html', {
        'children': children,
        'selected_child': selected_child,
        'milestones': milestones,
        'age_in_months': age_in_months
    })



def delete_child(request, child_id):
    try:
        child = Child.objects.get(id=child_id)
        child_name = child.child_name
        child.delete()
        messages.success(request, f"Child '{child_name}' deleted successfully.")
    except Child.DoesNotExist:
        messages.error(request, "The selected child record no longer exists.")
    return redirect('admin_dashboard')

def generate_ai_suggestion_view(request, child_id):
    child = get_object_or_404(Child, id=child_id)
    suggestion = generate_ai_suggestion(child)
    messages.success(request, "AI suggestion generated successfully!")
    return render(request, 'ai_suggestion.html', {'child': child, 'suggestion': suggestion})

def enrolled_children(request):
    children = []

    try:
        # Get the profile for the logged-in user
        profile = request.user.profile
        if profile.role != 'daycare':
            # Not a daycare user
            return render(request, 'enrolled_children.html', {'children': []})

        # Get the daycare linked to this profile
        daycare = Daycare.objects.get(profile=profile)

        # Fetch all children enrolled in this daycare
        children = Child.objects.filter(daycare=daycare)

    except (Profile.DoesNotExist, Daycare.DoesNotExist):
        # Either the profile or daycare doesn't exist
        children = []
    # Search logic
    query = request.GET.get('q')
    if query:
        children = children.filter(child_name__icontains=query)

    return render(request, 'enrolled_children.html', {
        'children': children,
        'query': query or ''
    })

    # return render(request, 'enrolled_children.html', {'children': children})
from .models import GeminiSuggestion

def view_child(request, child_id):
    child = get_object_or_404(Child, id=child_id)

    # Activities
    activities = ActivityReport.objects.filter(child=child)

   
    # Milestones
    milestones = ChildMilestone.objects.filter(child=child).select_related('milestone')

    # AI Suggestions
    suggestions = GeminiSuggestion.objects.filter(child=child).order_by('-created_on')

    context = {
        'child': child,
        'activities': activities,
        'milestones': milestones,
        'suggestions': suggestions
    }
    return render(request, 'view_child.html', context)




@login_required
def chat_window(request):
    profile = request.user.profile
    user = request.user

    # Parent side
    if profile.role == 'parent':
        parent = profile.parent
        children = Child.objects.filter(parent=parent, daycare__verified=True)

        selected_daycare_id = request.GET.get('daycare_id') or request.POST.get('daycare_id')
        parent_user = parent.profile.user
        selected_daycare = None
        chat_partner_name = None
        messages = []

        # If a daycare is selected (by parent or via ?daycare_id=), show messages for that chat
        if selected_daycare_id:
            try:
                selected_daycare = Daycare.objects.get(id=selected_daycare_id)
                chat_partner_name = selected_daycare.name
                daycare_user = selected_daycare.profile.user

                # Handle sending a new message
                if request.method == 'POST' and request.POST.get('text'):
                    text = request.POST.get('text')
                    ChatMessage.objects.create(
                        sender=parent_user,
                        recipient=daycare_user,
                        message=text
                    )
                    return redirect(f"{request.path}?daycare_id={selected_daycare_id}")

                # Retrieve all chat messages between parent and daycare (both directions)
                chat_qs = ChatMessage.objects.filter(
                    (Q(sender=parent_user, recipient=daycare_user) |
                     Q(sender=daycare_user, recipient=parent_user))
                ).order_by('timestamp')

                messages = [
                    {
                        'sender': msg.sender,
                        'sender_name': msg.sender.username,
                        'text': msg.message,
                        'timestamp': msg.timestamp,
                        'image': getattr(msg, 'image', None),
                    }
                    for msg in chat_qs
                ]
            except Daycare.DoesNotExist:
                selected_daycare = None
                chat_partner_name = None
                messages = []
        
        context = {
            'selected_daycare_id': int(selected_daycare_id) if selected_daycare_id else None,
            'chat_partner_name': chat_partner_name,
            'messages': messages if len(messages) > 0 else [{'sender': 'None', 'sender_name': 'No messages yet', 'text': '', 'timestamp': '', 'image': None}],
            'user': user,
        }
        return render(request, 'chat_window.html', context)

    # Daycare side
    elif profile.role == 'daycare':
        daycare = profile.daycare
        children = Child.objects.filter(daycare=daycare)
        parent_set = set(child.parent for child in children)
        parent_list = list(parent_set)

        selected_parent_id = request.GET.get('parent_id') or request.POST.get('parent_id')
        daycare_user = daycare.profile.user
        selected_parent = None
        chat_partner_name = None
        messages = []

        # If a parent is selected (by daycare or via ?parent_id=), show messages for that chat
        if selected_parent_id:
            try:
                selected_parent = Parent.objects.get(id=selected_parent_id)
                chat_partner_name = f"{selected_parent.mother_name} & {selected_parent.father_name}"
                parent_user = selected_parent.profile.user

                if request.method == 'POST' and request.POST.get('text'):
                    text = request.POST.get('text')
                    ChatMessage.objects.create(
                        sender=daycare_user,
                        recipient=parent_user,
                        message=text
                    )
                    return redirect(f"{request.path}?parent_id={selected_parent_id}")

                chat_qs = ChatMessage.objects.filter(
                    (Q(sender=parent_user, recipient=daycare_user) |
                     Q(sender=daycare_user, recipient=parent_user))
                ).order_by('timestamp')

                messages = [
                    {
                        'sender': msg.sender,
                        'sender_name': msg.sender.username,
                        'text': msg.message,
                        'timestamp': msg.timestamp,
                        'image': getattr(msg, 'image', None),
                    }
                    for msg in chat_qs
                ]
            except Parent.DoesNotExist:
                selected_parent = None
                chat_partner_name = None
                messages = []
        else:
            # No parent selected: show chat previews for all parents
            for parent in parent_list:
                parent_user = parent.profile.user
                last_msg = ChatMessage.objects.filter(
                    (Q(sender=parent_user, recipient=daycare_user) |
                     Q(sender=daycare_user, recipient=parent_user))
                ).order_by('-timestamp').first()

        context = {
            'parent_list': parent_list,
            'selected_parent_id': int(selected_parent_id) if selected_parent_id else None,
            'chat_partner_name': chat_partner_name,
            'messages': messages,
            'user': user,
        }
        return render(request, 'chat_window.html', context)

    else:
        return redirect('home')

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