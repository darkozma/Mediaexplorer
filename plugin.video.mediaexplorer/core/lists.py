# -*- coding: utf-8 -*-
from core import friendpaste
from core.libs import *


def mainlist(item):
    logger.trace()
    itemlist = list()

    # Mi lista
    my_list_id = settings.get_setting('my_list_id', __file__)
    if not my_list_id:
        code = int(time.time())
        my_list_id = friendpaste.create("lista_vacia", code)
        settings.set_setting('my_list_id', my_list_id, __file__)
        settings.set_setting('my_list_code', code, __file__)

    if my_list_id:
        itemlist.append(item.clone(
            label="Mi lista",
            label_extra={"sublabel": " (ID: %s)" % my_list_id, "color": "color2", "value": "True"},
            action="categories",
            type="item",
            content_type='icons',
            list_id=my_list_id,
            poster="http://www.codigos-qr.com/qr/php/qr_img.php?d=%s&s=4&e=" % my_list_id
        ))

    # listado de listas añadidas
    remote_lists = settings.get_setting('remote_lists', __file__) or {}
    if remote_lists:
        itemlist.append(item.clone(
            type='label',
            label="Listas remotas:"
        ))
        itemlist_remotes = []
        for id, name in remote_lists.items():
            itemlist_remotes.append(item.clone(
                label=name,
                action="categories",
                type="item",
                content_type='icons',
                group=True,
                context=[
                    {"label": "Eliminar lista", "context_action": 'remove_list'},
                    {"label": "Cambiar nombre", "context_action": 'rename_list'}
                ],
                list_id=id
            ))
        itemlist_remotes.sort(key=lambda x: x.label)
        itemlist.extend(itemlist_remotes)

    itemlist.append(item.clone(
        type='label',
        label=""
    ))
    itemlist.append(item.clone(
        label="Añadir nueva lista",
        action="add_list",
        type="highlight"
    ))

    return itemlist


def categories(item):
    logger.trace()
    itemlist = list()
    movies = list()
    tvshows = list()

    lista = friendpaste.read(item.list_id)
    if lista and lista != 'lista_vacia':
        lista = eval(lista)

        if not isinstance(lista, list):
            return itemlist

        for i in lista:
            new_item = Item().fromurl(i)
            if new_item.type == 'movie':
                movies.append(new_item.clone())
            else:
                tvshows.append(new_item.clone())

        if item.label_extra: del item.label_extra
        if item.description: del item.description

        if movies:
            itemlist.append(item.clone(
                label='%s\nPelículas (%s)' % (item.label, len(movies)),
                action='show_list',
                category='movie',
                description='',
                poster='poster/movie.png',
                icon='icon/movie.png',
                thumb='thumb/movie.png',
                content_type='movies'))

        if tvshows:
            itemlist.append(item.clone(
                label='%s\nSeries (%s)' % (item.label, len(tvshows)),
                action='show_list',
                category='tvshow',
                description='',
                poster='poster/tvshow.png',
                icon='icon/tvshow.png',
                thumb='thumb/tvshow.png',
                content_type='tvshows'))



    elif item.list_id != settings.get_setting('my_list_id', __file__):
        # Lista eliminada o vacia
        if platformtools.dialog_yesno("Lista: %s" % item.label,
                                      "Esta lista parece que ha sido borrada o esta vacía.",
                                      "¿Desea eliminarla de su listado?"):
            remove_list(item)
            return

    return itemlist


def show_list(item):
    logger.trace()
    itemlist = list()

    lista = friendpaste.read(item.list_id)
    if lista and lista != 'lista_vacia':
        lista = eval(lista)
        if isinstance(lista, list):
            my_list_id = settings.get_setting('my_list_id', __file__)
            for i in lista:
                new_item = Item().fromurl(i)
                if new_item.type == item.category:
                    if item.list_id == my_list_id:
                        new_item.context = [{"label": 'Eliminar de Mi Lista',
                                             "context_channel": 'lists',
                                             "context_action": 'remove_from_my_list'}]

                    itemlist.append(new_item.clone(list_id=item.list_id))

    return itemlist


def add_list(item):
    logger.trace()
    controls = [
        {
            'id': 'name',
            'type': "text",
            'label': 'Nombre:',
            'default': ''
        },
        {
            'id': 'id',
            'type': "text",
            'label': 'ID:',
            'default': ''
        }]

    if platformtools.show_settings(controls=controls, title="Añadir lista", callback="add_list_callback", item=item):
        platformtools.itemlist_refresh()


def add_list_callback(item, values):
    logger.trace()
    remote_lists = settings.get_setting('remote_lists', __file__) or {}
    my_list_id = settings.get_setting('my_list_id', __file__)

    if not values['name'] or not values['id']:
        platformtools.dialog_ok("Error al añadir la lista",
                                "Para añadir una lista es necesario un nombre y un ID válidos")
        return False

    if values['id'] not in remote_lists.keys() and values['id'] != my_list_id:
        lista = friendpaste.read(values['id'])
        if not lista:
            platformtools.dialog_ok("Error al añadir la lista: %s" % values['name'],
                                    "Esta lista ha sido borrada o el ID: %s es incorrecto." % values['id'])
            return False

        elif lista == 'lista_vacia' and not platformtools.dialog_yesno("Añadir lista: %s" % values['name'],
                                                                       "Esta lista esta vacía.",
                                                                       "¿Desea añadirla igualmente a su listado?"):
            return False

        remote_lists[values['id']] = values['name']
        settings.set_setting('remote_lists', remote_lists, __file__)
        return True

    platformtools.dialog_ok("Error al añadir la lista", "ID duplicado:",
                            "Este ID pertenece a la lista '%s'" % remote_lists.get(values['id'], "Mi Lista"))


def remove_list(item):
    remote_lists = settings.get_setting('remote_lists', __file__)
    del remote_lists[item.list_id]
    settings.set_setting('remote_lists', remote_lists, __file__)
    platformtools.itemlist_refresh()


def rename_list(item):
    remote_lists = settings.get_setting('remote_lists', __file__)

    name = platformtools.dialog_input(remote_lists[item.list_id], 'Escribe el nombre de la lista')
    if name:
        remote_lists[item.list_id] = name

    settings.set_setting('remote_lists', remote_lists, __file__)
    platformtools.itemlist_refresh()


# Funciones llamadas desde el menu contextual
def remove_from_my_list(item):
    logger.trace()

    my_list_id = settings.get_setting('my_list_id', __file__)
    my_list = eval(friendpaste.read(my_list_id))

    if isinstance(my_list, list):
        for i in my_list:
            new_item = Item().fromurl(i)
            if new_item.url == item.url:
                my_list.remove(i)

                if not my_list:
                    my_list = "lista_vacia"

                if friendpaste.update(my_list_id, my_list, settings.get_setting('my_list_code', __file__)):
                    platformtools.dialog_notification("Eliminar de Mi Lista",
                                                      "'%s' eliminada correctamente" % item.title)
                    platformtools.itemlist_refresh()
                    return


def add_to_my_list(item):
    logger.trace()

    my_list_id = settings.get_setting('my_list_id', __file__)
    if not my_list_id:
        code = int(time.time())
        my_list_id = friendpaste.create("lista_vacia", code)
        settings.set_setting('my_list_id', my_list_id, __file__)
        settings.set_setting('my_list_code', code, __file__)

    if my_list_id:
        my_list = friendpaste.read(my_list_id)
        if my_list:
            if my_list == 'lista_vacia':
                my_list = list()
            else:
                try:
                    my_list = eval(my_list)
                except:
                    my_list = list()

            # Eliminar opciones del menu contextual
            if item.context_channel: del item.context_channel
            if item.context_action: del item.context_action

            if item.tourl() in my_list:
                # TODO de momento solo se comprueba a nivel de item. En el futuro podriamos comprobar codigos y permitir añadir varios canales a la misma serie o pelicula
                platformtools.dialog_notification("Añadir a Mi Lista",
                                                  "'%s' ya habia sido añadida anteriormente" % item.title, 1, 9000)
                return

            my_list.append(item.tourl())
            if friendpaste.update(my_list_id, my_list, settings.get_setting('my_list_code', __file__)):
                platformtools.dialog_notification("Añadir a Mi Lista",
                                                  "'%s' añadida correctamente" % item.title)
                return

    platformtools.dialog_ok("Error al añadir a Mi Lista",
                            "Ha sido imposible añadir '%s' a Mi Lista" % item.title,
                            "Por favor, vuelva a intentarlo pasado unos minutos.")
