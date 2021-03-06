import os
import random
import locale
import gettext

local = locale.setlocale(locale.LC_ALL, '')
if 'es_' in local:
	languages = ['es']
else:
	languages = ['en']
languages = ['none']

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
t = gettext.translation('config',
                        localedir,
                        languages=languages,
                        fallback=True)
_ = t.gettext

# only use common browsers
if random.randint(0, 1) == 0:
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
else:
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'

update_msg = ''

isWindows = os.name == 'nt'

proxy = False
if proxy:
	http_proxy  = "http://127.0.0.1:8080"
	https_proxy = "socks5://127.0.0.1:9050" #Default Tor proxy address
	proxyDict = {"http": http_proxy, "https": https_proxy}
else:
	proxyDict = {}

ids_cache = None
cities_cache = None
menu_cities = ''
infoUser = ''
ikaFile = '.ikabot'
city_url = 'view=city&cityId='
island_url = 'view=island&islandId='
prompt = ' >>  '
materials_names = [_('Wood'), _('Wine'), _('Marble'), _('Cristal'), _('Sulfur')]
materials_names_english = ['Wood', 'Wine', 'Marble', 'Cristal', 'Sulfur']
materials_names_tec = ['wood', 'wine', 'marble', 'glass', 'sulfur']
tradegoods_names = [_('Saw mill'), _('Vineyard'), _('Quarry'), _('Crystal Mine'), _('Sulfur Pit')]
ConnectionError_wait = 5 * 60
actionRequest = 'REQUESTID'

debugON_alertAttacks          = False
debugON_alertLowWine          = False
debugON_donationBot           = False
debugON_searchForIslandSpaces = False
debugON_loginDaily            = False
debugON_enviarVino            = False
debugON_sendResources         = False
debugON_constructionList      = False
debugON_buyResources          = False
debugON_activateMiracle       = False
