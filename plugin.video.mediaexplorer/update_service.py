from core.libs import *
import xbmc
from core import updates

if __name__ == '__main__':
    # Desactivar el modo de adultos si es necesario
    if settings.get_setting('adult_mode') == 1:
        settings.set_setting('adult_mode', 0)

    update_interval = settings.get_setting('update_interval') # ["Nunca", "Al iniciar", "Cada hora", "Una vez al dia"]

    if update_interval == 1 and updates.check_updates():
        platformtools.dialog_notification("MediaExplorer", "Actualizaciones disponibles", sound=False)

    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        update_interval = settings.get_setting('update_interval')
        last_check_updates = updates.last_check_updates()

        if ((update_interval == 2 and time.time() - last_check_updates > 3600) or
            (update_interval == 3 and time.time() - last_check_updates > 3600 * 24)) and \
            updates.check_updates():
                platformtools.dialog_notification("MediaExplorer", "Actualizaciones disponibles", sound=False)

        if monitor.waitForAbort(3600):break