from django.db import models


# =========================================================
# CLASS & STANDARD CHOICES (SCHOOL, JR COLLEGE & MCA)
# =========================================================
CLASS_CHOICES = [
    # School Section
    ('Nursery', 'Nursery'),
    ('LKG', 'LKG'),
    ('UKG', 'UKG'),
    ('1st', 'Class 1st'),
    ('2nd', 'Class 2nd'),
    ('3rd', 'Class 3rd'),
    ('4th', 'Class 4th'),
    ('5th', 'Class 5th'),
    ('6th', 'Class 6th'),
    ('7th', 'Class 7th'),
    ('8th', 'Class 8th'),
    ('9th', 'Class 9th'),
    ('10th', 'Class 10th'),

    # Junior College Section
    ('11th_Science', '11th Science'),
    ('11th_Commerce', '11th Commerce'),
    ('12th_Science', '12th Science'),
    ('12th_Commerce', '12th Commerce'),

    # College Section
    ('MCA_1', 'MCA - Year I'),
    ('MCA_2', 'MCA - Year II'),
]


# =========================================================
# DRIVER MODEL
# =========================================================
class Driver(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    license_number = models.CharField(max_length=50, unique=True)
    experience_years = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
        ],
        default='Active'
    )

    def __str__(self):
        return self.name


# =========================================================
# ROUTE MODEL
# =========================================================
class Route(models.Model):
    name = models.CharField(max_length=100, default='')
    start_point = models.CharField(max_length=150)
    destination = models.CharField(max_length=150, default='College')
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    travel_time_min = models.PositiveIntegerField()

    # Bus fee charges for this route
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
        ],
        default='Active'
    )

    def __str__(self):
        return f"{self.name} (Fare: Rs. {self.fee})"


# =========================================================
# BUS MODEL
# =========================================================
class Bus(models.Model):
    bus_number = models.CharField(max_length=20, unique=True)
    registration_number = models.CharField(max_length=20, unique=True)

    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='buses'
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='buses'
    )

    capacity = models.PositiveIntegerField(default=40)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
            ('Maintenance', 'Maintenance'),
        ],
        default='Active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.bus_number


# =========================================================
# STOP MODEL
# =========================================================
class Stop(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='stops'
    )

    name = models.CharField(max_length=150, default='')
    stop_order = models.PositiveIntegerField()
    arrival_time = models.TimeField(null=True, blank=True)

        # Monthly bus pass fee for this stop
    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.route.name})"


# =========================================================
# STUDENT MODEL
# =========================================================
class Student(models.Model):
    student_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15)

    # Class selection (Nursery to 12th + MCA)
    student_class = models.CharField(
        max_length=30,
        choices=CLASS_CHOICES,
        default='1st'
    )

    course = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=20, blank=True, null=True)

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    pickup_stop = models.ForeignKey(
        Stop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending Approval'),
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
        ],
        default='Pending'
    )
          # =========================================================
    # DIGITAL BUS PASS
    # =========================================================

    pass_number = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True
    )

    pass_issued_date = models.DateField(
        null=True,
        blank=True
    )

    pass_expiry_date = models.DateField(
        null=True,
        blank=True
    )

    pass_status = models.CharField(
        max_length=20,
        choices=[
            ('Not Issued', 'Not Issued'),
            ('Active', 'Active'),
            ('Expired', 'Expired'),
            ('Revoked', 'Revoked'),
        ],
        default='Not Issued'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.student_class}"


# =========================================================
# PARENT MODEL
# =========================================================
class Parent(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='parent'
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} (Parent of {self.student.name})"


# =========================================================
# STAFF MODEL
# =========================================================
class Staff(models.Model):
    staff_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=100, default='')
    department = models.CharField(max_length=100, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
        ],
        default='Active'
    )

    def __str__(self):
        return self.name


# =========================================================
# ATTENDANCE MODEL
# =========================================================
class BusAttendance(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance'
    )

    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name='attendance'
    )

    date = models.DateField()

    boarding_stop = models.ForeignKey(
        Stop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    boarding_time = models.TimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Present', 'Present'),
            ('Absent', 'Absent'),
        ],
        default='Present'
    )

    def __str__(self):
        return f"{self.student.name} - {self.date}"


# =========================================================
# LIVE BUS LOCATION MODEL
# =========================================================
class BusLocation(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name='locations'
    )

    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    speed = models.FloatField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus.bus_number} - {self.recorded_at}"


# =========================================================
# BUS OCCUPANCY MODEL
# =========================================================
class BusOccupancy(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name='occupancy_records'
    )

    date = models.DateField()
    time = models.TimeField()
    occupied_seats = models.PositiveIntegerField(default=0)

    def available_seats(self):
        return max(self.bus.capacity - self.occupied_seats, 0)

    def occupancy_percentage(self):
        if self.bus.capacity == 0:
            return 0
        return round((self.occupied_seats / self.bus.capacity) * 100, 2)

    def __str__(self):
        return f"{self.bus.bus_number} - {self.date} {self.time}"


# =========================================================
# OCCUPANCY PREDICTION (ML) MODEL
# =========================================================
class OccupancyPrediction(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name='predictions'
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='predictions'
    )

    prediction_date = models.DateField()
    prediction_time = models.TimeField()
    predicted_occupancy = models.PositiveIntegerField()
    predicted_available_seats = models.PositiveIntegerField()
    model_name = models.CharField(max_length=100, default='Random Forest')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bus.bus_number} - {self.predicted_occupancy} students"


# =========================================================
# BUS ALLOCATION MODEL
# =========================================================
# =========================================================
# BUS ALLOCATION
# =========================================================

class BusAllocation(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name='allocations'
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='allocations'
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='allocations'
    )

    allocation_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Assigned', 'Assigned'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled'),
        ],
        default='Assigned'
    )

    def __str__(self):
        return (
            f"{self.bus.bus_number} - "
            f"{self.route.name} - "
            f"{self.allocation_date}"
        )


# =========================================================
# BUS DELAY & EMERGENCY ALERTS
# =========================================================

class BusAlert(models.Model):
    ALERT_TYPES = [
        ('Delay', 'Traffic / Delay'),
        ('Emergency', 'Emergency Alert'),
        ('Route_Change', 'Route Change'),
        ('General', 'General Notice'),
    ]

    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )

    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        default='Delay'
    )

    message = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alert_type}: {self.message}"


# =========================================================
# DIGITAL BUS PASS APPLICATION
# =========================================================

class BusPassApplication(models.Model):
    PASS_TYPES = [
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Yearly', 'Yearly'),
    ]

    APPLICATION_STATUS = [
        ('Pending Payment', 'Pending Payment'),
        ('Payment Pending', 'Payment Pending'),
        ('Payment Successful', 'Payment Successful'),
        ('Payment Failed', 'Payment Failed'),
        ('Cancelled', 'Cancelled'),
    ]

    application_number = models.CharField(
        max_length=40,
        unique=True
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='bus_pass_applications'
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    pickup_stop = models.ForeignKey(
        Stop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    pass_type = models.CharField(
        max_length=20,
        choices=PASS_TYPES,
        default='Yearly'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    application_status = models.CharField(
        max_length=30,
        choices=APPLICATION_STATUS,
        default='Pending Payment'
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application_number} - {self.student.name}"


# =========================================================
# BUS PASS PAYMENT
# =========================================================

class BusPassPayment(models.Model):
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Successful', 'Successful'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    application = models.ForeignKey(
        BusPassApplication,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    payment_number = models.CharField(
        max_length=50,
        unique=True
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    payment_date = models.DateTimeField(
        null=True,
        blank=True
    )

    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment_number} - {self.payment_status}"


# =========================================================
# DIGITAL BUS PASS
# =========================================================

class DigitalPass(models.Model):
    PASS_STATUS = [
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Revoked', 'Revoked'),
    ]

    pass_number = models.CharField(
        max_length=50,
        unique=True
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='digital_passes'
    )

    application = models.OneToOneField(
        BusPassApplication,
        on_delete=models.PROTECT,
        related_name='digital_pass'
    )

    payment = models.ForeignKey(
        BusPassPayment,
        on_delete=models.PROTECT,
        related_name='digital_passes'
    )

    issue_date = models.DateField()
    expiry_date = models.DateField()

    pass_status = models.CharField(
        max_length=20,
        choices=PASS_STATUS,
        default='Active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pass_number} - {self.student.name}"


# =========================================================
# DIGITAL PASS EMAIL LOG
# =========================================================

class PassEmailLog(models.Model):
    EMAIL_STATUS = [
        ('Pending', 'Pending'),
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='pass_email_logs'
    )

    digital_pass = models.ForeignKey(
        DigitalPass,
        on_delete=models.CASCADE,
        related_name='email_logs',
        null=True,
        blank=True
    )

    recipient_email = models.EmailField()

    subject = models.CharField(
        max_length=255,
        default='SmartBus Digital Bus Pass'
    )

    email_status = models.CharField(
        max_length=20,
        choices=EMAIL_STATUS,
        default='Pending'
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient_email} - {self.email_status}"
    



# from django.db import models


# class Driver(models.Model):
#     name = models.CharField(max_length=100)
#     phone = models.CharField(max_length=15)
#     license_number = models.CharField(max_length=50, unique=True)
#     experience_years = models.PositiveIntegerField(default=0)

#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ('Active', 'Active'),
#             ('Inactive', 'Inactive'),
#         ],
#         default='Active'
#     )

#     def __str__(self):
#         return self.name


# # class Route(models.Model):
# #     name = models.CharField(max_length=100)
# #     start_point = models.CharField(max_length=150)
# #     destination = models.CharField(max_length=150, default='College')
# #     distance_km = models.DecimalField(max_digits=6, decimal_places=2)
# #     travel_time_min = models.PositiveIntegerField()

# #     status = models.CharField(
# #         max_length=20,
# #         choices=[
# #             ('Active', 'Active'),
# #             ('Inactive', 'Inactive'),
# #         ],
# #         default='Active'
# #     )

# #     def __str__(self):
# #         return self.name
# class Route(models.Model):
#     name = models.CharField(
#         max_length=100,
#         default=''
#     )

#     start_point = models.CharField(max_length=150)

#     destination = models.CharField(
#         max_length=150,
#         default='College'
#     )

#     distance_km = models.DecimalField(
#         max_digits=6,
#         decimal_places=2
#     )

#     travel_time_min = models.PositiveIntegerField()

#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ('Active', 'Active'),
#             ('Inactive', 'Inactive'),
#         ],
#         default='Active'
#     )

#     def __str__(self):
#         return self.name


# class Bus(models.Model):
#     bus_number = models.CharField(max_length=20, unique=True)
#     registration_number = models.CharField(max_length=20, unique=True)

#     driver = models.ForeignKey(
#         Driver,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='buses'
#     )

#     route = models.ForeignKey(
#         Route,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='buses'
#     )

#     capacity = models.PositiveIntegerField(default=40)

#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ('Active', 'Active'),
#             ('Inactive', 'Inactive'),
#             ('Maintenance', 'Maintenance'),
#         ],
#         default='Active'
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.bus_number


# class Stop(models.Model):
#     route = models.ForeignKey(
#         Route,
#         on_delete=models.CASCADE,
#         related_name='stops'
#     )

#     # IMPORTANT: default='' added here
#     name = models.CharField(max_length=150, default='')

#     stop_order = models.PositiveIntegerField()
#     arrival_time = models.TimeField(
#     null=True,
#     blank=True
# )

#     latitude = models.DecimalField(
#         max_digits=10,
#         decimal_places=7,
#         null=True,
#         blank=True
#     )

#     longitude = models.DecimalField(
#         max_digits=10,
#         decimal_places=7,
#         null=True,
#         blank=True
#     )

#     def __str__(self):
#         return self.name


# class Student(models.Model):
#     student_id = models.CharField(max_length=30, unique=True)
#     name = models.CharField(max_length=100)
#     email = models.EmailField(
#     unique=True,
#     blank=True,
#     null=True
# )
#     phone = models.CharField(max_length=15)
#     course = models.CharField(max_length=100)
#     year = models.CharField(max_length=20)

#     route = models.ForeignKey(
#         Route,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='students'
#     )

#     pickup_stop = models.ForeignKey(
#         Stop,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='students'
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ('Active', 'Active'),
#             ('Inactive', 'Inactive'),
#         ],
#         default='Active'
#     )

#     def __str__(self):
#         return self.name


# class Parent(models.Model):
#     student = models.OneToOneField(
#         Student,
#         on_delete=models.CASCADE,
#         related_name='parent'
#     )

#     name = models.CharField(max_length=100)
#     phone = models.CharField(max_length=15)
#     email = models.EmailField(blank=True, null=True)

#     def __str__(self):
#         return self.name



# # class Staff(models.Model):
# #     staff_id = models.CharField(max_length=30, unique=True)
# #     name = models.CharField(max_length=100)
# #     email = models.EmailField(unique=True)
# #     phone = models.CharField(max_length=15)

# #     # IMPORTANT: default='' added here
# #     role = models.CharField(max_length=100, default='')

# #     department = models.CharField(max_length=100, blank=True)

# #     status = models.CharField(
# #         max_length=20,
# #         choices=[
# #             ('Active', 'Active'),
# #             ('Inactive', 'Inactive'),
# #         ],
# #         default='Active'
# #     )

# #     def __str__(self):
# #         return self.name

# class Staff(models.Model):
#     staff_id = models.CharField(max_length=30, unique=True)
#     name = models.CharField(max_length=100)

#     email = models.EmailField(
#         unique=True,
#         null=True,
#         blank=True
#     )

#     phone = models.CharField(max_length=15)

#     role = models.CharField(
#         max_length=100,
#         default=''
#     )

#     department = models.CharField(
#         max_length=100,
#         blank=True
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ('Active', 'Active'),
#             ('Inactive', 'Inactive'),
#         ],
#         default='Active'
#     )

#     def __str__(self):
#         return self.name


#     ##############################
# class BusAttendance(models.Model):
#     student = models.ForeignKey(
#         Student,
#         on_delete=models.CASCADE,
#         related_name='attendance'
#     )

#     bus = models.ForeignKey(
#         Bus,
#         on_delete=models.CASCADE,
#         related_name='attendance'
#     )

#     date = models.DateField()

#     boarding_stop = models.ForeignKey(
#         Stop,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True
#     )

#     boarding_time = models.TimeField(
#         null=True,
#         blank=True
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ('Present', 'Present'),
#             ('Absent', 'Absent'),
#         ],
#         default='Present'
#     )

#     def __str__(self):
#         return f"{self.student.name} - {self.date}"


# class BusLocation(models.Model):
#     bus = models.ForeignKey(
#         Bus,
#         on_delete=models.CASCADE,
#         related_name='locations'
#     )

#     latitude = models.DecimalField(
#         max_digits=10,
#         decimal_places=7
#     )

#     longitude = models.DecimalField(
#         max_digits=10,
#         decimal_places=7
#     )

#     speed = models.FloatField(default=0)

#     recorded_at = models.DateTimeField(
#         auto_now_add=True
#     )

#     def __str__(self):
#         return f"{self.bus.bus_number} - {self.recorded_at}"


# class BusOccupancy(models.Model):
#     bus = models.ForeignKey(
#         Bus,
#         on_delete=models.CASCADE,
#         related_name='occupancy_records'
#     )

#     date = models.DateField()
#     time = models.TimeField()

#     occupied_seats = models.PositiveIntegerField(
#         default=0
#     )

#     def available_seats(self):
#         return max(
#             self.bus.capacity - self.occupied_seats,
#             0
#         )

#     def occupancy_percentage(self):
#         if self.bus.capacity == 0:
#             return 0

#         return round(
#             (self.occupied_seats / self.bus.capacity) * 100,
#             2
#         )

#     def __str__(self):
#         return f"{self.bus.bus_number} - {self.date} {self.time}"


# class OccupancyPrediction(models.Model):
#     bus = models.ForeignKey(
#         Bus,
#         on_delete=models.CASCADE,
#         related_name='predictions'
#     )

#     route = models.ForeignKey(
#         Route,
#         on_delete=models.CASCADE,
#         related_name='predictions'
#     )

#     prediction_date = models.DateField()
#     prediction_time = models.TimeField()

#     predicted_occupancy = models.PositiveIntegerField()

#     predicted_available_seats = models.PositiveIntegerField()

#     model_name = models.CharField(
#         max_length=100,
#         default='Random Forest'
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )

#     def __str__(self):
#         return f"{self.bus.bus_number} - {self.predicted_occupancy} students"


# class BusAllocation(models.Model):
#     bus = models.ForeignKey(
#         Bus,
#         on_delete=models.CASCADE,
#         related_name='allocations'
#     )

#     driver = models.ForeignKey(
#     Driver,
#     on_delete=models.SET_NULL,
#     null=True,
#     blank=True,
#     related_name='allocations'
# )

#     route = models.ForeignKey(
#         Route,
#         on_delete=models.CASCADE,
#         related_name='allocations'
#     )

#     allocation_date = models.DateField()

#     start_time = models.TimeField(
#         null=True,
#         blank=True
#     )

#     end_time = models.TimeField(
#         null=True,
#         blank=True
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=[
#             ('Assigned', 'Assigned'),
#             ('Completed', 'Completed'),
#             ('Cancelled', 'Cancelled'),
#         ],
#         default='Assigned'
#     )

#     def __str__(self):
#         return f"{self.bus.bus_number} - {self.route.name} - {self.allocation_date}"

#     #--------------------------------
    
# from django import forms
# from .models import Stop



