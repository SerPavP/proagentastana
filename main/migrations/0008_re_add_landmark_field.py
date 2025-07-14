from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_add_landmark_field'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE announcements 
            ADD COLUMN IF NOT EXISTS landmark VARCHAR(50) NULL;
            """,
            reverse_sql="""
            ALTER TABLE announcements 
            DROP COLUMN IF EXISTS landmark;
            """
        ),
    ] 