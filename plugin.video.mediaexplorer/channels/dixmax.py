# -*- coding: utf-8 -*-
from core.libs import *

HOST = 'https://dixmax.com'

LNG = Languages({
    Languages.es: ['Castellano'],
    Languages.en: ['Ingles'],
    Languages.la: ['Latino'],
    #Languages.vos: ['vos'],
    Languages.sub_es: ['sub_Castellano'],
    Languages.sub_en: ['sub_Ingles'],
    Languages.sub_la: ['sub_Latino']
})

QLT = Qualities({
    Qualities.rip: ['Rip'],
    Qualities.hd: ['HD 720'],
    Qualities.hd_full: ['HD 1080'],
    Qualities.scr: ['TS-Screener']
})


"""
def logout():
    # TODO only debug
    httptools.downloadpage(HOST + '/logout.php')
    logger.debug(is_logged())
"""


def is_logged():
    logger.trace()

    if 'href="?view=perfil"><i class="fa fa-user">' in httptools.downloadpage(HOST).data:
        return True
    else:
        return False


def login():
    logger.trace()

    if is_logged():
        return True

    post = {
        'username': settings.get_setting('user', __file__),
        'password': settings.get_setting('password', __file__),
        'remember': '0'
    }
    httptools.downloadpage(HOST + '/login.php', post=post)

    if 'Sesion iniciada correctamente!' in httptools.downloadpage(HOST + '/session.php?action=1', post=post).data:
        return True
    else:
        platformtools.dialog_notification('DixMax', 'Login incorrecto')
        return False


def config(item):
    v = platformtools.show_settings()
    platformtools.itemlist_refresh()
    return v


def mainlist(item):
    logger.trace()
    itemlist = list()

    # Advertencias
    if not settings.get_setting('user', __file__) or not settings.get_setting('user', __file__) or not login():
        itemlist.append(Item(
            label="Es necesario estar registrado en DixMax.com e introducir sus datos en la configuración.   ",
            type='user'
        ))

        itemlist.append(item.clone(
            action="config",
            label="Configuración",
            folder=False,
            category='all',
            type='setting'
        ))

    else:
        # Menu
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

        itemlist.append(item.clone(
            action="config",
            label="Configuración",
            folder=False,
            type='setting'
        ))

    return itemlist


def menupeliculas(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        action="contents",
        label="Populares",
        url= HOST + '/api/private/get/explore?limit=40&order=3&fichaType[]=2',
        type="item",
        group=True,
        content_type='movies'
    ))

    itemlist.append(item.clone(
        action="generos",
        label="Géneros",
        url=HOST + '/api/private/get/explore?limit=40&order=3&fichaType[]=2',
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        action="search",
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
        label="Populares",
        url=HOST + '/api/private/get/explore?limit=40&order=3&fichaType[]=1',
        type="item",
        group=True,
        content_type = 'tvshows'
    ))

    itemlist.append(item.clone(
        action="generos",
        label="Géneros",
        url=HOST + '/api/private/get/explore?limit=40&order=3&fichaType[]=1',
        type="item",
        group=True
    ))

    itemlist.append(item.clone(
        action="search",
        label="Buscar",
        query=True,
        type='search',
        group=True,
        content_type = 'tvshows'
    ))

    return itemlist


def generos(item):
    logger.trace()
    itemlist = list()

    generos = ['Acción', 'Animación', 'Anime', 'Aventura', 'Bélico', 'Ciencia ficción', 'Cine negro', 'Comedia',
               'Crimen', 'Drama', 'Fantástico' , 'Infantil', 'Intriga', 'Musical', 'Romance', 'Terror', 'Thriller']

    for genero in generos:
        new_item = item.clone(
            label=genero,
            action="contents",
            url = item.url + '&genres[]=%s' % genero
        )
        itemlist.append(new_item)

    return itemlist



def contents(item):
    logger.trace()
    itemlist = list()

    data = httptools.downloadpage(item.url).data
    #logger.debug(data)
    fichas_list = jsontools.load_json(data).get('result',{})
    #logger.debug(fichas_list)

    if item.query:
        fichas_list = fichas_list.get('all', [])
        fichas_list = filter(lambda f: f['info']['isSerie'] == ('0' if item.content_type == 'movies' else '1'),fichas_list)
    else:
        fichas_list = fichas_list.get('fichas', [])

    for ficha in fichas_list:
        info = ficha.get('info',{})
        new_item = item.clone(
            type=item.category,
            title=info['title'],
            poster= 'https://image.tmdb.org/t/p/original' + info['poster'],
            plot=info['sinopsis'],
            id=info['id'],
            year=info['year']
        )

        if info['isSerie'] == '0':
            new_item.action = 'findvideos'
            new_item.content_type = 'servers'

        else:
            new_item.action = 'seasons'
            new_item.content_type = 'seasons'
            new_item.tvshowtitle = info['title']

        itemlist.append(new_item)

    # Paginacion
    if not item.query and len(itemlist) == 40:
        start = scrapertools.find_single_match(item.url, '&start=(\d+)')
        if not start:
            next_url = item.url + '&start=40'
        else:
            next_url = item.url.replace('&start=%s' % start, '&start=%s' % (int(start) + 40))

        itemlist.append(item.clone(url=next_url, type='next'))

    return itemlist


def seasons(item):
    logger.trace()
    itemlist = list()

    try:
        data = httptools.downloadpage(HOST + '/get_all_links.php', {'id':item.id,'i':'false' if item.category == 'movie' else 'true'}).data
        sources = jsontools.load_json(data)
    except:
        return itemlist

    s = set()
    for source in sources:
        if not source['temporada'] in s:
            s.add(source['temporada'])
            itemlist.append(item.clone(
                season=int(source['temporada']),
                title="Temporada %s" % source['temporada'],
                year="",
                action="episodes",
                type='season',
                content_type='episodes'
            ))

    return sorted(itemlist, key=lambda i: i.season)


def episodes(item):
    logger.trace()
    itemlist = list()

    try:
        data = httptools.downloadpage(HOST + '/get_all_links.php', {'id':item.id,'i':'false' if item.category == 'movie' else 'true'}).data
        sources = jsontools.load_json(data)
    except:
        return itemlist

    s = set()
    for source in sources:
        if int(source['temporada']) == item.season:
            if not source['episodio'] in s:
                s.add(source['episodio'])
                itemlist.append(item.clone(
                    title=item.tvshowtitle,
                    action="findvideos",
                    episode=int(source['episodio']),
                    type='episode',
                    content_type='servers'
                ))


    return sorted(itemlist, key=lambda i: i.episode)


def search(item):
    logger.trace()
    item.url= HOST + '/api/private/get/search?query=%s&limit=40&f=1' % item.query.replace(" ", "+")
    return contents(item)


def findvideos(item):
    logger.trace()
    itemlist = list()

    try:
        data = httptools.downloadpage(HOST + '/get_all_links.php', {'id':item.id,'i':'false' if item.category == 'movie' else 'true'}).data
        sources = jsontools.load_json(data)
    except:
        return itemlist

    if item.season and item.episode:
        sources = filter(lambda x: x['temporada']==str(item.season) and x['episodio']==str(item.episode),sources)


    for source in sources:
        itemlist.append(item.clone(
            type='server',
            action='play',
            lang=LNG.get(source['audio'] if source['sub'] in ['Sin subtitulos', 'Otros'] else 'sub_' + source['audio']),
            quality=QLT.get('TS-Screener' if source['sonido'] == 'Screener' else source['calidad']),
            url=source['link'],
            date=datetime.datetime.strptime(source['fecha'], "%Y-%m-%d %H:%M:%S")
        ))

    return servertools.get_servers_itemlist(sorted(itemlist, key=lambda i: i.date, reverse=True))
