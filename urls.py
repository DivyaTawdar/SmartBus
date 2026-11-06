from django.urls import path
from . import views

urlpatterns = [
    # ================= PUBLIC LANDING & PORTAL =================
    path('', views.welcome, name='welcome'),
    path('student-registration/', views.student_registration, name='student_registration'),
    path('bus-tracker/', views.bus_tracker, name='bus_tracker'),
    path('api/route-info/<int:route_id>/', views.route_info_api, name='route_info_api'),
    path('api/bus-locations/', views.bus_locations_api, name='bus_locations_api'),

    # ================= AUTHENTICATION & DASHBOARD =================
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # ================= BUS MANAGEMENT =================
    path('buses/', views.buses, name='buses'),
    path('buses/add/', views.add_bus, name='add_bus'),
    path('buses/edit/<int:bus_id>/', views.edit_bus, name='edit_bus'),
    path('buses/delete/<int:bus_id>/', views.delete_bus, name='delete_bus'),
    path('buses/view/<int:bus_id>/', views.view_bus, name='view_bus'),

    # ================= DRIVER MANAGEMENT =================
    path('drivers/', views.drivers, name='drivers'),
    path('drivers/add/', views.add_driver, name='add_driver'),
    path('drivers/edit/<int:driver_id>/', views.edit_driver, name='edit_driver'),
    path('drivers/delete/<int:driver_id>/', views.delete_driver, name='delete_driver'),
    path('drivers/view/<int:driver_id>/', views.view_driver, name='view_driver'),

    # ================= ROUTE MANAGEMENT =================
    path('routes/', views.routes, name='routes'),
    path('routes/add/', views.add_route, name='add_route'),
    path('routes/edit/<int:route_id>/', views.edit_route, name='edit_route'),
    path('routes/delete/<int:route_id>/', views.delete_route, name='delete_route'),
    path('routes/view/<int:route_id>/', views.view_route, name='view_route'),

    # ================= STOP MANAGEMENT =================
    path('stops/', views.stops, name='stops'),
    path('stops/add/', views.add_stop, name='add_stop'),
    path('stops/view/<int:stop_id>/', views.view_stop, name='view_stop'),
    path('stops/edit/<int:stop_id>/', views.edit_stop, name='edit_stop'),
    path('stops/delete/<int:stop_id>/', views.delete_stop, name='delete_stop'),

    # ================= STUDENT MANAGEMENT =================
    path('students/', views.students, name='students'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/view/<int:student_id>/', views.view_student, name='view_student'),
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:student_id>/', views.delete_student, name='delete_student'),

    # ================= PARENT MANAGEMENT =================
    path('parents/', views.parents, name='parents'),
    path('parents/add/', views.add_parent, name='add_parent'),
    path('parents/view/<int:parent_id>/', views.view_parent, name='view_parent'),
    path('parents/edit/<int:parent_id>/', views.edit_parent, name='edit_parent'),
    path('parents/delete/<int:parent_id>/', views.delete_parent, name='delete_parent'),

    # ================= ALLOCATION MANAGEMENT =================
    path('allocation/', views.allocation_list, name='allocation_list'),
    path('allocations/add/', views.allocation_create, name='allocation_create'),
    path('allocations/<int:pk>/edit/', views.allocation_edit, name='allocation_edit'),
    path('allocations/<int:pk>/delete/', views.allocation_delete, name='allocation_delete'),

    # ================= STAFF MANAGEMENT =================
    path('staff/', views.staff, name='staff'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/edit/<int:id>/', views.edit_staff, name='edit_staff'),
    path('staff/delete/<int:id>/', views.delete_staff, name='delete_staff'),

    # ================= ANALYTICS & ATTENDANCE =================
    path('analytics/', views.analytics, name='analytics'),
    path('attendance/', views.attendance, name='attendance'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),

    path('driver-tracker/', views.driver_tracker, name='driver_tracker'),
    path('api/update-location/', views.update_location_api, name='update_location_api'),


    path('alerts/', views.manage_alerts, name='manage_alerts'),
    path('alerts/delete/<int:alert_id>/', views.delete_alert, name='delete_alert'),
    path('api/active-alerts/', views.active_alerts_api, name='active_alerts_api'),
    path('bus-fees/', views.bus_fees, name='bus_fees'),


    path("occupancy/", views.occupancy_page, name="occupancy"),


    path(
    'students/<int:student_id>/approve/',
    views.approve_student,
    name='approve_student'
),

  path(
    'digital-pass/<int:student_id>/',
    views.digital_pass,
    name='digital_pass'
),


# ================= DIGITAL BUS PASS APPLICATION =================
path(
    'apply-bus-pass/',
    views.apply_bus_pass,
    name='apply_bus_pass'
),

path('manage-fees/', views.manage_fees, name='manage_fees'),

path(
    'search-students/',
    views.search_students,
    name='search_students'
),


# DIGITAL BUS PASS MANAGEMENT DASHBOARD
path(
    'digital-pass-management/',
    views.digital_pass_management,
    name='digital_pass_management'
),

path(
    'digital-pass/<int:pass_id>/download/',
    views.download_digital_pass_pdf,
    name='download_digital_pass_pdf'
),

]  