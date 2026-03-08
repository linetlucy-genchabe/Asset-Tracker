from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import (
    Device, DeviceLog, DeviceStatus, DeviceType,
    User, CommunityHealthUnit, SubCounty, County,
    CommunityHealthPromoter,
)
from .forms import DeviceForm, DeviceStatusForm, UserProfileForm, CHPForm


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def device_summary(qs):
    """Return a dict of status counts for a queryset."""
    counts = {s.value: 0 for s in DeviceStatus}
    for row in qs.values('status').annotate(n=Count('id')):
        counts[row['status']] = row['n']
    return {'total': qs.count(), **counts}


def can_edit_device(user, device):
    if user.is_country_admin or user.is_county_focal or user.is_subcounty_focal:
        return True
    if user.is_cha and device.chu in user.chus.all():
        return True
    return False


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user    = request.user
    qs      = user.scoped_devices()
    summary = device_summary(qs)

    breakdown = []
    if user.is_country_admin:
        for county in County.objects.all():
            cqs = qs.filter(chu__subcounty__county=county)
            breakdown.append({'label': county.name, 'summary': device_summary(cqs)})
    elif user.is_county_focal:
        for sc in SubCounty.objects.filter(county=user.county):
            cqs = qs.filter(chu__subcounty=sc)
            breakdown.append({'label': sc.name, 'summary': device_summary(cqs)})
    elif user.is_subcounty_focal:
        for chu in CommunityHealthUnit.objects.filter(subcounty=user.subcounty):
            cqs = qs.filter(chu=chu)
            breakdown.append({'label': chu.name, 'summary': device_summary(cqs)})
    elif user.is_cha:
        for chu in user.chus.all():
            cqs = qs.filter(chu=chu)
            breakdown.append({'label': chu.name, 'summary': device_summary(cqs)})

    recent_logs = DeviceLog.objects.filter(
        device__in=qs
    ).select_related('device', 'changed_by')[:10]

    return render(request, 'assetapp/dashboard.html', {
        'summary':     summary,
        'breakdown':   breakdown,
        'recent_logs': recent_logs,
    })


# ─── DEVICE LIST ─────────────────────────────────────────────────────────────

@login_required
def device_list(request):
    user   = request.user
    qs     = user.scoped_devices()
    status = request.GET.get('status', '')
    dtype  = request.GET.get('type', '')
    search = request.GET.get('q', '').strip()

    if status:
        qs = qs.filter(status=status)
    if dtype:
        qs = qs.filter(device_type=dtype)
    if search:
        qs = qs.filter(
            Q(make__icontains=search)  |
            Q(model__icontains=search) |
            Q(imei__icontains=search)          |
            Q(serial_number__icontains=search)  |
            Q(assigned_to__first_name__icontains=search) |
            Q(assigned_to__last_name__icontains=search)  |
            Q(chu__name__icontains=search)
        )

    return render(request, 'assetapp/device_list.html', {
        'devices':      qs,
        'statuses':     DeviceStatus.choices,
        'device_types': DeviceType.choices,
        'active_status': status,
        'active_type':   dtype,
        'search':        search,
        'total_count':   qs.count(),
    })


# ─── DEVICE DETAIL ───────────────────────────────────────────────────────────

@login_required
def device_detail(request, pk):
    user   = request.user
    device = get_object_or_404(user.scoped_devices(), pk=pk)
    logs   = device.logs.select_related('changed_by').all()
    return render(request, 'assetapp/device_detail.html', {
        'device':   device,
        'logs':     logs,
        'can_edit': can_edit_device(user, device),
    })


# ─── ADD DEVICE ──────────────────────────────────────────────────────────────

@login_required
def device_add(request):
    user = request.user


    if request.method == 'POST':
        form = DeviceForm(request.POST, user=user)
        if form.is_valid():
            device          = form.save(commit=False)
            device.added_by = user
            device.save()
            DeviceLog.objects.create(
                device=device, changed_by=user,
                new_status=device.status, note='Device added to system.',
            )
            messages.success(request, f"✅ Device '{device.make} {device.model}' added successfully.")
            return redirect('device_detail', pk=device.pk)
    else:
        form = DeviceForm(user=user)

    return render(request, 'assetapp/device_form.html', {
        'form': form, 'action': 'Add New',
    })


# ─── EDIT DEVICE ─────────────────────────────────────────────────────────────

@login_required
def device_edit(request, pk):
    user       = request.user
    device     = get_object_or_404(user.scoped_devices(), pk=pk)
    old_status = device.status

    if not can_edit_device(user, device):
        messages.error(request, "You don't have permission to edit this device.")
        return redirect('device_detail', pk=pk)

    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device, user=user)
        if form.is_valid():
            device = form.save()
            if device.status != old_status:
                DeviceLog.objects.create(
                    device=device, changed_by=user,
                    old_status=old_status, new_status=device.status,
                    note=form.cleaned_data.get('notes', ''),
                )
            messages.success(request, "Device updated successfully.")
            return redirect('device_detail', pk=device.pk)
    else:
        form = DeviceForm(instance=device, user=user)

    return render(request, 'assetapp/device_form.html', {
        'form': form, 'action': 'Edit', 'device': device,
    })


# ─── QUICK STATUS CHANGE ─────────────────────────────────────────────────────

@login_required
def device_status(request, pk):
    user   = request.user
    device = get_object_or_404(user.scoped_devices(), pk=pk)

    if not can_edit_device(user, device):
        messages.error(request, "You don't have permission to change this device's status.")
        return redirect('device_detail', pk=pk)

    if request.method == 'POST':
        form = DeviceStatusForm(request.POST)
        if form.is_valid():
            old_status    = device.status
            new_status    = form.cleaned_data['status']
            note          = form.cleaned_data['note']
            device.status = new_status
            device.save()
            DeviceLog.objects.create(
                device=device, changed_by=user,
                old_status=old_status, new_status=new_status, note=note,
            )
            messages.success(request, f"Status updated to '{device.get_status_display()}'.")
            return redirect('device_detail', pk=pk)
    else:
        form = DeviceStatusForm(initial={'status': device.status})

    return render(request, 'assetapp/device_status.html', {
        'form': form, 'device': device,
    })


# ─── PROFILE ─────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'assetapp/profile.html', {'form': form})


# ─── CHP HELPERS ─────────────────────────────────────────────────────────────

def scoped_chps(user):
    """Return CHPs visible to this user based on their role."""
    if user.is_country_admin:
        return CommunityHealthPromoter.objects.select_related('chu__subcounty__county').all()
    if user.is_county_focal:
        return CommunityHealthPromoter.objects.select_related('chu__subcounty__county').filter(
            chu__subcounty__county=user.county)
    if user.is_subcounty_focal:
        return CommunityHealthPromoter.objects.select_related('chu__subcounty__county').filter(
            chu__subcounty=user.subcounty)
    if user.is_cha:
        return CommunityHealthPromoter.objects.select_related('chu__subcounty__county').filter(
            chu__in=user.chus.all())
    return CommunityHealthPromoter.objects.none()


def can_manage_chps(user):
    """Country admin, county focal, sub-county focal and CHA can all manage CHPs."""
    return user.is_country_admin or user.is_county_focal or user.is_subcounty_focal or user.is_cha


# ─── CHP LIST ────────────────────────────────────────────────────────────────

@login_required
def chp_list(request):
    user   = request.user
    qs     = scoped_chps(user)
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)  |
            Q(phone__icontains=search)      |
            Q(chu__name__icontains=search)
        )
    return render(request, 'assetapp/chp_list.html', {
        'chps':        qs,
        'search':      search,
        'total_count': qs.count(),
        'can_manage':  can_manage_chps(user),
    })


# ─── ADD CHP ─────────────────────────────────────────────────────────────────

@login_required
def chp_add(request):
    user = request.user
    if not can_manage_chps(user):
        messages.error(request, "You don't have permission to add CHPs.")
        return redirect('chp_list')

    if request.method == 'POST':
        form = CHPForm(request.POST, user=user)
        if form.is_valid():
            chp = form.save()
            messages.success(request, f"✅ CHP '{chp.get_full_name()}' added successfully.")
            return redirect('chp_list')
    else:
        form = CHPForm(user=user)

    return render(request, 'assetapp/chp_form.html', {
        'form': form, 'action': 'Add New',
    })


# ─── EDIT CHP ────────────────────────────────────────────────────────────────

@login_required
def chp_edit(request, pk):
    user = request.user
    if not can_manage_chps(user):
        messages.error(request, "You don't have permission to edit CHPs.")
        return redirect('chp_list')

    chp = get_object_or_404(scoped_chps(user), pk=pk)

    if request.method == 'POST':
        form = CHPForm(request.POST, instance=chp, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"CHP '{chp.get_full_name()}' updated successfully.")
            return redirect('chp_list')
    else:
        form = CHPForm(instance=chp, user=user)

    return render(request, 'assetapp/chp_form.html', {
        'form': form, 'action': 'Edit', 'chp': chp,
    })