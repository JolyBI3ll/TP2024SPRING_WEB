# Generated by Django 5.0.4 on 2024-04-10 15:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0002_alter_answerlike_status_alter_questionlike_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerlike',
            name='status',
            field=models.CharField(choices=[('l', 'Like'), ('d', 'Dislike'), ('n', 'Not liked')], default='n',
                                   max_length=10),
        ),
        migrations.AlterField(
            model_name='questionlike',
            name='status',
            field=models.CharField(choices=[('l', 'Like'), ('d', 'Dislike'), ('n', 'Not liked')], default='n',
                                   max_length=10),
        ),
    ]