from core.libs import *
import xbmc
from core import library

if __name__ == '__main__':
    update_interval = settings.get_setting('library_update', library.__file__)
    last_check_updates = settings.get_setting('last_check_updates', library.__file__) or 0

    if update_interval == 1:
        library.check_updates()

    monitor = xbmc.Monitor()
    while not monitor.abortRequested():

        if update_interval == 2 and time.time() - last_check_updates > 86400:
            library.check_updates()

        if monitor.waitForAbort(3600):
            break