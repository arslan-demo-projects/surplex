import re
from html import unescape


def clean(text):
    if not text:
        return ''
    text = unescape(text or '')
    for c in ['\r\n', '\n\r', u'\n', u'\r', u'\t', u'\xa0', '...']:
        text = text.replace(c, ' ')
    return re.sub(' +', ' ', text).strip()


def join_seq(seq, sep=', '):
    return f'{sep}'.join(clean(e) for e in seq if clean(e))


def clean_seq(seq):
    return [clean(e) for e in seq if clean(e)]


def get_first(seq, up_to=1, sep=""):
    return f"{sep}".join([clean(e) for e in seq if clean(e)][:up_to])


def clean_price(price, currency_symbol='€'):
    return (price or '').replace('.', '').replace(',', '').replace(currency_symbol, '').strip()


def clean_date(dt):
    return dt.split('T')[0]
