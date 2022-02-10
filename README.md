# How to Setup Backblaze B2 in a Django Project

_Forked from the excellent [simple-s3-setup](https://github.com/sibtc/simple-s3-setup) by [sibtc](https://github.com/sibtc/)_.

Each of the directories are an independent Django Project.

For the most part you can run all of them by following the steps below:

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
