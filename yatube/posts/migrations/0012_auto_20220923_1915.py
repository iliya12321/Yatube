# Generated by Django 2.2.16 on 2022-09-23 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20220923_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации'),
        ),
    ]
