''' CLI Utility that takes files (PNG spritesheet) in given folder
and generates Tiled SW JSON file to each of them based on the provided
json template.

Motivation:
    Creation of Tiled spritesheets for the pyRPG can be a time-consuming process - defining
    all optional attributes (direction, action, repeat, action frame) and specifying the
    animation fields. As most of the spritesheets are taken from LPC (Liberated Pixel Cup)
    contest, they have similar structure. Hence, it is enough to define all the optional
    attributes and animations only once and use that generated TILED json file as a template
    for other spritesheets stored in PNG format.

How it works:
    The program takes template.json and modifies 'image' and 'name' field in it based on
    PNG file name. E.g. If there is test_spritesheet.png in the path, the program generates
    'test_spritesheet.json' containing reference to test_spritesheet.png inside the json file.

Usage:
    python generate_tiled_json_from_template.py PATH TEMPLATE MASK [ACTIONS]

    PATH ... Path to the directory where PNG files are located and where JSON Tiles files
            will be created.

    TEMPLATE ... Template file located in the PATH. All created json files will be similar
            to this file

    MASK ... e.g. *.png, male_*.png

    ACTIONS ... (OPTIONAL) actions that should be removed from the resulting JSON.

Examples:
    python generate_tiled_json_from_template.py . template.json *.png

Notes:
    The generated json files are fine to be opened in Tiled SW, but are not nicelly formated
    for reading. Opening and saving the files in Tiled software formats the JSON nicely in the
    files.
'''

import glob, os, sys
import json

if __name__ == "__main__":
    try:
        print(f'Path: "{sys.argv[1]}"')
        print(f'Template: "{sys.argv[2]}"')
        print(f'Mask: "{sys.argv[3]}"')
    except IndexError:
        print(f'Not enough parameters provided')

    path = sys.argv[1]
    template = sys.argv[2]
    mask = sys.argv[3]
    
    # Get the actions to remove from the file
    try:
        to_remove = sys.argv[4:]
    except IndexError:
        to_remove = False

    print(to_remove)

    # Check input parameters
    try:
        assert os.path.isdir(path), print(f'Directory "{path}" not found.')
        assert os.path.exists(os.path.join(path, template)), print(f'Template "{os.path.join(path, template)}" does not exist.')
        assert os.path.isfile(os.path.join(path, template)), print(f'Template "{os.path.join(path, template)}" does not exist.')
    except AssertionError:
        raise

    # Change the directory
    os.chdir(path)

    # Read the json that is included in the template
    template_data = {}

    try:
        with open(os.path.join(path, template), 'r') as template_file:
            json_template_data = template_file.read()
            template_data = json.loads(json_template_data)
    except FileNotFoundError:
        print(f"Entity file {os.path.join(path, template)} not found.")
        raise

    # Cycle all the files
    for file in glob.glob(mask):

        # Get name and extension of the PNG file
        base, extension = os.path.splitext(file)

        # Change the JSON data
        adjusted_img_data = template_data.copy()
        adjusted_img_data["image"] = file
        adjusted_img_data["name"] = base
        adjusted_tiles_data = template_data["tiles"].copy()

        # If some actions need to be removed
        if to_remove:
            for tile in template_data["tiles"]:
                #print(f'Tile: {tile}')
                tile_to_delete = False
                for property in tile["properties"]:

                    if property["name"] == "action" and (property["value"] in to_remove):
                        tile_to_delete = True
                        #print(f'Action {property["value"]} ... will be deleted')

                if tile_to_delete:
                    adjusted_tiles_data.remove(tile)
                    #print('DELETED')


            adjusted_img_data["tiles"] = adjusted_tiles_data

        # Write adjusted data to new json file
        with open(os.path.join(path, base + '.json'), 'w') as new_json_file:
            json.dump(adjusted_img_data, new_json_file)
            print(f'File {os.path.join(path, base + ".json")} created.')

