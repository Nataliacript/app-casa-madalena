from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('despesas', '0001_initial'),  # ou o nome do último arquivo de migration que você tiver
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyFriend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guest_name', models.CharField(max_length=100)),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('adults', models.IntegerField(default=1)),
                ('nights', models.IntegerField(default=1)),
                ('amount_per_night', models.DecimalField(decimal_places=2, max_length=10, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_length=10, max_digits=10)),
                ('payment_method', models.CharField(max_length=100)),
                ('payment_date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]