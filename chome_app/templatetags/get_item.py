from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def is_url(value):
    if not value:
        return False

    text = str(value).strip()
    if not text:
        return False

    return text.startswith(("http://", "https://", "www.")) or "://" in text
