# Generated by Django 3.0.3 on 2020-03-03 23:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='instance',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='customer', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='manager',
            name='instance',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='manager', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
