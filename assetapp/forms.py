from django import forms
from django.db.models import Q
from .models import Device, DeviceStatus, User, CommunityHealthUnit, CommunityHealthPromoter


class DeviceForm(forms.ModelForm):
    class Meta:
        model  = Device
        fields = [
            'device_type', 'make', 'model', 'imei', 'serial_number',
            'status', 'assigned_to', 'chp_assigned_to', 'chu',
            'date_assigned', 'purchase_date', 'notes',
        ]
        widgets = {
            'device_type':   forms.Select(attrs={'class': 'form-select'}),
            'status':        forms.Select(attrs={'class': 'form-select'}),
            'assigned_to':     forms.Select(attrs={'class': 'form-select'}),
            'chp_assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'chu':           forms.Select(attrs={'class': 'form-select'}),
            'make':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Samsung'}),
            'model':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Galaxy A14'}),
            'imei':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 123456789012345'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SN-ABC123456'}),
            'date_assigned': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes':         forms.Textarea(attrs={'rows': 3, 'class': 'form-control',
                                                   'placeholder': 'Any additional notes…'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            if user.is_country_admin:
                chu_qs  = CommunityHealthUnit.objects.all()
                user_qs = User.objects.all()

            elif user.is_county_focal:
                chu_qs  = CommunityHealthUnit.objects.filter(subcounty__county=user.county)
                user_qs = User.objects.filter(
                    Q(county=user.county) |
                    Q(subcounty__county=user.county) |
                    Q(chus__subcounty__county=user.county)
                )

            elif user.is_subcounty_focal:
                chu_qs  = CommunityHealthUnit.objects.filter(subcounty=user.subcounty)
                user_qs = User.objects.filter(
                    Q(subcounty=user.subcounty) |
                    Q(chus__subcounty=user.subcounty)
                )

            elif user.is_cha:
                chu_qs  = user.chus.all()
                user_qs = User.objects.filter(chus__in=user.chus.all())

            else:
                chu_qs  = CommunityHealthUnit.objects.none()
                user_qs = User.objects.none()

            self.fields['chu'].queryset             = chu_qs.distinct()
            self.fields['assigned_to'].queryset     = user_qs.distinct()

            # Scope CHPs to the same CHUs the user can see
            if user.is_country_admin:
                chp_qs = CommunityHealthPromoter.objects.all()
            elif user.is_county_focal:
                chp_qs = CommunityHealthPromoter.objects.filter(chu__subcounty__county=user.county)
            elif user.is_subcounty_focal:
                chp_qs = CommunityHealthPromoter.objects.filter(chu__subcounty=user.subcounty)
            elif user.is_cha:
                chp_qs = CommunityHealthPromoter.objects.filter(chu__in=user.chus.all())
            else:
                chp_qs = CommunityHealthPromoter.objects.none()
            self.fields['chp_assigned_to'].queryset = chp_qs.distinct()

        # Add empty labels
        self.fields['assigned_to'].empty_label     = '— Select system user (CHA/Focal) —'
        self.fields['chp_assigned_to'].empty_label = '— Select CHP (if applicable) —'
        self.fields['chu'].empty_label              = '— Select CHU —'


class DeviceStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=DeviceStatus.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    note = forms.CharField(
        required=False,
        label='Note (optional)',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Describe what happened or what was done…',
        })
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254…'}),
        }


class CHPForm(forms.ModelForm):
    class Meta:
        model  = CommunityHealthPromoter
        fields = ['first_name', 'last_name', 'phone', 'chu']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254…'}),
            'chu':        forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            if user.is_country_admin:
                chu_qs = CommunityHealthUnit.objects.all()
            elif user.is_county_focal:
                chu_qs = CommunityHealthUnit.objects.filter(subcounty__county=user.county)
            elif user.is_subcounty_focal:
                chu_qs = CommunityHealthUnit.objects.filter(subcounty=user.subcounty)
            elif user.is_cha:
                chu_qs = user.chus.all()
            else:
                chu_qs = CommunityHealthUnit.objects.none()
            self.fields['chu'].queryset = chu_qs.distinct().order_by('subcounty__name', 'name')
        self.fields['chu'].empty_label = '— Select CHU —'