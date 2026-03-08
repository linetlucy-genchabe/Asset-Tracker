from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User, County, SubCounty, CommunityHealthUnit, CommunityHealthPromoter, Device, DeviceLog, Role


# ─── CUSTOM FORMS ────────────────────────────────────────────────────────────

class CHISUserCreationForm(UserCreationForm):
    """User creation form that includes role + location fields from step 1."""

    role      = forms.ChoiceField(
        choices=Role.choices,
        required=True,
        initial=None,
        widget=forms.Select(attrs={'id': 'id_role'}),
        help_text='Select the role for this user.'
    )
    phone     = forms.CharField(required=False, max_length=20)
    county    = forms.ModelChoiceField(
        queryset=County.objects.all().order_by('name'),
        required=False,
        empty_label='— Select County —',
        help_text='Required for County Focal Person.'
    )
    subcounty = forms.ModelChoiceField(
        queryset=SubCounty.objects.all().select_related('county').order_by('county__name', 'name'),
        required=False,
        empty_label='— Select Sub-County —',
        help_text='Required for Sub-County Focal Person.'
    )
    chus      = forms.ModelMultipleChoiceField(
        queryset=CommunityHealthUnit.objects.all().select_related('subcounty').order_by('subcounty__name', 'name'),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Community Health Units', is_stacked=False),
        help_text='Select one or more CHUs. Required for CHA.'
    )

    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'role', 'phone', 'county', 'subcounty', 'chus')

    def clean(self):
        cleaned = super().clean()
        role      = cleaned.get('role')
        county    = cleaned.get('county')
        subcounty = cleaned.get('subcounty')
        chus      = cleaned.get('chus')

        if role == Role.COUNTY_FOCAL and not county:
            self.add_error('county', 'County is required for a County Focal Person.')
        if role == Role.SUBCOUNTY_FOCAL and not subcounty:
            self.add_error('subcounty', 'Sub-County is required for a Sub-County Focal Person.')
        if role == Role.CHA and not chus:
            self.add_error('chus', 'At least one CHU must be selected for a CHA.')
        return cleaned


class CHISUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


# ─── USER ADMIN ──────────────────────────────────────────────────────────────

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form         = CHISUserChangeForm
    add_form     = CHISUserCreationForm

    # ── List view ────────────────────────────────────────────────────────────
    list_display  = ['username', 'get_full_name', 'role', 'county', 'subcounty', 'is_active']
    list_filter   = ['role', 'county', 'subcounty', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering      = ['role', 'last_name']

    # ── Edit existing user ───────────────────────────────────────────────────
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('CHIS Role & Location', {
            'fields': ('role', 'county', 'subcounty', 'chus'),
            'description': (
                '<strong>County Focal:</strong> set County only. '
                '<strong>Sub-County Focal:</strong> set Sub-County (and County for reference). '
                '<strong>CHA:</strong> select one or more CHUs.'
            ),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    # ── Create new user ──────────────────────────────────────────────────────
    add_fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone'),
        }),
        ('CHIS Role & Location', {
            'description': (
                '<strong>County Focal Person</strong> → select a County.<br>'
                '<strong>Sub-County Focal Person</strong> → select a Sub-County.<br>'
                '<strong>CHA</strong> → select one or more CHUs.'
            ),
            'fields': ('role', 'county', 'subcounty', 'chus'),
        }),
    )

    filter_horizontal = ['chus']

    class Media:
        js = ('admin/js/chis_user_role.js',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # On creation, M2M chus must be set after save
        if not change and 'chus' in form.cleaned_data:
            obj.chus.set(form.cleaned_data['chus'])


# ─── LOCATION ADMINS ─────────────────────────────────────────────────────────

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display  = ['name']
    search_fields = ['name']
    ordering      = ['name']


@admin.register(SubCounty)
class SubCountyAdmin(admin.ModelAdmin):
    list_display  = ['name', 'county']
    list_filter   = ['county']
    search_fields = ['name', 'county__name']
    ordering      = ['county__name', 'name']


@admin.register(CommunityHealthUnit)
class CHUAdmin(admin.ModelAdmin):
    list_display  = ['name', 'subcounty', 'get_county']
    list_filter   = ['subcounty__county', 'subcounty']
    search_fields = ['name', 'subcounty__name']
    ordering      = ['subcounty__county__name', 'subcounty__name', 'name']

    def get_county(self, obj):
        return obj.subcounty.county.name
    get_county.short_description = 'County'
    get_county.admin_order_field = 'subcounty__county__name'



@admin.register(CommunityHealthPromoter)
class CHPAdmin(admin.ModelAdmin):
    list_display  = ['get_full_name', 'chu', 'get_subcounty', 'get_county', 'phone']
    list_filter   = ['chu__subcounty__county', 'chu__subcounty', 'chu']
    search_fields = ['first_name', 'last_name', 'phone', 'chu__name']
    ordering      = ['last_name', 'first_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Name'

    def get_subcounty(self, obj):
        return obj.chu.subcounty.name if obj.chu else '—'
    get_subcounty.short_description = 'Sub-County'

    def get_county(self, obj):
        return obj.chu.subcounty.county.name if obj.chu else '—'
    get_county.short_description = 'County'


# ─── DEVICE ADMINS ───────────────────────────────────────────────────────────

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display       = ['__str__', 'status', 'assigned_to', 'chp_assigned_to', 'chu', 'updated_at']
    list_filter        = ['status', 'device_type', 'chu__subcounty__county']
    search_fields      = ['make', 'model', 'imei', 'serial_number', 'assigned_to__username']
    autocomplete_fields = ['assigned_to', 'chp_assigned_to', 'chu']
    readonly_fields    = ['added_by']


@admin.register(DeviceLog)
class DeviceLogAdmin(admin.ModelAdmin):
    list_display    = ['device', 'old_status', 'new_status', 'changed_by', 'timestamp']
    list_filter     = ['new_status']
    readonly_fields = ['timestamp']