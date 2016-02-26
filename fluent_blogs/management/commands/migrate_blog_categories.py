from optparse import make_option

import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import NoArgsCommand, CommandError
from django.db import connection, models, transaction
from django.utils.six import python_2_unicode_compatible
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from parler.models import TranslatableModel

from fluent_blogs import appsettings
from fluent_blogs.models import get_entry_model


class Command(NoArgsCommand):
    """
    Migrate a the blog category model data and constraints.

    The django-categories 1.2.3 release still doesn't have Django 1.8 support.
    The ideal replacement is django-categories-i18n, which also allows the category names
    to be translated. This command migrates the data, and adjusts the foreign key in the M2M table.
    """
    args = "--from=APP.MODEL --to=APP.MODEL"
    help = (
        "Migrate categories to a new model. This can be used when the old project used django-categories,\n"
        "but you would like to migrate that to django-categories-i18n. Take the following steps:\n\n"
        " - make sure 'categories_i18n' is in INSTALLED_APPS.\n"
        " - run: manage.py migrate_blog_categories --from=categories.Category --to=categories_i18n.Category\n"
        " - remove 'categories' from INSTALLED_APPS.\n"
    )
    option_list = NoArgsCommand.option_list + (
        make_option('-f', '--from', action='store', dest='from', help="The old model to read data from"),
        make_option('-t', '--to', action='store', dest='to', help="The new model to migrate to"),
    )

    def handle_noargs(self, **options):
        try:
            from django.apps import apps
        except ImportError:
            # Don't bother migrating old south tables, first migrate to Django 1.7 please.
            raise CommandError("This is a Django 1.7+ command only")

        Entry = get_entry_model()
        CategoryM2M = Entry.categories.through
        old_fk = CategoryM2M._meta.get_field('category')
        CurrentModel = old_fk.rel.to
        self.stdout.write("Current Entry.categories model: <{0}.{1}>".format(
            CurrentModel._meta.app_label, CurrentModel._meta.object_name
        ))

        old = options['from']
        new = options['to']
        if not old or not new:
            raise CommandError("Expected --from and --to options")

        if old.lower() == 'categories.category' and 'categories' not in settings.INSTALLED_APPS:
            # Can't import it in a Django 1.8+ project.
            OldModel = DummyCategoryBase
        else:
            try:
                OldModel = apps.get_model(old)
            except LookupError as e:
                raise CommandError("Invalid --from value: {0}".format(e))

        if not issubclass(OldModel, MPTTModel):
            raise CommandError("Expected MPTT model for --from value")

        try:
            NewModel = apps.get_model(new)
        except LookupError as e:
            raise CommandError("Invalid --to value: {0}".format(e))

        if not issubclass(NewModel, MPTTModel):
            raise CommandError("Expected MPTT model for --to value")

        if NewModel.objects.all().exists():
            raise CommandError("New model already has records, it should be an empty table!")

        old_i18n = issubclass(OldModel, TranslatableModel)
        new_i18n = issubclass(NewModel, TranslatableModel)
        old_title = _detect_title_field(OldModel)
        new_title = _detect_title_field(NewModel)
        mptt_fields = "lft, rght, tree_id, level, parent_id"

        with transaction.atomic():
            if not old_i18n and not new_i18n:
                # Untranslated to untranslated
                self.stdout.write("* Copying category fields...")
                with connection.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO {new_model}(id, slug, {new_title}, {mptt_fields}})'
                        ' SELECT id, slug, {old_title}, {mptt_fields} FROM {old_model}'.format(
                            new_model=NewModel._meta.db_table,
                            new_title=new_title,
                            old_model=OldModel._meta.db_table,
                            old_title=old_title,
                            mptt_fields=mptt_fields,
                        ))
            elif not old_i18n and new_i18n:
                # Untranslated to translated
                # - base table fields
                with connection.cursor() as cursor:
                    self.stdout.write("* Copying category base fields...")
                    cursor.execute(
                        'INSERT INTO {new_model}(id, {mptt_fields})'
                        ' SELECT id, {mptt_fields} FROM {old_model}'.format(
                            new_model=NewModel._meta.db_table,
                            old_model=OldModel._meta.db_table,
                            mptt_fields=mptt_fields,
                        ))
                    # - create translations on fallback language
                    self.stdout.write("* Creating category translations...")
                    cursor.execute(
                        'INSERT INTO {new_translations}(master_id, language_code, slug, {new_title})'
                        ' SELECT id, %s, slug, {old_title} FROM {old_model}'.format(
                            new_translations=NewModel._parler_meta.root_model._meta.db_table,
                            new_title=new_title,
                            old_model=OldModel._meta.db_table,
                            old_title=old_title,
                        ), [appsettings.FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE])
            elif old_i18n and not new_i18n:
                # Reverse, translated to untranslated. Take fallback only
                # Convert all fields back to the single-language table.
                self.stdout.write("* Copying category fields and fallback language fields...")
                for old_category in OldModel.objects.all():
                    translations = old_category.translations.all()
                    try:
                        # Try default translation
                        old_translation = translations.get(language_code=appsettings.FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE)
                    except ObjectDoesNotExist:
                        try:
                            # Try internal fallback
                            old_translation = translations.get(language_code__in=('en-us', 'en'))
                        except ObjectDoesNotExist:
                            # Hope there is a single translation
                            old_translation = translations.get()

                    fields = dict(
                        id=old_category.id,
                        lft=old_category.lft,
                        rght=old_category.rght,
                        tree_id=old_category.tree_id,
                        level=old_category.level,
                        # parler fields
                        _language_code=old_translation.language_code,
                        slug=old_category.slug
                    )
                    fields[new_title] = getattr(old_translation, old_title)
                    NewModel.objects.create(**fields)

            elif old_i18n and new_i18n:
                # Translated to translated
                # - base table
                with connection.cursor() as cursor:
                    self.stdout.write("* Copying category base fields...")
                    cursor.execute(
                        'INSERT INTO {new_model}(id, {mptt_fields})'
                        ' SELECT id, {mptt_fields} FROM {old_model}'.format(
                            new_model=NewModel._meta.db_table,
                            old_model=OldModel._meta.db_table,
                            mptt_fields=mptt_fields,
                        ))
                    # - all translations
                    self.stdout.write("* Copying category translations...")
                    cursor.execute(
                        'INSERT INTO {new_translations}(master_id, language_code, slug, {new_title})'
                        ' SELECT id, languag_code, slug, {old_title} FROM {old_translations}'.format(
                            new_translations=NewModel._parler_meta.root_model._meta.db_table,
                            new_title=new_title,
                            old_translations=OldModel._parler_meta.root_model._meta.db_table,
                            old_title=old_title,
                        ), [appsettings.FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE])
            else:
                raise NotImplementedError()  # impossible combination

            self.stdout.write("* Switching M2M foreign key constraints...")
            __, __, __, kwargs = old_fk.deconstruct()
            kwargs['to'] = NewModel
            new_fk = models.ForeignKey(**kwargs)
            new_fk.set_attributes_from_name(old_fk.name)
            with connection.schema_editor() as schema_editor:
                schema_editor.alter_field(CategoryM2M, old_fk, new_fk)

        self.stdout.write("Done.\n")
        self.stdout.write("You may now remove the old category app from your project, INSTALLED_APPS and database.\n")


@python_2_unicode_compatible
class DummyCategoryBase(MPTTModel):
    """
    This base model includes the absolute bare bones fields and methods. One
    could simply subclass this model and do nothing else and it should work.
    """
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children')
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    class Meta:
        db_table = 'categories_category'
        managed = False

    def __str__(self):
        return self.name


def _detect_title_field(Model):
    if django.VERSION <(1, 8):
        field_names = Model._meta.get_all_field_names()
    else:
        field_names = [f.name for f in Model._meta.get_fields()]

    if 'name' in field_names:
        return 'name'
    elif 'title' in field_names:
        return 'title'

    if issubclass(Model, TranslatableModel):
        field_names = Model._parler_meta.get_translated_fields()
        if 'name' in field_names:
            return 'name'
        elif 'title' in field_names:
            return 'title'

    raise CommandError("No 'name' or 'title' field found in model <{0}.{1}>".format(
        Model.__module__, Model.__name__
    ))
