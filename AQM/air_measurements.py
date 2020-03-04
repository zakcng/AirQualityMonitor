# Default air measurements

"""
DAQI Bands
"""

DAQI_bands = {
    '1': ['Low', '#9cff9c'],
    '2': ['Low', '#31ff00'],
    '3': ['Low', '#31cf00'],
    '4': ['Moderate', '#ff0'],
    '5': ['Moderate', '#ffcf00'],
    '6': ['Moderate', '#ff9a00'],
    '7': ['High', '#ff6464'],
    '8': ['High', '#red'],
    '9': ['High', '#900'],
    '10': ['Very High', '#ce30ff'],
}

"""
PM2.5
https://uk-air.defra.gov.uk/air-pollution/daqi?view=more-info&pollutant=pm25#pollutant
"""
pm25_limits = {
    '1': [0, 11],
    '2': [12, 23],
    '3': [24, 35],
    '4': [36, 41],
    '5': [42, 47],
    '6': [48, 53],
    '7': [54, 58],
    '8': [59, 64],
    '9': [65, 70],
    '10': [71, None]
}

"""
PM10
https://uk-air.defra.gov.uk/air-pollution/daqi?view=more-info&pollutant=pm10#pollutant
"""
pm10_limits = {
    '1': [0, 16],
    '2': [17, 33],
    '3': [34, 50],
    '4': [51, 58],
    '5': [59, 66],
    '6': [67, 75],
    '7': [76, 83],
    '8': [84, 91],
    '9': [92, 100],
    '10': [101, None]
}
