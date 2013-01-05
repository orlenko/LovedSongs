import copy
import os
import urllib2
import mechanize
from mechanize._useragent import UserAgentBase
from mechanize import _response, _sockettimeout, _rfc3986
from mechanize._mechanize import BrowserStateError
from BeautifulSoup import BeautifulSoup


class Browser(mechanize.Browser):
    """We override native browser because we need to
    support custom headers in request.
    Sadly, mechanize does not make it easy.
    """

    def open(self,
            url,
            data=None,
            timeout=20, # Screw slow connections
            headers=None):
        return self._mech_open(url, data, timeout=timeout, headers=headers)

    def _mech_open(self,
                  url,
                  data=None,
                  update_history=True,
                  visit=None,
                  timeout=_sockettimeout._GLOBAL_DEFAULT_TIMEOUT,
                  headers=None):
        try:
            url.get_full_url
            if ' ' in url._Request__original:
                url._Request__original = url._Request__original.replace(' ', '%20')
        except AttributeError:
            # string URL -- convert to absolute URL if required
            scheme, _authority = _rfc3986.urlsplit(url)[:2]
            if scheme is None:
                # relative URL
                if self._response is None:
                    raise BrowserStateError(
                      "can't fetch relative reference: "
                      "not viewing any document")
                url = _rfc3986.urljoin(self._response.geturl(), url)
            if ' ' in url:
                url = url.replace(' ', '%20')
        request = self._request(url, data, visit, timeout)
        request.add_header("User-agent",
                         "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)")
        if headers:
            for headerName, headerValue in headers.items():
                request.add_header(headerName, headerValue)
        visit = request.visit
        if visit is None:
            visit = True

        if visit:
            self._visit_request(request, update_history)

        success = True
        try:
            response = UserAgentBase.open(self, request, data)
        except urllib2.HTTPError, error:
            success = False
            if error.fp is None:  # not a response
                raise
            response = error
        if visit:
            self._set_response(response, False)
            response = copy.copy(self._response)
        elif response is not None:
            response = _response.upgrade_response(response)
        if not success:
            raise response
        return response


def save_file(context, f, name, encoding):
    print 'Context: %r, name: %r' % (context, name)
    path_parts = [part.decode(encoding).encode('utf8') for part in context['path']]
    path = '/'.join(path_parts)
    if path:
        if not os.path.exists(path):
            os.makedirs(path)
    else:
        path = '.'
    fname = os.path.join(path, name.decode(encoding).encode('utf8'))
    if not os.path.exists(fname):
        open(fname, 'wb').write(f.read())


def crawl(context, url, encoding='utf8'):
    context = context or {
        'path': [],
    }
    browser = Browser()
    browser.set_handle_robots(None)
    browser.open(url)
    for link in browser.links():
        if link.url.startswith('/') or '?' in link.url:
            continue
        if link.url.endswith('/'):
            new_context = copy.deepcopy(context)
            new_context['path'].append(urllib2.unquote(os.path.basename(link.url.strip('/'))))
            print 'Descending into %r' % link.url
            crawl(new_context, link.absolute_url, encoding)
        else:
            print 'Saving %r' % link.url
            save_file(context,
                      mechanize.urlopen(link.absolute_url),
                      urllib2.unquote(os.path.basename(link.url.strip('/'))), encoding)


if __name__ == '__main__':
    urls = [
        'http://pub.jian.spb.ru/%eb%ce%c9%d6%ce%d9%ca%20%d5%c7%cf%cc%cf%cb/2.%e8%d5%c4%cf%d6%c5%d3%d4%d7%c5%ce%ce%d9%c5%20%cb%ce%c9%c7%c9/%ed%d5%da%d9%cb%c1%cc%d8%ce%c1%d1%20%db%cb%c1%d4%d5%cc%cb%c1/Russia/',
    ]
    for url in urls:
        crawl(None, url, 'koi8-r')