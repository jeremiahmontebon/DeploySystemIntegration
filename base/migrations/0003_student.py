# Generated by Django 5.0 on 2024-04-24 17:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_delete_student'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(default='', max_length=50)),
                ('last_name', models.CharField(default='', max_length=50)),
                ('face_image', models.ImageField(upload_to='student_faces')),
                ('course', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='base.course')),
            ],
        ),
    ]