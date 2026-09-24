from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("chome_app", "0011_report_reportfile"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="report",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterField(
            model_name="report",
            name="report_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="ReportCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="chome_app.user")),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.AddField(
            model_name="report",
            name="category",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reports", to="chome_app.reportcategory"),
        ),
        migrations.AddConstraint(
            model_name="reportcategory",
            constraint=models.UniqueConstraint(fields=("user", "name"), name="unique_report_category_per_user"),
        ),
    ]