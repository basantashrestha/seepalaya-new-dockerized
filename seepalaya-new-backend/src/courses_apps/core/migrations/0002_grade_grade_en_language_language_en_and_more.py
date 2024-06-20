# Generated by Django 4.2 on 2024-05-29 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='grade_en',
            field=models.CharField(max_length=11, null=True, verbose_name='Grade'),
        ),
        migrations.AddField(
            model_name='language',
            name='language_en',
            field=models.CharField(max_length=11, null=True, verbose_name='Language'),
        ),
        migrations.AddField(
            model_name='subject',
            name='subject_en',
            field=models.CharField(max_length=50, null=True, verbose_name='Subject'),
        ),
    ]