# Generated by Django 4.1.7 on 2024-04-02 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_checkpayment_comment_currencyname_forgetpassword_job_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkpayment',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='PostedBy_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='forgetpassword',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='likes',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='views',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='notice',
            name='UserTo_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='likes',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='views',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='productcomment',
            name='PostedBy_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='productcomment',
            name='product_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='productcomment',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='searchproduct',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='viewjob',
            name='job_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='viewjob',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='viewpost',
            name='product_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='viewpost',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
    ]
