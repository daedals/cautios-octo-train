import re

def replace_qml_coordinates(file_path, lat, lon):
    
    pattern = r'QtPositioning\.coordinate\(([-+]?\d*\.\d+|\d+), ([-+]?\d*\.\d+|\d+)\)'
    # ([-+]?\d*\.\d+|\d+) matches positive and negative floats or decimials

    with open(file_path, 'r') as file:
        content = file.read()

    replaced_content, number_of_replacements = re.subn(pattern, f'QtPositioning.coordinate({lat:.5f}, {lon:.5f})', content)

    print(number_of_replacements)

    with open(file_path, 'w') as file:
        file.write(replaced_content)

if __name__ == "__main__":
    replace_qml_coordinates("map_dummy_for_qmladjuster.qml", 5.0, 5.0)