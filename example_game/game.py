# Path to the pyrpg engine module
pyrpg_path = '../pyrpg'

# Bring pyrpg package onto the path
import sys, os, getopt
from pathlib import Path

print(f'Path before change: {sys.path}')
#sys.path.append(os.path.abspath(os.path.join('..', 'pyrpg')))
sys.path.append(os.path.abspath(Path(pyrpg_path)))
print(f'Path after change: {sys.path}')

# Now do your import
from pyrpg.main import init

def main(argv):
    '''Run the game using the CLI arguments'''

    console = True
    filepath = None

    # Games
    #filepath = 'new/games/kill_all/kill_all_level01.json'
    #filepath = 'new/games/sokoban/sokoban_new_level02.json'    NOT WORKING
    #filepath = 'new/games/sokoban/sokoban_new_level01.json'    NOT WORKING
    #filepath = 'new/games/sokoban/sokoban_new.json'            NOT WORKING
    #filepath = 'new/games/sokoban/sokoban.json'                NOT WORKING
    #filepath = 'new/games/collect_coins/collect_coins.json'

    # 12_ai
    #filepath = 'new/tests/12_ai/test_entity_seen.jsonc' - old, does not work, fix it
    #filepath = 'new/tests/12_ai/move_between_2_points.jsonc'
    filepath = 'new/tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear_using_template.jsonc'
    #filepath = 'new/tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear_using_events.jsonc'
    #filepath = 'new/tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear.jsonc'
    #filepath = 'new/tests/12_ai/guard_and_fight_back_if_ambushed_using_events.jsonc'
    #filepath = 'new/tests/12_ai/guard_and_fight_back_if_ambushed.jsonc'
    #filepath = 'new/tests/12_ai/guard_and_attack_on_sight.jsonc'

    #filepath = 'new/tests/12_ai/simple/test_damaged.jsonc'
    #filepath = 'new/tests/12_ai/simple/test_bb_value.jsonc'
    #filepath = 'new/tests/12_ai/simple/do_parallel.jsonc'
    #filepath = 'new/tests/12_ai/simple/move_between_checkpoints.jsonc'
    #filepath = 'new/tests/12_ai/simple/move_to_vect.jsonc'
    #filepath = 'new/tests/12_ai/simple/move_to_target.jsonc'
    #filepath = 'new/tests/12_ai/simple/move_to.jsonc'

    #filepath = 'new/tests/12_ai/simple/attack.jsonc'
    #filepath = 'new/tests/12_ai/simple/face_target.jsonc'
    #filepath = 'new/tests/12_ai/simple/move_to_pos_target_vect.jsonc'
    #filepath = 'new/tests/12_ai/simple/move_to_pos_target.jsonc'
    #filepath = 'new/tests/12_ai/simple/move_to_pos_tile_vect.jsonc'
    #filepath = 'new/tests/12_ai/simple/move_to_pos_px_vect.jsonc'
    #filepath = 'new/tests/12_ai/simple/move_to_pos_tile.jsonc'
    #filepath = 'new/tests/12_ai/simple/move_to_pos_px.jsonc'

    # 11_sensors
    #filepath = 'new/tests/11_sensors/test_sensors_01.jsonc'

    # 10_effects
    #filepath = 'new/tests/10_effects/test_fx_01.jsonc'

    # 09_projectiles
    #filepath = 'new/tests/09_projectiles/test_projectile_score_generation.jsonc'
    #filepath = 'new/tests/09_projectiles/test_projectile_generation.jsonc'
    #filepath = 'new/tests/09_projectiles/test_projectile_damage.jsonc'
    #filepath = 'new/tests/09_projectiles/test_projectile_collision.jsonc'

    # 08_arm_ammo
    #filepath = 'new/tests/08_arm_ammo/test_arm_ammo_01.json'

    # 07_arm_weapon
    #filepath = 'new/tests/07_arm_weapon/test_arm_weapon_01.json'

    # 06_teleportation
    #filepath = 'new/tests/06_teleportation/test_teleportation_02.json'
    #filepath = 'new/tests/06_teleportation/test_teleportation_01.json'

    # 05_pickup
    #filepath = 'new/tests/05_pickup/test_pickup_01.jsonc'

    # 04_collisions
    #filepath = 'new/tests/04_collisions/test_collisions_05.yaml'
    #filepath = 'new/tests/04_collisions/test_collisions_05.jsonc'
    #filepath = 'new/tests/04_collisions/test_collisions_04.jsonc'
    #filepath = 'new/tests/04_collisions/test_collisions_03.jsonc'
    #filepath = 'new/tests/04_collisions/test_collisions_02.jsonc'
    #filepath = 'new/tests/04_collisions/test_collisions_01.jsonc'

    # 03_animations
    #filepath = 'new/tests/03_animations/test_weapon_animations.jsonc'
    #filepath = 'new/tests/03_animations/test_animations_01.jsonc'

    # 02_commands
    #filepath = 'new/tests/02_commands/test_commands_03.jsonc'
    #filepath = 'new/tests/02_commands/test_commands_02.jsonc'
    #filepath = 'new/tests/02_commands/test_commands_01.jsonc'
    #filepath = 'new/tests/02_commands/play_commands_03.jsonc'
    #filepath = 'new/tests/02_commands/play_commands_02.jsonc'
    #filepath = 'new/tests/02_commands/play_commands_01.jsonc'
    #filepath = 'new/tests/02_commands/record_commands.jsonc'

    # 01_movements
    #filepath = 'new/tests/01_movements/test_controls_12'
    #filepath = 'new/tests/01_movements/test_movement_11.jsonc'
    #filepath = 'new/tests/01_movements/test_movement_10.jsonc'
    #filepath = 'new/tests/01_movements/test_movement_09.jsonc'
    #filepath = 'new/tests/01_movements/test_movement_08.jsonc'
    #filepath = 'new/tests/01_movements/test_movement_07.jsonc'
    #filepath = 'new/tests/01_movements/test_movement_06.jsonc'
    #filepath = 'new/tests/01_movements/test_movement_05.jsonc'
    #filepath = 'new/tests/01_movements/test_movement_04.jsonc'
    #filepath = 'new/tests/01_movements/test_movement_03.jsonc'
    #filepath = 'new/tests/01_movements/test_movement_02.jsonc'
    #filepath = 'new/tests/01_movements/test_movement_01.jsonc'

    # 00_render
    #filepath = 'new/tests/00_render/test_render_02.jsonc'
    #filepath = 'new/tests/00_render/test_render_01.jsonc'


    usage_info = '''
DESCRIPTION
    pyrpg is a game engine.

OPTIONS
    -h, --help 
        Output usage information and exit.

    --disable-console
        Disable displaying of the console. By default, console is enabled.

    -f FILE, --file FILE
        Load particular game file. Skips the menu and runs the game immediatelly. The path must be relative to QUEST_PATH defined in configuration.

EXAMPLES
    pyrpg.py -h
        Outputs usage information and exits.

    pyrpg.py --disable-console
        Run pyrpg game without console.

    pyrpg.py --disable-console --file=new/tests/04_collisions/new_test_collisions_01.json
        Run game specified in new_game.json without console.
'''

    try:
      opts, _ = getopt.getopt(argv, "hf:",["help", "file=", "disable-console"])
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
            filepath = arg

    print(f'Starting PYRPG with the following arguments:\n"console"={console}\n"filepath"={filepath}')

    from pyrpg.main import init
    init(console=console, filepath=filepath, timed=False)

if __name__ == '__main__':
    main(sys.argv[1:])