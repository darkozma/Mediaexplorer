# -*- coding: utf-8 -*-
from core.libs import *


def get_controls(mod=None):
    logger.trace()
    if mod:
        module_path = '%s.json' % os.path.splitext(mod)[0]
    else:
        module_path = os.path.join(sysinfo.runtime_path, 'core', 'ajustes.json')

    if os.path.isfile(module_path):
        try:
            return jsontools.load_file(module_path).get('settings', [])
        except Exception:
            logger.error()
            return []
    else:
        return []


def is_compatible(reqs):
    from distutils.version import LooseVersion

    if reqs.get('python') and LooseVersion(reqs['python']) > LooseVersion(sysinfo.py_version):
            return False

    if reqs.get('main') and LooseVersion(reqs['main']) > LooseVersion(sysinfo.main_version):
            return False

    return True


def get_module_name(mod):
    logger.trace()
    module_path = '%s.json' % os.path.splitext(mod)[0]
    if os.path.isfile(module_path):
        try:
            return jsontools.load_file(module_path)['name']
        except Exception:
            return os.path.splitext(os.path.basename(mod))[0]
    else:
        return os.path.splitext(os.path.basename(mod))[0]


def get_module_parameters(mod):
    logger.trace()
    module_path = '%s.json' % os.path.splitext(mod)[0]
    if os.path.isfile(module_path):
        try:
            return jsontools.load_file(module_path)
        except Exception:
            logger.error()
            return []
    return {}


def get_channels():
    itemlist = []
    for f in os.listdir(os.path.join(sysinfo.runtime_path, 'channels')):
        f = os.path.join(sysinfo.runtime_path, 'channels', f)
        if not f.endswith('.json'):
            continue

        data = jsontools.load_file(f)
        if data and data['active']:
            #logger.debug(data['name'])
            data['path'] = f
            itemlist.append(data)
        else:
            continue

    return sorted(itemlist, key=lambda x: x['name'])


def get_servers():
    itemlist = []
    for f in os.listdir(os.path.join(sysinfo.runtime_path, 'servers')):
        f = os.path.join(sysinfo.runtime_path, 'servers', f)
        if not f.endswith('.json'):
            continue
            
        data = jsontools.load_file(f)
        if data:
            data['path'] = f
            itemlist.append(data)
        else:
            continue

    return sorted(itemlist, key=lambda x: x['name'])


def get_debriders():
    itemlist = []
    for f in os.listdir(os.path.join(sysinfo.runtime_path, 'debriders')):
        f = os.path.join(sysinfo.runtime_path, 'debriders', f)
        if not f.endswith('.json'):
            continue

        data = jsontools.load_file(f)
        if data:
            data['path'] = f
            itemlist.append(data)
        else:
            continue

    return sorted(itemlist, key=lambda x: x['name'])


def serverinfo(server):
    logger.trace()
    try:
        f = os.path.join(sysinfo.runtime_path, 'servers', '%s.json' % server)
        data = jsontools.load_file(f)
        return platformtools.dialog_ok(
            'Información del servidor %s' % data['name'],
            'Version: %s' % data['version'],
            'Fecha: %s' % data['changes'][0]['date'],
            'Cambios: %s' % data['changes'][0]['description']
        )
    except Exception:
        logger.error()


def channelinfo(channel):
    logger.trace()
    try:
        f = os.path.join(sysinfo.runtime_path, 'channels', '%s.json' % channel)
        data = jsontools.load_file(f)
        return platformtools.dialog_ok(
            'Información del canal %s' % data['name'],
            'Version: %s' % data['version'],
            'Fecha: %s' % data['changes'][0]['date'],
            'Cambios: %s' % data['changes'][0]['description']
        )
    except Exception:
        logger.error()
