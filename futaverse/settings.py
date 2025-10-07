import os
from datetime import timedelta
from pathlib import Path
import dj_database_url
from  dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1&^(s=j&v^w$2o6^g-8nv@z!l)0!9cmt^be4jn5!oo$gcw89rq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["futaverse-backend-1.onrender.com", "localhost", "127.0.0.1"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'cloudinary_storage',
    # 'cloudinary',
    
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    "corsheaders",
    
    'core',
    'alumnus',
    'students',
    'internships',
]

AUTH_USER_MODEL = "core.User"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware", 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'futaverse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'futaverse.wsgi.application'

# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.environ['DATABASE_URL'], 
#         ssl_require=True)
#     }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': 'aws-1-eu-west-1.pooler.supabase.com',
        'PORT': '6543',
        'OPTIONS': {
            'sslmode': 'verify-full',
            'sslrootcert': os.path.join(BASE_DIR, 'root.crt'),
        }
    }
}


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    # "PAGE_SIZE": 10,
    # "PAGE_SIZE_QUERY_PARAM": "size",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,            
    "BLACKLIST_AFTER_ROTATION": True,        
    "UPDATE_LAST_LOGIN": True,
    "SIGNING_KEY": os.environ.get("DJANGO_SECRET_KEY"),
    "ALGORITHM": "HS256",
    "TOKEN_BLACKLIST_ENABLED": True,
    # "TOKEN_OBTAIN_SERIALIZER": "core.serializers.CustomTokenObtainPairSerializer",
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'FutaVerse API',
    'DESCRIPTION': 'FutaVerse API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    "TAGS": [
        {"name": "Auth", "description": "Authentication endpoints"},
        {"name": "Internships", "description": "Internship management"},
        {"name": "Users", "description": "User management"},
    ],
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.environ.get("MAIL_USERNAME")         
EMAIL_HOST_PASSWORD = os.environ.get("MAIL_PASSWORD") 
DEFAULT_FROM_EMAIL = "Futaverse Support"
SERVER_EMAIL = DEFAULT_FROM_EMAIL        
EMAIL_TIMEOUT = 20  

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  
    "http://127.0.0.1:5173",
    "http://localhost:5174",  
    "http://127.0.0.1:5174",
] 

CORS_ALLOW_CREDENTIALS = True

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET')
}

# MEDIA_URL = '/media/'  
DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'

SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
# SUPABASE_ROOT_PATH = '/futaverse-media/'

AWS_ACCESS_KEY_ID = os.getenv('SUPABASE_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('SUPABASE_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'futaverse-media'
AWS_S3_ENDPOINT_URL = f"{os.getenv('SUPABASE_URL')}/storage/v1/s3"
AWS_S3_REGION_NAME = 'eu-west-1'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_CUSTOM_DOMAIN = f"{os.getenv('SUPABASE_URL').replace('https://', '')}/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}"

APPEND_SLASH=False 
