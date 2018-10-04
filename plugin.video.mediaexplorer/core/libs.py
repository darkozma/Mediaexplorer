# -*- coding: utf-8 -*-
# Sistema
import sys
import os
import re
import urllib2
import urllib
import urlparse
import time
import datetime
from threading import Lock
from threading import Thread as _Thread


# fix for datatetime.strptime returns None
class proxydt(datetime.datetime):
    def __init__(self, *args, **kwargs):
        super(proxydt, self).__init__(*args, **kwargs)

    @staticmethod
    def strptime(date_string, format):
        return datetime.datetime(*(time.strptime(date_string, format)[0:6]))


datetime.datetime = proxydt


class Thread(_Thread):
    def __stop(self):
        try:
            logger.logger_object.end_thread()
        finally:
            _Thread.__stop(self)


# MediaExplorer
from platformcode import platformsettings


class SysInfo():
    def __init__(self):
        self.runtime_path = platformsettings.runtime_path
        self.data_path = platformsettings.data_path
        self.temp_path = platformsettings.temp_path
        self.bookmarks_path = platformsettings.bookmarks_path
        self.os = sys.platform
        self. platform_name = platformsettings.platform_name
        self.platform_version = platformsettings.platform_version
        self.main_version = platformsettings.main_version
        self.py_version = '%d.%d.%d' % sys.version_info[0:3]
        self.profile = {}


sysinfo = SysInfo()
sys.path.append(os.path.join(sysinfo.runtime_path, 'lib'))

from core import servertools
from core import settings
from core import logger
from core import jsontools
from core import moduletools
from core import scrapertools
from core import filetools
from core.item import *
from platformcode import platformtools
from core import httptools
from core.mediainfo import MediaInfo
from core import mediainfo
from core import bbdd

# Reloads
reload(logger)
reload(settings)
reload(platformsettings)
reload(platformtools)
reload(jsontools)
reload(servertools)
reload(moduletools)
reload(httptools)
reload(scrapertools)
reload(filetools)
reload(bbdd)

# Inits
logger.init_logger()
settings.check_directories()
httptools.load_cookies()
sysinfo.profile = platformtools.get_profile()[1]
dump = datetime.datetime.strptime('20110101', '%Y%m%d')  # Necesario para iniciar strptime
bbdd.create()
