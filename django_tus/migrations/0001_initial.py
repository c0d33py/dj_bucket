# Generated by Django 4.2.4 on 2023-08-24 19:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='TusFileModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='GUID')),
                ('filename', models.CharField(blank=True, max_length=255)),
                ('length', models.BigIntegerField(default=-1)),
                ('offset', models.BigIntegerField(default=0)),
                ('metadata', models.JSONField(default=dict)),
                ('tmp_path', models.CharField(max_length=4096, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('uploaded_file', models.FileField(blank=True, max_length=255, null=True, upload_to='public')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tusfilemodel', to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tusfilemodel', to=settings.AUTH_USER_MODEL, verbose_name='user that uploads the file')),
            ],
            options={
                'verbose_name': 'Tus File',
                'verbose_name_plural': 'Tus Files',
                'ordering': ['-id'],
            },
        ),
    ]
