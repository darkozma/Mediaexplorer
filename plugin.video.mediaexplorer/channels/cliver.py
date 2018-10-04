# -*- coding: utf-8 -*-
from core.libs import *

HOST = 'http://www.cliver.tv'

LNG = Languages({
    Languages.es: ['es'],
    Languages.la: ['lat', 'es_la'],
    Languages.sub_es: ['vose']
})


def mainlist(item):
    logger.trace()
    itemlist = list()


    new_item = item.clone(
        type='label',
        label="Películas",
        category='movie',
        banner='banner/movie.png',
        icon='icon/movie.png',
        poster='poster/movie.png'
    )
    itemlist.append(new_item)
    itemlist.extend(menupeliculas(new_item))

    new_item = item.clone(
        type='label',
        label="Series",
        category='tvshow',
        banner='banner/tvshow.png',
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
        action="contents",
        label="Estrenos",
        url=HOST + "/peliculas/estrenos/",
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="contents",
        label="Novedades",
        url=HOST,
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="generos",
        label="Géneros",
        url=HOST,
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        action="search_movies",
        label="Buscar",
        query=True,
        type='search',
        group=True,
        content_type='movies'
    ))

    return itemlist


def menuseries(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        action="contents",
        label="Mas vistas",
        url=HOST + "/series/mas-vistas/",
        type="item",
        group=True,
        content_type='tvshows'
    ))

    itemlist.append(item.clone(
        action="newest_episodes",
        label="Nuevos episodios",
        url=HOST + '/series/nuevos-capitulos/',
        type="item",
        group=True,
        content_type='episodes'
    ))

    itemlist.append(item.clone(
        action="generos",
        label="Géneros",
        url=HOST + '/series/',
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        action="search_tv",
        label="Buscar",
        query=True,
        type='search',
        group=True,
        content_type='tvshows'
    ))

    return itemlist


def generos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    data = scrapertools.find_single_match(data, '<div class="generos">(.*?)<div class="anios">')

    patron = '<a href="([^"]+)"><span class="cat">([^<]+)</span>'
    for url, title in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            label=title,
            url=url,
            content_type='movies' if item.category == 'movie' else 'tvshows',
            action='contents'))

    return sorted(itemlist, key=lambda x: x.label)


def search_tv(item):
    logger.trace()
    item.category = 'tvshow'
    item.url = HOST + '/buscar/?txt=%s' % item.query.replace(" ", "+")
    return contents(item)


def search_movies(item):
    logger.trace()
    item.category = 'movie'
    item.url = HOST + '/buscar/?txt=%s' % item.query.replace(" ", "+")
    return contents(item)


def contents(item):
    logger.trace()
    itemlist = list()
    #logger.debug(item)
    headers={'Cookie': 'tipo_contenido=%s' % ('peliculas' if item.category == 'movie' else 'series')}

    data = httptools.downloadpage(item.url, post=item.post, headers=headers)
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data.data)
    #logger.debug(data)
    if not item.post:
        item.post = {'pagina': 0}

        if item.url==HOST:
            patron = '<div class="tipo-contenido">PELÍCULAS RECIÉN AGREGADAS</div>(.*?)' \
                     '<div class="nuevo-contenido"></div>'
            item.post['tipo'] = 'index'
        elif '/estrenos/' in item.url:
            patron = '<div class="tipo-contenido"><h1 class="t-cont">PELÍCULAS ESTRENOS</h1></div>(.*?)' \
                     '<div class="nuevo-contenido"></div>'
            item.post['tipo'] = 'estrenos'
        elif '/genero/' in item.url:
            patron = '<div class="tipo-contenido">(.*?)<div class="nuevo-contenido"></div>'
            item.post['tipo'] = 'genero' if item.category=='movie' else 'generosSeries'
            item.post['adicional'] = item.url[:-1].split('/')[-1]
        elif '/buscar/' in item.url:
            patron = '<div class="tipo-contenido">(.*?)<div class="nuevo-contenido"></div>'
            item.post['tipo'] = 'buscador' if item.category=='movie' else 'buscadorSeries'
            item.post['adicional'] = item.query
        elif '/series/mas-vistas/' in item.url:
            patron = '<div class="tipo-contenido"><h1 class="t-cont">SERIES MÁS VISTAS</h1></div>(.*?)' \
                     '<div class="nuevo-contenido"></div>'
            item.post['tipo'] = 'mas-vistas-series'

        data = scrapertools.find_single_match(data, patron)

    if item.category == 'tvshow':
        patron = '<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)">(.*?)<span>(\d{4})'
    else:
        patron = '<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"><div class="idiomas">(.*?)' \
                 '<div class="titulo-p">.*?<span>(\d{4})</span>'

    for url, poster, title, idiomas, year in scrapertools.find_multiple_matches(data,patron):
        lng = scrapertools.find_multiple_matches(idiomas, '<div class="([^"]+)"></div>')
        new_item = item.clone(
            title=title,
            url=url,
            poster=poster,
            year=year,
            lang=[LNG.get(l) for l in lng],
            type=item.category,
            action='findvideos',
            content_type='servers'
        )

        if item.category == 'tvshow':
            new_item.action='seasons'
            new_item.content_type='seasons'

        itemlist.append(new_item)

    # Paginador
    if itemlist:
        new_item = item.clone(
            action=item.action,
            url=HOST + '/frm/cargar-mas.php',
            type='next'
        )
        new_item.post['pagina']+= 1

        if httptools.downloadpage(new_item.url, post=new_item.post).data != 'error':
            itemlist.append(new_item)


    return itemlist


def seasons(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    patron = '<div class="contenido-menu-s" id="temp-(\d+)">'
    for num_season in scrapertools.find_multiple_matches(data, patron):
        itemlist.append(item.clone(
            season=int(num_season),
            tvshowtitle=item.title,
            title='Temporada %s' % num_season,
            action="episodes",
            type='season',
            content_type='episodes'))

    return itemlist


def episodes(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)

    patron = '<img src="([^"]+)"></div><div class="mic-cont"><div class="mic-cont-header">' \
             '<div class="mic-cont-header-titulo">([^<]+)</div></div><p>([^<]+)</p></div>' \
             '<div class="mic-play" data-id="([^"]+)'

    for thumb, title, plot, data_id in scrapertools.find_multiple_matches(data, patron):
        num_season, num_episode = scrapertools.get_season_and_episode(title)

        if num_season == item.season:
            itemlist.append(item.clone(
                #data_id=data_id,
                title=title.split('-')[1].strip(),
                thumb=thumb,
                action="findvideos",
                episode=num_episode,
                season=num_season,
                type='episode',
                plot= plot,
                content_type='servers'
            ))

    return itemlist


def newest_episodes(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url, post=item.post, headers={'Cookie': 'tipo_contenido=series'}).data
    data = re.sub(r"\n|\r|\t|\s{2}|&nbsp;", "", data)
    data = scrapertools.find_single_match(data, '<div class="tipo-contenido">(.*?)<div class="nuevo-contenido"></div>')

    if not item.post:
        item.post = {'pagina': 0, 'tipo':'nuevos-capitulos'}

    patron = '<img src="([^"]+)".*?<a href="([^"]+)"><h2>([^<]+)</h2></a><span>([^<]+)</span>'
    for thumb, url, tvshowtitle, title in scrapertools.find_multiple_matches(data, patron):
        num_season, num_episode = scrapertools.get_season_and_episode(title)

        itemlist.append(item.clone(
            tvshowtitle=tvshowtitle,
            label=tvshowtitle,
            url=url,
            thumb=thumb,
            action="findvideos",
            episode=num_episode,
            season=num_season,
            type='episode',
            content_type='servers'
        ))

    return itemlist


def findvideos(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data

    if item.type=='movie':
        data = httptools.downloadpage(
            'http://www.cliver.tv/frm/obtener-enlaces-pelicula.php',
            post={'pelicula': scrapertools.find_single_match(data,"'datoAdicional': '(\d*)'")}).data
        #logger.debug(eval(data))

        for lng, v in eval(data).items():
            for enlace in v:
                url = eval(httptools.downloadpage(
                    'http://directvideo.stream/getFile.php',
                    post={'hash':enlace['token']}).data)['url'].replace('\\','')

                if url:
                    itemlist.append(item.clone(
                        url=url,
                        action='play',
                        type='server',
                        lang=LNG.get(lng),
                        stream=True
                    ))


    else:
        patron = '<div class="mic-play".*?data-numcap="%s" data-numtemp="%s".*?data-idiomas="([^"]+)([^>]+)>'\
                 % (item.episode, item.season)
        lng, urls = scrapertools.find_single_match(data, patron)

        for i in lng.split(','):
            itemlist.append(item.clone(
                url=scrapertools.find_single_match(urls, 'data-url-%s="([^"]+)"' % i),
                action='play',
                type='server',
                lang=LNG.get(i),
                stream=True
            ))

    #logger.debug(servertools.get_servers_itemlist(itemlist))
    return servertools.get_servers_itemlist(itemlist)

