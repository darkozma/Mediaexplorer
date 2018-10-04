# -*- coding: utf-8 -*-
from core.libs import *


def mainlist(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        label='Configuración general',
        type='item1',
        action='config',
        folder=False,
        description='Ajustes generales'
    ))

    itemlist.append(item.clone(
        label='Configuración especifica para %s' % sysinfo.platform_name,
        type='item1',
        action='platform_config',
        folder=False,
        description='Ajustes especificos para %s' % sysinfo.platform_name
    ))

    itemlist.append(item.clone(
        label='Configuración de aspecto',
        type='item1',
        action='visual_config',
        folder=False,
        description='Todos los ajustes sobre la apariencia de MediaExplorer los encontrarás aquí'
    ))

    itemlist.append(item.clone(
        label='Configuración de canales',
        type='item1',
        action='menuchannels',
        folder=True,
        description='Ajustes de canales: Activar/Desactivar canales, Configurar cuentas de usuario, etc...',
    ))

    itemlist.append(item.clone(
        label='Configuración de servidores',
        type='item1',
        action='menuservers',
        folder=True,
        description='Ajustes de servidores: Activar/Desactivar servidores, Seleccionar los servidores favoritos, '
                    'Cuentas premium, etc...',
    ))


    itemlist.append(item.clone(
        label='Configuración de Anti Captcha',
        type='item1',
        action='config',
        channel='anticaptcha',
        description='Ajustes para el servicio anti captcha, necesario para algunas webs, requiere registro en '
                    'https://anti-captcha.com el servicio es de pago',
    ))



    itemlist.append(item.clone(label='', action=''))
    itemlist.append(item.clone(label='Ajustes por secciones:', type='label', action=''))

    itemlist.append(item.clone(
        label='Configuración de la Biblioteca',
        type='item',
        channel='library',
        action='config',
        folder=False,
        group=True,
        description='Todos los ajustes sobre la Biblioteca los encontrarás aquí'
    ))

    itemlist.append(item.clone(
        label='Configuración del Buscador',
        type='item',
        channel='finder',
        action='settings_menu',
        group=True,
        description='Todos los ajustes sobre el Buscador los encontrarás aquí'
    ))

    itemlist.append(item.clone(
        label='Configuración de Novedades',
        type='item',
        channel='newest',
        action='config_menu',
        folder=True,
        group=True,
        description='Todos los ajustes sobre la sección \'Novedades\' los encontrarás aquí'
    ))

    itemlist.append(item.clone(
        label='Configuración de Descargas',
        type='item',
        channel='downloads',
        action='config',
        folder=False,
        group=True,
        description='Todos los ajustes sobre la sección \'Descargas\' los encontrarás aquí'
    ))

    return itemlist


def platform_config(item):
    from platformcode import platformsettings
    platformsettings.config()


def config(item):
    platformtools.show_settings(callback='save_config')


def save_config(item, values):
    if sysinfo.platform_name == 'mediaserver' and 'adult_mode' in values:
        from platformcode import mediaserver
        if values['adult_mode'] == 1:
            values['adult_mode'] = 0
            mediaserver.set_adult_client()
        else:
            mediaserver.set_adult_client(False)
    set_settings(values)


def langs_filter(item):
    logger.trace()

    controls = []

    disabled_langs = settings.get_setting('disabled_langs') or []

    controls.append({
        'id': 'lang_filter_server',
        'label': 'Filtrar idiomas en el listado de servidores:',
        'type': 'bool',
        'value': settings.get_setting('lang_filter_server') or False
    })

    '''controls.append({
        'id': 'lang_filter_media',
        'label': 'Filtrar idiomas en el listado de contenido:',
        'type': 'bool',
        'value': settings.get_setting('lang_filter_media') or False
    })'''

    controls.append({
        'label': 'Idiomas que desea ocultar:',
        'type': 'label',
    })

    for lang in sorted(Languages().all, key=lambda obj: obj.label):
        controls.append({
            'id': lang.name,
            'label': lang.label,
            'type': 'bool',
            'value': lang.name in disabled_langs,
            'enabled': 'eq(-%s,true)|eq(-%s,true)' % (len(controls), len(controls) - 1)
        })

    return platformtools.show_settings(controls=controls,
                                       title=item.label,
                                       callback="langs_save"
                                       )


def langs_save(item, values):
    logger.trace()
    settings.set_setting('lang_filter_server', values.pop('lang_filter_server'))
    #settings.set_setting('lang_filter_media', values.pop('lang_filter_media'))
    settings.set_setting('disabled_langs', [k for k, v in values.items() if v is True])


def qualities_filter(item):
    logger.trace()

    controls = []

    disabled_qualities = settings.get_setting('disabled_qualities') or []
    controls.append({
        'id': 'quality_filter_server',
        'label': 'Filtrar calidades en el listado de servidores:',
        'type': 'bool',
        'value': settings.get_setting('quality_filter_server') or False
    })

    '''controls.append({
        'id': 'quality_filter_media',
        'label': 'Filtrar calidades en el listado de contenido:',
        'type': 'bool',
        'value': settings.get_setting('quality_filter_media') or False
    })'''

    controls.append({
        'label': 'Calidades que desea ocultar:',
        'type': 'label',
    })

    for quality in sorted(Qualities().all, key=lambda obj: obj.level):
        controls.append({
            'id': quality.name,
            'label': quality.label,
            'type': 'bool',
            'value': quality.name in disabled_qualities,
            'enabled': 'eq(-%s,true)|eq(-%s,true)' % (len(controls), len(controls) - 1)
        })

    return platformtools.show_settings(controls=controls,
                                       title=item.label,
                                       callback="qualities_save"
                                       )


def qualities_save(item, values):
    logger.trace()
    settings.set_setting('quality_filter_server', values.pop('quality_filter_server'))
    #settings.set_setting('quality_filter_media', values.pop('quality_filter_media'))
    settings.set_setting('disabled_qualities', [k for k, v in values.items() if v is True])


def visual_config(item):
    from platformcode import viewtools
    return platformtools.show_settings(mod=viewtools.__file__, title=item.label)


def menuchannels(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        label='Activar o desactivar canales',
        action='active_channels',
        folder=False,
        description='Desactiva los canales que no quieras que se muestren en MediaExplorer'
    ))

    itemlist.append(item.clone(label='', action=''))
    itemlist.append(item.clone(label='Ajustes propios de cada canal:', type='label', action=''))

    channel_list = moduletools.get_channels()

    for channel in channel_list:
        if not channel.get('settings'):
            continue

        controls = filter(lambda s: not s['id'].startswith('include_in_'), channel['settings'])

        if not controls:
            continue

        itemlist.append(item.clone(
            label=channel['name'],
            type='item',
            action='config_channel',
            path=channel['path'],
            folder=False,
            thumb='',
            group=True,
            description='Configuracíón indiviual para el canal %s' % channel['name']
        ))

    return itemlist


def menuservers(item):
    logger.trace()
    itemlist = list()

    itemlist.append(item.clone(
        label='Configuración general de servidores',
        action='config',
        channel='servertools',
        folder=False,
        description='Ajustes generales de los servidores'
    ))

    itemlist.append(item.clone(
        label='Activar o desactivar servidores',
        action='active_servers',
        folder=False,
        description='Desactiva los servidores que no quieras que se muestren en MediaExplorer'
    ))

    itemlist.append(item.clone(
        label='Servidores preferidos',
        action='priority_servers',
        folder=False,
        description='Selecciona los servidores preferidos, estos se mostraran al principio del listado'
    ))

    itemlist.append(item.clone(
        label='Filtrar servidores por idiomas',
        action='langs_filter',
        folder=False,
        description='Selecciona que idiomas que no deseas que se muestren en los resultados'
    ))

    itemlist.append(item.clone(
        label='Filtrar servidores por calidades',
        action='qualities_filter',
        folder=False,
        description='Selecciona que calidades que no deseas que se muestren en los resultados'
    ))

    itemlist.append(item.clone(label='', action=''))
    itemlist.append(item.clone(label='Ajustes propios de debriders:', type='label', action=''))

    debriders = moduletools.get_debriders()

    for debrider in debriders:
        if not debrider.get('settings'):
            continue

        itemlist.append(item.clone(
            label=debrider['name'],
            type='item',
            action='config_channel',
            path=debrider['path'],
            folder=False,
            thumb='',
            group=True,
            description='Configuracíón indiviual para el servidor %s' % debrider['name']
        ))

    itemlist.append(item.clone(label='', action=''))
    itemlist.append(item.clone(label='Ajustes propios de cada servidor:', type='label', action=''))

    server_list = moduletools.get_servers()

    for server in server_list:
        if not server.get('settings'):
            continue

        controls = filter(lambda s: not s['id'].startswith('include_in_'), server['settings'])

        if not controls:
            continue

        itemlist.append(item.clone(
            label=server['name'],
            type='item',
            action='config_channel',
            path=server['path'],
            folder=False,
            thumb='',
            group=True,
            description='Configuracíón indiviual para el servidor %s' % server['name']
        ))

    return itemlist


def priority_servers(item):
    logger.trace()

    server_list = moduletools.get_servers()
    namelist = ['Ninguno'] + [s['name'] for s in server_list]
    idlist = [None] + [s['id'] for s in server_list]

    controls = []

    for c in range(10):
        value = idlist.index(get_setting('priority_%s' % c, servertools.__file__))
        control = {'id': str(c),
                   'type': "list",
                   'label': 'Servidor #%s' % (c + 1),
                   'value': value,
                   'default': 0,
                   'enabled': (True, 'gt(-1,0)')[bool(c)],
                   'lvalues': namelist
                   }

        controls.append(control)

    return platformtools.show_settings(controls=controls,
                                       title=item.label,
                                       callback="priority_servers_save",
                                       item=idlist
                                       )


def priority_servers_save(item, values):
    logger.trace()
    progreso = platformtools.dialog_progress("Guardando configuración...", "Espere un momento por favor.")

    n = len(values)

    server_list = moduletools.get_servers()
    serverslist = [None] + [s['id'] for s in server_list]

    for i, v in values.items():
        progreso.update((int(i) * 100) / n, "Guardando configuración...")
        set_setting('priority_%s' % i, serverslist[v], servertools.__file__)

    progreso.close()


def config_channel(item):
    return platformtools.show_settings(mod=item.path,
                                       title=item.label
                                       )


def active_servers(item):
    logger.trace()

    server_list = moduletools.get_servers()

    controls = []
    for server in server_list:
        control = {'id': server['path'],
                   'type': "bool",
                   'label': server['name'],
                   'value': not get_setting('disabled', server['path']),
                   'default': True
                   }

        controls.append(control)

    return platformtools.show_settings(controls=controls,
                                       title=item.label,
                                       callback="save_active_channels"
                                       )


def active_channels(item):
    logger.trace()

    channel_list = moduletools.get_channels()

    controls = []
    for channel in channel_list:
        control = {'id': channel['path'],
                   'type': "bool",
                   'label': channel['name'],
                   'value': not get_setting('disabled', channel['path']),
                   'default': True
                   }

        controls.append(control)

    return platformtools.show_settings(controls=controls,
                                       title=item.label,
                                       callback="save_active_channels"
                                       )


def save_active_channels(item, values):
    logger.trace()
    progreso = platformtools.dialog_progress("Guardando configuración...", "Espere un momento por favor.")
    n = len(values)
    for i, v in enumerate(values):
        progreso.update((i * 100) / n, "Guardando configuración...")
        set_setting("disabled", not values[v], v)

    progreso.close()


#######################################################################################
def check_directories():
    logger.trace()
    if not os.path.exists(sysinfo.data_path):
        os.makedirs(sysinfo.data_path)


def set_setting(name, value, mod=__file__):
    settings_path = '%s.json' % os.path.splitext(
        mod.replace(sysinfo.runtime_path, os.path.join(sysinfo.data_path, 'settings'))
    )[0]

    data = {}

    if os.path.isfile(settings_path):
        try:
            data = jsontools.load_file(settings_path)
        except Exception:
            logger.error()

    data[name] = value
    jsontools.dump_file(data, settings_path)


def set_settings(values, mod=__file__):
    if sysinfo.runtime_path not in mod and ('/' in mod or '\\' in mod):
        mod = os.path.join(sysinfo.runtime_path, mod.replace('/', '\\').replace('\\', os.path.sep))

    settings_path = '%s.json' % os.path.splitext(
        mod.replace(sysinfo.runtime_path, os.path.join(sysinfo.data_path, 'settings')))[0]

    data = {}

    if os.path.isfile(settings_path):
        try:
            data = jsontools.load_file(settings_path)
        except Exception:
            logger.error()

    data.update(values)
    jsontools.dump_file(data, settings_path)


def get_setting(name, mod=__file__, getvalue=False):
    if sysinfo.runtime_path not in mod and ('/' in mod or '\\' in mod):
        mod = os.path.join(sysinfo.runtime_path, mod.replace('/', '\\').replace('\\', os.path.sep))

    settings_path = '%s.json' % os.path.splitext(
        mod.replace(sysinfo.runtime_path, os.path.join(sysinfo.data_path, 'settings')))[0]


    def get_value(v, n, m, t):
        if not t:
            return v

        controls = moduletools.get_controls(m)
        for control in controls:
            if control.get('id') == n and control.get('type') == 'list':
                try:
                    return control.get('lvalues')[v]
                except Exception:
                    pass
        return v

    if os.path.isfile(settings_path):
        try:
            data = jsontools.load_file(settings_path)
            if name in data:
                if name == 'adult_mode' and sysinfo.platform_name == 'mediaserver' and data[name] == 0:
                    from platformcode import mediaserver
                    return get_value(mediaserver.get_adult_client(), name, mod, getvalue)
                return get_value(data[name], name, mod, getvalue)
        except Exception:
            logger.error()

    controls = moduletools.get_controls(mod)

    for control in controls:
        if control.get('id') == name:
            if type(control['default']) == str and re.match('^eval\((.*?)\)$', control['default']):
                return get_value(eval(re.match('^eval\((.*?)\)$', control['default']).group(1)), name, mod, getvalue)
            else:
                return get_value(control['default'], name, mod, getvalue)
