# -*- coding: utf-8 -*-
import cookielib
import gzip
import ssl
from HTMLParser import HTMLParser
from StringIO import StringIO

from core.cloudflare import Cloudflare
from core.libs import *

cookies_lock = Lock()
cj = cookielib.MozillaCookieJar()
cookies_path = os.path.join(sysinfo.data_path, "cookies.dat")

# Headers por defecto, si no se especifica nada
default_headers = dict()
default_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0"
default_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
default_headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
default_headers["Accept-Charset"] = "UTF-8"
default_headers["Accept-Encoding"] = "gzip"

# No comprobar certificados
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


def get_cloudflare_headers(url):
    """
    Añade los headers para cloudflare
    :param url: Url
    :type url: str
    """
    domain_cookies = cj._cookies.get("." + urlparse.urlparse(url)[1], {}).get("/", {})

    if "cf_clearance" not in domain_cookies:
        return url

    headers = dict()
    headers["User-Agent"] = default_headers["User-Agent"]
    headers["Cookie"] = "; ".join(["%s=%s" % (c.name, c.value) for c in domain_cookies.values()])

    return url + '|%s' % '&'.join(['%s=%s' % (k, v) for k, v in headers.items()])


def load_cookies():
    """
    Carga el fichero de cookies
    """
    logger.trace()
    cookies_lock.acquire()

    if os.path.isfile(cookies_path):
        try:
            cj.load(cookies_path, ignore_discard=True)
        except Exception:
            logger.info("El fichero de cookies existe pero es ilegible, se borra")
            os.remove(cookies_path)

    cookies_lock.release()


def save_cookies():
    """
    Guarda las cookies
    """
    logger.trace()
    cookies_lock.acquire()
    cj.save(cookies_path, ignore_discard=True)
    cookies_lock.release()


def get_cookies(domain):
    return dict((c.name, c.value) for c in cj._cookies.get("." + domain, {}).get("/", {}).values())


def downloadpage(url, post=None, headers=None, timeout=None, follow_redirects=True, cookies=True, replace_headers=False,
                 add_referer=False, only_headers=False, bypass_cloudflare=True, no_decode=False):
    """
    Descarga una página web y devuelve los resultados
    :type url: str
    :type post: dict, str
    :type headers: dict, list
    :type timeout: int
    :type follow_redirects: bool
    :type cookies: bool, dict
    :type replace_headers: bool
    :type add_referer: bool
    :type only_headers: bool
    :type bypass_cloudflare: bool
    :return: Resultado
    """
    logger.trace()
    response = {}

    # Post tipo dict
    if type(post) == dict:
        post = urllib.urlencode(post)

    # Url quote
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")

    # Headers por defecto, si no se especifica nada
    request_headers = default_headers.copy()

    # Headers pasados como parametros
    if headers is not None:
        if not replace_headers:
            request_headers.update(dict(headers))
        else:
            request_headers = dict(headers)

    # Referer
    if add_referer:
        request_headers["Referer"] = "/".join(url.split("/")[:3])

    logger.info("Headers:")
    logger.info(request_headers)

    # Handlers
    handlers = list()
    handlers.append(urllib2.HTTPHandler(debuglevel=False))

    # No redirects
    if not follow_redirects:
        handlers.append(NoRedirectHandler())
    else:
        handlers.append(HTTPRedirectHandler())

    # Dict con cookies para la sesión
    if type(cookies) == dict:
        for name, value in cookies.items():
            ck = cookielib.Cookie(
                version=0,
                name=name,
                value=value,
                port=None,
                port_specified=False,
                domain=urlparse.urlparse(url)[1],
                domain_specified=False,
                domain_initial_dot=False,
                path='/',
                path_specified=True,
                secure=False,
                expires=time.time() + 3600 * 24,
                discard=True,
                comment=None,
                comment_url=None,
                rest={'HttpOnly': None},
                rfc2109=False
            )
            cj.set_cookie(ck)

    if cookies:
        handlers.append(urllib2.HTTPCookieProcessor(cj))

    # Opener
    opener = urllib2.build_opener(*handlers)

    # Contador
    inicio = time.time()

    # Request
    req = urllib2.Request(url, post, request_headers)

    try:
        logger.info("Realizando Peticion")
        handle = opener.open(req, timeout=timeout)
        logger.info('Peticion realizada')

    except urllib2.HTTPError, handle:
        logger.info('Peticion realizada con error')
        response["sucess"] = False
        response["code"] = handle.code
        response["error"] = handle.__dict__.get("reason", str(handle))
        response["headers"] = handle.headers.dict
        response['cookies'] = get_cookies(urlparse.urlparse(url)[1])
        if not only_headers:
            logger.info('Descargando datos...')
            response["data"] = handle.read()
        else:
            response["data"] = ""
        response["time"] = time.time() - inicio
        response["url"] = handle.geturl()

    except Exception, e:
        logger.info('Peticion NO realizada')
        response["sucess"] = False
        response["code"] = e.__dict__.get("errno", e.__dict__.get("code", str(e)))
        response["error"] = e.__dict__.get("reason", str(e))
        response["headers"] = {}
        response['cookies'] = get_cookies(urlparse.urlparse(url)[1])
        response["data"] = ""
        response["time"] = time.time() - inicio
        response["url"] = url

    else:
        response["sucess"] = True
        response["code"] = handle.code
        response["error"] = None
        response["headers"] = handle.headers.dict
        response['cookies'] = get_cookies(urlparse.urlparse(url)[1])
        if not only_headers:
            logger.info('Descargando datos...')
            response["data"] = handle.read()
        else:
            response["data"] = ""
        response["time"] = time.time() - inicio
        response["url"] = handle.geturl()

    logger.info("Terminado en %.2f segundos" % (response["time"]))
    logger.info("Response sucess     : %s" % (response["sucess"]))
    logger.info("Response code       : %s" % (response["code"]))
    logger.info("Response error      : %s" % (response["error"]))
    logger.info("Response data length: %s" % (len(response["data"])))
    logger.info("Response headers:")
    logger.info(response['headers'])

    # Guardamos las cookies
    if cookies:
        save_cookies()

    # Gzip
    if response["headers"].get('content-encoding') == 'gzip':
        response["data"] = gzip.GzipFile(fileobj=StringIO(response["data"])).read()

    if not no_decode:
        try:
            response["data"] = HTMLParser().unescape(unicode(response["data"], 'utf8')).encode('utf8')
        except:
            pass

    # Anti Cloudflare
    if bypass_cloudflare:
        cf = Cloudflare(response)
        if cf.is_cloudflare:
            logger.info("cloudflare detectado, esperando %s segundos..." % cf.wait_time)
            auth_url = cf.get_url()
            logger.info("Autorizando... url: %s" % auth_url)
            if downloadpage(auth_url, headers=request_headers, replace_headers=True, bypass_cloudflare=False).sucess:
                logger.info("Autorización correcta, descargando página")
                resp = downloadpage(url=response["url"], post=post, headers=headers, timeout=timeout,
                                    follow_redirects=follow_redirects,
                                    cookies=cookies, replace_headers=replace_headers, add_referer=add_referer)
                response["sucess"] = resp.sucess
                response["code"] = resp.code
                response["error"] = resp.error
                response["headers"] = resp.headers
                response["cookies"] = resp.cookies
                response["data"] = resp.data
                response["time"] = resp.time
                response["url"] = resp.url
            else:
                logger.info("No se ha podido autorizar")

    return type('HTTPResponse', (), response)


class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl

    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302


class HTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if 'Authorization' in req.headers:
            req.headers.pop('Authorization')
        return urllib2.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)
