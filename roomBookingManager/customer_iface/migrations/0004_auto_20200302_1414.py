# Generated by Django 3.0.3 on 2020-03-02 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer_iface', '0003_isolatedresdata'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='isolatedresdata',
            options={'ordering': ['date'], 'verbose_name': 'isolated reservation data'},
        ),
    ]
