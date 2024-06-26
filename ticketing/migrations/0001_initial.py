# Generated by Django 4.1.7 on 2023-03-23 11:17

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import ticketing.models.users
import ticketing.models.validators.user_validator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message='First Name must consist of 3-50 letters', regex='^[A-Za-z\\s]{3,}$')])),
                ('last_name', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message='Last Name must consist of 3-50 letters', regex='^[A-Za-z\\s]{3,}$')])),
                ('role', models.CharField(choices=[('ST', 'Student'), ('SP', 'Specialist'), ('DI', 'Director')], default='ST', max_length=2)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['id'],
            },
            managers=[
                ('objects', ticketing.models.users.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('date_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentMessage',
            fields=[
                ('message_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='ticketing.message')),
            ],
            bases=('ticketing.message',),
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Closed', 'Closed')], default='Open', max_length=20)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticketing.department')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, validators=[ticketing.models.validators.user_validator.validate_user_as_student])),
            ],
            options={
                'ordering': ['status'],
            },
        ),
        migrations.CreateModel(
            name='Subsection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator('^\\D+$', 'Only alphabetic characters are allowed in this field.')])),
                ('department', models.ForeignKey(db_column='department', on_delete=django.db.models.deletion.CASCADE, to='ticketing.department')),
            ],
        ),
        migrations.CreateModel(
            name='SpecialistInbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialist', models.ForeignKey(db_column='specialist', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, validators=[ticketing.models.validators.user_validator.validate_user_as_specialist])),
                ('ticket', models.ForeignKey(db_column='ticket', on_delete=django.db.models.deletion.CASCADE, to='ticketing.ticket')),
            ],
        ),
        migrations.CreateModel(
            name='SpecialistDepartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.ForeignKey(db_column='department', on_delete=django.db.models.deletion.CASCADE, to='ticketing.department')),
                ('specialist', models.ForeignKey(db_column='specialist', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, validators=[ticketing.models.validators.user_validator.validate_user_as_specialist])),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ticketing.ticket'),
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=250)),
                ('answer', models.CharField(max_length=750)),
                ('department', models.ForeignKey(db_column='department', on_delete=django.db.models.deletion.CASCADE, to='ticketing.department')),
                ('specialist', models.ForeignKey(db_column='specialist', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('subsection', models.ForeignKey(db_column='subsection', on_delete=django.db.models.deletion.CASCADE, to='ticketing.subsection')),
            ],
            options={
                'ordering': ['department', 'subsection', 'specialist'],
            },
        ),
        migrations.CreateModel(
            name='SpecialistMessage',
            fields=[
                ('message_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='ticketing.message')),
                ('responder', models.ForeignKey(db_column='responder', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, validators=[ticketing.models.validators.user_validator.validate_user_as_specialist])),
            ],
            bases=('ticketing.message',),
        ),
    ]
