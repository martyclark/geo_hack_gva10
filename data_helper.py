import os
import json

data_path = os.path.join(os.path.dirname(__file__), 'data')
city_heat_maps_path = os.path.join(os.path.dirname(__file__), 'data', 'city_heat_maps')
global_data_file = os.path.join(data_path, 'global_dataset.geojson')


def load_global_data_and_labels():
    """
    Load data and labels from the geojson file
    """

    # Load data from files
    with open(global_data_file, 'r') as f:
        data = json.load(f)

    return data['features']


def get_heat_map_by_city_name(city_name):
    file_path = os.path.join(city_heat_maps_path, city_name + '.geojson')
    # Load data from files
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)

        return data['features']
    else:
        return None


def get_data_by_id(data, facility_id):
    for f in data:
        if str(f["properties"]["ID_HDC_G0"]) == facility_id:
            return f["properties"]
    return None
