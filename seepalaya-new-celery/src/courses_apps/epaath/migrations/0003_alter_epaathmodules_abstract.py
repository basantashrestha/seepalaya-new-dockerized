# Generated by Django 4.2 on 2024-05-29 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epaath', '0002_remove_epaathmodules_is_published_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epaathmodules',
            name='abstract',
            field=models.TextField(blank=True, null=True),
        ),
    ]
