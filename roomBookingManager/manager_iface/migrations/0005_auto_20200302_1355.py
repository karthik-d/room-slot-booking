# Generated by Django 3.0.3 on 2020-03-02 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager_iface', '0004_auto_20200302_0648'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='slot',
            options={'ordering': ['room__room_no'], 'verbose_name': 'slot'},
        ),
    ]
