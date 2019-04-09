import os
import locale
import gettext

local = locale.setlocale(locale.LC_ALL, '')
if 'es_' in local:
	idiomas = ['en']
else:
	idiomas = ['en']
localedir = 'locale'
t = gettext.translation('config', 
                        localedir, 
                        languages=idiomas,
                        fallback=True)
_ = t.gettext


ids = None
ciudades = None
infoUser = ''
cookieFile = '.cookies.txt'
telegramFile = '.telegram.txt'
urlCiudad = 'view=city&cityId='
urlIsla = 'view=island&islandId='
prompt = ' >>  '
tipoDeBien = [_('Madera'), _('Vino'), _('Marmol'), _('Cristal'), _('Azufre')]
ConnectionError_wait = 5 * 60
debugON_alertarAtaques    = False
debugON_alertarPocoVino   = False
debugON_botDonador        = False
debugON_buscarEspacios    = False
debugON_entrarDiariamente = False
debugON_enviarVino        = False
debugON_menuRutaComercial = False
debugON_subirEdificio     = False
debugON_session           = False
debugON_comprarRecursos   = False
