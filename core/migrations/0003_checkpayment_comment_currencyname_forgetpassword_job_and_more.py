# Generated by Django 4.1.7 on 2024-04-02 14:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_user_num_like_alter_user_num_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('Period', models.CharField(max_length=255)),
                ('approved', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, null=True, upload_to='payment')),
                ('Price', models.CharField(max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('PostedBy_id', models.IntegerField()),
                ('Body', models.CharField(max_length=255)),
                ('PostedBy', models.CharField(max_length=255)),
                ('PostedTo', models.CharField(max_length=255)),
                ('Name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CurrencyName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currencyName', models.CharField(max_length=255)),
                ('symbol', models.CharField(max_length=255)),
                ('Price', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='ForgetPassword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('email', models.EmailField(max_length=255)),
                ('token', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('phone', models.CharField(max_length=20)),
                ('likes', models.IntegerField()),
                ('views', models.IntegerField()),
                ('share_by', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted', models.BooleanField(default=False)),
                ('Title', models.CharField(max_length=255)),
                ('Description', models.CharField(max_length=255)),
                ('Company', models.CharField(max_length=255)),
                ('Website', models.CharField(max_length=255)),
                ('Period', models.CharField(max_length=255)),
                ('JobNature', models.CharField(max_length=255)),
                ('Skill', models.CharField(max_length=255)),
                ('Education', models.CharField(max_length=255)),
                ('State', models.CharField(max_length=255)),
                ('Country', models.CharField(max_length=255)),
                ('Payment', models.CharField(max_length=15)),
                ('AD_payment', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('Body', models.CharField(max_length=255)),
                ('UserTo', models.CharField(max_length=255)),
                ('Name', models.CharField(max_length=255)),
                ('UserFrom', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('opened', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('UserFrom', models.CharField(max_length=255)),
                ('UserTo_id', models.IntegerField()),
                ('Name', models.CharField(max_length=255)),
                ('Message', models.CharField(max_length=255)),
                ('Link', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('opened', models.BooleanField(default=False)),
                ('viewed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('Period', models.CharField(max_length=255)),
                ('start_at', models.DateTimeField(auto_now_add=True)),
                ('end_at', models.DateTimeField()),
                ('active', models.BooleanField(default=True)),
                ('check_payment', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('phone', models.CharField(max_length=20)),
                ('likes', models.IntegerField()),
                ('views', models.IntegerField()),
                ('share_by', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted', models.BooleanField(default=False)),
                ('Category', models.CharField(max_length=255)),
                ('Title', models.CharField(max_length=255)),
                ('Description', models.CharField(max_length=255)),
                ('Itemcondition', models.CharField(max_length=255)),
                ('City', models.CharField(max_length=255)),
                ('State', models.CharField(max_length=255)),
                ('Country', models.CharField(max_length=255)),
                ('Price', models.CharField(max_length=15)),
                ('Negotiation', models.CharField(max_length=3)),
                ('Brand', models.CharField(max_length=255)),
                ('AD_payment', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ProductComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('PostedBy_id', models.IntegerField()),
                ('Body', models.CharField(max_length=255)),
                ('PostedBy', models.CharField(max_length=255)),
                ('Name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('Category', models.CharField(max_length=255)),
                ('Title', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SearchProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('search_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ViewJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('job_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ViewPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('product_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductImg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='media')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='core.product')),
            ],
        ),
    ]
