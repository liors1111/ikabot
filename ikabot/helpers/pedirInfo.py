#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import json
import gettext
from decimal import *
from ikabot.config import *
from ikabot.helpers.getJson import *
from ikabot.helpers.gui import *

t = gettext.translation('pedirInfo', 
                        localedir, 
                        languages=idiomas,
                        fallback=True)
_ = t.gettext

getcontext().prec = 30

def read(min=None, max=None, digit=False, msg=prompt, values=None, empty=False): # lee input del usuario
	"""Reads input from user
	Parameters
	----------
	min : int
		smallest number acceptable as input
	max : int
		greatest number acceptable as input
	digit : bool
		boolean indicating whether or not the input MUST be an int
	msg : str
		string printed before the user is asked for input
	values : list
		list of strings which are acceptable as input
	empty : bool
		a boolean indicating whether or not an empty string is acceptable as input

	Returns
	-------
	result : str
		string representing the user's input
	"""
	def _invalido():
		print('\033[1A\033[K', end="") # Borro linea
		return read(min, max, digit, msg, values)

	try:
		leido = input(msg)
	except EOFError:
		return _invalido()

	if leido == '' and empty is True:
		return leido

	if digit is True or min is not None or max is not None:
		if leido.isdigit() is False:
			return _invalido()
		else:
			try:
				leido = eval(leido)
			except SyntaxError:
				return _invalido()
	if min is not None and leido < min:
		return _invalido()
	if max is not None and leido > max:
		return _invalido()
	if values is not None and leido not in values:
		return _invalido()
	return leido

def chooseCity(s, foreign=False):
	"""Prompts the user to chose a city
	Parameters
	----------
	s : Session
		Session object
	foreign : bool
		lets the user choose a foreign city
	
	Returns
	-------
	city : City 
		a city object representing the chosen city
	"""
	global menuCiudades
	(ids, ciudades) = getIdsOfCities(s)
	if menuCiudades == '':
		maxNombre = 0
		for unId in ids:
			largo = len(ciudades[unId]['name'])
			if largo > maxNombre:
				maxNombre = largo
		pad = lambda name: ' ' * (maxNombre - len(name) + 2)
		bienes = {'1': '(V)', '2': '(M)', '3': '(C)', '4': '(A)'}
		prints = []
		i = 0
		if foreign:
			print(_(' 0: ciudad ajena'))
		else:
			print('')
		for unId in ids:
			i += 1
			tradegood = ciudades[unId]['tradegood']
			bien = bienes[tradegood]
			nombre = ciudades[unId]['name']
			matches = re.findall(r'u[0-9a-f]{4}', nombre)
			for match in matches:
				to_unicode = '\\' + match
				to_unicode = to_unicode.encode().decode('unicode-escape')
				nombre = nombre.replace(match, to_unicode)
			num = ' ' + str(i) if i < 10 else str(i)
			menuCiudades += '{}: {}{}{}\n'.format(num, nombre, pad(nombre), bien)
		menuCiudades = menuCiudades[:-1]
	if foreign:
		print(_(' 0: ciudad ajena'))
	print(menuCiudades)

	if foreign:
		eleccion = read(min=0, max=len(ids))
	else:
		eleccion = read(min=1, max=len(ids))
	if eleccion == 0:
		return chooseForeignCity(s)
	else:
		html = s.get(urlCiudad + ids[eleccion -1])
		return getCiudad(html,s)

def chooseForeignCity(s):
	"""Prompts the user to select an island, and a city on that island (is only used in chooseCity)
	Parameters
	----------
	s : Session
		Session object

	Returns
	-------
	 city : City
		a city object representing the city the user chose
	"""
	banner()
	x = read(msg='coordenada x:', digit=True)
	y = read(msg='coordenada y:', digit=True)
	print('')
	url = 'view=worldmap_iso&islandX={}&islandY={}&oldBackgroundView=island&islandWorldviewScale=1'.format(x, y)
	html = s.get(url)
	try:
		jsonIslas = re.search(r'jsonData = \'(.*?)\';', html).group(1)
		jsonIslas = json.loads(jsonIslas, strict=False)
		idIsla = jsonIslas['data'][str(x)][str(y)][0]
	except:
		print(_('Coordenadas incorrectas'))
		enter()
		banner()
		return chooseCity(s, foreign=True)
	html = s.get(urlIsla + idIsla)
	isla = getIsla(html)
	maxNombre = 0
	for ciudad in isla['cities']:
		if ciudad['type'] == 'city':
			largo = len(ciudad['name'])
			if largo > maxNombre:
				maxNombre = largo
	pad = lambda name: ' ' * (maxNombre - len(name) + 2)
	i = 0
	opciones = []
	for ciudad in isla['cities']:
		if ciudad['type'] == 'city' and ciudad['state'] == '' and ciudad['Name'] != s.username:
			i += 1
			num = ' ' + str(i) if i < 10 else str(i)
			print('{}: {}{}({})'.format(num, ciudad['name'], pad(ciudad['name']), ciudad['Name']))
			opciones.append(ciudad)
	if i == 0:
		print(_('No hay ciudades donde enviar recursos en esta isla'))
		enter()
		return chooseCity(s, foreign=True)
	eleccion = read(min=1, max=i)
	ciudad = opciones[eleccion - 1]
	ciudad['islandId'] = isla['id']
	ciudad['cityName'] = ciudad['name']
	ciudad['propia'] = False
	return ciudad

def getBuildings(s, cityId):
	"""
	Parameters
	----------
	s : Session
		Session object
	cityID : str
		Represents the ID of the target city
	Returns
	-------
	selection : list
		a list of integers representing THE SAME POSITION, x number of times, where x is the number of upgrades necessary to reach the user's desired level for the position
	"""
	html = s.get(urlCiudad + cityId)
	ciudad = getCiudad(html)
	i = 0
	pos = -1
	prints = []
	posiciones = []
	prints.append(_('(0)\t\tsalir'))
	posiciones.append(None)
	for posicion in ciudad['position']:
		pos += 1
		if posicion['name'] != 'empty':
			i += 1
			level = posicion['level']
			if int(level) < 10:
				level = ' ' + level
			if posicion['isBusy']:
				level = level + '+'
			prints.append(_('({:d})\tlv:{}\t{}').format(i, level, posicion['name']))
			posiciones.append(pos)
	eleccion = getPositionAndTargetLevel(prints, ciudad, posiciones) #prints - what to print , cuidad - city, posiciones - non-empty positions
	return eleccion

def getPositionAndTargetLevel(prints, city, positions):
	"""Lets the user select a position, and a desired level for the position (Don't use this function. It is only used in getBuildings)
	Parameters
	----------
	prints : list
		a list of strings to print on the screen
	city : City
		a city object from which the user will be selecting positions
	positions : list
		a list of integers representing non-empty, non-currently-upgrading positions from which the user will be able to chose

	Returns
	-------
	rta : list
		a list of integers representing THE SAME POSITION, x number of times, where x is the number of upgrades necessary to reach the user's desired level for the position
	"""
	banner()
	for textoEdificio in prints:
		print(textoEdificio)

	eleccion = read(min=0, max=len(prints)-1)

	if eleccion == 0:
		return []
	posicion = positions[eleccion]
	nivelActual = int(city['position'][posicion]['level']) 
	if city['position'][posicion]['isBusy']: #sets the acutal level od the building 1 up, because it's being built right now
		nivelActual += 1

	banner()
	print(_('edificio:{}').format(city['position'][posicion]['name']))
	print(_('nivel actual:{}').format(nivelActual))

	nivelFinal = read(min=nivelActual, msg=_('subir al nivel:'))

	niveles = nivelFinal - nivelActual
	rta = []
	for i in range(0, niveles):
		rta.append(posicion)
	return rta

def askForValue(text, max):
	"""Displays text and asks the user to enter a value between 0 and max

	Parameters
	----------
	text : str
		text to be displayed when asking the user for input
	max : int
		integer representing the number of input options
	
	Returns
	-------
	var : int
		integer representing the user's input
		if the user has inputed nothing, 0 will be returned instead
	"""
	var = read(msg=text, min=0, max=max, empty=True)
	if var == '':
		var = 0
	return var

def getIdsOfCities(s, all=False):
	"""Gets the user's cities
	Parameters
	----------
	s : Session
		Session object
	all : bool
		boolean indicating whether all cities should be returned, or only those that belong to the current user

	Returns
	-------
	(ids, cities) : tuple
		a tuple containing the a list of city IDs and a list of city objects
	"""
	global ciudades
	global ids
	if ids is None or ciudades is None or s.padre is False:
		html = s.get()
		ciudades = re.search(r'relatedCityData:\sJSON\.parse\(\'(.+?),\\"additionalInfo', html).group(1) + '}'
		ciudades = ciudades.replace('\\', '')
		ciudades = ciudades.replace('city_', '')
		ciudades = json.loads(ciudades, strict=False)

		ids = [ciudad for ciudad in ciudades]
		ids = sorted(ids)

	# {'coords': '[x:y] ', 'id': idCiudad, 'tradegood': '..', 'name': 'nomberCiudad', 'relationship': 'ownCity'|'occupiedCities'|..}
	if all is False:
		ids_own   = [ciudad for ciudad in ciudades if ciudades[ciudad]['relationship'] == 'ownCity']
		ids_other = [ciudad for ciudad in ciudades if ciudades[ciudad]['relationship'] != 'ownCity']
		ciudades_own = ciudades.copy()
		for id in ids_other:
			del ciudades_own[id]
		return (ids_own, ciudades_own)
	else:
		return (ids, ciudades)

def getIdsOfIslands(s):
	"""Gets the IDs of islands the user has cities on
	Parameters
	----------
	s : Session
		Session object
	
	Returns
	-------
	idsIslas : list
		a list containing the IDs of the users islands
	"""
	(idsCiudades, ciudades) = getIdsOfCities(s)
	idsIslas = set()
	for idCiudad in idsCiudades:
		html = s.get(urlCiudad + idCiudad)
		ciudad = getCiudad(html)
		idIsla = ciudad['islandId']
		idsIslas.add(idIsla)
	return list(idsIslas)
