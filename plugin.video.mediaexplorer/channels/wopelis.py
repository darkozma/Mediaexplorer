# -*- coding: utf-8 -*-
from core.libs import *

HOST = 'http://www.wopelis.com'

LNG = Languages({
    Languages.es: ['esp'],
    Languages.en: ['english'],
    Languages.la: ['argentina'],
    Languages.vos: ['vos'],
    Languages.sub_es: ['sub_esp'],
    Languages.sub_en: ['sub_english'],
    Languages.sub_la: ['sub_argentina']
})

QLT = Qualities({
    Qualities.rip: ['rip', 'hdrip', 'hdrvrip'],
    Qualities.hd: ['hd720'],
    Qualities.sd: ['dvdfull'],
    Qualities.hd_full: ['hdfull', 'hd1080'],
    Qualities.scr: ['screener']
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

    url = HOST + "/galep.php?solo=cenlaces&empen=0"
    itemlist.append(item.clone(
        action="movies",
        label="Novedades",
        url=url + "&ord=recie",
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="movies",
        label="Más populares de la semana",
        url=url + "&ord=popu",
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="generos",
        label="Géneros",
        url=HOST + "/index.php",
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        action="movie_search",
        label="Buscar",
        query=True,
        url=url,
        type='search',
        group=True,
        content_type='movies'
    ))

    return itemlist


def menuseries(item):
    logger.trace()
    itemlist = list()

    url = HOST + "/gales.php?empen=0"
    itemlist.append(item.clone(
        action="tvshows",
        label="Series actualizadas",
        url=url,
        type="item",
        group=True,
        content_type='tvshows'
    ))

    itemlist.append(item.clone(
        action="tvshows",
        label="Nuevos episodios",
        url=url + "&ord=recie",
        type="item",
        group=True,
        content_type='tvshows'
    ))

    itemlist.append(item.clone(
        action="tvshows",
        label="Más populares de la semana",
        url=url + "&ord=popu",
        type="item",
        group=True,
        content_type='tvshows'
    ))

    itemlist.append(item.clone(
        action="generos",
        label="Géneros",
        url=HOST + "/series.php",
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        action="tv_search",
        label="Buscar",
        query=True,
        url=url + "&ord=popu",
        type='search',
        group=True,
        content_type='tvshows'
    ))

    return itemlist


def config(item):
    pass


def movies(item):
    logger.trace()
    itemlist = list()

    data = downloadpage(item.url)

    patron = '<div class="ddItemContainer modelContainer" data-model="peli" data-id="([^"]+).*?'
    patron += '<a class="extended" href=".([^"]+).*?'
    patron += '<img class="centeredPicFalse"([^>]+).*?'
    patron += '<span class="year">(\d{4})</span>.*?'
    patron += '<span class="value"><img src="./images/star.png" style="display: inline;">([^<]+).*?'
    patron += '<span class="title">(.*?)</span>'

    for id, url, pic, year, rating, title in scrapertools.find_multiple_matches(data, patron):
        poster = scrapertools.find_single_match(pic, 'src="([^"]+)')
        if not poster or poster == "/images/cover-notfound.png":
            poster = HOST + "/images/cover-notfound.png"

        itemlist.append(item.clone(
            action='findvideos',
            label=title,
            title=title,
            url=HOST + url.replace('peli.php?id=', 'venlaces.php?npl='),
            poster=poster,
            type='movie',
            content_type='servers',
            year=year,
            wopelisid=id,
            rating=rating
        ))

    # Si es necesario añadir paginacion
    if len(itemlist) == 35:
        empen = scrapertools.find_single_match(item.url, 'empen=(\d+)')
        url_next_page = item.url.replace('empen=%s' % empen, 'empen=%s' % (int(empen) + 35))
        itemlist.append(item.clone(
            url=url_next_page,
            type='next'
        ))

    return itemlist


def tvshows(item):
    logger.trace()
    itemlist = list()

    data = downloadpage(item.url)

    patron = '<div class="ddItemContainer modelContainer" data-model="peli" data-id="([^"]+).*?'
    patron += '<a class="extended" href=".([^"]+).*?'
    patron += '<img class="centeredPicFalse"([^>]+).*?'
    patron += '<span class="year">(\d{4})</span>.*?'
    patron += '<span class="value"><img src="./images/star.png" style="display: inline;">([^<]+).*?'
    patron += '<span class="title">(.*?)</span>'

    for id, url, pic, year, rating, title in scrapertools.find_multiple_matches(data, patron):
        poster = scrapertools.find_single_match(pic, 'src="([^"]+)')
        if not poster or poster == "/images/cover-notfound.png":
            poster = HOST + "/images/cover-notfound.png"

        title = title.replace(' - 0x0', '')

        new_item = item.clone(
            action='seasons',
            label=title,
            tvshowtitle=title,
            title=title,
            url=HOST + url,
            poster=poster,
            type='tvshow',
            content_type='seasons',
            year=year,
            wopelisid=id,
            rating=rating
        )

        season_episode = scrapertools.get_season_and_episode(title)
        if season_episode:
            new_item.tvshowtitle = title.split('-', 1)[1].strip()
            new_item.title = new_item.label = new_item.tvshowtitle

            if "ord=reci" in item.url:
                # episode
                new_item.season, new_item.episode = season_episode
                new_item.type = "episode"
                new_item.action = "episodes_newest"
                new_item.content_type = 'servers'
                new_item.thumb = new_item.poster

        itemlist.append(new_item)

    # Si es necesario añadir paginacion
    if len(itemlist) == 35:
        empen = scrapertools.find_single_match(item.url, 'empen=(\d+)')
        url_next_page = item.url.replace('empen=%s' % empen, 'empen=%s' % (int(empen) + 35))
        itemlist.append(item.clone(
            url=url_next_page,
            type='next'
        ))

    return itemlist


def seasons(item):
    logger.trace()
    itemlist = list()

    data = downloadpage(item.url)
    patron = '<div class="checkSeason" data-num="([^"]+)[^>]+>([^<]+)'

    for num_season, title in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            season=int(num_season),
            title=title,
            year="",
            action="episodes",
            type='season',
            content_type='episodes'
        ))

    return itemlist


def episodes(item):
    logger.trace()
    itemlist = list()

    data = downloadpage(item.url)
    patron = '<div class="checkSeason" data-num="([^"]+)(.*?)</div></div></div>'
    for num_season, data in scrapertools.find_multiple_matches(data, patron):
        # TODO posible fallo si temporada o episodio buscados son 0
        if item.season and item.season != int(num_season):
            # Si buscamos los episodios de una temporada concreta y no es esta (num_season)...
            continue

        patron = '<div class="info"><a href="..([^"]+).*?class="number">([^<]+)'
        for url, num_episode in scrapertools.find_multiple_matches(data, patron):
            if item.episode and item.episode != int(num_episode):
                # Si buscamos un episodio concreto y no es este (num_episode)...
                continue

            itemlist.append(item.clone(
                title=item.tvshowtitle,
                url=HOST + url,
                action="findvideos",
                episode=int(num_episode),
                season=int(num_season),
                type='episode',
                content_type='servers'
            ))

    return itemlist


def episodes_newest(item):
    logger.trace()
    itemlist = []

    episodelist = episodes(item)
    if len(episodelist) == 1:
        new_item = item.clone(url=episodelist[0].url, episode=episodelist[0].episode, season=episodelist[0].season)

        itemlist = findvideos(new_item)

    return itemlist


def tv_search(item):
    logger.trace()
    item.url = "%s&busqueda=%s" % (item.url, item.query.replace(" ", "+"))

    return tvshows(item)


def movie_search(item):
    logger.trace()
    item.url = "%s&busqueda=%s" % (item.url, item.query.replace(" ", "+"))

    return movies(item)


def generos(item):
    # TODO crear una coleccion de imagenes para los generos
    logger.trace()
    itemlist = list()

    data = downloadpage(item.url)
    data = scrapertools.find_single_match(data, '<select name="gener">(.*?)</select>')

    for genero in scrapertools.find_multiple_matches(data, '<option value="([^"]+)'):
        if genero == 'Todos':
            continue

        new_item = item.clone(
            label=genero,
            type='item'
        )
        if 'series' in item.url:
            new_item.url = HOST + "/gales.php?empen=0&gener=%s" % genero
            new_item.content_type = 'tvshows'
            new_item.action = "tvshows"
        else:
            new_item.url = HOST + "/galep.php?solo=cenlaces&empen=0&gener=%s" % genero
            new_item.content_type = 'movies'
            new_item.action = 'movies'

        itemlist.append(new_item)

    return itemlist


def findvideos(item):
    logger.trace()
    itemlist = list()

    data1 = downloadpage(item.url)

    if "Descarga:</h1>" in data1:
        list_showlinks = [('Online:', 'Online:</h1>(.*?)Descarga:</h1>'),
                          ('Download:', 'Descarga:</h1>(.*?)</section>')]
    else:
        list_showlinks = [('Online:', 'Online:</h1>(.*?)</section>')]

    patron = 'onclick="redir\(([^\)]+).*?'
    patron += '<span[^>]+>([^<]+).*?'
    patron += '<img(.*?)width="30px"'

    for i, t in enumerate(list_showlinks):
        data = scrapertools.find_single_match(data1, t[1])

        if data:
            for redir, quality, langs in scrapertools.find_multiple_matches(data, patron):
                audio, subtitulos = scrapertools.find_multiple_matches(langs, 'src="./images/([^\.]+)')
                lang = LNG.get(audio)
                if subtitulos != 'ntfof':
                    lang = LNG.get("sub_" + subtitulos)

                itemlist.append(item.clone(
                    url=redir.split(",")[0][1:-1],
                    action='play',
                    type='server',
                    lang=lang,
                    quality=QLT.get(quality.lower()),
                    stream=(i == 0)
                ))

    itemlist = servertools.get_servers_itemlist(itemlist)

    return itemlist


def downloadpage(url):
    data = httptools.downloadpage(url).data
    if "Hola bienvenido" in data:
        data = httptools.downloadpage(url, cookies=get_cookie(data)).data

    return re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)


def get_cookie(data):
    import random
    cookievalue = ""
    cookiename = scrapertools.find_single_match(data, 'document.cookie\s*=\s*"([^"]+)"')
    cookiename = cookiename.replace("=", "")
    posible = scrapertools.find_single_match(data, 'var possible\s*=\s*"([^"]+)"')
    bloque = scrapertools.find_single_match(data, 'function cok(.*?);')
    lengths = scrapertools.find_multiple_matches(bloque, '([\S]{1}\d+)')
    for numero in lengths:
        if numero.startswith("("):
            for i in range(0, int(numero[1:])):
                cookievalue += posible[int(random.random() * len(posible))]
        else:
            cookievalue += numero[1:]

    return {cookiename: cookievalue}
