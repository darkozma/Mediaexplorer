# -*- coding: utf-8 -*-
import xbmcgui
import xbmc
from core.libs import *

# TODO: No funciona


class Recaptcha(xbmcgui.WindowXMLDialog):
    def start(self, key, referer):
        logger.trace()
        self.referer = referer
        self.key = key
        self.headers = {'Referer': self.referer}
        
        api_js = httptools.downloadpage("http://www.google.com/recaptcha/api.js?hl=es").data
        version = scrapertools.find_single_match(api_js, 'po.src = \'(.*?)\';').split("/")[5]
        self.url = "http://www.google.com/recaptcha/api/fallback?k=%s&hl=es&v=%s&t=2&ff=true" % (self.key, version)
        self.doModal()
        
        #Reload
        if self.result == {}:
            skin = 'Estuary' if xbmc.getSkinDir() == 'skin.estuary' else 'Default'
            self.result = Recaptcha("Recaptcha.xml", sysinfo.runtime_path, skin).start(self.key, self.referer)
            
        return self.result


    def update_window(self):
        logger.trace()
        data = httptools.downloadpage(self.url, headers=self.headers).data
        self.message = scrapertools.find_single_match(data, '<div class="rc-imageselect-desc-no-canonical">(.*?)(?:</label>|</div>)').replace("<strong>", "[B]").replace("</strong>","[/B]")
        self.token = scrapertools.find_single_match(data, 'name="c" value="([^"]+)"')
        self.image = "http://www.google.com/recaptcha/api2/payload?k=%s&c=%s" % (self.key, self.token)
        self.result = {}
        self.getControl(10020).setImage(self.image)
        self.getControl(10000).setText(self.message)
        self.setFocusId(10005)

    def onInit(self):
        logger.trace()
        self.setCoordinateResolution(2)
        self.update_window()

        
    def onClick(self, control):
        logger.trace()
        if control == 10003:
            self.result = None
            self.close()
            
        elif control == 10004:
            self.result = {}
            self.close()
            
        elif control == 10002:
            self.result = [int(k) for k in range(9) if self.result.get(k, False) == True]
            post = "c=%s" % self.token

            for r in self.result:
                post += "&response=%s" % r

            data = httptools.downloadpage(self.url, post, headers=self.headers).data
            self.result = scrapertools.find_single_match(data, '<div class="fbc-verification-token">.*?>([^<]+)<')
            if self.result:
                platformtools.dialog_notification("Captcha Correcto", "La verificación ha concluido")
                self.close()
            else:
                self.result = {}
                self.close()
        else:
            self.result[control - 10005] = not self.result.get(control - 10005, False)

