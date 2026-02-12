from django.utils.html import format_html

from django.contrib import admin
from .models import ActivityReport, ChatMessage, ChildEnrollmentRequest, ChildMilestone, DaycareRequest, DaycareReview, GeminiSuggestion, Milestone, Notification, Profile, Daycare, Parent, Child

# ------------------------------
# Profile Admin
# ------------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'role')


# ------------------------------
# Daycare Admin
# ------------------------------
@admin.register(Daycare)
class DaycareAdmin(admin.ModelAdmin):
    list_display = ('name', 'profile', 'contact_number', 'verified', 'license_document')
    list_filter = ('verified',)
    search_fields = ('name', 'profile__user__username', 'contact_number')
    readonly_fields = ('verified',)  # Only admin can change manually if needed


# ------------------------------
# Parent Admin
# ------------------------------
@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('mother_name', 'father_name', 'profile', 'email', 'phone')  # Added email
    search_fields = ('mother_name', 'father_name', 'profile__user__username', 'phone', 'email')


# ------------------------------
# Child Admin
# ------------------------------
@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('child_name', 'parent', 'daycare', 'date_of_birth', 'unique_id')
    search_fields = ('child_name', 'parent__profile__user__username', 'daycare__name', 'unique_id')
    list_filter = ('daycare',)

@admin.register(ActivityReport)
class ActivityReportAdmin(admin.ModelAdmin):
    list_display = ('child', 'date', 'activities_done', 'image_tag')
    list_filter = ('date',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;"/>', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Image'


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('category', 'description', 'typical_age')

@admin.register(ChildMilestone)
class ChildMilestoneAdmin(admin.ModelAdmin):
    list_display = ('child', 'milestone', 'status', 'updated_on')
    list_filter = ('status',)

@admin.register(GeminiSuggestion)
class GeminiSuggestionAdmin(admin.ModelAdmin):
    list_display = ('child', 'created_on', 'suggestion_text')

@admin.register(ChildEnrollmentRequest)    
class ChildEnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ('child_name', 'parent', 'daycare', 'status', 'applied_on')
    list_filter = ('status', 'daycare')  # Filter by status or daycare
    search_fields = ('child_name', 'parent__mother_name', 'parent__father_name', 'daycare__name')
    readonly_fields = ('applied_on',)  # Applied date should not be editable

@admin.register(DaycareRequest)
class DaycareRequestAdmin(admin.ModelAdmin):
    list_display = ('child_name', 'parent_name', 'contact', 'status')
    list_filter = ('status',)
    search_fields = ('child_name', 'parent_name')
    ordering = ('-id',)
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'created_on', 'is_read')
    list_filter = ('is_read', 'created_on')
    search_fields = ('title', 'recipient__username', 'message')
    readonly_fields = ('title', 'recipient', 'message', 'created_on')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp')
    search_fields = ('sender__username', 'recipient__username', 'message')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)

@admin.register(DaycareReview)
class DaycareReviewAdmin(admin.ModelAdmin):
    list_display = ("daycare", "parent", "rating", "created_on")
    list_filter = ("rating", "created_on", "daycare")
    search_fields = ("daycare__name", "parent__user__username", "comment")
    readonly_fields = ("created_on",)