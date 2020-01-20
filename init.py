
# Settings have  paths etc.
Engine('settings.json')

{
  "WINDOW_TITLE" : "New Game",
  "WINDOW_SIZE" : [1024,768],
  "FULLSCREEN" : "False",
  "FPS" : 25,
  "TILE_RESOLUTION" : 64,
  "CELL_STEPS_WIDTH" : 2,
  "CELL_STEPS_HEIGHT" : 2,
  "DEBUG" : "False",
  "MAX_DISTANCE" : 20,
  "FONT_PATH" : "fonts/",
  "IMAGE_PATH" : "images/",
  "MAP_PATH" : "maps/",
  "SETTING_PATH" : "setting/"
}


# Load quest map and init player
# Create Map -> add to list of maps -> Create player(assign map to him) -> add to the list of players -> create screen -> add player to the screen -> add screen to the list of screens

Engine.load_game('main_quest')

{
  "screens" : [
    {
      "type"          : "MapScreen2D",
      "dimension"     : "500, 500",
      "position"      : "10, 10",
      "player_idx"    : "0",
      "textures"      : "True",
      "pix_per_step"  : "32"
    },
    {
      "type"          : "MapScreen2D",
      "dimension"     : "500, 500",
      "position"      : "520, 10",
      "player_idx"    : "1",
      "textures"      : "True",
      "pix_per_step"  : "64"
    },
    {
      "type"          : "InfoScreen",
      "dimension"     : "500, 500",
      "position"      : "10, 10",
      "player_idx"    : "1",
      "font"          : "default.ttf",
      "font_size"     : "18",
      "display_options" : [
        "entity_name",
        "entity_cell_position",
        "entity_map_position",
        "entity_move_vector",
        "entity_steps",
        "entity_speed",
        "entity_action",
        "entity_last_frame",
        "entity_no_of_arrows",
        "entity_inventory_info"
      ]
    },
    {
      "type"          : "ScriptScreen",
      "dimension"     : "500, 500",
      "position"      : "520, 10",
      "player_idx"    : "1",
      "font"          : "default.ttf",
      "font_size"     : "18"
    }
  ]
}