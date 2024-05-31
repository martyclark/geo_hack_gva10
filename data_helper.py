import os
import json

data_path = os.path.join(os.path.dirname(__file__), 'data')
deta_file = os.path.join(data_path, 'global_dataset.geojson')

def load_data_and_labels():
    """
    Load data and labels from the geojson file
    """

    # Load data from files
    with open(deta_file, 'r') as f:
        data = json.load(f)

    return data['features']
