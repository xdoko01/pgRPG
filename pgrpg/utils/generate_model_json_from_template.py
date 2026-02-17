''' CLI Utility that takes files (PNG spritesheet) in given folder
and generates Tiled SW JSON file to each of them based on the provided
json template.

Motivation:
    Creation of Tiled spritesheets for the pgrpg can be a time-consuming process - defining
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
    python generate_model_json_from_template.py TEMPLATE FILES [ACTIONS]


    TEMPLATE ... Template file with path. All created json files will be similar
            to this file

    MASK ... including path to the files e.g. *.png, male_*.png

    ACTIONS ... (OPTIONAL) actions that should be removed from the resulting JSON.

Examples:
    python generate_tiled_json_from_template.py c:\template.json c:\*.png shoot shoot_idle


Notes:
    The generated json files are fine to be opened in Tiled SW, but are not nicelly formated
    for reading. Opening and saving the files in Tiled software formats the JSON nicely in the
    files.
'''

import glob, os, sys, pathlib
import json

if __name__ == "__main__":
    try:
        template = pathlib.Path(sys.argv[1])
        files = pathlib.Path(sys.argv[2])

        assert os.path.isfile(template), print(f'Template "{template}" does not exist.')

    except IndexError:
        print(f'Not enough parameters provided')
    except AssertionError:
        raise

    # Get the actions to remove from the file
    try:
        actions_to_remove = sys.argv[3:]
    except IndexError:
        actions_to_remove = False

    # Get separatelly path to files and the mask
    path_to_files = pathlib.Path(*files.parts[:-1])
    filemask = files.parts[-1]

    print(f'Template: {template}')
    print(f'Files: {path_to_files}, mask: {filemask}')
    print(f'Actions to remove: {actions_to_remove}')

    # Read the json that is included in the template
    template_data = {}

    try:
        with open(template, 'r') as template_file:
            json_template_data = template_file.read()
            template_data = json.loads(json_template_data)
    except FileNotFoundError:
        print(f"Entity file {template} not found.")
        raise

    # Cycle all the files
    for file in path_to_files.glob(filemask):

        # Get path, name and extension of the PNG file
        path = pathlib.Path(*file.parts[:-1])
        base, extension = os.path.splitext(pathlib.Path(file.parts[-1]))
        #print(f'Path: {path} File base: {base} File ext: {extension}')

        # Change the JSON data
        adjusted_img_data = template_data.copy()
        adjusted_img_data["image"] = base + extension
        adjusted_img_data["name"] = base
        adjusted_tiles_data = template_data["tiles"].copy()

        # If some actions need to be removed
        if actions_to_remove:
            for tile in template_data["tiles"]:
                #print(f'Tile: {tile}')
                tile_to_delete = False
                for property in tile["properties"]:

                    if property["name"] == "action" and (property["value"] in actions_to_remove):
                        tile_to_delete = True
                        #print(f'Action {property["value"]} ... will be deleted')

                if tile_to_delete:
                    adjusted_tiles_data.remove(tile)
                    #print('DELETED')


            adjusted_img_data["tiles"] = adjusted_tiles_data

        # Write adjusted data to new json file
        with open(path / str(base + '.json'), 'w') as new_json_file:
            json.dump(adjusted_img_data, new_json_file)
            print(f'File {path / str(base + ".json")} created.')
