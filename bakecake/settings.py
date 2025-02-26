import os
from pathlib import Path
from datetime import datetime
from environs import Env

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

# Добавляем отладочные принты
print("BASE_DIR:", BASE_DIR)
print("BASE_DIR.parent:", BASE_DIR.parent)

SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'order_management',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bakecake.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'bakecake.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DATE_INPUT_FORMATS = ['%Y-%m-%d']
TIME_INPUT_FORMATS = ['%H:%M']


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR.parent, 'static'),
]

# Добавим отладочные принты
print("\nDEBUG STATIC FILES SETTINGS:")
print(f"BASE_DIR: {BASE_DIR}")
print(f"STATIC_URL: {STATIC_URL}")
print(f"STATIC_ROOT: {STATIC_ROOT}")
print(f"STATICFILES_DIRS: {STATICFILES_DIRS}")

# Проверка существования директорий
for static_dir in STATICFILES_DIRS:
    print(f"\nChecking static directory: {static_dir}")
    if os.path.exists(static_dir):
        print("Directory exists!")
        print("Contents:", os.listdir(static_dir))
    else:
        print("Directory does not exist!")
        # Создаем структуру директорий
        os.makedirs(os.path.join(static_dir, 'img'), exist_ok=True)
        os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
        os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)
        os.makedirs(os.path.join(static_dir, 'fonts'), exist_ok=True)
        print("Created directory structure!")

# Печатаем пути к статическим файлам
print("STATICFILES_DIRS:", STATICFILES_DIRS)
print("Full path to static:", os.path.join(BASE_DIR.parent, 'static'))
print("Static directory exists:", os.path.exists(os.path.join(BASE_DIR.parent, 'static')))

# Печатаем содержимое директории static, если она существует
static_dir = os.path.join(BASE_DIR.parent, 'static')
if os.path.exists(static_dir):
    print("Static directory contents:", os.listdir(static_dir))
else:
    print("Static directory not found!")

# Проверяем наличие конкретных файлов
test_files = [
    os.path.join(static_dir, 'img', 'Logo.svg'),
    os.path.join(static_dir, 'css', 'Style.css'),
    os.path.join(static_dir, 'js', 'index.js')
]

for file_path in test_files:
    print(f"File {file_path} exists:", os.path.exists(file_path))


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
