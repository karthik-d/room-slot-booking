# Generated by Django 3.0.3 on 2020-03-02 06:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager_iface', '0002_room_manager'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='slot',
            options={'ordering': ['room__room_no'], 'verbose_name': 'slot'},
        ),
    ]
