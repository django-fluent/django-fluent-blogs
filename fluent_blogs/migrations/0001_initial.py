import slug_preview.models
from django.conf import settings
from django.db import migrations, models

import fluent_blogs.appsettings
import fluent_blogs.base_models


def make_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    if Site.objects.count() == 0:
        site = Site()
        site.pk = settings.SITE_ID
        site.name = "example"
        site.domain = "example.com"
        site.save()


def remove_site(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        migrations.swappable_dependency(fluent_blogs.appsettings.FLUENT_BLOGS_CATEGORY_MODEL),
    ]

    operations = [
        migrations.RunPython(make_site, reverse_code=remove_site),
        migrations.CreateModel(
            name="Entry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "enable_comments",
                    models.BooleanField(default=True, verbose_name="Enable comments"),
                ),
                (
                    "status",
                    models.CharField(
                        default="d",
                        max_length=1,
                        verbose_name="status",
                        db_index=True,
                        choices=[("p", "Published"), ("d", "Draft")],
                    ),
                ),
                (
                    "publication_date",
                    models.DateTimeField(
                        help_text='When the entry should go live, status must be "Published".',
                        null=True,
                        verbose_name="publication date",
                        db_index=True,
                    ),
                ),
                (
                    "publication_end_date",
                    models.DateTimeField(
                        db_index=True, null=True, verbose_name="publication end date", blank=True
                    ),
                ),
                (
                    "creation_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="creation date"),
                ),
                (
                    "modification_date",
                    models.DateTimeField(auto_now=True, verbose_name="last modification"),
                ),
                (
                    "author",
                    models.ForeignKey(
                        verbose_name="author",
                        on_delete=models.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "categories",
                    models.ManyToManyField(
                        to=fluent_blogs.appsettings.FLUENT_BLOGS_CATEGORY_MODEL,
                        verbose_name="Categories",
                        blank=True,
                    ),
                ),
                (
                    "parent_site",
                    models.ForeignKey(
                        default=fluent_blogs.base_models._get_current_site,
                        on_delete=models.CASCADE,
                        editable=False,
                        to="sites.Site",
                    ),
                ),
            ],
            options={
                "ordering": ("-publication_date",),
                "verbose_name": "Blog entry",
                "verbose_name_plural": "Blog entries",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Entry_Translation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "language_code",
                    models.CharField(db_index=True, max_length=15, verbose_name="Language"),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Title")),
                ("slug", slug_preview.models.SlugPreviewField(verbose_name="Slug")),
                ("intro", models.TextField(verbose_name="Introtext")),
                (
                    "meta_keywords",
                    models.CharField(
                        default="",
                        help_text="When this field is not filled in, the the tags will be used.",
                        max_length=255,
                        verbose_name="keywords",
                        blank=True,
                    ),
                ),
                (
                    "meta_description",
                    models.CharField(
                        default="",
                        help_text="When this field is not filled in, the contents or intro text will be used.",
                        max_length=255,
                        verbose_name="description",
                        blank=True,
                    ),
                ),
                (
                    "meta_title",
                    models.CharField(
                        help_text="When this field is not filled in, the menu title text will be used.",
                        max_length=255,
                        null=True,
                        verbose_name="page title",
                        blank=True,
                    ),
                ),
                (
                    "master",
                    models.ForeignKey(
                        related_name="translations",
                        on_delete=models.CASCADE,
                        editable=False,
                        to="fluent_blogs.Entry",
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Blog entry translation",
                "verbose_name_plural": "Blog entry translations",
            },
            bases=(models.Model,),
        ),
    ]
