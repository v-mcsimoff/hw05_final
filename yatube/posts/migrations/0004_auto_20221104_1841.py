# Generated by Django 2.2.16 on 2022-11-04 18:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20221019_2100'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'пост', 'verbose_name_plural': 'посты'},
        ),
    ]