# Generated by Django 5.0.4 on 2024-05-10 07:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_rename_listing_user_listing_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='price',
            new_name='start_bid',
        ),
    ]