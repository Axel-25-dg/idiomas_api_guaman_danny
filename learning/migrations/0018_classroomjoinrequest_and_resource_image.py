from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0017_gamification_resources_live_sessions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassroomJoinRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('approved', 'Aprobada'), ('rejected', 'Rechazada')], db_index=True, default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_requests', to='learning.classroom')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classroom_join_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('classroom', 'student')},
            },
        ),
        migrations.AddField(
            model_name='teacherresource',
            name='image',
            field=models.ImageField(blank=True, help_text='Imagen subida directamente por el profesor.', max_length=500, null=True, upload_to='teacher_resources/images/%Y/%m/%d/'),
        ),
    ]
