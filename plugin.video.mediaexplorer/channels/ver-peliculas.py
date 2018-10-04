# -*- coding: utf-8 -*-
from core.libs import *

HOST = ''

LNG = Languages({
    Languages.es: ['español', 'spanish', 'esp'],
    Languages.la: ['latino', 'lat'],
    Languages.vos: ['subtituladas', 'subtitulos', 'sub', 'subtitulosp'],
})

QLT = Qualities({
    Qualities.hd: ['HD', '720'],
    Qualities.sd: ['BR'],
    Qualities.scr: ['BR-SCR', 'TS', 'HDTS-SCR', 'DVD-SCR', 'DVD-SCRE', 'HDTS', 'CAM', 'HDTV-SCR', 'WEB-SCR'],
    Qualities.rip: ['DVDRIP', 'HDRIP']
})

def mainlist(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        label='Novedades',
        type="item",
        action='movies',
        content_type='movies',
        url="http://ver-peliculas.io/peliculas/"
    ))

    itemlist.append(item.clone(
        label='Películas en español',
        type="item",
        action='movies',
        content_type='movies',
        lang=[LNG.get('español')],
        url="http://ver-peliculas.io/peliculas/en-espanol/"
    ))

    itemlist.append(item.clone(
        label='Películas en latino',
        type="item",
        action='movies',
        content_type='movies',
        lang=[LNG.get('latino')],
        url="http://ver-peliculas.io/peliculas/en-latino/"
    ))

    itemlist.append(item.clone(
        label='Películas subtituladas',
        type="item",
        action='movies',
        content_type='movies',
        lang=[LNG.get('subtituladas')],
        url="http://ver-peliculas.io/peliculas/subtituladas/"
    ))

    itemlist.append(item.clone(
        label='Géneros',
        type="item",
        action='generos',
        content_type='items',
        url="http://ver-peliculas.io"
    ))

    itemlist.append(item.clone(
        label='Buscar',
        action='search',
        content_type='movies',
        query=True,
        type='search'
    ))

    return itemlist


def movies(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<div class="ml-item"><a href="([^"]+)" data-url="([^"]+).*?' \
             '<img (?:src|data-original)="([^"]+).*?"mli-info"><h2>([^<]+)'

    for url, url_info, poster, title in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            action='findvideos',
            title=title,
            url=url,
            url_info=url_info,
            poster=poster,
            type='movie',
            content_type='servers',
            year=scrapertools.find_single_match(url, '-(\d{4})-online')
        ))

    # Paginador
    next_url = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
    if next_url:
        itemlist.append(item.clone(
            action='movies',
            url="http://ver-peliculas.io" + next_url,
            type='next'))
    elif len(itemlist) > 40:
        if not item.page:
            item.page = 0
        itemlist = itemlist[item.page:]
        if len(itemlist) > 40:
            itemlist = itemlist[:40]
            itemlist.append(item.clone(
                page = item.page + 40,
                type='next'))


    # Si es necesario buscar idiomas
    if not item.lang:
        def find_info(item):
            if item.url_info:
                data = httptools.downloadpage(item.url_info).data
                data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

                patron = '<div class="jtip-quality">([^<]+)</div>(.*?)<div class="jtip-top">.*?' \
                         '<p class="f-desc">(.*?)</p>'

                qlt, idiomas, plot = scrapertools.find_single_match(data, patron)
                idiomas = scrapertools.find_multiple_matches(idiomas, '<div class="([^"]+)">')

                item.quality = QLT.get(qlt)
                item.lang = [LNG.get(lng) for lng in idiomas]
                item.plot = plot

        # Busqueda multihilos
        threads = []
        for item in itemlist:
            t = Thread(target=find_info, args=[item])
            t.setDaemon(True)
            t.start()
            threads.append(t)

        while [t for t in threads if t.isAlive()]:
            time.sleep(0.5)

    return itemlist


def generos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<a href="#" title="Categorias">CATEGORIAS</a>(.*?)</ul>'

    data = scrapertools.find_single_match(data, patron)
    patron = '<a href="([^"]+)"[^>]+>([^<]+)<'

    for url, label in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            label=label,
            action='movies',
            url=url))


    return itemlist


def search(item):
    logger.trace()
    item.url= "http://ver-peliculas.io/buscar/%s.html" % item.query.replace(" ", "-")

    return movies(item)


def findvideos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url, add_referer=True).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = 'https:\/\/ver-peliculas\.(co|io|org)\/(?:peliculas|vipdevip|vippeliculas)\/(\d+)-(.*?)-\d{4}-online\.'
    url = scrapertools.find_single_match(item.url, patron)

    url = 'https://ver-peliculas.%s/core/api.php?id=%s&slug=%s' % (url[0], url[1], url[2])
    video_list = jsontools.load_json(httptools.downloadpage(url).data)['lista']

    for server, langs in video_list.items():
        if langs:
            for lng, v in langs.items():
                if isinstance(v, list):
                    for video in v:
                        new_item = item.clone(
                            action='play',
                            type='server',
                            server=server.split('.')[0],
                            stream= True,
                            post={"video": video['video'], "sub": 'anuncio2'},
                            quality=QLT.get(video['calidad']),
                            lang=LNG.get(lng)
                        )

                        if not item.lang or new_item.lang in item.lang:
                            itemlist.append(new_item)


    return servertools.get_servers_from_id(itemlist)


def play(item):
    logger.trace()
    data = httptools.downloadpage('https://ver-peliculas.co/core/videofinal.php', post=item.post).data
    item.url = jsontools.load_json(data)["playlist"][0]["sources"].split('?')[0]
    servertools.normalize_url(item)

    return item