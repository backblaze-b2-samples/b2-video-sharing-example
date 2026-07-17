from botocore.client import Config
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


def b2_botocore_config():
    # django-storages==1.12.3 has no setting for user_agent_extra.
    # Set Config before parent initialization so future upgrades revisit this.
    return Config(user_agent_extra=settings.B2_USER_AGENT_EXTRA)


class B2S3Storage(S3Boto3Storage):
    def __init__(self, **storage_settings):
        self.config = b2_botocore_config()
        super().__init__(**storage_settings)

    def get_default_settings(self):
        default_settings = super().get_default_settings()
        default_settings.update({
            'access_key': settings.B2_APPLICATION_KEY_ID,
            'secret_key': settings.B2_APPLICATION_KEY,
            'bucket_name': settings.B2_BUCKET_NAME,
            'object_parameters': settings.B2_OBJECT_PARAMETERS,
            'endpoint_url': settings.B2_STORAGE_ENDPOINT_URL,
            'region_name': settings.B2_REGION,
        })
        return default_settings


class StaticStorage(B2S3Storage):
    location = settings.B2_STATIC_LOCATION
    custom_domain = settings.B2_PUBLIC_URL_LOCATION
    querystring_auth = False
    url_protocol = settings.B2_PUBLIC_URL_PROTOCOL


class PublicMediaStorage(B2S3Storage):
    location = settings.B2_PUBLIC_MEDIA_LOCATION
    custom_domain = settings.B2_PUBLIC_URL_LOCATION
    file_overwrite = False
    querystring_auth = False
    url_protocol = settings.B2_PUBLIC_URL_PROTOCOL


class PrivateMediaStorage(B2S3Storage):
    bucket_name = settings.B2_PRIVATE_BUCKET_NAME
    location = settings.B2_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
