# -*- coding: utf-8 -*-
from core . libs import *
from core import launcher
import xbmc
import xbmcgui
import xbmcplugin
import logging
import base64 , array
if 64-64: i11iIiiIii
if 65-65: O0/iIii1I11I1II1 % OoooooooOO-i1IIi
def o0OO00 ( ) :
 if sys . argv [ 2 ] :
  oo = Item( ). fromurl (sys . argv[ 2 ] )
  if oo . strm :
   logger . debug ( 'Es un .strm, se reproduce un archivo vacío y se recarga...' )
   del oo . strm
   xbmcplugin . setResolvedUrl (
 int ( sys . argv [ 1 ] ) ,
 True ,
 xbmcgui . ListItem (
 path = os . path . join ( sysinfo . runtime_path , "resources" , "nomedia" )
 )
 )
   xbmc . Player ( ) . stop ( )
   from core import library
   oo.path = filetools.join(settings.get_setting('library_path', library.__file__), oo.path)
   xbmc.executebuiltin("ActivateWindow(10025, %s?%s, return)" % (sys.argv[0], oo.tourl()))
  else :
   launcher . run ( oo )
   if 27 - 27: oO0OooOoO * o0Oo
 else :
  if launcher . start ( ):
   launcher . run ( Item (
 channel = "channelselector" ,
 action = "mainlist" ,
 content_type = 'icons' ,
 category = 'all'
 ) )
  if 5 - 5: OoO0O00
  if 2 - 2: ooOO00oOo % oOo0O0Ooo * Ooo00oOo00o . oOoO0oo0OOOo + iiiiIi11i
 logging . shutdown ( )
 if 24 - 24: II11iiII / OoOO0ooOOoo0O + o0000oOoOoO0o * i1I1ii1II1iII % oooO0oo0oOOOO

def o0O00 ( ) :
 logger . debug ( '|--------------------------|' )
 logger . debug ( '|-------MediaExplorer------|' )
 logger . debug ( '|--------------------------|' )
try :
 exec('%s(%s.%s("aW1wb3J0IHhibWMKaWYgeGJtYy5nZXRJbmZvTGFiZWwoJ0NvbnRhaW5lci5QbHVnaW5OYW1lJykgbm90IGluICgnJywgJ3BsdWdpbi52aWRlby5tZWRpYWV4cGxvcmVyJyk6CiAgICBwbGF0Zm9ybXRvb2xzLmRpYWxvZ19vaygKICAgICAgICAnTWVkaWFFeHBsb3JlcicsCiAgICAgICAgJ0ludGVudGFzIGFjY2VkZXIgYSBNZWRpYUV4cGxvcmVyIGRlc2RlIG90cm8gYWRkb24nLAogICAgICAgICdFc3RvIG5vIGVzdMOhIHBlcm1pdGlkbyBwb3IgTWVkaWFFeHBsb3JlcicKICAgICkKICAgIGV4aXQoMCkKbzBPMDAgKCApCm8wT08wMCggKQ=="))' % (tuple([array.array('B',O0oO).tostring ( ) for O0oO in [[101,120,101,99],[98,97,115,101,54,52],[98,54,52,100,101,99,111,100,101]]])))
 if 68 - 68: o00ooo0 / Oo00O0
except Exception as IiiiIiI1iIiI1 :
 logger . error ( )
 raise IiiiIiI1iIiI1