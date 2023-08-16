from .settings import *
import os

DEBUG = False
SECRET_KEY = "django-insecure-" + os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = ["infoseoul.ap-northeast-2.elasticbeanstalk.com", 
                 "infoseoul.link", 
                 "*.infoseoul.link"]

# aws health check
import requests
EC2_PRIVATE_IP = None
try:
    security_token = requests.put(
        'http://169.254.169.254/latest/api/token',
        headers={'X-aws-ec2-metadata-token-ttl-seconds': '60'}).text

    EC2_PRIVATE_IP = requests.get(
        'http://169.254.169.254/latest/meta-data/local-ipv4',
        headers={'X-aws-ec2-metadata-token': security_token},
        timeout=0.01).text
except requests.exceptions.RequestException:
    pass

if EC2_PRIVATE_IP:
    ALLOWED_HOSTS.append(EC2_PRIVATE_IP)
    
    
# aws RDS
if "RDS_DB_NAME" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.environ["RDS_DB_NAME"],
            "USER": os.environ["RDS_USERNAME"],
            "PASSWORD": os.environ["RDS_PASSWORD"],
            "HOST": os.environ["RDS_HOSTNAME"],
            "PORT": os.environ["RDS_PORT"],
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    
    
    
# aws S3
INSTALLED_APPS += ["storages"]
STATIC_ROOT = BASE_DIR / "static/"
STATICFILES_DIRS = []

if "AWS_ACCESS_KEY_ID" in os.environ:
    AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_STORAGE_BUCKET_NAME = "de-3-1-ebdjango"
    AWS_S3_REGION_NAME = "ap-northeast-2"
    # AWS_S3_FILE_OVERWRITE = False
    # AWS_DEFAULT_ACL = None
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
