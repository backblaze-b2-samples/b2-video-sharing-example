from botocore.client import Config
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class B2S3Storage(S3Boto3Storage):
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

    def __init__(self, **storage_settings):
        super().__init__(**storage_settings)
        self.config = Config(
            s3={'addressing_style': self.addressing_style},
            signature_version=self.signature_version,
            proxies=self.proxies,
            user_agent_extra=settings.B2_USER_AGENT_EXTRA,
        )


class StaticStorage(B2S3Storage):
    location = settings.B2_STATIC_LOCATION


class PublicMediaStorage(B2S3Storage):
    location = settings.B2_PUBLIC_MEDIA_LOCATION
    file_overwrite = False


class PrivateMediaStorage(B2S3Storage):
    location = settings.B2_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
