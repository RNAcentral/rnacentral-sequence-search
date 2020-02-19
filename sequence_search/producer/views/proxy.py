import requests

from aiohttp import web
from urllib.parse import urlparse


def proxy(request):
    """Avoids mixed content warnings due to lack of https support"""
    url = request.rel_url.query['url']
    domain = urlparse(url).netloc
    rnacentral_domain = ['193.62.55.44:8002', '193.62.55.123:8002']

    if domain not in rnacentral_domain:
        return web.HTTPBadGateway(text="This proxy is for RNAcentral only")

    try:
        proxied_response = requests.get(url)
        if proxied_response.status_code == 200:
            return web.Response(content_type='text/html', body=proxied_response.text)
        else:
            raise web.HTTPNotFound()
    except:
        raise web.HTTPNotFound()
