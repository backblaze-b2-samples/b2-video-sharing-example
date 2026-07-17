from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cattube.storage_backends import PrivateMediaStorage, StaticStorage
from cattube.core.models import Video


class B2StorageConfigTests(TestCase):
    def test_static_storage_uses_public_url_base(self):
        storage = StaticStorage()

        self.assertEqual(
            storage.url('css/app.css'),
            f'{settings.B2_PUBLIC_URL_BASE}/{settings.B2_STATIC_LOCATION}/css/app.css',
        )
        self.assertFalse(storage.querystring_auth)

    def test_private_storage_uses_private_bucket_without_public_domain(self):
        storage = PrivateMediaStorage()

        self.assertEqual(storage.bucket_name, settings.B2_PRIVATE_BUCKET_NAME)
        self.assertNotEqual(storage.bucket_name, settings.B2_BUCKET_NAME)
        self.assertFalse(storage.custom_domain)
        self.assertTrue(storage.querystring_auth)
        self.assertIn('(backblaze-b2-samples)', storage.config.user_agent_extra)


class TranscoderNotificationTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='alice')
        self.video = Video.objects.create(user=user, title='Victim', raw='victim.mov')
        self.url = reverse('notification')

    def callback_payload(self, video=None, token=None):
        video = video or self.video
        raw_name = video.raw.name
        stem = raw_name.rsplit('.', 1)[0]
        return {
            'status': 'success',
            'inputObject': f'{settings.B2_PRIVATE_MEDIA_LOCATION}/{raw_name}',
            'outputObject': f'{settings.B2_PRIVATE_MEDIA_LOCATION}/{stem}.mp4',
            'thumbnail': f'{settings.B2_PRIVATE_MEDIA_LOCATION}/{stem}.jpg',
            'token': token if token is not None else video.transcoder_token,
        }

    def test_valid_callback_updates_video_outputs(self):
        response = self.client.post(
            self.url,
            self.callback_payload(),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 204)
        self.video.refresh_from_db()
        self.assertEqual(self.video.transcoded.name, 'victim.mp4')
        self.assertEqual(self.video.thumbnail.name, 'victim.jpg')

    def test_missing_token_is_rejected(self):
        payload = self.callback_payload()
        payload.pop('token')

        response = self.client.post(self.url, payload, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.video.refresh_from_db()
        self.assertFalse(self.video.transcoded)
        self.assertFalse(self.video.thumbnail)

    def test_invalid_token_is_rejected(self):
        response = self.client.post(
            self.url,
            self.callback_payload(token='wrong-token'),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)
        self.video.refresh_from_db()
        self.assertFalse(self.video.transcoded)
        self.assertFalse(self.video.thumbnail)

    def test_token_for_one_video_cannot_update_another_video(self):
        user = User.objects.create_user(username='mallory')
        attacker_video = Video.objects.create(user=user, title='Attacker', raw='attacker.mov')

        response = self.client.post(
            self.url,
            self.callback_payload(token=attacker_video.transcoder_token),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)
        self.video.refresh_from_db()
        self.assertFalse(self.video.transcoded)
        self.assertFalse(self.video.thumbnail)

    def test_output_keys_must_match_expected_private_names(self):
        payload = self.callback_payload()
        payload['outputObject'] = f'{settings.B2_PRIVATE_MEDIA_LOCATION}/attacker.mp4'

        response = self.client.post(self.url, payload, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.video.refresh_from_db()
        self.assertFalse(self.video.transcoded)
        self.assertFalse(self.video.thumbnail)

    def test_output_keys_must_stay_inside_private_prefix(self):
        payload = self.callback_payload()
        payload['thumbnail'] = f'{settings.B2_PUBLIC_MEDIA_LOCATION}/victim.jpg'

        response = self.client.post(self.url, payload, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.video.refresh_from_db()
        self.assertFalse(self.video.transcoded)
        self.assertFalse(self.video.thumbnail)
