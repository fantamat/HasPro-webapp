from pathlib import Path    
import os
import logging


# Configure logging
logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
logger = logging.getLogger(__name__)



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'haspro_app' / 'templates'
STATIC_DIR = BASE_DIR / 'haspro_app' / 'static'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', './media/')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', ";S=qioad=Kdw7}=N=-w,#X;N_h-.ů")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['171f-178-255-168-221.ngrok-free.app', 'localhost', '127.0.0.1', os.environ.get('DOMAIN_NAME', 'haspro.local')]

CSRF_TRUSTED_ORIGINS = [
    "http://" + os.environ.get('DOMAIN_NAME', 'haspro.local'),
    "https://" + os.environ.get('DOMAIN_NAME', 'haspro.local'),
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django apps
    'django.contrib.sites',  # Required for allauth
    
    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Add social providers as needed
    'allauth.socialaccount.providers.google',
    "allauth.socialaccount.providers.linkedin_oauth2",
    # MFA if needed
    'allauth.mfa',
    
    # Your custom user app
    'haspro_app',
    'users',

    'cookie_consent',  # For cookie consent management
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cookie_consent.middleware.CleanCookiesMiddleware',     
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'haspro_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            TEMPLATES_DIR,
            BASE_DIR / 'users' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'haspro_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DATABASE_USER', ''),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', ''),
        'PORT': os.environ.get('DATABASE_PORT', ''),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'cs'

LANGUAGES = [
    ('cs', 'Čeština'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


STATIC_ROOT = os.environ.get('STATIC_ROOT', BASE_DIR / 'staticfiles')
STATIC_URL = 'static/'
STATICFILES_DIRS = [STATIC_DIR]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Allauth settings
AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Allauth settings
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# Disable mandatory email verification during development
# ACCOUNT_EMAIL_VERIFICATION = 'none'  # Or 'none' to completely disable
ACCOUNT_ADAPTER = 'users.allauth.AccountAdapter'
LOGIN_REDIRECT_URL = '/'


# Updated django-allauth Settings
ACCOUNT_LOGIN_METHODS = {'email', 'username'}  # Allow login with either email or username

# Use the new signup fields format with email required (note the asterisk)
ACCOUNT_SIGNUP_FIELDS = ['username', 'email*', 'password1', 'password2']

ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = True


SITE_ID = 1


if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.example.com')
    EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'

    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    SERVER_EMAIL = EMAIL_HOST_USER  # Used for error messages

SUPPORT_EMAILS = os.environ.get('SUPPORT_EMAILS', 'support@palmaf.com').split(',')

# Allauth Google provider configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

