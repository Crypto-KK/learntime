import environ

ROOT_DIR = (
    environ.Path(__file__) - 3
)  # (learntime/config/settings/base.py - 3 = learntime/)
APPS_DIR = ROOT_DIR.path("learntime")

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Asia/Shanghai"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "zh-hans"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = False
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres:///learntime")
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    # "django.contrib.admin"
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "ckeditor",
    "ckeditor_uploader",
    "djcelery_email",
    "django_celery_beat",
    "django_crontab",
    #"channels"

    'corsheaders'
]

LOCAL_APPS = [
    "learntime.users.apps.UsersConfig",
    "learntime.student.apps.StudentConfig",
    "learntime.activity.apps.ActivityConfig",
    "learntime.operation.apps.OperationConfig",
    "learntime.statistic.apps.StatisticConfig",
    "learntime.globalconf.apps.GlobalconfConfig",

    "learntime.webapi.apps.WebapiConfig"
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "learntime.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    #"django.contrib.auth.backends.ModelBackend",
    # "learntime.users.backends.EmailBackend",
    "learntime.users.backends.CustomBackend"
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# # https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
# LOGIN_REDIRECT_URL = "users:redirect"
# # https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "users:login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    #"django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "learntime.globalconf.middleware.SystemMiddleware",

    'corsheaders.middleware.CorsMiddleware',
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR("staticfiles"))
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR.path("static"))]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR("media"))

# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR.path("templates"))],
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "learntime.utils.context_processors.settings_context",
                "learntime.utils.oss_processor.ali_media",
            ],
        },
    }
]

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json", 'msgpack']
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "msgpack"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_TIME_LIMIT = 5 * 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_SOFT_TIME_LIMIT = 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#beat-scheduler
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap4"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
#SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
#CSRF_COOKIE_HTTPONLY = False
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
#SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
#X_FRAME_OPTIONS = "DENY"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
# EMAIL_BACKEND = env(
#     "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
# )
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="djcelery_email.backends.CeleryEmailBackend"
)
# https://docs.djangoproject.com/en/2.2/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5


# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(message)s"
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s %(lineno)d %(message)s'
        },  # 日志记录级别+时间日期+模块名称+函数名称+行号+记录消息
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ROOT_DIR.path("logs").path("info.log"),
            'maxBytes': 300 * 1024 * 1024,  # 300M大小
            'backupCount': 5,
            'formatter': 'simple',
            'encoding': 'utf-8'
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "propagate": True,
            "level": "INFO"
        }
    }
    #"root": {"level": "INFO", "handlers": ["console", "file"]},
}

# django-compressor
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/quickstart/#installation
INSTALLED_APPS += ["compressor"]
STATICFILES_FINDERS += ["compressor.finders.CompressorFinder"]

# Your stuff...
# ------------------------------------------------------------------------------
# jwt
import datetime
# drf框架的配置信息
REST_FRAMEWORK = {
    # 用户登陆认证方式
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '3/min',
        'user': '1111/min'
    }
}

# jwt载荷中的有效期设置
JWT_AUTH = {
    #token 有效期
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=1),
    'JWT_ALLOW_REFRESH': True,
     #续期有效期（该设置可在24小时内带未失效的token 进行续期）
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(hours=12),
    # 自定义返回格式，需要手工创建
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'learntime.webapi.utils.jwt_response_payload_handler',
}
REST_FRAMEWORK_EXTENSIONS = {
      # 过期时间  单位是秒
    # 缓存4小时
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 10
}

EMAIL_HOST = env('DJANGO_EMAIL_HOST', default="smtp.qq.com")
EMAIL_USE_SSL = env('DJANGO_EMAIL_USE_SSL', default=True)
EMAIL_PORT = env('DJANGO_EMAIL_PORT', default=465)
EMAIL_HOST_USER = env('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('DJANGO_EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL')
EMAIL_RECIPIENT_LIST = ['705555262@qq.com']

# aliyun
PREFIX_URL = 'http://'
ACCESS_KEY_ID = env('ACCESS_KEY_ID')
ACCESS_KEY_SECRET = env('ACCESS_KEY_SECRET')
END_POINT = env('END_POINT')
BUCKET_NAME = env('BUCKET_NAME')
#ALIYUN_OSS_CNAME = "" # 自定义域名，如果不需要可以不填写
BUCKET_ACL_TYPE = env('BUCKET_ACL_TYPE') # private, public-read, public-read-write
# mediafile将自动上传
DEFAULT_FILE_STORAGE = 'learntime.aliyun_oss2_storage.backends.AliyunMediaStorage'
# staticfile将自动上传
#STATICFILES_STORAGE = 'learntime.aliyun_oss2_storage.backends.AliyunStaticStorage'
ALI_MEDIA_URL = PREFIX_URL + BUCKET_NAME + "." + END_POINT + '/media/'


# ckeditor配置
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Undo', "Redo"],
            ['FontSize', ],
            ['Bold', 'Italic', 'Underline', 'TextColor'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            # ['Link', 'Unlink'],
            ['Image', 'Table'],
            ['Preview', 'Source'],

        ],
        'height': 300,
        'width': 730,
    },
}
CKEDITOR_UPLOAD_PATH = 'activity/images/'
#CKEDITOR_IMAGE_BACKEND = 'pillow'

# 学时类型属性名和中文名匹配
CREDIT_TYPE = {
    "身心素质": "xl_credit",
    "法律素养": "fl_credit",
    "文体素质": "wt_credit",
    "思想品德素质": "sxdd_credit",
    "创新创业素质": "cxcy_credit"
}


#统计模块
CRONJOBS = (
    # ('*/1 * * * *', 'django.core.management.call_command', ['runstat', '--test']),
    # 每个月第一天执行一次 统计学时
    ('0 1 1 * *', 'django.core.management.call_command', ['runstat', '--record']),

)


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
