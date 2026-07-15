# State-only correction: an uncommitted local migration
# (core.0005_alter_customer_id_alter_meal_id_alter_restaurant_id) was applied
# to the live database on 2026-01-05, converting Customer/Meal/Restaurant's
# id from BigAutoField to AutoField, but its migration file was never added
# to version control. The database has always had plain `int` id columns
# since then; this migration only brings Django's on-disk migration state
# back in sync with that reality. database_operations is intentionally
# empty -- no ALTER TABLE runs, since the database is already correct.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_restaurant_status'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='customer',
                    name='id',
                    field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
                ),
                migrations.AlterField(
                    model_name='meal',
                    name='id',
                    field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
                ),
                migrations.AlterField(
                    model_name='restaurant',
                    name='id',
                    field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
                ),
            ],
            database_operations=[],
        ),
    ]
