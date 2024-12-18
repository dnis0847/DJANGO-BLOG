# Generated by Django 5.1.4 on 2024-12-12 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_post_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='content_type',
            field=models.CharField(choices=[('PL', 'Plain Text'), ('MD', 'Markdown')], default='PL', max_length=2),
        ),
    ]