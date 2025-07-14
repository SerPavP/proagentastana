from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_re_add_landmark_field'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                INSERT INTO landmarks (code, name, created_at) VALUES
                ('central_mosque', 'Центральная (Новая) Мечеть', NOW()),
                ('expo_mega', 'ЭКСПО и ТРЦ "MEGA Silkway"', NOW()),
                ('nazarbayev_university', 'Назарбаев Университет', NOW()),
                ('ellington_mall', 'ТРК "Эллингтон Молл"', NOW()),
                ('barys_astana_arena', 'Барыс Арена и Астана Арена', NOW()),
                ('botanical_garden', 'Ботанический сад', NOW()),
                ('sphere_park', 'Сфера Парк', NOW()),
                ('presidential_park_left', 'Президентский парк (Левый берег)', NOW()),
                ('presidential_park_right', 'Президентский парк (Правый берег)', NOW()),
                ('khan_shatyr', 'Хан Шатыр', NOW()),
                ('abu_dhabi_baiterek', 'Абу Даби Плаза и Байтерек', NOW()),
                ('central_park', 'Центральный парк', NOW()),
                ('pyramid', 'Пирамида', NOW()),
                ('new_station', 'Новый вокзал', NOW()),
                ('triathlon_park', 'Триатлон Парк', NOW()),
                ('meeting_center', 'ТЦ "Встреча"', NOW()),
                ('eurasia_mall', 'ТРЦ "Евразия"', NOW()),
                ('akimat_museum', 'Здание акимата (Музей первого Президента)', NOW()),
                ('koktal_park', 'Парк "Коктал"', NOW()),
                ('artem_market', 'Рынок Артём', NOW()),
                ('old_station', 'Старый вокзал', NOW()),
                ('central_embankment', 'Центральная набережная', NOW())
                ON CONFLICT (code) DO NOTHING;
            """,
            reverse_sql="DELETE FROM landmarks WHERE code IN ('central_mosque', 'expo_mega', 'nazarbayev_university', 'ellington_mall', 'barys_astana_arena', 'botanical_garden', 'sphere_park', 'presidential_park_left', 'presidential_park_right', 'khan_shatyr', 'abu_dhabi_baiterek', 'central_park', 'pyramid', 'new_station', 'triathlon_park', 'meeting_center', 'eurasia_mall', 'akimat_museum', 'koktal_park', 'artem_market', 'old_station', 'central_embankment');"
        ),
    ] 