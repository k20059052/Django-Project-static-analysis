from ticketing.models import User
from django import template
from urllib import parse
register = template.Library()

# https://stackoverflow.com/questions/63556726/django-template-add-get-parameter-after-current-url
@register.simple_tag
def set_url_param(url, rep_start, rep_end):
    """
    function to replace the query string of url.
    :param `url` is string full url or GET query params.
    :param `rep` is string replacer.
    """
    rep = rep_start + str(rep_end)
    rep_list = rep.split('=')
    queries = url
    if len(rep_list) > 1:
        rep_key = rep_list[0]
        rep_val = rep_list[1]
        if 'http' in url:
            queries = parse.urlsplit(url).query
        dict_params = dict(parse.parse_qsl(queries))
        dict_params.update({rep_key: rep_val})
        queries_list = []

        for (k, v) in dict_params.items():
            queries_list.append('%s=%s' % (k, v))
        base_url_list = url.split('?')
        base_url = base_url_list[0]
        
        if len(base_url_list) <= 1:
            base_url = ''
        queries_str = '&'.join(queries_list)
        return '%s?%s' % (base_url, queries_str)
    return url
