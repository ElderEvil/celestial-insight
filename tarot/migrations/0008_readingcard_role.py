# Generated by Django 5.1.5 on 2025-01-16 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tarot', '0007_alter_card_number_alter_reading_celestial_insight'),
    ]

    operations = [
        migrations.AddField(
            model_name='readingcard',
            name='role',
            field=models.CharField(blank=True, help_text='Role of the card in this specific reading (e.g., Outcome, Advice, Significator).', max_length=50, null=True, verbose_name='Role'),
        ),
    ]
