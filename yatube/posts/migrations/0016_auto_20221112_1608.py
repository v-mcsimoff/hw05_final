# Generated by Django 2.2.16 on 2022-11-12 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0015_auto_20221112_1335'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',), 'verbose_name_plural': 'Комментарии к постам'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-created',), 'verbose_name': 'пост', 'verbose_name_plural': 'посты'},
        ),
    ]
