# How to Setup Backblaze B2 in a Django Project

_Forked from the excellent [simple-s3-setup](https://github.com/sibtc/simple-s3-setup) by [sibtc](https://github.com/sibtc/)_.

Each of the directories is an independent Django Project.

For the most part you can run all of them by following the steps below:

Configure each of the samples for Backblaze B2 by adding your B2 configuration to `settings.py`:

```bash
AWS_ACCESS_KEY_ID = '<your b2 application key id>'
AWS_SECRET_ACCESS_KEY = '<your b2 application key>'
# AWS_PRIVATE_BUCKET_NAME applies to s3-example-public-and-private only
AWS_PRIVATE_BUCKET_NAME = '<a private bucket>'
AWS_STORAGE_BUCKET_NAME = '<a public bucket>'
AWS_S3_ENDPOINT_URL = 'https://<your b2 endpoint>'
AWS_S3_CUSTOM_DOMAIN = '%s.<your b2 endpoint>' % AWS_STORAGE_BUCKET_NAME
```

```bash
pip install -r requirements.txt
```

```bash
python manage.py migrate
```

```bash
python manage.py createsuperuser
```

```bash
python manage.py collectstatic
```

```bash
python manage.py runserver
```
