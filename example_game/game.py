# Path to the pyrpg engine module
pyrpg_path = '../pyrpg'

# Bring pyrpg package onto the path
import sys, os, getopt
from pathlib import Path

sys.path.append(os.path.abspath(Path(pyrpg_path)))

# Now do your import
from pyrpg.main import init

def main(argv):
    '''Run the game using the CLI arguments'''

    console = True
    scene_path = None
    config_path = Path("config.json")

    # Games
    #scene_path = 'games/kill_all/kill_all_level01.json'
    #scene_path = 'games/sokoban/sokoban_new_level02.json'    NOT WORKING
    #scene_path = 'games/sokoban/sokoban_new_level01.json'    NOT WORKING
    #scene_path = 'games/sokoban/sokoban_new.json'            NOT WORKING
    #scene_path = 'games/sokoban/sokoban.json'                NOT WORKING
    #scene_path = 'games/collect_coins/collect_coins.json'

    # 12_ai
    #scene_path = 'tests/12_ai/test_entity_seen.jsonc' - old, does not work, fix it
    #scene_path = 'tests/12_ai/move_between_2_points.jsonc'
    scene_path = 'tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear_using_template.jsonc'
    #scene_path = 'tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear_using_events.jsonc'
    #scene_path = 'tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear.jsonc'
    #scene_path = 'tests/12_ai/guard_and_fight_back_if_ambushed_using_events.jsonc'
    #scene_path = 'tests/12_ai/guard_and_fight_back_if_ambushed.jsonc'
    #scene_path = 'tests/12_ai/guard_and_attack_on_sight.jsonc'

    #scene_path = 'tests/12_ai/simple/test_damaged.jsonc'
    #scene_path = 'tests/12_ai/simple/test_bb_value.jsonc'
    #scene_path = 'tests/12_ai/simple/do_parallel.jsonc'
    #scene_path = 'tests/12_ai/simple/move_between_checkpoints.jsonc'
    #scene_path = 'tests/12_ai/simple/move_to_vect.jsonc'
    #scene_path = 'tests/12_ai/simple/move_to_target.jsonc'
    #scene_path = 'tests/12_ai/simple/move_to.jsonc'

    #scene_path = 'tests/12_ai/simple/attack.jsonc'
    #scene_path = 'tests/12_ai/simple/face_target.jsonc'
    #scene_path = 'tests/12_ai/simple/move_to_pos_target_vect.jsonc'
    #scene_path = 'tests/12_ai/simple/move_to_pos_target.jsonc'
    #scene_path = 'tests/12_ai/simple/move_to_pos_tile_vect.jsonc'
    #scene_path = 'tests/12_ai/simple/move_to_pos_px_vect.jsonc'
    #scene_path = 'tests/12_ai/simple/move_to_pos_tile.jsonc'
    #scene_path = 'tests/12_ai/simple/move_to_pos_px.jsonc'

    # 11_sensors
    #scene_path = 'tests/11_sensors/test_sensors_01.jsonc'
    # 10_effects
    #scene_path = 'tests/10_effects/test_fx_01.jsonc'

    # 09_projectiles
    #scene_path = 'tests/09_projectiles/test_projectile_score_generation.jsonc'
    #scene_path = 'tests/09_projectiles/test_projectile_generation.jsonc'
    #scene_path = 'tests/09_projectiles/test_projectile_damage.jsonc'
    #scene_path = 'tests/09_projectiles/test_projectile_collision.jsonc'

    # 08_arm_ammo
    #scene_path = 'tests/08_arm_ammo/test_arm_ammo_01.json'

    # 07_arm_weapon
    #scene_path = 'tests/07_arm_weapon/test_arm_weapon_01.json'

    # 06_teleportation
    #scene_path = 'tests/06_teleportation/test_teleportation_02.json'
    #scene_path = 'tests/06_teleportation/test_teleportation_01.json'

    # 05_pickup
    #scene_path = 'tests/05_pickup/test_pickup_01.jsonc'

    # 04_collisions
    #scene_path = 'tests/04_collisions/test_collisions_05.yaml'
    #scene_path = 'tests/04_collisions/test_collisions_05.jsonc'
    #scene_path = 'tests/04_collisions/test_collisions_04.jsonc'
    #scene_path = 'tests/04_collisions/test_collisions_03.jsonc'
    #scene_path = 'tests/04_collisions/test_collisions_02.jsonc'
    #scene_path = 'tests/04_collisions/test_collisions_01.jsonc'

    # 03_animations
    #scene_path = 'tests/03_animations/test_weapon_animations.jsonc'
    #scene_path = 'tests/03_animations/test_animations_01.jsonc'

    # 02_commands
    #scene_path = 'tests/02_commands/test_commands_03.jsonc'
    #scene_path = 'tests/02_commands/test_commands_02.jsonc'
    #scene_path = 'tests/02_commands/test_commands_01.jsonc'
    #scene_path = 'tests/02_commands/play_commands_03.jsonc'
    #scene_path = 'tests/02_commands/play_commands_02.jsonc'
    #scene_path = 'tests/02_commands/play_commands_01.jsonc'
    #scene_path = 'tests/02_commands/record_commands.jsonc'

    # 01_movements
    #scene_path = 'tests/01_movements/test_controls_12'
    #scene_path = 'tests/01_movements/test_movement_11.jsonc'
    #scene_path = 'tests/01_movements/test_movement_10.jsonc'
    #scene_path = 'tests/01_movements/test_movement_09.jsonc'
    #scene_path = 'tests/01_movements/test_movement_08.jsonc'
    #scene_path = 'tests/01_movements/test_movement_07.jsonc'
    #scene_path = 'tests/01_movements/test_movement_06.jsonc'
    #scene_path = 'tests/01_movements/test_movement_05.jsonc'
    #scene_path = 'tests/01_movements/test_movement_04.jsonc'
    #scene_path = 'tests/01_movements/test_movement_03.jsonc'
    #scene_path = 'tests/01_movements/test_movement_02.jsonc'
    #scene_path = 'tests/01_movements/test_movement_01.jsonc'

    # 00_render
    #scene_path = 'tests/00_render/test_render_02.jsonc'
    #scene_path = 'tests/00_render/test_render_01.jsonc'


    usage_info = '''
DESCRIPTION
    Game demonstration using pyrpg.

OPTIONS
    -h, --help 
        Output usage information and exit.

    --disable-console
        Disable displaying of the console. By default, console is enabled.

    -f FILE, --file FILE
        Load particular scene file. Skips the menu and runs the scene immediatelly. The path must be relative to QUEST_PATH defined in configuration.

    -c CONFIG_FILE, --config CONFIG_FILE
        Load particular configuration file.

EXAMPLES
    game.py -h
        Outputs usage information and exits.

    game.py --disable-console
        Run example game without console.

    game.py --disable-console --file=tests/04_collisions/new_test_collisions_01.json
        Run scene without console.
'''

    try:
      opts, _ = getopt.getopt(argv, "hfc:",["help", "file=", "disable-console", "config="])
    except getopt.GetoptError:
      print(usage_info)
      sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(usage_info)
            sys.exit()
        elif opt in ("--disable-console"):
            console = False
        elif opt in ("-f", "--file"):
            scene_path = arg
        elif opt in ("-c", "--config"):
            config_file = arg

    print(f'Starting with the following arguments:\n{console=}\n{scene_path=}\n{config_path=}')

    from pyrpg.main import init
    init(console=console, scene_path=scene_path, config_path=config_path timed=False)

if __name__ == '__main__':
    main(sys.argv[1:])