from .settings import *
from environ import Env
import os

env = Env()
env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = True
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = ["*"]

# DB
if "RDS_DB_NAME_debug" in env:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": env("RDS_DB_NAME_debug"),
            "USER": env("RDS_USERNAME"),
            "PASSWORD": env("RDS_PASSWORD"),
            "HOST": env("RDS_HOSTNAME"),
            "PORT": env("RDS_PORT"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


INSTALLED_APPS += ["storages"]
if "AWS_ACCESS_KEY_ID" in env:
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = "de-3-1-ebdjango"
    AWS_S3_REGION_NAME = "ap-northeast-2"
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = "public-read"
    AWS_S3_CUSTOM_DOMAIN = "%s.s3.%s.amazonaws.com" % (
        AWS_STORAGE_BUCKET_NAME,
        AWS_S3_REGION_NAME,
    )
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    AWS_LOCATION = "static"
    STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
        "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"},
    }
