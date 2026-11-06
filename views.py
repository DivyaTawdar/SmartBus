from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from datetime import date, timedelta
import uuid
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required, user_passes_test


from io import BytesIO

from django.http import HttpResponse, Http404

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


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
    CLASS_CHOICES,
)

from .forms import (
    BusForm,
    DriverForm,
    RouteForm,
    StopForm,
    StudentForm,
    ParentForm,
    StaffForm,
    BusAttendanceForm,
)


# =========================================================
# PUBLIC PORTAL VIEWS (LANDING, REGISTRATION, TRACKING)
# =========================================================

def welcome(request):
    """
    Public Welcome / Landing page.
    """
    context = {
        'total_buses': Bus.objects.filter(status='Active').count(),
        'total_routes': Route.objects.filter(status='Active').count(),
        'total_students': Student.objects.count(),
    }
    return render(request, "welcome.html", context)


# =========================================================
# ROUTE DISTANCE-BASED FEE CALCULATION
# =========================================================

DAILY_FEE_PER_KM = Decimal("3")
DAYS_PER_MONTH = Decimal("30")


def calculate_route_fees(distance_km):
    """
    Calculate route fees based on distance.

    Daily fee    = Distance x Rs. 3
    Monthly fee  = Daily fee x 30
    Quarterly    = Monthly fee x 3
    Yearly       = Monthly fee x 12
    """

    distance = Decimal(str(distance_km or 0))

    daily_fee = (
        distance * DAILY_FEE_PER_KM
    ).quantize(Decimal("0.01"))

    monthly_fee = (
        daily_fee * DAYS_PER_MONTH
    ).quantize(Decimal("0.01"))

    quarterly_fee = (
        monthly_fee * Decimal("3")
    ).quantize(Decimal("0.01"))

    yearly_fee = (
        monthly_fee * Decimal("12")
    ).quantize(Decimal("0.01"))

    return {
        "distance_km": distance,
        "daily_fee": daily_fee,
        "monthly_fee": monthly_fee,
        "quarterly_fee": quarterly_fee,
        "yearly_fee": yearly_fee,
    }


def search_students(request):

    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({
            'students': []
        })

    students = Student.objects.filter(
        name__icontains=query
    ).order_by('name')[:10]

    student_data = []

    for student in students:

        student_data.append({
            'student_id': student.student_id,
            'name': student.name,
            'phone': student.phone or '',
            'email': student.email or '',
            'course': getattr(student, 'course', '') or '',
            'year': getattr(student, 'year', '') or '',
            'pickup_stop_id': (
                student.pickup_stop.id
                if student.pickup_stop
                else ''
            ),
            'pickup_stop': (
                student.pickup_stop.name
                if student.pickup_stop
                else ''
            ),
            'route': (
                student.route.name
                if student.route
                else ''
            ),
        })

    return JsonResponse({
        'students': student_data
    })

# =========================================================
# DIGITAL BUS PASS APPLICATION
# =========================================================

def apply_bus_pass(request):

    routes = Route.objects.filter(
        status="Active"
    ).order_by("name")

    all_stops = Stop.objects.filter(
        route__status="Active"
    ).select_related(
        "route"
    ).order_by(
        "route__name",
        "stop_order"
    )

    if request.method == "POST":

        student_id = request.POST.get(
            "student_id", ""
        ).strip()

        phone = request.POST.get(
            "phone", ""
        ).strip()

        pickup_stop_id = request.POST.get(
            "pickup_stop", ""
        ).strip()

        pass_type = request.POST.get(
            "pass_type", ""
        ).strip()

        if not all([
            student_id,
            phone,
            pickup_stop_id,
            pass_type
        ]):

            messages.error(
                request,
                "Please fill in all required fields."
            )

        elif pass_type not in [
            "Monthly",
            "Quarterly",
            "Yearly"
        ]:

            messages.error(
                request,
                "Please select a valid pass type."
            )

        else:

            student = Student.objects.filter(
                student_id=student_id,
                phone=phone
            ).first()

            if not student:

                messages.error(
                    request,
                    "Student ID or mobile number is incorrect."
                )

            else:

                pickup_stop = Stop.objects.filter(
                    id=pickup_stop_id,
                    route__status="Active"
                ).select_related(
                    "route"
                ).first()

                if not pickup_stop:

                    messages.error(
                        request,
                        "Please select a valid pickup stop."
                    )

                else:

                    route = pickup_stop.route

                    fees = calculate_route_fees(
                        route.distance_km
                    )

                    monthly_fee = fees["monthly_fee"]

                    fee_multipliers = {
                        "Monthly": Decimal("1"),
                        "Quarterly": Decimal("3"),
                        "Yearly": Decimal("12"),
                    }

                    if monthly_fee <= Decimal("0"):

                        messages.error(
                            request,
                            "The route distance is not configured. "
                            "Please contact the bus administrator."
                        )

                    else:

                        amount = (
                            monthly_fee *
                            fee_multipliers[pass_type]
                        ).quantize(
                            Decimal("0.01")
                        )

                        application_number = (
                            "BPA-" +
                            uuid.uuid4().hex[:12].upper()
                        )

                        BusPassApplication.objects.create(
                            application_number=application_number,
                            student=student,
                            route=route,
                            pickup_stop=pickup_stop,
                            pass_type=pass_type,
                            amount=amount,
                            application_status="Pending Payment"
                        )

                        messages.success(
                            request,
                            f"Application submitted successfully! "
                            f"Application Number: {application_number}. "
                            f"Total Fee: ₹{amount}. "
                            f"Please continue to payment."
                        )

                        return redirect("apply_bus_pass")

    context = {
        "routes": routes,
        "stops": all_stops,
    }

    return render(
        request,
        "apply_bus_pass.html",
        context
    )



# =========================================================
# MANAGE BUS STOP FEES
# =========================================================

@login_required(login_url='login')
def manage_fees(request):

    stops = Stop.objects.select_related('route').all().order_by(
        'route__name',
        'stop_order'
    )

    if request.method == 'POST':
        stop_id = request.POST.get('stop_id')
        monthly_fee = request.POST.get('monthly_fee')

        try:
            stop = Stop.objects.get(id=stop_id)

            fee = float(monthly_fee)

            if fee < 0:
                messages.error(request, 'Fee cannot be negative.')

            else:
                stop.monthly_fee = fee
                stop.save(update_fields=['monthly_fee'])

                messages.success(
                    request,
                    f'Monthly fee updated successfully for {stop.name}.'
                )

                return redirect('manage_fees')

        except (Stop.DoesNotExist, TypeError, ValueError):
            messages.error(
                request,
                'Invalid stop or fee. Please enter a valid amount.'
            )

    context = {
        'stops': stops,
        'total_stops': stops.count(),
    }

    return render(request, 'manage_fees.html', context)




# ============================================================

# DOWNLOAD DIGITAL BUS PASS AS PDF

# ============================================================
@login_required(login_url='login')
def download_digital_pass_pdf(request, pass_id):
    digital_pass = get_object_or_404(
        DigitalPass.objects.select_related(
            'student',
            'application',
            'payment',
            'application__route',
            'application__pickup_stop',
        ),
        id=pass_id,
        pass_status='Active',
        expiry_date__gte=date.today(),
        application__application_status='Payment Successful',
        payment__payment_status='Successful',
    )

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'PassTitle',
        parent=styles['Title'],
        alignment=TA_CENTER,
        textColor=colors.HexColor('#075985'),
        fontSize=20,
        spaceAfter=20,
    )

    elements.append(
        Paragraph('SMARTBUS DIGITAL BUS PASS', title_style)
    )
    elements.append(Spacer(1, 15))

    student = digital_pass.student
    application = digital_pass.application
    payment = digital_pass.payment
    route = application.route
    pickup_stop = application.pickup_stop

    pass_data = [
        ['Field', 'Details'],
        ['Pass Number', str(digital_pass.pass_number)],
        ['Student Name', str(student.name)],
        ['Student ID', str(student.student_id)],
        ['Email', student.email or 'Not Available'],
        ['Phone', str(student.phone or 'Not Available')],
        ['Route', route.name if route else 'Not Assigned'],
        [
            'Pickup Stop',
            str(pickup_stop) if pickup_stop else 'Not Assigned',
        ],
        ['Pass Type', str(application.pass_type)],
        [
            'Issue Date',
            digital_pass.issue_date.strftime('%d-%m-%Y'),
        ],
        [
            'Expiry Date',
            digital_pass.expiry_date.strftime('%d-%m-%Y'),
        ],
        ['Pass Status', str(digital_pass.pass_status)],
        ['Payment Status', str(payment.payment_status)],
        [
            'Receipt Number',
            payment.receipt_number or 'Not Available',
        ],
    ]

    pass_table = Table(
        pass_data,
        colWidths=[150, 330],
        repeatRows=1,
    )

    pass_table.setStyle(
        TableStyle([
            (
                'BACKGROUND',
                (0, 0),
                (-1, 0),
                colors.HexColor('#075985'),
            ),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            (
                'BACKGROUND',
                (0, 1),
                (0, -1),
                colors.HexColor('#E0F2FE'),
            ),
            (
                'GRID',
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor('#CBD5E1'),
            ),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
    )

    elements.append(pass_table)
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            'This digital bus pass is valid subject to the college bus transport rules.',
            styles['Normal'],
        )
    )

    pdf.build(elements)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/pdf',
    )

    response['Content-Disposition'] = (
        f'attachment; filename="SmartBus_Pass_{digital_pass.pass_number}.pdf"'
    )

    return response






# =========================================================
# DIGITAL BUS PASS MANAGEMENT DASHBOARD
# =========================================================



@login_required(login_url='login')
def digital_pass_management(request):

    # Fetch all applications with related information
    applications = (
        BusPassApplication.objects
        .select_related(
            'student',
            'route',
            'pickup_stop'
        )
        .prefetch_related(
            'payments',
            'digital_pass'
        )
        .order_by('-applied_at')
    )

    # Summary cards
    total_applications = applications.count()

    pending_payments = applications.filter(
        application_status__in=[
            'Pending Payment',
            'Payment Pending'
        ]
    ).count()

    paid_applications = applications.filter(
        application_status='Payment Successful'
    ).count()

    active_passes = DigitalPass.objects.filter(
        pass_status='Active'
    ).count()

    expired_passes = DigitalPass.objects.filter(
        Q(pass_status='Expired') |
        Q(expiry_date__lt=__import__('datetime').date.today())
    ).count()

    context = {
        'applications': applications,
        'total_applications': total_applications,
        'pending_payments': pending_payments,
        'paid_applications': paid_applications,
        'active_passes': active_passes,
        'expired_passes': expired_passes,
    }

    return render(
        request,
        'digital_pass_management.html',
        context
    )


# =========================================================
# DIGITAL BUS PASS
# =========================================================

@login_required(login_url='login')
def digital_pass(request, student_id):

    student = get_object_or_404(
        Student.objects.select_related('route', 'pickup_stop'),
        pk=student_id
    )

    context = {
        'student': student,
    }

    return render(request, 'digital_pass.html', context)





def student_registration(request):
    """
    Public student and parent bus registration portal.
    Handles class selection (Nursery to 12th + MCA) and route enrollment.
    """
    routes = Route.objects.filter(status='Active').order_by('name')

    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        student_name = request.POST.get("student_name", "").strip()
        student_email = request.POST.get("student_email", "").strip() or None
        student_phone = request.POST.get("student_phone", "").strip()
        student_class = request.POST.get("student_class", "").strip()

        parent_name = request.POST.get("parent_name", "").strip()
        parent_phone = request.POST.get("parent_phone", "").strip()
        parent_email = request.POST.get("parent_email", "").strip() or None

        route_id = request.POST.get("route")
        pickup_stop_id = request.POST.get("pickup_stop")

        # Basic validation
        if not student_id or not student_name or not student_phone:
            messages.error(request, "Please fill in all required student details.")
            return redirect("student_registration")

        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, f"Student ID '{student_id}' is already registered.")
            return redirect("student_registration")

        selected_route = get_object_or_404(Route, id=route_id) if route_id else None
        selected_stop = get_object_or_404(Stop, id=pickup_stop_id) if pickup_stop_id else None

        # Create new Student record with Pending status
        student = Student.objects.create(
            student_id=student_id,
            name=student_name,
            email=student_email,
            phone=student_phone,
            student_class=student_class,
            route=selected_route,
            pickup_stop=selected_stop,
            status="Pending",
        )

        # Create Parent record
        Parent.objects.create(
            student=student,
            name=parent_name,
            phone=parent_phone,
            email=parent_email,
        )

        messages.success(
            request,
            f"Registration submitted successfully for {student_name}! Application is pending admin approval."
        )
        return redirect("welcome")

    context = {
        'routes': routes,
        'class_choices': CLASS_CHOICES,
    }
    return render(request, "student_registration.html", context)


def route_info_api(request, route_id):
    """
    API endpoint: Returns route fee, stops, and real-time seat availability
    when a student selects a route.
    """
    try:
        route = Route.objects.get(id=route_id)
        stops = route.stops.all().order_by('stop_order')

        stop_list = [
            {
                'id': stop.id,
                'name': stop.name,
                'order': stop.stop_order,
                'arrival_time': stop.arrival_time.strftime("%I:%M %p") if stop.arrival_time else "TBD"
            }
            for stop in stops
        ]

        buses = Bus.objects.filter(route=route, status='Active')
        bus_list = []

        total_route_capacity = 0
        total_route_occupied = 0

        for bus in buses:
            latest_occupancy = (
                BusOccupancy.objects
                .filter(bus=bus)
                .order_by("-date", "-time")
                .first()
            )
            occupied = latest_occupancy.occupied_seats if latest_occupancy else 0
            available = max(bus.capacity - occupied, 0)

            total_route_capacity += bus.capacity
            total_route_occupied += occupied

            bus_list.append({
                'bus_number': bus.bus_number,
                'capacity': bus.capacity,
                'occupied': occupied,
                'available': available,
                'is_full': available == 0,
            })

        total_available = max(total_route_capacity - total_route_occupied, 0)
        route_status = "Full" if (total_available == 0 and total_route_capacity > 0) else "Available"

        return JsonResponse({
            'success': True,
            'route_name': route.name,
            'fee': float(route.fee),
            'start_point': route.start_point,
            'destination': route.destination,
            'distance_km': float(route.distance_km),
            'travel_time_min': route.travel_time_min,
            'total_capacity': total_route_capacity,
            'total_occupied': total_route_occupied,
            'total_available': total_available,
            'status': route_status,
            'stops': stop_list,
            'buses': bus_list,
        })
    except Route.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Route not found'}, status=404)


def bus_tracker(request):
    """
    Live Bus Tracker map view for parents and students.
    """
    active_buses = Bus.objects.filter(status='Active').select_related('route', 'driver')
    return render(request, "bus_tracker.html", {'buses': active_buses})


def bus_locations_api(request):
    """
    API endpoint: Returns all active fleet buses with their latest GPS coordinates or route starting point.
    """
    buses = Bus.objects.filter(status='Active').select_related('route', 'driver')
    locations = []

    # Default campus coordinates (Sangli)
    DEFAULT_LAT = 16.8524
    DEFAULT_LNG = 74.5815

    for bus in buses:
        latest_loc = (
            BusLocation.objects
            .filter(bus=bus)
            .order_by("-recorded_at")
            .first()
        )

        # Check if live location exists
        if latest_loc:
            lat = float(latest_loc.latitude)
            lng = float(latest_loc.longitude)
            speed = latest_loc.speed
            is_live = True
            updated_str = latest_loc.recorded_at.strftime("%I:%M:%S %p")
        else:
            # Fallback to route stop coordinates or default campus location
            first_stop = bus.route.stops.filter(latitude__isnull=False).order_by('stop_order').first() if bus.route else None
            lat = float(first_stop.latitude) if (first_stop and first_stop.latitude) else DEFAULT_LAT
            lng = float(first_stop.longitude) if (first_stop and first_stop.longitude) else DEFAULT_LNG
            speed = 0.0
            is_live = False
            updated_str = "Scheduled"

        locations.append({
            'bus_id': bus.id,
            'bus_number': bus.bus_number,
            'registration_number': bus.registration_number,
            'route_name': bus.route.name if bus.route else 'Unassigned Route',
            'driver_name': bus.driver.name if bus.driver else 'Not Assigned',
            'driver_phone': bus.driver.phone if bus.driver else 'N/A',
            'lat': lat,
            'lng': lng,
            'speed': speed,
            'is_live': is_live,
            'updated_at': updated_str,
        })

    return JsonResponse({'success': True, 'locations': locations})

# =========================================================
# ADMIN AUTHENTICATION
# =========================================================

def admin_login(request):
    """
    Admin authentication view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_message = None
    if request.method == 'POST':
        username_val = request.POST.get('username')
        password_val = request.POST.get('password')

        user = authenticate(request, username=username_val, password=password_val)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = "Invalid username or password! Please try again."

    return render(request, 'login.html', {'error': error_message})


def admin_logout(request):
    """
    Logs out the admin and redirects to the landing page.
    """
    logout(request)
    return redirect('welcome')


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@login_required(login_url='login')
def dashboard(request):
    """
    Main Administrator Dashboard.
    """
    context = {
        'total_buses': Bus.objects.count(),
        'active_buses': Bus.objects.filter(status='Active').count(),
        'total_drivers': Driver.objects.count(),
        'total_routes': Route.objects.count(),
        'total_stops': Stop.objects.count(),
        'total_students': Student.objects.count(),
        'total_parents': Parent.objects.count(),
        'total_staff': Staff.objects.count(),
        'total_attendance': BusAttendance.objects.count(),
        'total_locations': BusLocation.objects.count(),
        'total_occupancy_records': BusOccupancy.objects.count(),
        'total_predictions': OccupancyPrediction.objects.count(),
        'total_allocations': BusAllocation.objects.count(),
    }
    return render(request, 'dashboard.html', context)


# =========================================================
# BUS MANAGEMENT
# =========================================================

@login_required(login_url='login')
def buses(request):
    search = request.GET.get('search', '').strip()
    buses_qs = Bus.objects.select_related('driver', 'route').all()

    if search:
        buses_qs = buses_qs.filter(
            Q(bus_number__icontains=search) |
            Q(registration_number__icontains=search) |
            Q(status__icontains=search)
        )

    context = {
        'buses': buses_qs,
        'search': search,
        'total_buses': buses_qs.count(),
        'active_buses': buses_qs.filter(status='Active').count(),
        'maintenance_buses': buses_qs.filter(status='Maintenance').count(),
        'inactive_buses': buses_qs.filter(status='Inactive').count(),
    }
    return render(request, 'buses.html', context)


@login_required(login_url='login')
def add_bus(request):
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('buses')
    else:
        form = BusForm()
    return render(request, 'add_bus.html', {'form': form})


@login_required(login_url='login')
def edit_bus(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            return redirect('buses')
    else:
        form = BusForm(instance=bus)
    return render(request, 'edit_bus.html', {'form': form, 'bus': bus})


@login_required(login_url='login')
def delete_bus(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    if request.method == 'POST':
        bus.delete()
        return redirect('buses')
    return render(request, 'delete_bus.html', {'bus': bus})


@login_required(login_url='login')
def view_bus(request, bus_id):
    bus = get_object_or_404(Bus.objects.select_related('driver', 'route'), id=bus_id)
    return render(request, 'view_bus.html', {'bus': bus})


# =========================================================
# DRIVER MANAGEMENT
# =========================================================

@login_required(login_url='login')
def drivers(request):
    search = request.GET.get("search", "").strip()
    drivers_qs = Driver.objects.all().order_by("name")

    if search:
        drivers_qs = drivers_qs.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search) |
            Q(license_number__icontains=search)
        )

    context = {
        "drivers": drivers_qs,
        "total_drivers": drivers_qs.count(),
        "active_drivers": drivers_qs.filter(status="Active").count(),
        "inactive_drivers": drivers_qs.filter(status="Inactive").count(),
        "search": search,
    }
    return render(request, "drivers.html", context)


@login_required(login_url='login')
def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('drivers')
    else:
        form = DriverForm()
    return render(request, 'add_driver.html', {'form': form})


@login_required(login_url='login')
def edit_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            return redirect('drivers')
    else:
        form = DriverForm(instance=driver)
    return render(request, 'edit_driver.html', {'form': form, 'driver': driver})


@login_required(login_url='login')
def delete_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    if request.method == 'POST':
        driver.delete()
        return redirect('drivers')
    return render(request, 'delete_driver.html', {'driver': driver})


@login_required(login_url='login')
def view_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    return render(request, 'view_driver.html', {'driver': driver})


# =========================================================
# ROUTE MANAGEMENT
# =========================================================

@login_required(login_url='login')
def routes(request):
    routes_qs = Route.objects.all()
    context = {
        'routes': routes_qs,
        'total_routes': routes_qs.count(),
        'active_routes': routes_qs.filter(status='Active').count(),
        'inactive_routes': routes_qs.filter(status='Inactive').count(),
    }
    return render(request, 'routes.html', context)


@login_required(login_url='login')
def add_route(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('routes')
    else:
        form = RouteForm()
    return render(request, 'add_route.html', {'form': form})


@login_required(login_url='login')
def edit_route(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            return redirect('routes')
    else:
        form = RouteForm(instance=route)
    return render(request, 'edit_route.html', {'form': form, 'route': route})


@login_required(login_url='login')
def delete_route(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST':
        route.delete()
        return redirect('routes')
    return render(request, 'delete_route.html', {'route': route})


@login_required(login_url='login')
def view_route(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    return render(request, 'view_route.html', {'route': route})


# =========================================================
# STOP MANAGEMENT
# =========================================================

@login_required(login_url='login')
def stops(request):
    stops_qs = Stop.objects.select_related('route').all().order_by('route', 'stop_order')
    total_stops = stops_qs.count()
    routes_with_stops = Stop.objects.values('route').distinct().count()
    average_stops = round(total_stops / routes_with_stops, 1) if routes_with_stops > 0 else 0

    context = {
        'stops': stops_qs,
        'total_stops': total_stops,
        'routes_with_stops': routes_with_stops,
        'average_stops': average_stops,
    }
    return render(request, 'stops.html', context)


@login_required(login_url='login')
def add_stop(request):
    if request.method == 'POST':
        form = StopForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stops')
    else:
        form = StopForm()
    return render(request, 'add_stop.html', {'form': form})


@login_required(login_url='login')
def view_stop(request, stop_id):
    stop = get_object_or_404(Stop.objects.select_related('route'), id=stop_id)
    return render(request, 'view_stop.html', {'stop': stop})


@login_required(login_url='login')
def edit_stop(request, stop_id):
    stop = get_object_or_404(Stop, id=stop_id)
    if request.method == 'POST':
        form = StopForm(request.POST, instance=stop)
        if form.is_valid():
            form.save()
            return redirect('stops')
    else:
        form = StopForm(instance=stop)
    return render(request, 'edit_stop.html', {'form': form, 'stop': stop})


@login_required(login_url='login')
def delete_stop(request, stop_id):
    stop = get_object_or_404(Stop.objects.select_related('route'), id=stop_id)
    if request.method == 'POST':
        stop.delete()
        return redirect('stops')
    return render(request, 'delete_stop.html', {'stop': stop})


# =========================================================
# STUDENT MANAGEMENT (ADMIN)
# =========================================================

@login_required(login_url='login')
def students(request):
    students_qs = Student.objects.select_related('route', 'pickup_stop').all().order_by('student_id')
    context = {
        'students': students_qs,
        'total_students': students_qs.count(),
        'active_students': students_qs.filter(status='Active').count(),
        'inactive_students': students_qs.filter(status='Inactive').count(),
    }
    return render(request, 'students.html', context)


@login_required(login_url='login')
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students')
    else:
        form = StudentForm()
    return render(request, 'add_student.html', {'form': form})

# =========================================================
# APPROVE STUDENT & GENERATE DIGITAL BUS PASS
# =========================================================

@login_required(login_url='login')
def approve_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        # Generate unique pass number
        if not student.pass_number:
            student.pass_number = f"SB-{uuid.uuid4().hex[:8].upper()}"

        # Approve student
        student.status = 'Active'

        # Generate pass dates
        student.pass_issued_date = date.today()
        student.pass_expiry_date = date.today() + timedelta(days=365)

        # Activate digital pass
        student.pass_status = 'Active'

        student.save()

        return redirect('students')

    return render(
        request,
        'approve_student.html',
        {'student': student}
    )


@login_required(login_url='login')
def view_student(request, student_id):
    student = get_object_or_404(
        Student.objects.select_related('route', 'pickup_stop'), id=student_id
    )
    return render(request, 'view_student.html', {'student': student})


# @login_required(login_url='login')
# def edit_student(request, student_id):
#     student = get_object_or_404(Student, id=student_id)
#     if request.method == 'POST':
#         form = StudentForm(request.POST, instance=student)
#         if form.is_valid():
#             form.save()
#             return redirect('students')
#     else:
#         form = StudentForm(instance=student)
#     return render(request, 'edit_student.html', {'form': form, 'student': student})

@login_required(login_url='login')
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)

        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('students')
        else:
            messages.error(
                request,
                'Unable to update student. Please correct the errors below.'
            )
    else:
        form = StudentForm(instance=student)

    return render(
        request,
        'edit_student.html',
        {
            'form': form,
            'student': student,
        }
    )



@login_required(login_url='login')
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('students')
    return render(request, 'delete_student.html', {'student': student})


# =========================================================
# PARENT MANAGEMENT (ADMIN)
# =========================================================

@login_required(login_url='login')
def parents(request):
    parents_qs = Parent.objects.select_related('student').all().order_by('name')
    return render(request, 'parents.html', {'parents': parents_qs, 'total_parents': parents_qs.count()})


@login_required(login_url='login')
def add_parent(request):
    if request.method == 'POST':
        form = ParentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('parents')
    else:
        form = ParentForm()
    return render(request, 'add_parent.html', {'form': form})


@login_required(login_url='login')
def view_parent(request, parent_id):
    parent = get_object_or_404(Parent.objects.select_related('student'), id=parent_id)
    return render(request, 'view_parent.html', {'parent': parent})


@login_required(login_url='login')
def edit_parent(request, parent_id):
    parent = get_object_or_404(Parent, id=parent_id)
    if request.method == 'POST':
        form = ParentForm(request.POST, instance=parent)
        if form.is_valid():
            form.save()
            return redirect('parents')
    else:
        form = ParentForm(instance=parent)
    return render(request, 'edit_parent.html', {'form': form, 'parent': parent})


@login_required(login_url='login')
def delete_parent(request, parent_id):
    parent = get_object_or_404(Parent, id=parent_id)
    if request.method == 'POST':
        parent.delete()
        return redirect('parents')
    return render(request, 'delete_parent.html', {'parent': parent})


# =========================================================
# BUS ALLOCATION MANAGEMENT
# =========================================================

@login_required(login_url='login')
def allocation_list(request):
    allocations = BusAllocation.objects.select_related("bus", "driver", "route").order_by("-allocation_date", "-id")
    return render(request, "allocation_list.html", {"allocations": allocations})


@login_required(login_url='login')
def allocation_create(request):
    buses_qs = Bus.objects.all()
    drivers_qs = Driver.objects.all()
    routes_qs = Route.objects.all()

    if request.method == "POST":
        bus_id = request.POST.get("bus")
        driver_id = request.POST.get("driver")
        route_id = request.POST.get("route")
        allocation_date = request.POST.get("allocation_date")
        start_time = request.POST.get("start_time") or None
        end_time = request.POST.get("end_time") or None
        status = request.POST.get("status")

        bus = get_object_or_404(Bus, id=bus_id)
        driver = get_object_or_404(Driver, id=driver_id) if driver_id else None
        route = get_object_or_404(Route, id=route_id)

        BusAllocation.objects.create(
            bus=bus,
            driver=driver,
            route=route,
            allocation_date=allocation_date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )
        messages.success(request, "Bus allocation added successfully.")
        return redirect("allocation_list")

    return render(
        request,
        "allocation_form.html",
        {"buses": buses_qs, "drivers": drivers_qs, "routes": routes_qs}
    )


@login_required(login_url='login')
def allocation_edit(request, pk):
    allocation = get_object_or_404(BusAllocation, id=pk)
    buses_qs = Bus.objects.all()
    drivers_qs = Driver.objects.all()
    routes_qs = Route.objects.all()

    if request.method == "POST":
        allocation.bus_id = request.POST.get("bus")
        allocation.driver_id = request.POST.get("driver") or None
        allocation.route_id = request.POST.get("route")
        allocation.allocation_date = request.POST.get("allocation_date")
        allocation.start_time = request.POST.get("start_time") or None
        allocation.end_time = request.POST.get("end_time") or None
        allocation.status = request.POST.get("status")
        allocation.save()

        messages.success(request, "Bus allocation updated successfully.")
        return redirect("allocation_list")

    return render(
        request,
        "allocation_form.html",
        {"allocation": allocation, "buses": buses_qs, "drivers": drivers_qs, "routes": routes_qs}
    )


@login_required(login_url='login')
def allocation_delete(request, pk):
    allocation = get_object_or_404(BusAllocation, id=pk)
    if request.method == "POST":
        allocation.delete()
        messages.success(request, "Bus allocation deleted successfully.")
        return redirect("allocation_list")
    return render(request, "allocation_confirm_delete.html", {"allocation": allocation})


# =========================================================
# STAFF MANAGEMENT
# =========================================================

@login_required(login_url='login')
def staff(request):
    staff_members = Staff.objects.all()
    context = {
        'staff_members': staff_members,
        'total_staff': staff_members.count(),
        'active_staff': staff_members.filter(status='Active').count(),
        'inactive_staff': staff_members.filter(status='Inactive').count(),
    }
    return render(request, 'staff.html', context)


@login_required(login_url='login')
def add_staff(request):
    if request.method == "POST":
        staff_id = request.POST.get("staff_id", "").strip()
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        department = request.POST.get("department", "").strip()

        if not staff_id:
            return render(request, "add_staff.html", {"error": "Staff ID is required."})

        if Staff.objects.filter(staff_id=staff_id).exists():
            return render(request, "add_staff.html", {"error": f"Staff ID {staff_id} already exists."})

        Staff.objects.create(
            staff_id=staff_id,
            name=name,
            email=email,
            phone=phone,
            department=department
        )
        return redirect("staff")

    return render(request, "add_staff.html")


@login_required(login_url='login')
def edit_staff(request, id):
    staff_member = get_object_or_404(Staff, id=id)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff_member)
        if form.is_valid():
            form.save()
            return redirect('staff')
    else:
        form = StaffForm(instance=staff_member)
    return render(request, 'edit_staff.html', {'form': form, 'staff_member': staff_member})


@login_required(login_url='login')
def delete_staff(request, id):
    staff_member = get_object_or_404(Staff, id=id)
    if request.method == 'POST':
        staff_member.delete()
        return redirect('staff')
    return render(request, 'delete_staff.html', {'staff_member': staff_member})


@login_required(login_url='login')
def view_staff(request, id):
    staff_member = get_object_or_404(Staff, id=id)
    return render(request, 'view_staff.html', {'staff_member': staff_member})


# =========================================================
# ATTENDANCE MANAGEMENT
# =========================================================

@login_required(login_url='login')
def attendance(request):
    attendance_records = BusAttendance.objects.select_related(
        "student", "bus", "boarding_stop"
    ).all().order_by("-date", "-id")

    context = {
        "attendance_records": attendance_records,
        "total_attendance": attendance_records.count(),
        "present_attendance": attendance_records.filter(status="Present").count(),
        "absent_attendance": attendance_records.filter(status="Absent").count(),
    }
    return render(request, "attendance.html", context)


@login_required(login_url='login')
def add_attendance(request):
    if request.method == "POST":
        form = BusAttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance record added successfully!")
            return redirect("attendance")
    else:
        form = BusAttendanceForm()
    return render(request, "add_attendance.html", {"form": form})


# =========================================================
# SYSTEM ANALYTICS
# =========================================================

@login_required(login_url='login')
def analytics(request):
    total_buses = Bus.objects.count()
    active_buses = Bus.objects.filter(status="Active").count()
    total_drivers = Driver.objects.count()
    total_routes = Route.objects.count()
    total_stops = Stop.objects.count()
    total_students = Student.objects.count()
    total_parents = Parent.objects.count()
    total_staff = Staff.objects.count()

    total_attendance = BusAttendance.objects.count()
    total_occupancy = BusOccupancy.objects.count()
    total_locations = BusLocation.objects.count()
    total_predictions = OccupancyPrediction.objects.count()
    total_allocations = BusAllocation.objects.count()

    # Bus Occupancy Analysis
    occupancy_data = []
    buses_qs = Bus.objects.all().order_by("bus_number")

    for bus in buses_qs:
        latest_occ = (
            BusOccupancy.objects.filter(bus=bus).order_by("-date", "-time").first()
        )
        if latest_occ:
            occupied = latest_occ.occupied_seats
            capacity = bus.capacity
            available = max(capacity - occupied, 0)
            percentage = round((occupied / capacity) * 100, 2) if capacity > 0 else 0

            if percentage < 40:
                status = "Low"
            elif percentage < 70:
                status = "Normal"
            elif percentage < 90:
                status = "High"
            else:
                status = "Overcrowded"
        else:
            occupied = 0
            capacity = bus.capacity
            available = capacity
            percentage = 0
            status = "No Data"

        occupancy_data.append({
            "bus_number": bus.bus_number,
            "capacity": capacity,
            "occupied": occupied,
            "available": available,
            "percentage": percentage,
            "status": status,
        })

    total_capacity = sum(item["capacity"] for item in occupancy_data)
    total_occupied = sum(item["occupied"] for item in occupancy_data)
    average_occupancy = round((total_occupied / total_capacity) * 100, 2) if total_capacity > 0 else 0
    overcrowded_buses = sum(1 for item in occupancy_data if item["status"] == "Overcrowded")

    # Route Analysis
    route_data = []
    routes_qs = Route.objects.all().order_by("name")

    for route in routes_qs:
        student_count = Student.objects.filter(route=route).count()
        bus_count = Bus.objects.filter(route=route).count()
        allocation_count = BusAllocation.objects.filter(route=route).count()

        route_capacity = sum(b.capacity for b in Bus.objects.filter(route=route))
        route_occupied = 0
        for b in Bus.objects.filter(route=route):
            latest_occ = BusOccupancy.objects.filter(bus=b).order_by("-date", "-time").first()
            if latest_occ:
                route_occupied += latest_occ.occupied_seats

        route_occupancy = round((route_occupied / route_capacity) * 100, 2) if route_capacity > 0 else 0

        if student_count == 0:
            demand_status = "No Students"
        elif route_capacity == 0:
            demand_status = "No Bus"
        elif student_count > route_capacity:
            demand_status = "High Demand"
        elif student_count >= route_capacity * 0.70:
            demand_status = "Normal Demand"
        else:
            demand_status = "Low Demand"

        route_data.append({
            "route_name": route.name,
            "start_point": route.start_point,
            "destination": route.destination,
            "distance": route.distance_km,
            "travel_time": route.travel_time_min,
            "students": student_count,
            "buses": bus_count,
            "allocations": allocation_count,
            "capacity": route_capacity,
            "occupied": route_occupied,
            "occupancy": route_occupancy,
            "demand_status": demand_status,
        })

    # Bus Utilization
    utilization_data = []
    for bus in Bus.objects.all().order_by("bus_number"):
        capacity = bus.capacity
        latest_occ = BusOccupancy.objects.filter(bus=bus).order_by("-date", "-time").first()
        occupied = latest_occ.occupied_seats if latest_occ else 0
        available = max(capacity - occupied, 0)
        percentage = round((occupied / capacity) * 100, 2) if capacity > 0 else 0

        if percentage == 0:
            status = "No Usage"
        elif percentage < 40:
            status = "Underutilized"
        elif percentage < 70:
            status = "Normal"
        elif percentage < 90:
            status = "High Utilization"
        else:
            status = "Overloaded"

        utilization_data.append({
            "bus_number": bus.bus_number,
            "capacity": capacity,
            "occupied": occupied,
            "available": available,
            "utilization": percentage,
            "status": status,
            "route": bus.route.name if bus.route else "Not Assigned",
            "driver": bus.driver.name if bus.driver else "Not Assigned",
            "allocations": BusAllocation.objects.filter(bus=bus).count(),
        })

    # Attendance Percentages
    present_att = BusAttendance.objects.filter(status="Present").count()
    absent_att = BusAttendance.objects.filter(status="Absent").count()
    attendance_percentage = round((present_att / total_attendance) * 100, 2) if total_attendance > 0 else 0

    context = {
        "total_buses": total_buses,
        "active_buses": active_buses,
        "total_drivers": total_drivers,
        "total_routes": total_routes,
        "total_stops": total_stops,
        "total_students": total_students,
        "total_parents": total_parents,
        "total_staff": total_staff,
        "total_attendance": total_attendance,
        "total_occupancy": total_occupancy,
        "total_locations": total_locations,
        "total_predictions": total_predictions,
        "total_allocations": total_allocations,
        "occupancy_data": occupancy_data,
        "average_occupancy": average_occupancy,
        "overcrowded_buses": overcrowded_buses,
        "route_data": route_data,
        "utilization_data": utilization_data,
        "present_attendance": present_att,
        "absent_attendance": absent_att,
        "attendance_percentage": attendance_percentage,
    }
    return render(request, "analytics.html", context)

def student_registration(request):
    """
    Public student and parent bus registration portal with route fee structure.
    """
    # Fetch active routes with live capacity and fee statistics
    active_routes = Route.objects.filter(status='Active').order_by('name')
    route_fee_list = []

    for route in active_routes:
        buses = Bus.objects.filter(route=route, status='Active')
        total_capacity = sum(b.capacity for b in buses)
        total_occupied = 0

        for b in buses:
            latest_occ = BusOccupancy.objects.filter(bus=b).order_by("-date", "-time").first()
            if latest_occ:
                total_occupied += latest_occ.occupied_seats

        available_seats = max(total_capacity - total_occupied, 0)
        is_full = (available_seats == 0 and total_capacity > 0)

        route_fee_list.append({
            'id': route.id,
            'name': route.name,
            'start_point': route.start_point,
            'destination': route.destination,
            'distance_km': route.distance_km,
            'travel_time_min': route.travel_time_min,
            'fee': route.fee,
            'bus_count': buses.count(),
            'total_capacity': total_capacity,
            'available_seats': available_seats,
            'is_full': is_full,
        })

    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        student_name = request.POST.get("student_name", "").strip()
        student_email = request.POST.get("student_email", "").strip() or None
        student_phone = request.POST.get("student_phone", "").strip()
        student_class = request.POST.get("student_class", "").strip()

        parent_name = request.POST.get("parent_name", "").strip()
        parent_phone = request.POST.get("parent_phone", "").strip()
        parent_email = request.POST.get("parent_email", "").strip() or None

        route_id = request.POST.get("route")
        pickup_stop_id = request.POST.get("pickup_stop")

        if not student_id or not student_name or not student_phone:
            messages.error(request, "Please fill in all required student details.")
            return redirect("student_registration")

        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, f"Student ID '{student_id}' is already registered.")
            return redirect("student_registration")

        selected_route = get_object_or_404(Route, id=route_id) if route_id else None
        selected_stop = get_object_or_404(Stop, id=pickup_stop_id) if pickup_stop_id else None

        student = Student.objects.create(
            student_id=student_id,
            name=student_name,
            email=student_email,
            phone=student_phone,
            student_class=student_class,
            route=selected_route,
            pickup_stop=selected_stop,
            status="Pending",
        )

        Parent.objects.create(
            student=student,
            name=parent_name,
            phone=parent_phone,
            email=parent_email,
        )

        messages.success(
            request,
            f"Registration submitted successfully for {student_name}! Application is pending admin approval."
        )
        return redirect("welcome")

    context = {
        'routes': active_routes,
        'route_fee_list': route_fee_list,
        'class_choices': CLASS_CHOICES,
    }
    return render(request, "student_registration.html", context)




import json
from django.views.decorators.csrf import csrf_exempt

def driver_tracker(request):
    """
    Mobile-friendly interface for bus drivers to transmit real-time GPS coordinates.
    """
    active_buses = Bus.objects.filter(status='Active').select_related('driver', 'route').order_by('bus_number')
    return render(request, "driver_tracker.html", {'buses': active_buses})


@csrf_exempt
def update_location_api(request):
    """
    API endpoint receiving GPS coordinates from the driver's phone.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            bus_id = data.get('bus_id')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            speed = data.get('speed', 0.0)

            if not bus_id or latitude is None or longitude is None:
                return JsonResponse({'success': False, 'error': 'Missing parameters'}, status=400)

            bus = get_object_or_404(Bus, id=bus_id)

            # Record GPS update in BusLocation
            BusLocation.objects.create(
                bus=bus,
                latitude=latitude,
                longitude=longitude,
                speed=float(speed) if speed else 0.0
            )

            return JsonResponse({'success': True, 'message': 'Location updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)



from .models import BusAlert

@login_required(login_url='login')
def manage_alerts(request):
    """
    Admin interface to create and manage delay/emergency alerts.
    """
    buses = Bus.objects.filter(status='Active').select_related('route')
    routes = Route.objects.filter(status='Active')
    alerts = BusAlert.objects.select_related('bus', 'route').order_by('-created_at')

    if request.method == "POST":
        bus_id = request.POST.get("bus") or None
        route_id = request.POST.get("route") or None
        alert_type = request.POST.get("alert_type", "Delay")
        message_text = request.POST.get("message", "").strip()

        if message_text:
            selected_bus = Bus.objects.get(id=bus_id) if bus_id else None
            selected_route = Route.objects.get(id=route_id) if route_id else None

            BusAlert.objects.create(
                bus=selected_bus,
                route=selected_route,
                alert_type=alert_type,
                message=message_text,
                is_active=True
            )
            messages.success(request, "Emergency / Delay alert published successfully!")
            return redirect('manage_alerts')

    return render(request, "manage_alerts.html", {
        'buses': buses,
        'routes': routes,
        'alerts': alerts
    })


@login_required(login_url='login')
def delete_alert(request, alert_id):
    """
    Deactivates or deletes an alert.
    """
    alert = get_object_or_404(BusAlert, id=alert_id)
    alert.delete()
    messages.success(request, "Alert removed.")
    return redirect('manage_alerts')


def active_alerts_api(request):
    """
    API endpoint: returns currently active alerts for the live map ticker.
    """
    active_alerts = BusAlert.objects.filter(is_active=True).select_related('bus', 'route').order_by('-created_at')[:5]
    alert_list = []

    for alert in active_alerts:
        alert_list.append({
            'id': alert.id,
            'type': alert.alert_type,
            'message': alert.message,
            'bus_number': alert.bus.bus_number if alert.bus else 'All Buses',
            'route_name': alert.route.name if alert.route else 'All Routes',
            'time': alert.created_at.strftime("%I:%M %p"),
        })

    return JsonResponse({'success': True, 'alerts': alert_list})
def bus_fees(request):
    """
    Dedicated view to display Route Fees, Assigned Bus Numbers, and Availability.
    """
    routes = Route.objects.filter(status='Active').prefetch_related('buses', 'stops').order_by('name')
    route_details = []

    for route in routes:
        assigned_buses = route.buses.filter(status='Active')
        total_capacity = sum(b.capacity for b in assigned_buses)
        total_occupied = 0

        for bus in assigned_buses:
            latest_occ = BusOccupancy.objects.filter(bus=bus).order_by("-date", "-time").first()
            if latest_occ:
                total_occupied += latest_occ.occupied_seats

        available_seats = max(total_capacity - total_occupied, 0)
        is_full = (available_seats == 0 and total_capacity > 0)

        route_details.append({
            'route': route,
            'buses': assigned_buses,
            'stops': route.stops.all().order_by('stop_order'),
            'total_capacity': total_capacity,
            'available_seats': available_seats,
            'is_full': is_full,
        })

    return render(request, "bus_fees.html", {'route_details': route_details})


def occupancy_page(request):
    return render(request, "occupancy.html")




