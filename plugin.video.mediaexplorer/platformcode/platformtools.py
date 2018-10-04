# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcplugin

from core.libs import *
from platformcode import viewtools


def dialog_ok(heading, line1, line2="", line3=""):
    """
    Muestra un diálogo
    :param heading:
    :param line1:
    :param line2:
    :param line3:
    :return:
    """
    dialog = xbmcgui.Dialog()
    return dialog.ok(heading, line1, line2, line3)


def dialog_notification(heading, message, icon=0, t=5000, sound=True):
    """
    Muestra una notificaión
    :param heading:
    :param message:
    :param icon:
    :param t:
    :param sound:
    :return:
    """
    dialog = xbmcgui.Dialog()
    l_icono = xbmcgui.NOTIFICATION_INFO, xbmcgui.NOTIFICATION_WARNING, xbmcgui.NOTIFICATION_ERROR
    dialog.notification(heading, message, l_icono[icon], t, sound)


def dialog_yesno(heading, line1, line2="", line3="", nolabel="No", yeslabel="Si", autoclose=""):
    """
    Muestra un dialogo con dos opciones (si y no)
    :param heading:
    :param line1:
    :param line2:
    :param line3:
    :param nolabel:
    :param yeslabel:
    :param autoclose:
    :return:
    """
    dialog = xbmcgui.Dialog()
    if autoclose:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel, autoclose)
    else:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)


def dialog_img_yesno(img, heading="", message="", no_show = True, yes_label ='Aceptar', no_label='Cancelar'):
    """
        Muestra un dialogo con una imagen y dos opciones (si y no)
        :param heading: Titulo del cuadro de dialogo
        :param message: Texto multilinea
        :param no_show: Mostrar o no el boton NO
        :param yeslabel: Etiqueta boton YES
        :param nolabel: Etiqueta boton NO
        :return: True si se pulsa el boton YES, False en caso contrario.
    """
    from dialog_img_yesno import Dialog_img_yesno
    skin = 'Estuary' if xbmc.getSkinDir() == 'skin.estuary' else 'Default'
    return Dialog_img_yesno("Dialog_img.xml", sysinfo.runtime_path, skin).start(img, heading, message, no_show,
                                                                                yes_label, no_label)


def dialog_select(heading, _list):
    """
    Muestra un cuadro de selección
    :param heading:
    :param _list:
    :return:
    """
    return xbmcgui.Dialog().select(heading, _list)


def dialog_progress(heading, line1, line2="\n", line3="\n"):
    """
    Muestra un dialogo de progreso
    :param heading:
    :param line1:
    :param line2:
    :param line3:
    :return:
    """
    dialog = xbmcgui.DialogProgress()
    dialog.create(heading, line1, line2, line3)
    return dialog


def dialog_progress_bg(heading, message=""):
    """
    Muestra un dialogo de progresoen segundo plano
    :param heading:
    :param message:
    :return:
    """
    dialog = xbmcgui.DialogProgressBG()
    dialog.create(heading, message)
    return dialog


def dialog_input(default="", heading="", hidden=False):
    """
    Muestra un diálogo para introducir texto
    :param default:
    :param heading:
    :param hidden:
    :return:
    """
    keyboard = xbmc.Keyboard(default, heading, hidden)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    else:
        return None


def dialog_numeric(_type, heading, default=""):
    """
    Muestra un diálogo para introducir numeros
    :param _type:
    :param heading:
    :param default:
    :return:
    """
    dialog = xbmcgui.Dialog()
    d = dialog.numeric(_type, heading, default)
    return d


def show_settings(controls=None, title="", callback=None, item=None, custom_button=None, mod=None):
    """
    Muestra la ventana de configuración
    :param controls:
    :param title:
    :param callback:
    :param item:
    :param custom_button:
    :param mod:
    :return:
    """
    from settings_window import SettingsWindow
    skin = 'Estuary' if xbmc.getSkinDir() == 'skin.estuary' else 'Default'
    return SettingsWindow("ChannelSettings.xml", sysinfo.runtime_path, skin).start(
        controls=controls,
        title=title,
        callback=callback,
        item=item,
        custom_button=custom_button,
        mod=mod
    )


def show_info(item, title=""):
    """
    Muestra una ventana con la información del item (movie, tvshow, season, episode) en caso de que
    el item sea un list con varios, permite elegir uno y devuelve el index del item seleccionado
    :param item:
    :param title:
    :return:
    """
    from info_window import InfoWindow
    skin = 'Estuary' if xbmc.getSkinDir() == 'skin.estuary' else 'Default'
    return InfoWindow("InfoWindow.xml", sysinfo.runtime_path, skin).start(item, title=title)


def show_recaptcha(url, key):
    """
    reCaptcha
    :param key:
    :param url:
    :return:
    """
    from core.anticaptcha import Anticaptcha
    return Anticaptcha().solve_recaptcha(url, key)


def show_captcha(url):
    """
    Muetra una imagen con el captcha y devuelve el texto escrito por el usuario
    :param url:
    :return:
    """
    from captcha import Captcha
    skin = 'Estuary' if xbmc.getSkinDir() == 'skin.estuary' else 'Default'
    return Captcha("Captcha.xml", sysinfo.runtime_path, skin).start(url)


def show_first_run():
    from firstrun import FirstRun
    skin = 'Estuary' if xbmc.getSkinDir() == 'skin.estuary' else 'Default'
    return FirstRun("FirstRun.xml", sysinfo.runtime_path, skin).start()


def media_info(item):
    xbmc.executebuiltin('XBMC.Action(Info)')


def itemlist_refresh():
    """
    Actualiza la ventana recargando el mismo item
    :return:
    """
    xbmc.executebuiltin("Container.Refresh")


def itemlist_update(item):
    """
    Actualiza la ventana cargando el item pasado
    :param item:
    :return:
    """
    xbmc.executebuiltin("Container.Refresh(" + sys.argv[0] + "?" + item.tourl() + ")")


def get_profile():
    """
    Obtiene el perfil y los datos
    :return:
    """
    logger.trace()

    profiles_path = os.path.join(sysinfo.runtime_path, 'resources', 'profiles')
    skin_name = xbmc.getSkinDir()
    saved_profile = settings.get_setting('color_profile', viewtools.__file__)

    # Si tenemos un perfil configurado, comprobamos si vale para nuestro skin
    if saved_profile:
        try:
            profile_data = jsontools.load_file(os.path.join(profiles_path, saved_profile))
        except Exception:
            logger.error()
        else:
            if skin_name in profile_data.get('skin_list', []) or saved_profile == 'default.json':
                return saved_profile, profile_data

    # Si no tenemos o no nos vale, cargamos el perfil por defecto para nuestro skin
    for fname in os.listdir(profiles_path):
        if not fname.endswith('.json'):
            continue
        try:
            profile_data = jsontools.load_file(os.path.join(profiles_path, fname))
        except Exception:
            logger.error()
        else:
            if skin_name in profile_data.get('skin_default', []):
                return fname, profile_data

    # Sino tenemos perfil para nuestro skin, cargamos elbásico
    return 'default.json', jsontools.load_file(os.path.join(profiles_path, 'default.json'))


def get_profile_list():
    """
    Obtiene la lista de perfiles para el skin seleccionado
    :return:
    """
    logger.trace()
    itemlist = list()

    profiles_path = os.path.join(sysinfo.runtime_path, 'resources', 'profiles')
    skin_name = xbmc.getSkinDir()

    for fname in os.listdir(profiles_path):
        if not fname.endswith('.json'):
            continue
        try:
            profile_data = jsontools.load_file(os.path.join(profiles_path, fname))
        except Exception:
            logger.error()
        else:
            if skin_name in profile_data.get('skin_list', []) or 'all' in profile_data.get('skin_list', []):
                if skin_name in profile_data.get('skin_default', []):
                    itemlist.insert(0, [fname, profile_data['name']])
                else:
                    itemlist.append([fname, profile_data['name']])

    return itemlist


def render_items(itemlist, parent_item):
    """
    Muestra los items del itemlist en la pantalla
    :param itemlist:
    :param parent_item:
    :return:
    """
    logger.trace()

    # Si no es un list no hay nada que mostrar, salimos
    if not type(itemlist) == list:
        return

    # Si no hay items mostramos un aviso
    if not len(itemlist):
        itemlist.append(
            Item(
                label="No hay elementos que mostrar"
            )
        )
        parent_item.content_type = 'items'

    # Obtener información en el listado
    if settings.get_setting('itemlist_info', viewtools.__file__) and not parent_item.channel == 'library' and \
            not (parent_item.channel == 'newest' and settings.get_setting("group_result", 'core/newest') == 3) and \
            not (parent_item.channel == 'finder' and settings.get_setting("group_result", 'core/finder') == 3):

        dialog = platformtools.dialog_progress_bg('Obteniendo información de medios')
        for ready, total in mediainfo.get_itemlist_info(
                itemlist,
                extended=settings.get_setting('extended_info', viewtools.__file__),
                ask=False
        ):
            dialog.update(ready * 100 / total, 'Obteniendo información de medios', '%s de %s' % (ready, total))

        dialog.close()

    if settings.get_setting('media_info', viewtools.__file__) and parent_item.type in (
            'movie', 'tvshow', 'season', 'episode'):
        i = parent_item.clone(label='Información', action='info', channel=None, thumb='', fanart='')
        itemlist.insert(0, i)
        if i.type == 'movie':
            mediainfo.get_movie_info(i, extended=True, ask=False)
        if i.type == 'tvshow':
            mediainfo.get_tvshow_info(i, extended=True, ask=False)
        if i.type == 'season':
            mediainfo.get_season_info(i, extended=True, ask=False)
        if i.type == 'episode':
            mediainfo.get_episode_info(i, extended=True, ask=False)
        i.type = 'info'

    # Recorremos el itemlist
    for item in itemlist:
        # Si el item está marcado como adulto pero no está activado en la configuración lo saltamos
        if item.adult and not settings.get_setting('adult_mode'):
            continue

        # Creamos el listitem
        listitem = xbmcgui.ListItem(viewtools.set_label_format(item))

        # Añadir marca de visto si procede
        command_context = {"label": "Desmarcar visto", "context_action": 'set_no_viewed'}
        if item.type in ['movie', 'episode']:
            if bbdd.media_viewed_is_viewed(item):
                item.watched = True
                item.context.append(command_context)

        # Añadimos la información
        viewtools.set_item_info(item, listitem)
        viewtools.set_art(item, parent_item, listitem)

        # Añadimos el menú contextual
        listitem.addContextMenuItems(set_context_commands(item, parent_item), replaceItems=True)
        if command_context in item.context:
            item.context.remove(command_context)

        # Si el item es un server preparamos la reproduccion con setResolvedUrl
        if item.action == 'play' and settings.get_setting('setResolvedUrl', platformsettings.__file__):
            listitem.setProperty('IsPlayable', 'true')
            item.folder = False

        # Añadimos el item al listitem
        xbmcplugin.addDirectoryItem(
            handle=int(sys.argv[1]),
            url='%s?%s' % (sys.argv[0], item.tourl()),
            listitem=listitem,
            isFolder=item.folder,
            totalItems=len(itemlist)
        )

    # Añadimosel nombre del canal
    xbmcplugin.setPluginCategory(
        handle=int(sys.argv[1]),
        category=parent_item.name
    )

    # No ordenar
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_NONE)

    # Seleccionamos el tipo de vista
    viewtools.set_viewmode(parent_item)

    # Cerramos
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)


def set_context_commands(item, parent_item):
    """
    Crea los elementos del menu contextual
    :param item:
    :param parent_item:
    :return:
    """
    logger.trace()
    context_commands = []

    # Opciones segun item.context
    for command in item.context:
        if type(command) == dict:
            if "goto" in command:
                context_commands.append(
                    (
                        command["label"],
                        "XBMC.Container.Refresh (%s?%s)" % (
                            sys.argv[0],
                            item.clone(**command).tourl()
                        )
                    )
                )
            else:
                context_commands.append(
                    (
                        command["label"],
                        "XBMC.RunPlugin(%s?%s)" % (
                            sys.argv[0],
                            item.clone(**command).tourl()
                        )
                    )
                )

    # Abrir configuración
    context_commands.append(
        (
            "Abrir configuración",
            "XBMC.Container.Update(%s?%s)" % (
                sys.argv[0],
                Item(
                    channel='settings',
                    action="mainlist",
                    thumb='thumb/setting.png',
                    icon='icon/setting.png',
                    poster='poster/setting.png',
                    content_type='items'
                ).tourl()
            )
        )
    )

    # Biblioteca
    if not item.channel == 'library':
        # Añadir película a la biblioteca
        if item.type == 'movie':
            context_commands.append(
                (
                    "Añadir Película a la biblioteca",
                    "XBMC.RunPlugin(%s?%s)" % (
                        sys.argv[0],
                        item.clone(
                            context_channel='library',
                            context_action='add_to_library'
                        ).tourl()
                    )
                )
            )

        # Añadir serie a la bilioteca
        if item.type == 'tvshow':
            context_commands.append(
                (
                    "Añadir Serie a la biblioteca",
                    "XBMC.RunPlugin(%s?%s)" % (
                        sys.argv[0],
                        item.clone(
                            context_channel='library',
                            context_action='add_to_library'
                        ).tourl()
                    )
                )
            )

        # Añadir vídeo a la biblioteca
        if item.type == 'video':
            context_commands.append(
                (
                    "Añadir Vídeo a la biblioteca",
                    "XBMC.RunPlugin(%s?%s)" % (
                        sys.argv[0],
                        item.clone(
                            context_channel='library',
                            context_action='add_to_library'
                        ).tourl()
                    )
                )
            )

    # Descargar película
    if item.type == 'movie':
        context_commands.append(
            (
                "Descargar película",
                "XBMC.RunPlugin(%s?%s)" % (
                    sys.argv[0],
                    item.clone(
                        context_channel='downloads',
                        context_action='add_to_downloads'
                    ).tourl()
                )
            )
        )

    # Descargar serie
    if item.type == 'tvshow':
        context_commands.append(
            (
                "Descargar serie",
                "XBMC.RunPlugin(%s?%s)" % (
                    sys.argv[0],
                    item.clone(
                        context_channel='downloads',
                        context_action='add_to_downloads'
                    ).tourl()
                )
            )
        )

    # Descargar vídeo
    if item.type == 'video':
        context_commands.append(
            (
                "Descargar vídeo",
                "XBMC.RunPlugin(%s?%s)" % (
                    sys.argv[0],
                    item.clone(
                        context_channel='downloads',
                        context_action='add_to_downloads'
                    ).tourl()
                )
            )
        )

    # Ir al Menu Principal (channelselector.mainlist)
    if parent_item.channel != 'channelselector':
        context_commands.append(
            (
                "Ir al Menu Principal",
                "XBMC.Container.Refresh (%s?%s)" % (
                    sys.argv[0],
                    Item(
                        channel="channelselector",
                        action="mainlist",
                        content_type='icons',
                        category='all'
                    ).tourl()
                )
            )
        )

    # Información del canal
    if item.type == 'channel':
        context_commands.append(
            (
                "Información del canal",
                "XBMC.RunPlugin(%s?%s)" % (
                    sys.argv[0],
                    item.clone(context_channel='channelselector',
                               context_action='channel_info').tourl()
                )
            )
        )

    # Autoplay
    if item.type in ['movie', 'episode']:
        if not settings.get_setting('autoplay'):
            context_commands.append(
                (
                    "Autoplay",
                    "XBMC.RunPlugin(%s?%s)" % (
                        sys.argv[0],
                        item.clone(context_autoplay=True).tourl()
                    )
                )
            )
        else:
            context_commands.append(
                (
                    "Ver servidores",
                    "XBMC.Container.Refresh (%s?%s)" % (
                        sys.argv[0],
                        item.clone(context_autoplay=False).tourl()
                    )
                )
            )

    # Añadir a Mi Lista
    if item.type in ['movie', 'tvshow'] and not item.list_id:
        context_commands.append(
            (
                "Añadir a Mi Lista",
                "XBMC.RunPlugin(%s?%s)" % (
                    sys.argv[0],
                    item.clone(
                        context_channel='lists',
                        context_action='add_to_my_list'
                    ).tourl()
                )
            )
        )

    # Buscar
    if item.type in ('season', 'episode', 'tvshow', 'movie'):
        context_commands.append(
            (
                "Buscar '%s'" % (item.tvshowtitle or item.title),
                "XBMC.Container.Refresh (%s?%s)" % (
                    sys.argv[0],
                    item.clone(
                        context_channel='finder',
                        context_action='search',
                        search_categories={'movie': True} if item.type == 'movie' else {'tvshow': True},
                        content_type='movies' if item.type == 'movie' else 'tvshows',
                        query=item.tvshowtitle or item.title,
                    ).tourl()
                )
            )
        )

    # Para versiones anteriores a kodi v17
    if sysinfo.platform_version < 17:
        # Información del medio
        if item.type in ('season', 'episode', 'tvshow', 'movie', 'server'):
            context_commands.append(
                (
                    "Información",
                    "XBMC.Action(Info)"
                )
            )

        # Favoritos
        if item.type in ('season', 'episode', 'tvshow', 'movie', 'channel'):
            if parent_item.channel != 'bookmarks':
                context_commands.append(
                    (
                        "Añadir a favoritos",
                        "XBMC.RunPlugin(%s?%s)" % (
                            sys.argv[0],
                            item.clone(context_channel='bookmarks',
                                       context_action='add_bookmark',
                                       label=item.label).tourl()
                        )
                    )
                )

    return sorted(context_commands, key=lambda comand: comand[0])


def is_playing():
    """
    Compruena si se está reproducioendo
    :return:
    """
    return xbmc.Player().isPlaying()


def stop_video():
    """
    Deteniene la reproducción del video
    :return:
    """
    xbmc.Player().stop()


def play(item):
    """
    Muestra el dialogo con las opciones de reproducción y lanza la función adecuada segun la opcion selecionada
    :param item:
    :return:
    """
    logger.trace()

    # Ponemos el tipo correcto
    item = item.clone(type=item.mediatype)

    # Buscar información
    if settings.get_setting('play_info', viewtools.__file__):
        from core import mediainfo
        if item.type == 'movie':
            mediainfo.get_movie_info(item, True)
        if item.type == 'episode':
            mediainfo.get_episode_info(item, True)

    # Si el item no tiene video_urls se asignan
    if not item.video_urls:
        if item.server:
            item.video_urls = servertools.resolve_video_urls(item)
        else:
            item.video_urls = [Video(url=item.url, server='Directo')]

    # Si video_urls es un str es que hay un error, se muestra
    if type(item.video_urls) == str:
        if not item.autoplay:
            dialog_ok('No puedes ver el video', item.video_urls)
            if settings.get_setting('setResolvedUrl', platformsettings.__file__):
                xbmcplugin.setResolvedUrl(
                    int(sys.argv[1]),
                    True,
                    xbmcgui.ListItem(
                        path=os.path.join(sysinfo.runtime_path, "resources", "nomedia")
                    )
                )
                xbmc.Player().stop()
        return

    # Cargamos las opciones devueltas por el servidor ordenadas por resolucion
    options = [
        item.clone(
            action=('play_video', 'play_torrent')[item.server == 'torrent'],
            url=v.url,
            label='Ver el video: [%s]%s [%s]' % (v.type, ('', ' [%s]' % v.res)[bool(v.res)], v.server),
            channel='',
            subtitle=v.subtitle or item.subtitle,
            mpd=v.mpd,
            headers=v.headers
        )
        for v in item.video_urls  # Las video_url deben estar ordenadas de mejor a peor calidad
    ]

    # Añadimos otras funciones en funcion de ciertos parametros
    if item.channel == 'downloads':
        options.append(item.clone(
            action='remove',
            channel='downloads',
            label='Eliminar archivo',
            title=item.title or item.label,
        ))

    # Si hay mas de una opcion y no venimos de autoplay...
    if len(options) > 1 and not item.autoplay:
        # ... abrimos el menu de selección
        index = dialog_select('Selecciona una opcion', [o.label for o in options])
        if index == -1:
            if settings.get_setting('setResolvedUrl', platformsettings.__file__):
                xbmcplugin.setResolvedUrl(
                    int(sys.argv[1]),
                    True,
                    xbmcgui.ListItem(
                        path=os.path.join(sysinfo.runtime_path, "resources", "nomedia")
                    )
                )
                xbmc.Player().stop()
            return
    else:
        # ...sino seleccionamos la unica opcion posible
        index = 0

    # Si el action está en otro canal, lo lanzamos mediante el launcher
    if options[index].channel:
        from core import launcher
        launcher.run(options[index].clone())

    # En caso contrario, lanzamos la funcion aquí
    else:
        getattr(sys.modules[__name__], options[index].action)(options[index])


def play_video(item):
    """
    Lanza el reproductor de kodi con el vídeo seleccionado
    :param item:
    :return:
    """
    logger.trace()

    # Creamos el listItem
    listitem = xbmcgui.ListItem()

    # Asignamos los datos
    viewtools.set_item_info(item, listitem)
    listitem.setArt({'fanart': item.fanart})
    listitem.setArt({'poster': item.poster})
    listitem.setArt({'banner': item.banner})
    listitem.setArt({'thumb': item.thumb})

    # Si es mpd lo añade
    if item.mpd:
        listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')

    # Si la url tiene headeres, se pasan a str
    if type(item.headers) == dict:
        headers = '|' + '&'.join(['%s=%s' % (k, v) for k, v in item.headers.items()])
    else:
        headers = ''

    # Reproducimos
    if item.autoplay or not settings.get_setting('setResolvedUrl', platformsettings.__file__):
        # Creamos el playlist
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()

        # Añadimos la url y reproducimos
        playlist.add(item.url + headers, listitem)
        xbmc.Player().play(playlist, listitem)
        # Kodi 18 - Evitar que se quede en loading al reproducir
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
    else:
        # Añadimos la url y reproducimos
        listitem.setPath(item.url + headers)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

    # Si hay subtitulos, los cargamos
    if item.subtitle:
        xbmc.Player().setSubtitles(item.subtitle)

    # Marcar como visto
    def mark_as_watched_subThread(item):
        time_limit = time.time() + 10
        while not xbmc.Player().isPlaying() and time.time() < time_limit:
            time.sleep(1)

        if xbmc.Player().isPlaying():
            try:
                time_for_watched = ['0', '300', 'totaltime * 0.3', 'totaltime * 0.5', 'totaltime * 0.8']
                totaltime = xbmc.Player().getTotalTime()
                time_for_watched = eval(
                    time_for_watched[settings.get_setting("time_for_watched", platformsettings.__file__)])
                while xbmc.Player().isPlaying():
                    # logger.debug(xbmc.Player().getTime())
                    # logger.debug(time_for_watched)
                    if xbmc.Player().getTime() >= time_for_watched:
                        bbdd.media_viewed_set(item)
                        # xbmc.Player().stop() #TODO debug
                        break
                    time.sleep(30)
            except:
                logger.error()

    if settings.get_setting("mark_as_watched", platformsettings.__file__):
        t = Thread(target=mark_as_watched_subThread, args=[item])
        t.setDaemon(True)
        t.start()


def play_torrent(item):
    """
    Reproduce un torrent
    :param item:
    :return:
    """
    logger.trace()

    # Creamos el listItem
    listitem = xbmcgui.ListItem()

    # Asignamos los datos
    viewtools.set_item_info(item, listitem)
    listitem.setArt({'fanart': item.fanart})
    listitem.setArt({'poster': item.poster})
    listitem.setArt({'banner': item.banner})
    listitem.setArt({'thumb': item.thumb})

    # Opciones disponibles para Reproducir torrents
    options = list()

    options.append(
        ["Cliente interno (necesario libtorrent)"]
    )

    # Plugins externos se pueden añadir otros
    if xbmc.getCondVisibility('System.HasAddon("plugin.video.xbmctorrent")'):
        options.append(
            [
                "Plugin externo: xbmctorrent",
                "plugin://plugin.video.xbmctorrent/play/%s"
            ]
        )

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.pulsar")'):
        options.append(
            [
                "Plugin externo: pulsar",
                "plugin://plugin.video.pulsar/play?uri=%s"
            ]
        )

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.quasar")'):
        options.append(
            [
                "Plugin externo: quasar",
                "plugin://plugin.video.quasar/play?uri=%s"
            ]
        )

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.stream")'):
        options.append(
            [
                "Plugin externo: stream",
                "plugin://plugin.video.stream/play/%s"
            ]
        )

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.torrenter")'):
        options.append(
            [
                "Plugin externo: torrenter",
                "plugin://plugin.video.torrenter/?action=playSTRM&url=%s"
            ]
        )

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.torrentin")'):
        options.append(
            [
                "Plugin externo: torrentin",
                "plugin://plugin.video.torrentin/?uri=%s&image="
            ]
        )

    if xbmc.getCondVisibility('System.HasAddon("plugin.video.elementum")'):
        options.append(
            [
                "Plugin externo: Elementum",
                "plugin://plugin.video.elementum/play?uri=%s"
            ]
        )

    if len(options) > 1:
        index = dialog_select("Abrir torrent con...", [o[0] for o in options])
    else:
        index = 0

    if index == 0:
        # Reproductor propio (libtorrent)
        played = False
        first = True
        debug = settings.get_setting("debug") == 3

        # Importamos el cliente
        from btserver import Client

        # Directorio torrent
        client_tmp_path = os.path.join(sysinfo.data_path, 'torrent')

        # Si no existe el directorio lo creamos
        if not os.path.isdir(client_tmp_path):
            os.makedirs(client_tmp_path)

        # Iniciamos el cliente:
        c = Client(
            url=item.url,
            is_playing_fnc=xbmc.Player().isPlaying,
            wait_time=None,
            timeout=10,
            temp_path=client_tmp_path,
            print_status=debug
        )

        # Mostramos el progreso
        dialog = dialog_progress("Torrent", "Iniciando...")

        # Mientras el progreso no sea cancelado ni el cliente cerrado
        while not c.closed:
            try:
                # Obtenemos el estado del torrent
                s = c.status
                if debug:
                    # Montamos las tres lineas con la info del torrent
                    txt = '%.2f%% de %.1fMB %s | %.1f kB/s' % (
                        s.progress_file,
                        s.file_size,
                        s.str_state,
                        s.download_rate
                    )
                    txt2 = 'S: %d(%d) P: %d(%d) | DHT:%s (%d) | Trakers: %d' % (
                        s.num_seeds,
                        s.num_complete,
                        s.num_peers,
                        s.num_incomplete,
                        s.dht_state,
                        s.dht_nodes,
                        s.trackers
                    )
                    txt3 = 'Origen Peers TRK: %d DHT: %d PEX: %d LSD %d ' % (
                        s.trk_peers,
                        s.dht_peers,
                        s.pex_peers,
                        s.lsd_peers
                    )
                else:
                    txt = '%.2f%% de %.1fMB %s | %.1f kB/s' % (
                        s.progress_file,
                        s.file_size,
                        s.str_state,
                        s.download_rate
                    )
                    txt2 = 'S: %d(%d) P: %d(%d)' % (
                        s.num_seeds,
                        s.num_complete,
                        s.num_peers,
                        s.num_incomplete
                    )

                    txt3 = 'Deteniendo automaticamente en: %s' % s.timeout

                dialog.update(s.buffer, txt, txt2, txt3)
                time.sleep(0.5)

                if dialog.iscanceled():
                    dialog.close()
                    if s.buffer == 100:
                        if dialog_yesno("Torrent", "¿Deseas iniciar la reproduccion?"):
                            played = False
                            dialog = dialog_progress("Torrent", "")
                            dialog.update(s.buffer, txt, txt2, txt3)
                        else:
                            dialog = dialog_progress("Torrent", "")
                            break

                    else:
                        if dialog_yesno("Torrent", "¿Deseas cancelar el proceso?"):
                            dialog = dialog_progress("Torrent", "")
                            break

                        else:
                            dialog = dialog_progress("Torrent", "")
                            dialog.update(s.buffer, txt, txt2, txt3)

                # Si el buffer se ha llenado y la reproduccion no ha sido iniciada, se inicia
                if s.buffer == 100 and not played:
                    # Cerramos el progreso
                    dialog.close()

                    # Reproducimos
                    if not settings.get_setting('setResolvedUrl', platformsettings.__file__) or not first:

                        # Creamos el playlist
                        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                        playlist.clear()

                        # Añadimos la url y reproducimos
                        playlist.add(c.get_play_list(), listitem)
                        xbmc.Player().play(playlist, listitem)
                        # Kodi 18 - Evitar que se quede en loading al reproducir
                        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                    else:
                        first = False
                        # Añadimos la url y reproducimos
                        listitem.setPath(c.get_play_list())
                        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
                        logger.debug(xbmc.Player().isPlaying())
                        time.sleep(1)

                    # Marcamos como reproducido para que no se vuelva a iniciar
                    played = True

                    # Y esperamos a que el reproductor se cierre
                    while xbmc.Player().isPlaying():
                        time.sleep(1)

                    # Cuando este cerrado,  Volvemos a mostrar el dialogo
                    dialog = dialog_progress("Torrent", "")
                    dialog.update(s.buffer, txt, txt2, txt3)

            except Exception:
                logger.error()
                break

        dialog.update(100, "Terminando y eliminando datos", " ", " ")

        # Detenemos el cliente
        if not c.closed:
            c.stop()

        # Y cerramos el progreso
        dialog.close()

    elif index > 0:
        # Plugins externos
        logger.debug("Llamando a %s..." % options[index][0])
        xbmc.executebuiltin(
            'PlayMedia(%s)' % (options[index][1] % urllib.quote_plus(item.url))
        )

    # Fix ventana Lista Abortada
    if settings.get_setting('setResolvedUrl', platformsettings.__file__):
        xbmcplugin.setResolvedUrl(
            int(sys.argv[1]),
            True,
            xbmcgui.ListItem(
                path=os.path.join(sysinfo.runtime_path, "resources", "nomedia")
            ))
        xbmc.Player().stop()
