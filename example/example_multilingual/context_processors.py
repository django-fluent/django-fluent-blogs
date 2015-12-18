from django.conf import settings


def multilingual(request):
    lang_list = settings.PARLER_LANGUAGES.get(settings.SITE_ID, ())
    return {
        'MULTILINGUAL_LANGUAGES': [item['code'] for item in lang_list],
    }
