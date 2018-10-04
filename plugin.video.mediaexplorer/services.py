# -*- coding: utf-8 -*-
import threading

from core.libs import *
logger.init_logger('services.log', 3)

threading.Thread(
    target=execfile,
    args=[
        os.path.join(sysinfo.runtime_path, 'library_service.py'),
        {},
        {'__name__': '__main__'}]
).start()

threading.Thread(
    target=execfile,
    args=[
        os.path.join(sysinfo.runtime_path, 'update_service.py'),
        {},
        {'__name__': '__main__'}]
).start()
