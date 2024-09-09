# QUest File Structure Description

## Templates
Template can be defined 
 - as external file
 - as part of `templates` section within the quest

Examples of possible json template definitions

 - as `string`
    - `"new/model/body/male/human/white"`
    - `"new/model/body/male/human/white()"`
    - `"t_tile_pos(5, 5, test_arena_sand)"`
    - `"t_tile_pos($tileX=5, $tileY=5, test_arena_sand)"`
    - `"t_tile_pos(5, 5, $map=test_arena_sand)"`
    - `"t_tile_pos($map=test_arena_sand, $tileY=5, $tileX=5)"`
    - `"new/_special/hunter(player01, 150, 1200, 100)"`

  - as `list`
    - `["t_tile_pos", [5, 5, "test_arena_sand"]]`
    - `["t_tile_pos", {"$tileX": 5, "$tileY": 5, "$map": "test_arena_sand"}]`
    - `["t_tile_pos", [5, 5], {"$map": "test_arena_sand"}]`

