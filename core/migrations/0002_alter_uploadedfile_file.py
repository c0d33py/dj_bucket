# Generated by Django 4.2.4 on 2023-08-26 14:55

from django.db import migrations
import s3_file_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='file',
            field=s3_file_field.fields.S3FileField(),
        ),
    ]
