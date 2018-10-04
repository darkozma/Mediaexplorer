# -*- coding: utf-8 -*-
import base64
import hashlib
from distutils.version import LooseVersion

from core.libs import *

auth = 'aimares:vLaXqJYWVPQGL8FBUREA'  # TODO: Cuando el repo sea publico esto se elimina
user = 'media_explorer'
repo = 'mediaexplorer'
headers = {'Authorization': 'Basic %s' % base64.b64encode(auth)}  # TODO: Cuando el repo sea publico esto se elimina
updates_file = os.path.join(sysinfo.data_path, 'updates.json')


def mainlist(item):
    logger.trace()
    itemlist = list()

    itemlist.append(Item(
        label='Version actual: %s' % sysinfo.main_version,
        type='label'
    ))

    itemlist.append(item.clone(
        action='check',
        label='Buscar actualizaciones ahora',
        description='Busca si hay actualizaciones disponibles',
        type='highlight'
    ))

    try:
        updates = get_updates()
        if updates['main']:
            for x, u in enumerate(updates['main']):
                itemlist.append(item.clone(
                    action='update',
                    label='Actualizar a la versión %s %s' % (u['version'], ['', ' (beta)'][u['beta']]),
                    description='Fecha: %s\nVersión: %s\nCambios: %s' % (
                        u['date'],
                        u['version'],
                        u['changes']
                    ),
                    date=u['date'],
                    version=u['version'],
                    url=u['url'],
                    mode='main',
                    type='highlight' if x == 0 else 'item'
                ))

        if count('channels'):
            itemlist.append(item.clone(
                action='list_to_update',
                mode='channels',
                label='Actualizaciones de canales (%s)' % count('channels'),
                description='Actualiza los canales',
                type='highlight'
            ))
        if count('servers'):
            itemlist.append(item.clone(
                action='list_to_update',
                mode='servers',
                label='Actualizaciones de servidores (%s)' % count('servers'),
                description='Actualiza los servidores',
                type='highlight'
            ))
    except Exception:
        pass
    return itemlist


def list_to_update(item):
    logger.trace()
    itemlist = list()

    updates = get_updates()['modules']

    for upd in updates[item.mode].values():
        if upd['compatible'] or not settings.get_setting('update_hide_incompatible'):
            new_item = item.clone(
                label=upd['name'] + (' [No compatible]' if not upd['compatible'] else ''),
                type='update',
                id=upd['id'],
                name=upd['name'],
                date=upd['date'],
                version=upd['version'],
                compatible=upd['compatible'],
                min_version=upd['min_version'],
                url=upd['url'],
                description='Fecha: %s\nVersión: %s\nCambios: %s\n' % (upd['date'], upd['version'], upd['changes']),
                action='update',
                icon="icon/%s.png" % upd['id'],
                poster="poster/%s.png" % upd['id'],
                thumb=upd.get('thumb', "thumb/%s.png" % upd['id']),
                mode=item.mode
            )
            itemlist.append(new_item)

    if itemlist:
        itemlist.insert(0, item.clone(
            label='Actualizar todos los %s' % ('canales' if item.mode == 'channels' else 'servidores'),
            action='update_all',
            type='highlight',
            description='Actualiza todos los %s' % ('canales' if item.mode == 'channels' else 'servidores')
        ))

    return itemlist


def update_all(item):
    logger.trace()

    if item.mode == 'channels' or item.mode == 'servers':
        dialog = platformtools.dialog_progress_bg('Actualizaciones', 'Actualizando...')
        c = 0
        updates = get_updates()['modules']
        for k, v in updates[item.mode].items():
            text = "Actualizando canal %s" if item.mode == 'channels' else "Actualizando servidor %s"
            dialog.update(c * 100 / len(updates[item.mode]), 'Actualizaciones', text % v['name'])
            c += 1
            update(Item(
                id=v['id'],
                mode=item.mode,
                all=True,
                name=v['name'],
                url=v['url'],
                version=v['version'],
                min_version=v['min_version'],
                compatible= moduletools.is_compatible(v['min_version'])
            ))
        dialog.close()


def update(item):
    logger.trace()

    if item.mode == 'main':
        from io import BytesIO
        from core import ziptools
        response = httptools.downloadpage(item.url, headers=headers)

        if response.sucess:
            fileobj = BytesIO()
            fileobj.write(response.data)
            if sysinfo.platform_name == 'kodi':
                if ziptools.extract(fileobj, os.path.dirname(sysinfo.runtime_path), True):
                    os.remove(updates_file)
            else:
                if ziptools.extract(fileobj, sysinfo.runtime_path, True):
                    os.remove(updates_file)
                    platformtools.itemlist_refresh()
                    os._exit(10)

        platformtools.itemlist_refresh()

    elif item.mode == 'channels' or item.mode == 'servers':
        if not item.compatible:
            if not item.all:
                platformtools.dialog_ok(
                    'Actualizaciones',
                    'El %s %s no es compatible, se requiere:' % (
                        ('canal', 'servidor')[item.mode == 'server'],
                        item.name
                    ),
                    'MediaExplorer: %s (actual %s)' % (
                        item.min_version.get('main'),
                        sysinfo.main_version
                    ),
                    'Python: %s (actual %s)' % (
                        item.min_version.get('python'),
                        sysinfo.py_version
                    )
                )
            return
        if item.url.startswith('http://www.mediaexplorer.tk'):
            json_data = httptools.downloadpage(item.url, post={
                "beta": ['false', 'true'][settings.get_setting('update_channel')],
            }).data
            py_data = httptools.downloadpage(item.url.replace('.json', '.py'), post={
                "beta": ['false', 'true'][settings.get_setting('update_channel')],
            }).data
        else:
            json_data = httptools.downloadpage(item.url, headers=headers).data
            py_data = httptools.downloadpage(item.url.replace('.json', '.py'), headers=headers).data

        if py_data and json_data:
            path = sysinfo.runtime_path
            open(os.path.join(path, item.mode, item.url.split('/')[-1]), 'wb').write(json_data)
            open(os.path.join(path, item.mode, item.url.split('/')[-1].replace('.json', '.py')), 'wb').write(py_data)
            # TODO: Eliminar .pyc?

            updates = get_updates()
            del updates['modules'][item.mode][item.id]
            set_updates(updates)

            if not item.all:
                text = 'Canal %s actualizado correctamente' if item.mode == 'channels' else 'Servidor %s actualizado correctamente'
                platformtools.dialog_ok('Actualizaciones', text % item.name)

            if not updates['modules'][item.mode]:
                platformtools.itemlist_update(Item(channel='updates', action='mainlist'))
            else:
                platformtools.itemlist_refresh()


def check(item):
    logger.trace()
    if not check_updates():
        platformtools.dialog_notification("Buscar actualizaciones", "No hay nuevas actualizaciones")
    platformtools.itemlist_refresh()


def last_check_updates():
    logger.trace()
    updates = get_updates()
    return updates['last_check_updates']


def count(m_type=None):
    logger.trace()
    updates = get_updates()
    count = 0

    if m_type == 'main':
        return 1 if updates.get('main') else 0

    if settings.get_setting('update_hide_incompatible'):
        if m_type:
            for id in updates['modules'].get(m_type, {}).keys():
                if updates['modules'][m_type][id].get('compatible', True):
                    count += 1
        else:
            for m_type in updates['modules'].keys():
                for id in updates['modules'].get(m_type, {}).keys():
                    if updates['modules'][m_type][id].get('compatible', True):
                        count += 1
            count += 1 if updates.get('main') else 0

    else:
        if m_type:
            count = len(updates['modules'].get(m_type, {}))

        else:
            count = len(updates['modules']['channels']) + len(updates['modules']['servers']) + \
                    (1 if updates.get('main') else 0)

    return count


def check_updates():
    logger.trace()
    updates = {
        'modules': get_modules_updates(),
        'main': get_main_updates(),
        'last_check_updates': time.time()
    }

    set_updates(updates)

    return count()


def set_updates(updates):
    jsontools.dump_file(updates, updates_file)


def get_updates():
    empty_updates = {
        'modules': {'channels': {}, 'servers': {}},
        'main': [],
        'last_check_updates': 0
    }

    if os.path.isfile(updates_file):
        updates = jsontools.load_file(updates_file)
        if 'modules' in updates and 'main' in updates and 'last_check_updates' in updates:
            if 'servers' in updates['modules'] and 'channels' in updates['modules']:
                return updates

    return empty_updates


def get_main_updates():
    # Primero probamos la API
    try:
        data = httptools.downloadpage(
            'http://www.mediaexplorer.tk/api/v1/updates/main',
            post={
                "beta": ['false', 'true'][settings.get_setting('update_channel')],
                "platform": sysinfo.platform_name,
                "version": sysinfo.main_version
            }
        ).data
        updates = jsontools.load_json(data)

    # Si la API no funciona, Bitbucket
    except Exception:
        logger.error()
        updates = []
        data = httptools.downloadpage(
            "https://api.bitbucket.org/2.0/repositories/media_explorer/mediaexplorer/downloads",
            headers=headers
        ).data
        try:
            data = jsontools.load_json(data).get('values', [])
            for i in filter(lambda dw: dw['name'].startswith("mediaexplorer-"), data):
                p, v, b = re.compile(
                    "mediaexplorer-([^-]+)-(.*?(?:\.([\d]{12}))?)\.zip"
                ).findall(i['name'])[0]

                if not p == sysinfo.platform_name:
                    continue

                if b and not settings.get_setting('update_channel'):
                    continue

                if not LooseVersion(v) > LooseVersion(sysinfo.main_version):
                    continue

                updates.append({
                    'version': v,
                    'date': i['created_on'][:19],
                    'changes': 'Sin información',
                    'url': i['links']['self']['href'],
                    'beta': bool(b),
                    'platform': p,
                    'filename': i['name']
                })

            updates.sort(key=lambda x: x['version'], reverse=True)
        except Exception:
            logger.error()
            updates = []
    return updates


def get_modules_updates():
    # Primero probamos la API
    data = {}
    d_url = ''
    try:
        data = jsontools.load_json(httptools.downloadpage(
            'http://www.mediaexplorer.tk/api/v1/updates/modules',
            post={
                "beta": ['false', 'true'][settings.get_setting('update_channel')]
            }
        ).data)
        d_url = 'http://www.mediaexplorer.tk/api/v1/updates/modules'
    # Si la API no funciona, Bitbucket
    except Exception:
        logger.error()
        try:
            m = ['master', 'develop'][settings.get_setting('update_channel')]
            data = jsontools.load_json(httptools.downloadpage(
                "https://api.bitbucket.org/2.0/repositories/media_explorer/mediaexplorer/downloads/modules_%s.json" % m,
                headers=headers
            ).data)

            # Obtenemos el json remoto y completamos los datos
            d_url = jsontools.load_json(httptools.downloadpage(
                'https://api.bitbucket.org/2.0/repositories/media_explorer/mediaexplorer/refs/branches/%s' % m,
                headers=headers
            ).data)['target']['links']['self']['href'].replace('/commit/', '/src/') + '/main'
        except Exception:
            logger.error()

    updates = {
        'servers': {},
        'channels': {}
    }

    for file_name, remote_data in data.items():
        m_type, m_path = file_name.split('/')
        if os.path.isfile(os.path.join(sysinfo.runtime_path, m_type, m_path)):
            data = open(os.path.join(sysinfo.runtime_path, m_type, m_path), 'rb').read()
            json_data = jsontools.load_json(data)
            hash_local = hashlib.sha1(data).hexdigest()
        else:
            hash_local = ''
            json_data = {'version': 0}

        if hash_local != remote_data['hash'] and remote_data['version'] > json_data['version']:
            updates[m_type][remote_data['id']] = remote_data

            updates[m_type][remote_data['id']]['url'] = d_url + '/%s/%s' % (m_type, m_path)
            updates[m_type][remote_data['id']]['compatible'] = moduletools.is_compatible(
                remote_data.get('min_version', {})
            )
            updates[m_type][remote_data['id']]['min_version'] = remote_data.get('min_version', {})


    return updates
