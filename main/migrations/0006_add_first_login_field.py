# Generated manually for first login tracking

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_add_thumbnail_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_first_login',
            field=models.BooleanField(default=True, verbose_name='Is First Login'),
        ),
    ] 