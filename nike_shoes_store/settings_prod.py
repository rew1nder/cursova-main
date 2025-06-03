import os
from pathlib import Path
from nike_shoes_store.settings import *

# Set DEBUG to False for production
DEBUG = True

# Secret key should be set by environment variable
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# Add the host names that your site can serve
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    "https://taras-sen-shoes.store",
    "https://*.taras-sen-shoes.store",
]


# Set up database (override with PostgreSQL if needed)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django-db',
        'USER': 'postgres',
        'PASSWORD': ')qnngn>I2&90',
        'HOST': 'database-1.c2h422um28s3.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}



# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS
CSRF_COOKIE_SECURE = False     # Set to True if using HTTPS
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Add WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}