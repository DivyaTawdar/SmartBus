from django import forms
from .models import (
    Bus,
    Driver,
    Route,
    Stop,
    Student,
    Parent,
    Staff,
    BusAttendance,
)


# =========================================================
# BUS FORM
# =========================================================
class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = [
            'bus_number',
            'registration_number',
            'driver',
            'route',
            'capacity',
            'status',
        ]
        widgets = {
            'bus_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bus number'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter registration number'
            }),
            'driver': forms.Select(attrs={
                'class': 'form-control'
            }),
            'route': forms.Select(attrs={
                'class': 'form-control'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter seat capacity'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


# =========================================================
# DRIVER FORM
# =========================================================
class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            'name',
            'phone',
            'license_number',
            'experience_years',
            'status',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter driver name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter license number'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter experience in years'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


# =========================================================
# ROUTE FORM
# =========================================================
class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = [
            'name',
            'start_point',
            'destination',
            'distance_km',
            'travel_time_min',
            'fee',
            'status',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter route name'
            }),
            'start_point': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter starting point'
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter destination'
            }),
            'distance_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter distance in km',
                'step': '0.01'
            }),
            'travel_time_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter travel time in minutes'
            }),
            'fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter route fee / charges',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


# =========================================================
# STOP FORM
# =========================================================
class StopForm(forms.ModelForm):
    class Meta:
        model = Stop
        fields = [
            'route',
            'name',
            'stop_order',
            'arrival_time',
            'latitude',
            'longitude',
        ]
        widgets = {
            'route': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter stop name'
            }),
            'stop_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: 1',
                'min': 1
            }),
            'arrival_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: 16.8524',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: 74.5815',
                'step': 'any'
            }),
        }


# =========================================================
# STUDENT FORM
# =========================================================
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'student_id',
            'name',
            'email',
            'phone',
            'student_class',
            'route',
            'pickup_stop',
            'status',
        ]
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Student ID'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Student Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Phone Number'
            }),
            'student_class': forms.Select(attrs={
                'class': 'form-control'
            }),
            'route': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pickup_stop': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


# =========================================================
# PARENT FORM
# =========================================================
class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = [
            'student',
            'name',
            'phone',
            'email',
        ]
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Parent Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email Address'
            }),
        }


# =========================================================
# STAFF FORM
# =========================================================
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            'staff_id',
            'name',
            'email',
            'phone',
            'role',
            'department',
            'status',
        ]
        widgets = {
            'staff_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter staff ID'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter staff name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'role': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter staff role'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


# =========================================================
# ATTENDANCE FORM
# =========================================================
class BusAttendanceForm(forms.ModelForm):
    class Meta:
        model = BusAttendance
        fields = [
            "student",
            "bus",
            "date",
            "boarding_stop",
            "boarding_time",
            "status",
        ]
        widgets = {
            "date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "boarding_time": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control"
            }),
            "student": forms.Select(attrs={
                "class": "form-select"
            }),
            "bus": forms.Select(attrs={
                "class": "form-select"
            }),
            "boarding_stop": forms.Select(attrs={
                "class": "form-select"
            }),
            "status": forms.Select(attrs={
                "class": "form-select"
            }),
        }



# from django import forms
# from django.core.serializers import python
# from .models import Bus,Driver, Route,Student,Parent
# from .models import BusAttendance



# class BusForm(forms.ModelForm):

#     class Meta:
#         model = Bus

#         fields = [
#             'bus_number',
#             'registration_number',
#             'driver',
#             'route',
#             'capacity',
#             'status',
#         ]

#         widgets = {
#             'bus_number': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter bus number'
#             }),

#             'registration_number': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter registration number'
#             }),

#             'driver': forms.Select(attrs={
#                 'class': 'form-control'
#             }),

#             'route': forms.Select(attrs={
#                 'class': 'form-control'
#             }),

#             'capacity': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter seat capacity'
#             }),

#             'status': forms.Select(attrs={
#                 'class': 'form-control'
#             }),
#         }

        


# class DriverForm(forms.ModelForm):

#     class Meta:
#         model = Driver

#         fields = [
#             'name',
#             'phone',
#             'license_number',
#             'experience_years',
#             'status',
#         ]

#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter driver name'
#             }),

#             'phone': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter phone number'
#             }),

#             'license_number': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter license number'
#             }),

#             'experience_years': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter experience in years'
#             }),

#             'status': forms.Select(attrs={
#                 'class': 'form-control'
#             }),
#         }

#         from .models import Route


# class RouteForm(forms.ModelForm):
#     class Meta:
#         model = Route
#         fields = [
#             'name',
#             'start_point',
#             'destination',
#             'distance_km',
#             'travel_time_min',
#             'status',
#         ]

#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter route name'
#             }),

#             'start_point': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter starting point'
#             }),

#             'destination': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter destination'
#             }),

#             'distance_km': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter distance in km',
#                 'step': '0.01'
#             }),

#             'travel_time_min': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter travel time in minutes'
#             }),

#             'status': forms.Select(attrs={
#                 'class': 'form-control'
#             }),
#         }


# from django import forms
# from .models import Stop


# # class StopForm(forms.ModelForm):

# #     class Meta:
# #         model = Stop

# #         fields = [
# #             'route',
# #             'name',
# #             'stop_order',
# #             'arrival_time',
# #         ]

# #         widgets = {

# #             'route': forms.Select(attrs={
# #                 'class': 'form-control'
# #             }),

# #             'name': forms.TextInput(attrs={
# #                 'class': 'form-control',
# #                 'placeholder': 'Enter stop name'
# #             }),

# #             'stop_order': forms.NumberInput(attrs={
# #                 'class': 'form-control',
# #                 'placeholder': 'Enter stop order',
# #                 'min': 1
# #             }),

# #             'arrival_time': forms.TimeInput(
# #                 attrs={
# #                     'class': 'form-control',
# #                     'type': 'time'
# #                 }
# #             ),
# #         }
# from django import forms
# from .models import Stop

# class StopForm(forms.ModelForm):
#     class Meta:
#         model = Stop
#         fields = [
#             'route',
#             'name',
#             'stop_order',
#             'arrival_time',
#             'latitude',
#             'longitude',
#         ]
#         widgets = {
#             'route': forms.Select(attrs={'class': 'form-control'}),
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter stop name'
#             }),
#             'stop_order': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Example: 1',
#                 'min': 1
#             }),
#             'arrival_time': forms.TimeInput(attrs={
#                 'class': 'form-control',
#                 'type': 'time'
#             }),
#             'latitude': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Example: 16.8524',
#                 'step': 'any'
#             }),
#             'longitude': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Example: 74.5815',
#                 'step': 'any'
#             }),
#         }


#     #---------------------------------------
    
# class StudentForm(forms.ModelForm):

#     class Meta:
#         model = Student

#         fields = [
#             'student_id',
#             'name',
#             'email',
#             'phone',
#             'course',
#             'year',
#             'route',
#             'pickup_stop',
#             'status',
#         ]

#         widgets = {

#             'student_id': forms.TextInput(
#                 attrs={
#                     'class': 'form-control',
#                     'placeholder': 'Enter Student ID'
#                 }
#             ),

#             'name': forms.TextInput(
#                 attrs={
#                     'class': 'form-control',
#                     'placeholder': 'Enter Student Name'
#                 }
#             ),

#             'email': forms.EmailInput(
#                 attrs={
#                     'class': 'form-control',
#                     'placeholder': 'Enter Email'
#                 }
#             ),

#             'phone': forms.TextInput(
#                 attrs={
#                     'class': 'form-control',
#                     'placeholder': 'Enter Phone Number'
#                 }
#             ),

#             'course': forms.TextInput(
#                 attrs={
#                     'class': 'form-control',
#                     'placeholder': 'Example: MCA'
#                 }
#             ),

#             'year': forms.TextInput(
#                 attrs={
#                     'class': 'form-control',
#                     'placeholder': 'Example: 2nd Year'
#                 }
#             ),

#             'route': forms.Select(
#                 attrs={
#                     'class': 'form-control'
#                 }
#             ),

#             'pickup_stop': forms.Select(
#                 attrs={
#                     'class': 'form-control'
#                 }
#             ),

#             'status': forms.Select(
#                 attrs={
#                     'class': 'form-control'
#                 }
#             ),
#         }
# #----------------------------------------------------------------

# class ParentForm(forms.ModelForm):
#     class Meta:
#         model = Parent
#         fields = [
#             'student',
#             'name',
#             'phone',
#             'email',
#         ]

#         widgets = {
#             'student': forms.Select(
#                 attrs={
#                     'class': 'form-control'
#                 }
#             ),

#             'name': forms.TextInput(
#                 attrs={
#                     'class': 'form-control',
#                     'placeholder': 'Enter Parent Name'
#                 }
#             ),

#             'phone': forms.TextInput(
#                 attrs={
#                     'class': 'form-control',
#                     'placeholder': 'Enter Phone Number'
#                 }
#             ),

#             'email': forms.EmailInput(
#                 attrs={
#                     'class': 'form-control',
#                     'placeholder': 'Enter Email Address'
#                 }
#             ),
#         }


# #========================================================================================

# from .models import Staff


# class StaffForm(forms.ModelForm):
#     class Meta:
#         model = Staff

#         fields = [
#             'staff_id',
#             'name',
#             'email',
#             'phone',
#             'role',
#             'department',
#             'status',
#         ]

#         widgets = {
#             'staff_id': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter staff ID'
#             }),

#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter staff name'
#             }),

#             'email': forms.EmailInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter email address'
#             }),

#             'phone': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter phone number'
#             }),

#             'role': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter staff role'
#             }),

#             'department': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter department'
#             }),

#             'status': forms.Select(attrs={
#                 'class': 'form-control'
#             }),
#         }



#     #===========================================================
# from .models import BusAttendance


# class BusAttendanceForm(forms.ModelForm):

#     class Meta:
#         model = BusAttendance
#         fields = [
#             "student",
#             "bus",
#             "date",
#             "boarding_stop",
#             "boarding_time",
#             "status",
#         ]

#         widgets = {
#             "date": forms.DateInput(
#                 attrs={
#                     "type": "date",
#                     "class": "form-control"
#                 }
#             ),

#             "boarding_time": forms.TimeInput(
#                 attrs={
#                     "type": "time",
#                     "class": "form-control"
#                 }
#             ),

#             "student": forms.Select(
#                 attrs={
#                     "class": "form-select"
#                 }
#             ),

#             "bus": forms.Select(
#                 attrs={
#                     "class": "form-select"
#                 }
#             ),

#             "boarding_stop": forms.Select(
#                 attrs={
#                     "class": "form-select"
#                 }
#             ),

#             "status": forms.Select(
#                 attrs={
#                     "class": "form-select"
#                 }
#             ),
#         }

