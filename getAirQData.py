#!/usr/bin/python3

# Import libraries
import urllib.request
import json

# Define helper functions
def read_json(url):
    '''Reads, parses and returns json data from url gave as argument'''
    json_url = urllib.request.urlopen(url)
    json_data = json_url.read().decode()
    parsed_json = json.loads(json_data)
    return parsed_json

nicknames = {530 : 'Śródmieście', 538 : 'Bielany', 550 : 'Ursynów', 552 : 'Targówek',
10434 : 'Konstancin-Jeziorna', 471 : 'Legionowo', 485 : 'Otwock', 10955 : 'Ursus', 10956 : 'Wawer'}

# Define cities of interest
selected_cities = ['Warszawa', 'Konstancin-Jeziorna', 'Otwock', 'Pruszków', 'Legionowo']

# Url where json data with list of all GIOŚ stations can be obtained
stations_url = 'http://api.gios.gov.pl/pjp-api/rest/station/findAll'

# Data of all GIOŚ stations
all_stations = read_json(stations_url)

# Table where stations from selected city will be stored
selected_stations = []

# Search for stations in selected city by dictionary keys
for station in all_stations:
    if station['city'] != None:
        city = station['city']['name']
        if city in selected_cities:
            if station['id'] in nicknames:
                station['stationName'] = nicknames[station['id']]
            selected_stations.append({'station_name' : station['stationName'],
                                      'station_id' : station['id']})

# Url where json data whith list of sensors on a specific station
# (add station's id number at the end)
sensors_url = 'http://api.gios.gov.pl/pjp-api/rest/station/sensors/'

for station in selected_stations:
    sensors = read_json(sensors_url + str(station['station_id']))
    for sensor in sensors:
        if sensor['param']['paramCode'] == 'PM10':
            station['PM10'] = {'id' : sensor['id']}
        elif sensor['param']['paramCode'] == 'PM2.5':
            station['PM2.5'] = {'id' : sensor['id']}

# Url where json data whith results of a sensor measurements can be obtained
# (add sensor's id number at the end)
value_url = 'http://api.gios.gov.pl/pjp-api/rest/data/getData/'

for station in selected_stations:
    if 'PM10' in station:
        data = read_json(value_url + str(station['PM10']['id']))

        if len(data['values']) == 0:
            station['PM10']['value'] = '-'
            station['PM10']['time'] = '--:--'
            break

        # Check if latest measurement has correct value
        # (latest measurements often have value None,
        # is such case we look at previous one and so on)
        value = None
        i = 0
        while not value:
            #print(station)
            #print(data['values'])
            value = data['values'][i]['value']
            station['PM10']['value'] = value
            station['PM10']['time'] = data['values'][i]['date'].split(' ')[-1][:-3]
            i += 1

            # If sensor will be out of order we may have no valid value
            if i >= len(data['values']):
                station['PM10']['value'] = '-'
                station['PM10']['time'] = '--:--'
                break

    if 'PM2.5' in station:
        data = read_json(value_url + str(station['PM2.5']['id']))

        if len(data['values']) == 0:
            station['PM10']['value'] = '-'
            station['PM10']['time'] = '--:--'
            break

        value = None
        i = 0
        while not value:
            value = data['values'][i]['value']
            station['PM2.5']['value'] = value
            station['PM2.5']['time'] = data['values'][i]['date'].split(' ')[-1][:-3]
            i += 1

            if i >= len(data['values']):
                station['PM10']['value'] = '-'
                station['PM10']['time'] = '--:--'
                break

outputFile = open('airQData.txt', 'w')

report = ''
for station in selected_stations:
    if 'PM10' in station or 'PM2.5' in station:
        try:
            station_report = ''
            station_report += station['station_name']
            if 'PM10' in station:
                station_report += '   PM10  '
                pm10_value = float(station['PM10']['value'])
                pm10_value = round(pm10_value, 1)
                station_report += str(pm10_value)
                station_report += ' µg/m³'
            if 'PM2.5' in station:
                station_report += '   PM2.5  '
                pm25_value = float(station['PM2.5']['value'])
                pm25_value = round(pm25_value, 1)
                station_report += str(pm25_value)
                station_report += ' µg/m³'
            station_report += '\n'
            report += station_report
        except:
            print('Invalid data')
            continue

# If GIOŚ system is down or there is no stations measuring
# PM10 or PM2.5 in selected city
if len(report) == 0:
	report = 'Brak danych z GIOŚ\n'

outputFile.write(report)

outputFile.close()
