from django.contrib import admin

from .models import (
    Driver,
    Route,
    Bus,
    Stop,
    Student,
    Parent,
    Staff,
    BusAttendance,
    BusLocation,
    BusOccupancy,
    OccupancyPrediction,
    BusAllocation,
    BusPassApplication,
    BusPassPayment,
    DigitalPass,
    PassEmailLog,
)


# ============================================================
# DRIVER
# ============================================================

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone',
        'license_number',
        'experience_years',
        'status',
    )

    search_fields = ('name', 'phone', 'license_number')
    list_filter = ('status',)


# ============================================================
# ROUTE
# ============================================================

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_point',
        'destination',
        'distance_km',
        'travel_time_min',
        'status',
    )

    search_fields = ('name', 'start_point', 'destination')
    list_filter = ('status',)


# ============================================================
# BUS
# ============================================================

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = (
        'bus_number',
        'registration_number',
        'driver',
        'route',
        'capacity',
        'status',
    )

    search_fields = ('bus_number', 'registration_number')
    list_filter = ('status',)


# ============================================================
# STOP
# ============================================================

@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'route',
        'stop_order',
        'arrival_time',
        'latitude',
        'longitude',
    )

    search_fields = ('name', 'route__name')
    list_filter = ('route',)


# ============================================================
# STUDENT
# ============================================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'student_id',
        'name',
        'email',
        'phone',
        'course',
        'year',
        'route',
        'pickup_stop',
        'status',
        'pass_number',
        'pass_issued_date',
        'pass_expiry_date',
        'pass_status',
    )

    search_fields = (
        'student_id',
        'name',
        'email',
        'phone',
        'pass_number',
    )

    list_filter = (
        'status',
        'course',
        'year',
        'pass_status',
        'pass_issued_date',
        'pass_expiry_date',
    )


# ============================================================
# PARENT
# ============================================================

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student', 'phone', 'email')

    search_fields = (
        'name',
        'student__name',
        'phone',
        'email',
    )


# ============================================================
# STAFF
# ============================================================

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = (
        'staff_id',
        'name',
        'email',
        'phone',
        'role',
        'department',
        'status',
    )

    search_fields = ('staff_id', 'name', 'email', 'phone')
    list_filter = ('status', 'department')


# ============================================================
# BUS ATTENDANCE
# ============================================================

@admin.register(BusAttendance)
class BusAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'bus',
        'date',
        'boarding_stop',
        'boarding_time',
        'status',
    )

    search_fields = ('student__name', 'bus__bus_number')
    list_filter = ('date', 'status')


# ============================================================
# BUS LOCATION
# ============================================================

@admin.register(BusLocation)
class BusLocationAdmin(admin.ModelAdmin):
    list_display = (
        'bus',
        'latitude',
        'longitude',
        'speed',
        'recorded_at',
    )

    search_fields = ('bus__bus_number',)
    list_filter = ('recorded_at',)


# ============================================================
# BUS OCCUPANCY
# ============================================================

@admin.register(BusOccupancy)
class BusOccupancyAdmin(admin.ModelAdmin):
    list_display = ('bus', 'date', 'time', 'occupied_seats')

    search_fields = ('bus__bus_number',)
    list_filter = ('date',)


# ============================================================
# OCCUPANCY PREDICTION
# ============================================================

@admin.register(OccupancyPrediction)
class OccupancyPredictionAdmin(admin.ModelAdmin):
    list_display = (
        'bus',
        'route',
        'prediction_date',
        'prediction_time',
        'predicted_occupancy',
        'predicted_available_seats',
        'model_name',
    )

    search_fields = ('bus__bus_number', 'route__name', 'model_name')
    list_filter = ('prediction_date', 'model_name')


# ============================================================
# BUS ALLOCATION
# ============================================================

@admin.register(BusAllocation)
class BusAllocationAdmin(admin.ModelAdmin):
    list_display = (
        'bus',
        'driver',
        'route',
        'allocation_date',
        'start_time',
        'end_time',
        'status',
    )

    search_fields = ('bus__bus_number', 'driver__name', 'route__name')
    list_filter = ('allocation_date', 'status')


# ============================================================
# BUS PASS APPLICATION
# ============================================================

@admin.register(BusPassApplication)
class BusPassApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'application_number',
        'student',
        'route',
        'pickup_stop',
        'pass_type',
        'amount',
        'application_status',
        'applied_at',
    )

    search_fields = (
        'application_number',
        'student__student_id',
        'student__name',
        'student__email',
    )

    list_filter = (
        'pass_type',
        'application_status',
        'applied_at',
    )

    readonly_fields = ('applied_at', 'updated_at')

    date_hierarchy = 'applied_at'


# ============================================================
# BUS PASS PAYMENT
# ============================================================

@admin.register(BusPassPayment)
class BusPassPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'payment_number',
        'application',
        'amount',
        'payment_status',
        'razorpay_order_id',
        'razorpay_payment_id',
        'payment_date',
        'receipt_number',
    )

    search_fields = (
        'payment_number',
        'application__application_number',
        'application__student__name',
        'razorpay_order_id',
        'razorpay_payment_id',
        'receipt_number',
    )

    list_filter = ('payment_status', 'payment_date')

    readonly_fields = (
        'created_at',
        'updated_at',
    )


# ============================================================
# DIGITAL PASS
# ============================================================

@admin.register(DigitalPass)
class DigitalPassAdmin(admin.ModelAdmin):
    list_display = (
        'pass_number',
        'student',
        'application',
        'payment',
        'issue_date',
        'expiry_date',
        'pass_status',
    )

    search_fields = (
        'pass_number',
        'student__student_id',
        'student__name',
        'application__application_number',
    )

    list_filter = (
        'pass_status',
        'issue_date',
        'expiry_date',
    )

    date_hierarchy = 'issue_date'


# ============================================================
# PASS EMAIL LOG
# ============================================================

@admin.register(PassEmailLog)
class PassEmailLogAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'recipient_email',
        'subject',
        'email_status',
        'sent_at',
        'created_at',
    )

    search_fields = (
        'student__student_id',
        'student__name',
        'recipient_email',
        'subject',
    )

    list_filter = ('email_status', 'created_at')

    readonly_fields = ('created_at',)