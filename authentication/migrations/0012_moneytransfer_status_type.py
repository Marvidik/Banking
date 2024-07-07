# Generated by Django 5.0.6 on 2024-07-07 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0011_loginpins_accountprofile_moneytransfer_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="moneytransfer",
            name="status_type",
            field=models.CharField(
                choices=[("PENDING", "PENDING"), ("APPROVED", "APPROVED")],
                default="PENDING",
                max_length=20,
            ),
        ),
    ]
