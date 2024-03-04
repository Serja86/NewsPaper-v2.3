from django import template

register = template.Library()

BAD_WORDS = ('пиздец', 'блядь', 'сука',)

@register.filter()
def censor(text, list_bad_words=BAD_WORDS):
    try:
        for word in list_bad_words:
            if text.find(word) != -1:
                change = f'{word[:1]}{"*" * (len(word) - 1)}'
                text = text.replace(word, change)
            elif text.find(word.capitalize()) != -1:
                change = f'{word.capitalize()[:1]}{"*" * (len(word) - 1)}'
                text = text.replace(word.capitalize(), change)
            elif text.find(word.upper()) != -1:
                change = f'{word.upper()[:1]}{"*" * (len(word) - 1)}'
                text = text.replace(word.upper(), change)
            else:
                pass
    except AttributeError as e:
        print(f'Выявлена ошибка {e}')
    return text

def hide_forbidden(value):
    words = value.split()
    result = []
    for word in words:
        if word in forbidden_words:
            result.append(word[0] + "*"*(len(word)-2) + word[-1])
        else:
            result.append(word)
    return " ".join(result)