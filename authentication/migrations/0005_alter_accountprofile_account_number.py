# Generated by Django 5.0.6 on 2024-07-17 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0004_alter_accountprofile_account_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accountprofile",
            name="account_number",
            field=models.CharField(max_length=12, null=True, unique=True),
        ),
    ]
