# Generated by Django 4.2 on 2024-06-07 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_portaluser_address_alter_portaluser_full_name_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmailAddress',
        ),
    ]
