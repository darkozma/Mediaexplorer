# -*- coding: utf-8 -*-
from core.libs import *
import base64
import binascii
from lib.aes import AESModeOfOperationCBC
import hashlib

HOST = "https://pelis123.tv"

LNG = Languages({
    Languages.sub_es: ['Subtitulado'],
    Languages.es: ['Castellano'],
    Languages.en: ['english'],
    Languages.la: ['Latino Dub'],
})

QLT = Qualities({
    Qualities.hd_full: ['Hd 1080'],
    Qualities.hd: ['HD'],
    Qualities.rip: ['Hd Rip'],
    Qualities.scr: ['CAM-TS'],
})


def mainlist(item):
    logger.trace()

    itemlist = list()

    new_item = item.clone(
        type='label',
        label="Películas",
        category='movie',
        thumb='thumb/movie.png',
        icon='icon/movie.png',
        poster='poster/movie.png'
    )
    itemlist.append(new_item)
    itemlist.extend(menupeliculas(new_item))

    new_item = item.clone(
        type='label',
        label="Series",
        category='tvshow',
        thumb='thumb/tvshow.png',
        icon='icon/tvshow.png',
        poster='poster/tvshow.png',
    )
    itemlist.append(new_item)
    itemlist.extend(menuseries(new_item))

    return itemlist


def menupeliculas(item):
    logger.trace()

    itemlist = list()

    itemlist.append(item.clone(
        label='Novedades',
        action='newest',
        content_type='movies',
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        label='Destacadas',
        action='movies',
        url=HOST + '/ajax.php',
        post={'Ajax_Filter': True, 'order': 'asc', 'orderby': 'Title', 'page': 1, 'type': 'movie', 'hot': 'featured'},
        content_type='movies',
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        label='Generos',
        action='generos',
        url=HOST + '/film.html',
        content_type='items',
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        label='Recientes',
        action='movies',
        url=HOST + '/ajax.php',
        post={'Ajax_Filter': True, 'order': 'desc', 'orderby': 'Year', 'page': 1, 'type': 'movie'},
        content_type='movies',
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        label='Buscar',
        action='search',
        content_type='movies',
        query=True,
        type='search',
        group=True
    ))
    return itemlist


def menuseries(item):
    logger.trace()

    itemlist = list()

    itemlist.append(item.clone(
        label='Últimos Episodios',
        action='tv_newest',
        content_type='episodes',
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        label='Generos',
        action='tv_generos',
        url=HOST + '/series.html',
        content_type='items',
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        label='Recientes',
        action='tvshows',
        url=HOST + '/ajax.php',
        post={'Ajax_Filter': True, 'order': 'desc', 'orderby': 'Year', 'page': 1, 'type': 'series'},
        content_type='tvshows',
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        label='Buscar',
        action='tv_search',
        content_type='tvshows',
        query=True,
        type='search',
        group=True
    ))
    return itemlist


def generos(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, '<option value="">Géneros: Todas</option>(.*?)</select>')

    patron = '<option value="([^"]+)">([^<]+)</option>'

    for value, name in re.compile(patron).findall(data):
        itemlist.append(item.clone(
            label=name,
            url='https://pelis123.tv/ajax.php',
            post={'Ajax_Filter': True, 'order': 'asc', 'orderby': 'Title', 'page': 1, 'type': 'movie', 'genre': value},
            content_type='movies',
            action='movies'
        ))

    return itemlist


def tv_generos(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    data = scrapertools.find_single_match(data, '<option value="">Géneros: Todas</option>(.*?)</select>')

    patron = '<option value="([^"]+)">([^<]+)</option>'

    for value, name in re.compile(patron).findall(data):
        itemlist.append(item.clone(
            label=name,
            url='https://pelis123.tv/ajax.php',
            post={'Ajax_Filter': True, 'order': 'asc', 'orderby': 'Title', 'page': 1, 'type': 'series', 'genre': value},
            content_type='tvshows',
            action='tvshows'
        ))

    return itemlist


def movies(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url, post=item.post).data

    movie_list = jsontools.load_json(fix_json(data))

    for movie in movie_list:
        itemlist.append(item.clone(
            action='findvideos',
            title=movie['title'],
            url=movie['url'],
            poster=movie['poster'],
            quality=QLT.get(movie['quality']),
            plot=movie['plot'],
            year=movie['year']['title'],
            type='movie',
            content_type='servers'
        ))

    # Paginador
    if movie_list[-1]['currentpage'] < movie_list[-1]['totalpage']:
        item.post.update({'page': movie_list[-1]['currentpage'] + 1})
        itemlist.append(item.clone(type='next'))

    return itemlist


def tvshows(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url, post=item.post).data

    tv_list = jsontools.load_json(fix_json(data))

    titles = []

    for tvshow in tv_list:
        if tvshow['title'] in titles:
            continue
        itemlist.append(item.clone(
            action='seasons',
            title=tvshow['title'],
            url=HOST + '/ajax.php',
            post={'Ajax_Filter': True, 'order': 'asc', 'orderby': 'Title', 'page': 1, 'type': 'series',
                  'search': tvshow['title']},
            poster=tvshow['poster'],
            quality=QLT.get(tvshow['quality']),
            plot=tvshow['plot'],
            year=tvshow['year']['title'],
            type='tvshow',
            content_type='seasons'
        ))
        titles.append(tvshow['title'])

    # Paginador
    if tv_list[-1]['currentpage'] < tv_list[-1]['totalpage']:
        item.post.update({'page': tv_list[-1]['currentpage'] + 1})
        itemlist.append(item.clone(type='next'))

    return itemlist


def seasons(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url, post=item.post).data

    tv_list = jsontools.load_json(fix_json(data))

    for tvshow in tv_list:
        if tvshow['title'] != item.title:
            continue
        season = int(tvshow['episode'].split('S')[1].split('E')[0])
        itemlist.append(item.clone(
            action='episodes',
            title='Temporada %s' % season,
            poster=tvshow['poster'],
            quality=QLT.get(tvshow['quality']),
            plot=tvshow['plot'],
            year=tvshow['year']['title'],
            url=tvshow['url'],
            type='season',
            season=season,
            content_type='episodes',
            tvshowtitle=item.title
        ))

    return itemlist


def episodes(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<li action="watch_playlist-item".*?episode="([^"]+)"> <a href="([^"]+)">.*?src="([^"]+)".*?<p>(.*?)</p>'

    for episode, url, thumb, lang in scrapertools.find_multiple_matches(data, patron):
        lng = scrapertools.find_multiple_matches(lang, 'alt="([^"]+)"')
        itemlist.append(item.clone(
            url=url,
            type='episode',
            lang=[LNG.get(l) for l in lng],
            action='findvideos',
            thumb=thumb,
            content_type='servers',
            title='Episodio %s' % episode,
            episode=int(episode)
        ))

    return itemlist


def newest(item):
    logger.trace()
    itemlist = []

    item.url = item.url or HOST + '/film.html'
    data = httptools.downloadpage(item.url).data

    patron = '<div class="tray-item item-medium init"> <div class="tray-item-content"> ' \
             '<a href="(?P<url>http[^"]+)">.*?src="(?P<poster>http[^"]+)".*?href="[^"]+">(?P<title>[^<]+).*?' \
             'class="tray-item-quality"> <div>(?P<quality>[^<]+).*?<div class="tray-item-episode-tag">(?P<lang>.*?)' \
             '<div class="tray-item-play">(.*?).*?<br><br>(?P<plot>.*?)">'

    for movie in re.compile(patron, re.DOTALL).finditer(data):
        title = scrapertools.find_single_match(movie.group('title'), "(.*) \(\d{4}\)") or movie.group('title')
        year = scrapertools.find_single_match(movie.group('title'), ".* \((\d{4})\)")
        lng = scrapertools.find_multiple_matches(movie.group('lang'), 'alt="([^"]+)"')
        itemlist.append(item.clone(
            action='findvideos',
            title=title,
            url=movie.group('url'),
            poster=movie.group('poster'),
            quality=QLT.get(movie.group('quality')),
            lang=[LNG.get(l) for l in lng],
            plot=movie.group('plot'),
            year=year,
            type='movie',
            content_type='servers'
        ))

    # Paginador
    next_url = scrapertools.find_single_match(data,
                                              '<li class="active"><a href="\?page=\d+">\d+</a></li> '
                                              '<li><a href="\?(page=\d+)">\d+</a></li>')
    if next_url:
        url = list(urlparse.urlparse(item.url))
        url[4] = next_url
        itemlist.append(item.clone(url=urlparse.urlunparse(url), type='next'))

    return itemlist


def tv_newest(item):
    logger.trace()
    itemlist = []

    item.url = item.url or HOST + '/series.html'
    data = httptools.downloadpage(item.url).data

    patron = '<div class="tray-item item-medium init"> <div class="tray-item-content"> ' \
             '<a href="(?P<url>http[^"]+)">.*?src="(?P<poster>http[^"]+)".*?href="[^"]+">(?P<title>[^<]+).*?' \
             '<div class="tray-item-episodes">(?P<episode>[^<]+)</div>.*?class="tray-item-quality"> ' \
             '<div>(?P<quality>[^<]+).*?<div class="tray-item-episode-tag">(?P<lang>.*?)' \
             '<div class="tray-item-play">(.*?).*?<br><br>(?P<plot>.*?)">'

    for movie in re.compile(patron, re.DOTALL).finditer(data):
        title = scrapertools.find_single_match(movie.group('title'), "(.*) S\d+") or movie.group('title')
        lng = scrapertools.find_multiple_matches(movie.group('lang'), 'alt="([^"]+)"')
        season = int(movie.group('episode').split('S')[1].split('E')[0])
        episode = int(movie.group('episode').split('E')[1])
        itemlist.append(item.clone(
            action='findvideos',
            tvshowtitle=title,
            label=title,
            url=movie.group('url'),
            thumb=movie.group('poster'),
            quality=QLT.get(movie.group('quality')),
            lang=[LNG.get(l) for l in lng],
            plot=movie.group('plot'),
            type='episode',
            content_type='servers',
            season=season,
            episode=episode
        ))

    # Paginador
    next_url = scrapertools.find_single_match(data,
                                              '<li class="active"><a href="\?page=\d+">\d+</a></li> '
                                              '<li><a href="\?(page=\d+)">\d+</a></li>')
    if next_url:
        url = list(urlparse.urlparse(item.url))
        url[4] = next_url
        itemlist.append(item.clone(url=urlparse.urlunparse(url), type='next'))

    return itemlist


def search(item):
    logger.trace()
    item.url = HOST + '/ajax.php'
    item.post = {'Ajax_Filter': True, 'order': 'asc', 'orderby': 'Title', 'page': 1, 'type': 'movie',
                 'search': item.query}
    item.action = 'movies'
    return movies(item)


def tv_search(item):
    logger.trace()
    item.url = HOST + '/ajax.php'
    item.post = {'Ajax_Filter': True, 'order': 'asc', 'orderby': 'Title', 'page': 1, 'type': 'series',
                 'search': item.query}
    item.action='tvshows'
    return tvshows(item)


def findvideos(item):
    logger.trace()
    itemlist = []

    data = httptools.downloadpage(item.url).data
    _id = scrapertools.find_single_match(data, 'var\s*MovieID\s*=\s*"([^"]+)"')

    post = {
        'Ajax_Episode': True,
        'action': 'episode_get',
        'episode': item.episode or 0,
        'movieid': _id
    }

    sources = jsontools.load_json(
        httptools.downloadpage('https://pelis123.tv/ajax.php?time=%s' % int(time.time() * 1000), post=post).data
    )

    for source in sources:
        decoded = Decoder(source['url'])
        itemlist.append(item.clone(
            url=decoded.url,
            type='server',
            lang=LNG.get(source['tag']),
            action='play',
            server='directo' if decoded.html5 else None,
            servername='Pelis123' if decoded.html5 else None
        ))

    return servertools.get_servers_itemlist(itemlist)


class Decoder:
    def __init__(self, url):
        data = httptools.downloadpage(url).data
        self.hash = jsontools.load_json(scrapertools.find_single_match(data, "var\s*hash\s*=\s*'([^']+)';"))
        self.cipher = base64.b64decode(self.hash['key1'])
        self.salt = binascii.unhexlify(self.hash['key3'])
        self.key, self.iv = self.evpKDF(base64.b64encode('ECaR8dUFkv78zsrXvRAD'), self.salt)
        data = AESModeOfOperationCBC(self.key, self.iv).decrypt(self.cipher).replace("\\", "")
        self.url = scrapertools.find_single_match(data, 'iframe src\s*=\s*["|\']([^"\']+)["|\']')
        if self.url:
            self.html5 = False
        else:
            self.url = scrapertools.find_single_match(data, 'source src\s*=\s*["|\']([^"\']+)["|\']')
            self.html5 = True

    @staticmethod
    def evpKDF(passwd, salt, key_size=8, iv_size=4, iterations=1, hash_algorithm="md5"):
        """
        https://github.com/Shani-08/ShaniXBMCWork2/blob/master/plugin.video.serialzone/jscrypto.py
        """
        target_key_size = key_size + iv_size
        derived_bytes = ""
        number_of_derived_words = 0
        block = None
        hasher = hashlib.new(hash_algorithm)
        while number_of_derived_words < target_key_size:
            if block is not None:
                hasher.update(block)

            hasher.update(passwd)
            hasher.update(salt)
            block = hasher.digest()
            hasher = hashlib.new(hash_algorithm)

            for i in range(1, iterations):
                hasher.update(block)
                block = hasher.digest()
                hasher = hashlib.new(hash_algorithm)

            derived_bytes += block[0: min(len(block), (target_key_size - number_of_derived_words) * 4)]

            number_of_derived_words += len(block) / 4

        return derived_bytes[0: key_size * 4], derived_bytes[key_size * 4:]


def fix_json(json_str):
    return re.sub(r'plot"\s*:\s*"(.*?)","',
        lambda x: 'plot":"' + x.group(1).replace('"', '\\"') + '","',
        json_str
    )
