from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('chat/', views.chat_window, name='chat'),

    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    path('dashboard/admin/daycare/<int:daycare_id>/approve/', views.approve_daycare, name='approve_daycare'),
    path('dashboard/admin/daycare/<int:daycare_id>/reject/', views.reject_daycare, name='reject_daycare'),


    path('daycare/dashboard/', views.daycare_dashboard, name='daycare_dashboard'),
    path('parent/dashboard/', views.parent_dashboard, name='parent_dashboard'),

    path('daycare/complete-profile/', views.daycare_complete_profile, name='daycare_complete_profile'),
    path('parent/complete-profile/', views.parent_complete_profile, name='parent_complete_profile'),

    path('daycare/admin/<int:daycare_id>/ban/', views.ban_daycare, name='ban_daycare'),
    path('parent/admin/<int:parent_id>/ban/', views.ban_parent, name='ban_parent'),

    path('my_children/', views.my_children, name='my_children'),       # My Child page
    path('daycares/', views.daycares_list, name='daycares_list'),      # List of verified daycares
    path('daycare/<int:daycare_id>/enroll/', views.enroll_child, name='enroll_child'),  # Enroll child form
    
    path('enrollment_requests/', views.enrollment_requests, name='enrollment_requests'),
    path('approve/<int:pk>/', views.approve_request, name='approve_request'),
    path('reject/<int:pk>/', views.reject_request, name='reject_request'),
     path('activity/add/', views.add_activity_report, name='add_activity_report'),

    path('milestones/', views.update_milestones, name='update_milestones'),

    path('redirect-dashboard/', views.redirect_dashboard, name='redirect_dashboard'),
    path('delete_child/<int:child_id>/', views.delete_child, name='delete_child'),
    # path('child/<int:child_id>/generate_ai_suggestion_view/', views.generate_ai_suggestion_view, name='generate_ai_suggestion_view'),

    path('generate_ai_suggestion/<int:child_id>/', views.generate_ai_suggestion_view, name='generate_ai_suggestion_view'),
    path('daycare/dashboard/enrolled/', views.enrolled_children, name='enrolled_children'),
    path('daycare/dashboard/child/<int:child_id>/', views.view_child, name='view_child'),

]
