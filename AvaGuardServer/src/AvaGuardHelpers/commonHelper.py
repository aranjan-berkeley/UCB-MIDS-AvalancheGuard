# Turns a dictionary into a class
class Dict2Class(object):

    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])


class AreaLatLangDecoder:
    MainAndSubArea: str = ""
    lat: float = 0
    lng: float = 0


def areaToLangLatMapList():
    dct = {
        "Alps/Tirol": (47.2537, 11.6015),  # Correct
        "Alps/Bavaria": (47.5558, 11.7400),  # Corrected
        "Tahoe-Sierras/North-West Tahoe": (39.2545, -120.0322),  # Corrected
        "Tahoe-Sierras/North-East Tahoe": (39.2545, -119.9524),  # Corrected
        "Tahoe-Sierras/South-West Tahoe": (38.9399, -120.0466),  # Corrected
        "Tahoe-Sierras/South-East Tahoe": (38.9399, -119.9097),  # Corrected
        "Colorado/Aspen": (39.1911, -106.8175),  # Corrected
        "Colorado/Front Range": (40.0150, -105.2705),  # Corrected
        "Colorado/Grand Mesa": (39.0957, -108.1253),  # Corrected
        "Colorado/Gunnison": (38.5458, -106.9253),  # Corrected
        "Colorado/Northern San Juan": (37.9318, -107.8046),  # Corrected
        "Colorado/Southern San Juan": (37.6125, -107.6332),  # Corrected
        "Colorado/Sawatch": (38.7870, -106.2934),  # Corrected
        "Colorado/Vail & Summit County": (39.6061, -106.3550),  # Corrected
        "Colorado/Sangre de Cristo": (37.7775, -105.5201),  # Corrected
        "Unknown/Unknown": (0.0000, 0.0000)  # Placeholder for unknown location
    }

    return dct


def mainAreaToLangLatMapList():
    dct = {
        "Alps": ((45.0, 5.5), (48.0, 16.0)),  # Alps region
        "Tahoe-Sierras": ((38.5, -120.5), (39.5, -119.8)),  # Corrected for Tahoe-Sierras
        "Colorado": ((36.0, -109.0), (40.0, -102.0)),  # Corrected for Colorado
        "Unknown": ((0.0, 0.0), (0.0, 0.0))  # Placeholder for unknown location
    }

    return dct
