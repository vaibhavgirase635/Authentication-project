# Generated by Django 4.1.3 on 2022-12-14 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myaccount', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Withdraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default='0')),
                ('Total_balance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myaccount.add_funds')),
            ],
        ),
    ]
