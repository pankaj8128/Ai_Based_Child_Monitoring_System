from django.db import models
from django.contrib.auth.models import User

# ------------------------------------------------
# Extended User Roles
# ------------------------------------------------
class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('daycare', 'Daycare'),
        ('parent', 'Parent'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# ------------------------------------------------
# Daycare Details
# ------------------------------------------------
class Daycare(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    license_document = models.FileField(upload_to="daycare_docs/")
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# ------------------------------------------------
# Parent Details
# ------------------------------------------------
class Parent(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    mother_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.mother_name} & {self.father_name}"


# ------------------------------------------------
# Child Details
# ------------------------------------------------
class Child(models.Model):
    daycare = models.ForeignKey(Daycare, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    child_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    birth_certificate = models.FileField(upload_to="child_docs/")
    medical_history = models.TextField(blank=True)
    unique_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.child_name
class ActivityReport(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    activities_done = models.TextField()
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to="activity_images/", blank=True, null=True)

    def __str__(self):
        return f"Report - {self.child.child_name} ({self.date})"

class Milestone(models.Model):
    category = models.CharField(max_length=50)  # e.g., Motor Skills, Language
    description = models.TextField(blank=False, null=False)  # Ensure description is always present
    typical_age = models.CharField(max_length=20)  # e.g., "6-12 months"

    def __str__(self):
        return f"{self.category}: {self.description[:50]}"
class ChildMilestone(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
    ]

    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.child.child_name} - {self.milestone.category}"
    
class GeminiSuggestion(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    suggestion_text = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Suggestion for {self.child.child_name}"
class ChildEnrollmentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    daycare = models.ForeignKey(Daycare, on_delete=models.CASCADE)
    child_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    birth_certificate = models.FileField(upload_to="child_docs/")
    medical_history = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.child_name} - {self.daycare.name} ({self.status})"



class DaycareRequest(models.Model):
    child_name = models.CharField(max_length=100)
    parent_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )

    def __str__(self):
        return f"{self.child_name} - {self.status}"


# models.py
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} -> {self.recipient.username}"

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username} at {self.timestamp}"

class DaycareReview(models.Model):
    daycare = models.ForeignKey(Daycare, on_delete=models.CASCADE, related_name='reviews')
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} stars for {self.daycare.name} by {self.parent}"