# getAirQData
Get air quality data for Poland from Chief Inspectorate Of Environmental Protection (GIOŚ) monitoring network

## Detailed description
Get air quality data via JSON file parsing ([link](http://api.gios.gov.pl/pjp-api/rest/station/findAll)). PM2.5 and PM10 values from cities present in **selected_cities** list are saved to file **airQData.txt**.

## Dependencies
Only Python 3 is needed.
