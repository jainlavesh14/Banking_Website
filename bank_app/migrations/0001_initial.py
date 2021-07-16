# Generated by Django 3.1.6 on 2021-07-03 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bank_Model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=90)),
                ('email', models.EmailField(max_length=100)),
                ('mobile_number', models.CharField(max_length=100)),
                ('balance', models.FloatField(max_length=30)),
                ('address', models.CharField(max_length=200)),
            ],
        ),
    ]
