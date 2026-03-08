from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file for local development
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-xyz123')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'jazzmin',                          # must be BEFORE django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'assetapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'asset_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'asset_tracker.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     os.environ.get('DB_NAME',     'chis_devices'),
        'USER':     os.environ.get('DB_USER',     'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST':     os.environ.get('DB_HOST',     'localhost'),
        'PORT':     os.environ.get('DB_PORT',     '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Only include STATICFILES_DIRS if the folder exists (avoids W004 warning)
_static_dir = BASE_DIR / 'static'
if _static_dir.exists():
    STATICFILES_DIRS = [_static_dir]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'assetapp.User'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# ─── JAZZMIN ─────────────────────────────────────────────────────────────────

JAZZMIN_SETTINGS = {
    # ── Branding ─────────────────────────────────────────────
    'site_title':        'CHIS Admin',
    'site_header':       'CHIS Device Manager',
    'site_brand':        'CHIS Devices',
    'welcome_sign':      'Welcome to the CHIS Device Admin Panel',
    'copyright':         'Ministry of Health Kenya',

    # ── Icons (Font Awesome 5) ────────────────────────────────
    'site_icon':         None,
    'site_logo':         None,

    'topmenu_links': [
        {'name': 'Main App',  'url': '/',         'new_window': False, 'icon': 'fas fa-home'},
        {'name': 'Devices',   'url': '/devices/', 'new_window': False, 'icon': 'fas fa-laptop'},
    ],

    # ── Sidebar model icons ───────────────────────────────────
    'icons': {
        'auth':                          'fas fa-users-cog',
        'assetapp.User':                 'fas fa-user',
        'assetapp.County':               'fas fa-map',
        'assetapp.SubCounty':            'fas fa-map-marker-alt',
        'assetapp.CommunityHealthUnit':         'fas fa-clinic-medical',
        'assetapp.CommunityHealthPromoter':     'fas fa-user-nurse',
        'assetapp.Device':               'fas fa-laptop',
        'assetapp.DeviceLog':            'fas fa-history',
    },
    'default_icon_parents':  'fas fa-folder',
    'default_icon_children': 'fas fa-circle',

    # ── Sidebar order ─────────────────────────────────────────
    'order_with_respect_to': [
        'assetapp',
        'assetapp.Device',
        'assetapp.DeviceLog',
        'assetapp.User',
        'assetapp.County',
        'assetapp.SubCounty',
        'assetapp.CommunityHealthUnit',
        'assetapp.CommunityHealthPromoter',
    ],

    # ── UI tweaks ─────────────────────────────────────────────
    'show_sidebar':              True,
    'navigation_expanded':       True,
    'hide_apps':                 [],
    'hide_models':               [],
    'related_modal_active':      True,
    'custom_css':                None,
    'custom_js':                 None,
    'use_google_fonts_cdn':      True,
    'show_ui_builder':           False,
    'changeform_format':         'horizontal_tabs',
    'changeform_format_overrides': {
        'auth.user':  'collapsible',
        'auth.group': 'vertical_tabs',
    },
    'language_chooser': False,
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text':      False,
    'footer_small_text':      False,
    'body_small_text':        False,
    'brand_small_text':       False,
    'brand_colour':           'navbar-primary',
    'accent':                 'accent-primary',
    'navbar':                 'navbar-white navbar-light',
    'no_navbar_border':       False,
    'navbar_fixed':           True,
    'layout_boxed':           False,
    'footer_fixed':           False,
    'sidebar_fixed':          True,
    'sidebar':                'sidebar-dark-primary',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent':   True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style':  False,
    'sidebar_nav_flat_style':    False,
    'theme':                  'default',
    'dark_mode_theme':        None,
    'button_classes': {
        'primary':   'btn-primary',
        'secondary': 'btn-secondary',
        'info':      'btn-info',
        'warning':   'btn-warning',
        'danger':    'btn-danger',
        'success':   'btn-success',
    },
}