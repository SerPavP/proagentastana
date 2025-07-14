# Generated manually for thumbnail fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_announcement_commission_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='thumbnail_path',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Thumbnail Path'),
        ),
        migrations.AddField(
            model_name='photo',
            name='thumbnail_size',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Thumbnail Size'),
        ),
    ]
