from django.db import models
from django.contrib.auth.models import AbstractUser


# ─── ROLES ───────────────────────────────────────────────────────────────────

class Role(models.TextChoices):
    COUNTRY_ADMIN   = 'country_admin',   'Country Admin'
    COUNTY_FOCAL    = 'county_focal',    'County Focal Person'
    SUBCOUNTY_FOCAL = 'subcounty_focal', 'Sub-County Focal Person'
    CHA             = 'cha',             'Community Health Assistant (CHA)'


# ─── LOCATION HIERARCHY ──────────────────────────────────────────────────────

class County(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Counties'
        ordering = ['name']

    def __str__(self):
        return self.name


class SubCounty(models.Model):
    name   = models.CharField(max_length=100)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='subcounties')

    class Meta:
        verbose_name        = 'Sub-County'
        verbose_name_plural = 'Sub-Counties'
        ordering            = ['county__name', 'name']
        unique_together     = ('name', 'county')

    def __str__(self):
        return f"{self.name} ({self.county.name})"


class CommunityHealthUnit(models.Model):
    name      = models.CharField(max_length=150)
    subcounty = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='chus')

    class Meta:
        verbose_name        = 'Community Health Unit'
        verbose_name_plural = 'Community Health Units'
        ordering            = ['subcounty__county__name', 'subcounty__name', 'name']
        unique_together     = ('name', 'subcounty')

    def __str__(self):
        return f"{self.name} – {self.subcounty.name}"




# ─── COMMUNITY HEALTH PROMOTER (no login) ────────────────────────────────────

class CommunityHealthPromoter(models.Model):
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    phone      = models.CharField(max_length=20, blank=True)
    chu        = models.ForeignKey(CommunityHealthUnit, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='chps',
                                   verbose_name='Community Health Unit')

    class Meta:
        verbose_name        = 'Community Health Promoter (CHP)'
        verbose_name_plural = 'Community Health Promoters (CHPs)'
        ordering            = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} – CHP ({self.chu.name if self.chu else 'No CHU'})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

# ─── USER ────────────────────────────────────────────────────────────────────

class User(AbstractUser):
    role      = models.CharField(max_length=20, choices=Role.choices, default=Role.CHA)
    phone     = models.CharField(max_length=20, blank=True)
    county    = models.ForeignKey(County,    on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    subcounty = models.ForeignKey(SubCounty, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    # CHAs/CHPs can belong to one or more CHUs
    chus      = models.ManyToManyField(CommunityHealthUnit, blank=True, related_name='members',
                                       verbose_name='Community Health Units')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # ── Role helpers ─────────────────────────────────────────────────────────
    @property
    def is_country_admin(self):   return self.role == Role.COUNTRY_ADMIN
    @property
    def is_county_focal(self):    return self.role == Role.COUNTY_FOCAL
    @property
    def is_subcounty_focal(self): return self.role == Role.SUBCOUNTY_FOCAL
    @property
    def is_cha(self):             return self.role == Role.CHA
    def scoped_devices(self):
        """Return all Devices visible to this user based on their role/scope."""
        qs = Device.objects.select_related('assigned_to', 'chp_assigned_to', 'chu__subcounty__county')
        if self.is_country_admin:
            return qs
        if self.is_county_focal:
            return qs.filter(chu__subcounty__county=self.county)
        if self.is_subcounty_focal:
            return qs.filter(chu__subcounty=self.subcounty)
        if self.is_cha:
            return qs.filter(chu__in=self.chus.all())
        return qs.none()


# ─── DEVICE ──────────────────────────────────────────────────────────────────

class DeviceType(models.TextChoices):
    PHONE  = 'phone',  'Phone'
    TABLET = 'tablet', 'Tablet'
    LAPTOP = 'laptop', 'Laptop'


class DeviceStatus(models.TextChoices):
    ACTIVE       = 'active',       'Active'
    DAMAGED      = 'damaged',      'Damaged'
    UNDER_REPAIR = 'under_repair', 'Under Repair'
    REPLACED     = 'replaced',     'Replaced'
    LOST         = 'lost',         'Lost'


class Device(models.Model):
    device_type   = models.CharField(max_length=10,  choices=DeviceType.choices)
    make          = models.CharField(max_length=100,  help_text='e.g. Samsung, Lenovo, Tecno')
    model         = models.CharField(max_length=100,  help_text='e.g. Galaxy A14, Tab A8')
    imei          = models.CharField(max_length=20,  unique=True, blank=True, null=True,
                                     verbose_name='IMEI Number',
                                     help_text='15-digit IMEI — applies to phones and tablets')
    serial_number = models.CharField(max_length=100, blank=True, null=True,
                                     verbose_name='Serial Number',
                                     help_text='Manufacturer serial number — applies to all devices')
    status        = models.CharField(max_length=15,   choices=DeviceStatus.choices,
                                     default=DeviceStatus.ACTIVE)
    assigned_to   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='devices')
    chp_assigned_to = models.ForeignKey('CommunityHealthPromoter', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='devices',
                                        verbose_name='Assigned CHP',
                                        help_text='Select if device is assigned to a CHP')
    chu           = models.ForeignKey(CommunityHealthUnit, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='devices',
                                      verbose_name='Community Health Unit')
    date_assigned = models.DateField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    added_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='devices_added')

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        identifier = self.imei or self.serial_number or 'No ID'
        return f"{self.get_device_type_display()} – {self.make} {self.model} ({identifier})"

    @property
    def status_color(self):
        return {
            'active':       'success',
            'damaged':      'danger',
            'under_repair': 'warning',
            'replaced':     'secondary',
            'lost':         'dark',
        }.get(self.status, 'secondary')


# ─── DEVICE LOG ──────────────────────────────────────────────────────────────

class DeviceLog(models.Model):
    device     = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='logs')
    changed_by = models.ForeignKey(User,   on_delete=models.SET_NULL, null=True,
                                   related_name='device_changes')
    old_status = models.CharField(max_length=15, choices=DeviceStatus.choices, blank=True)
    new_status = models.CharField(max_length=15, choices=DeviceStatus.choices, blank=True)
    note       = models.TextField(blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device} → {self.new_status} @ {self.timestamp:%Y-%m-%d %H:%M}"