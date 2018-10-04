# -*- coding: utf-8 -*-
from core.libs import *

HOST = 'https://seriesblanco.org'

LNG = Languages({
    #Languages.sub_es: ['jpsub', 'japovose', 'vose', 'vos'],
    Languages.sub_en: ['en'],
    Languages.es: ['es'],
    #Languages.vo: ['vo'],
    Languages.la: ['la']
})

QLT = Qualities({
    Qualities.hd_full: ['Micro-HD-1080p'],
    Qualities.hd: ['Micro-HD-720p', 'HD-720p', 'HDTV'],
    #Qualities.sd: ['sd']
})


def mainlist(item):
    logger.trace()
    itemlist = list()

    # Nuevos Episodios
    new_item = item.clone(
        action="newest_episodes",
        label="Nuevos episodios",
        type="item",
        content_type='episodes'
    )
    itemlist.append(new_item)

    itemlist.append(new_item.clone(
        label="Nuevos episodios en español",
        group=True,
        filtar_idioma='es'
    ))

    itemlist.append(new_item.clone(
        label="Nuevos episodios en latino",
        group=True,
        filtar_idioma='la'
    ))

    itemlist.append(new_item.clone(
        label="Nuevos episodios subtitulados",
        group=True,
        filtar_idioma='en'
    ))

    # "Series más vistas"
    new_item = item.clone(
        action="tvshows",
        label="Series más vistas",
        url=HOST + "/series-mas-vistas/#tabs-1",
        type="item",
        content_type='tvshows'
    )
    itemlist.append(new_item)

    itemlist.append(new_item.clone(
        label="Series más vistas esta semana",
        url=HOST + "/series-mas-vistas/#tabs-2",
        group=True
    ))

    itemlist.append(new_item.clone(
        label="Series más vistas este mes",
        url=HOST + "/series-mas-vistas/#tabs-3",
        group=True
    ))

    """
    # "Listado alfabético"
    itemlist.append(item.clone(
        action="tvshows_az",
        label="Listado alfabético",
        type="item",
        url=HOST,
        content_type='tvshows'
    ))
    """

    # "Series por género"
    itemlist.append(item.clone(
        action="generos",
        label="Géneros",
        url=HOST,
        type="item"
    ))

    # "Buscar"
    itemlist.append(item.clone(
        action="tv_search",
        label="Buscar",
        query=True,
        type='search',
        category='tvshow',
        content_type='tvshows'
    ))

    return itemlist


def generos(item):
    logger.trace()
    itemlist = list()

    GENEROS = {"Animación": "/genero/animacion/",
               "Aventuras": "/genero/aventuras/",
               "Ciencia Ficción": "/genero/ciencia-ficcion/",
               "Comedia": "/genero/comedia/",
               "Documental": "/genero/documental/",
               "Infantil": "/genero/infantil/",
               "Intriga": "/genero/intriga/",
               "Musical": "/genero/musical/",
               "Miniserie": "/genero/miniserie-de-tv/",
               "Romance": "/genero/romance/",
               "Telenovela": "/genero/telenovela/",
               "Terror": "/genero/terror/",
               "Thriller": "/genero/thriller/",
               "Western": "/genero/western/"}

    for label in sorted(GENEROS.keys()):
        itemlist.append(item.clone(
            action="tvshows",
            label=label,
            type="item",
            content_type='tvshows',
            url=HOST + GENEROS[label]
        ))

    return itemlist


def tv_search(item):
    logger.trace()
    item.query = item.query.decode('latin1').encode('utf8')
    item.url = 'https://seriesblanco.org/buscar/serie/'
    item.post = {
        'key': item.query,
        'keyword': 'title',
        'genre': '',
        'search_type': 'serie'}

    return tvshows(item)


def tvshows(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url,post=item.post).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    if '#tabs-' in item.url:
        # Series mas vistas
        patron = '<div id="tabs-%s">(.*?)</ul>' % item.url[-1]
        data = scrapertools.find_single_match(data, patron)
        patron = '<li class="thumb-episode"> <a href="([^"]+)" title="([^"]+)"><img class="img-shadow" src="([^"]+)'

        for url, title, poster in scrapertools.find_multiple_matches(data, patron):
            title= title.decode('utf8').encode('latin1')
            itemlist.append(item.clone(
                action='seasons',
                label=title,
                tvshowtitle=title,
                title=title,
                url=HOST + url,
                poster=poster,
                type='tvshow',
                content_type='seasons'))

    elif '/genero/' in item.url:
        # Series por genero
        patron = '<figure> <a title="([^"]+)" href="([^"]+)"><img class="thumb" src="([^"]+)".*?' \
                 '<p class="date">(\d{4}).*?<p class="excerpt">(.*?)</p>'
        for title, url, poster, year, plot in scrapertools.find_multiple_matches(data, patron):
            title = title.decode('utf8').encode('latin1')
            itemlist.append(item.clone(
                action='seasons',
                label=title,
                tvshowtitle=title,
                title=title,
                url=HOST + url.replace('ficha', 'capitulos'),
                poster=poster,
                year=year,
                plot=plot.decode('utf8').encode('latin1'),
                type='tvshow',
                content_type='seasons'))

    elif item.query:
        # Buscar serie
        patron = '<figure><a href="([^"]+)" title="([^"]+)"><img src="([^"]+).*?<div class="content">([^<]+)'
        for url, title, poster, plot in scrapertools.find_multiple_matches(data, patron):
            title = title.decode('utf8').encode('latin1')
            itemlist.append(item.clone(
                action='seasons',
                label=title,
                tvshowtitle=title,
                title=title,
                url=HOST + url,
                poster=poster,
                plot=plot.decode('utf8').encode('latin1'),
                type='tvshow',
                content_type='seasons'))


    # Si es necesario añadir paginacion
    next_page = scrapertools.find_single_match(data, '<div class="paginator">.*?</strong> <a href="([^"]+)')
    if itemlist and next_page:
        itemlist.append(item.clone(
            url=HOST + next_page,
            type='next'
        ))

    return itemlist

"""
def tvshows_az(item):
    logger.trace()
    itemlist = list()

    for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        itemlist.append(item.clone(
            action="tvshows",
            label=letra,
            type="item",
            content_type='tvshows',
            url=HOST + "/listado-%s/" % letra
        ))

    return itemlist
"""


def seasons(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    if not item.plot:
        item.plot = scrapertools.find_single_match(data, '<div id="description"><p>([^<]+)').decode('utf8').encode('latin1')
    """    
    if not item.trailer:
        patron = '<iframe frameborder="0" allowfullscreen="1" title="YouTube video player" width="290" ' \
                 'height="200" src="([^"]+)"></iframe>'
        item.trailer = scrapertools.find_single_match(data,patron)
    """
    for num_season in scrapertools.find_multiple_matches(data, '<h3 class="season"> <strong class="season_title">Temporada (\d+)'):
        itemlist.append(item.clone(
            action="episodes",
            season=int(num_season),
            type='season',
            content_type='episodes'
        ))

    return itemlist


def episodes(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<tr><td class="episode-title"> <span class="downloads allkind" ' \
             'title="Disponibles enlaces a descarga directa y visualizaciones"></span> <a target="_blank" ' \
             'href="([^"]+)"> <strong>([^<]+)</strong>.*?<td class="episode-lang" style="text-align: center;">(.*?)</td>'

    for url, season_episode, langs in scrapertools.find_multiple_matches(data, patron):
        num_season, num_episode = scrapertools.get_season_and_episode(season_episode)

        if item.season and item.season != num_season:
            # Si buscamos una temporada concreta y no es esta (num_season)...
            continue

        if item.episode and item.episode != num_episode:
            # Si buscamos un episodio concreto y no es este (num_episode)...
            continue

        itemlist.append(item.clone(
            title=item.tvshowtitle,
            url=url,
            action="findvideos",
            episode=num_episode,
            season=num_season,
            lang=[LNG.get(l) for l in
                  scrapertools.find_multiple_matches(langs, 'src="https://seriesblanco.org/img/lng/([^\.]+)\.png')],
            type='episode',
            content_type='servers'
        ))

    return itemlist


def newest_episodes(item):
    logger.trace()
    itemlist = list()

    if not item.url:
        item.url = "https://seriesblanco.org/inc/index.php?bloque=1&idioma=%s&page=0&genre=" % (item.filtar_idioma if item.filtar_idioma else 'all')

    data = httptools.downloadpage(item.url).data.replace('"', "'")
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = "<td><a href='([^']+)'><img width='105px' height='151px' src='([^']+).*?"
    patron += "<div class='transparent transparent-small'>(.*?)</div>.*?"
    patron += "<td title='([^']+).*?<br>([^<]+)</p>"

    for  url, thumb, lang, title, season_episode in scrapertools.find_multiple_matches(data, patron):
        season, episode = scrapertools.get_season_and_episode(season_episode)
        lang = scrapertools.find_multiple_matches(lang,"src='https://seriesblanco\.org/img/lng/(.*?)\.png'")
        title = title.decode('utf8').encode('latin1').strip()

        itemlist.append(item.clone(
            label=title,
            tvshowtitle=title,
            action="findvideos",
            lang=[LNG.get(l) for l in lang] if item.filtar_idioma not in ['es', 'la', 'sub'] else LNG.get(item.filtar_idioma),
            url=url,
            thumb=thumb,
            season=season,
            episode=episode,
            type='episode',
            content_type='servers'))

    # Paginador
    page = scrapertools.find_single_match(item.url, '&page=(\d+)')
    if page:
        itemlist.append(item.clone(
            url=item.url.replace('&page=%s' % page, '&page=%d' % (int(page) + 1)),
            type='next'))

    return itemlist


def findvideos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data#.replace('"', "'")
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<td class="episode-server" .*? href="([^"]+).*?' \
            '<td class="episode-server-img">.*?domain=([^\.]+).*?' \
            '<td class="episode-lang"><img src="https://seriesblanco.org/img/lng/([^\.]+).*?' \
            '<td class="episode-notes">([^<]+)</td>'

    for stream, sub_seccion in scrapertools.find_multiple_matches(data, '<h2 class="header-subtitle [^>]+> ([^<]+)<(.*?)</table>'):
        for url, server, lang,  quality in scrapertools.find_multiple_matches(sub_seccion, patron):
            if item.filtar_idioma and LNG.get(lang) != LNG.get(item.filtar_idioma):
                continue
                
            itemlist.append(item.clone(
                url=url,
                action='play',
                type='server',
                lang=LNG.get(lang),
                quality=QLT.get(quality),
                server=server,
                stream=('Ver' in stream)
            ))

    return servertools.get_servers_from_id(itemlist)


def play(item):
    logger.trace()

    data = httptools.downloadpage(item.url).data
    item.url = scrapertools.find_single_match(data, '<meta http-equiv="refresh" content="5; url=([^"]+)">')

    servertools.normalize_url(item)
    return item
