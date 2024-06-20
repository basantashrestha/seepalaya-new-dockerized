# Generated by Django 4.2 on 2024-05-29 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_grade_grade_en_language_language_en_and_more'),
        ('epaath', '0003_alter_epaathmodules_abstract'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epaathmodules',
            name='grade',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.grade'),
        ),
        migrations.AlterField(
            model_name='epaathmodules',
            name='language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.language'),
        ),
        migrations.AlterField(
            model_name='epaathmodules',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.subject'),
        ),
    ]