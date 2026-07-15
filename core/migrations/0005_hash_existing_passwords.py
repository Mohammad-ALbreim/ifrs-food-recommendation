from django.db import migrations
from django.contrib.auth.hashers import make_password, identify_hasher


def hash_existing_passwords(apps, schema_editor):
    Customer = apps.get_model('core', 'Customer')
    Restaurant = apps.get_model('core', 'Restaurant')

    for model in (Customer, Restaurant):
        for obj in model.objects.all():
            try:
                identify_hasher(obj.password)
            except ValueError:
                obj.password = make_password(obj.password)
                obj.save(update_fields=['password'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_meal_image'),
    ]

    operations = [
        migrations.RunPython(hash_existing_passwords, migrations.RunPython.noop),
    ]
