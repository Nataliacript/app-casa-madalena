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
                            ('name', models.CharField(max_length=200)),
                            ('bed_number', models.IntegerField()),
                            ('payment_date', models.DateField()),
                            ('check_in', models.DateField()),
                            ('check_out', models.DateField()),
                            ('amount_per_night', models.DecimalField(decimal_places=2, max_digits=10)),
                            ('nights', models.IntegerField()),
                            ('adults', models.IntegerField()),
                            ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                            ('payment_method', models.CharField(max_length=100)),
            ],
        ),
    ]
