from django.db import migrations, models

import cattube.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='transcoder_token',
            field=models.CharField(
                default=cattube.core.models.generate_transcoder_token,
                editable=False,
                max_length=128,
            ),
        ),
    ]
