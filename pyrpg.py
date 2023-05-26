''' pyrpg/pyrpg.py

    Called from:
    -> None (init module)

    Aim:
    -> Starts pyrpg.core.main.init() function which initiates pygame and starts the game.

    Usage:
    -> Run the pyrpg game

    Notes:

    Examples:
'''

import sys, getopt # for processing of cli arguments

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

    # 12_btrees
    filepath = 'new/tests/12_btrees/test_entity_seen.json'

    # 11_sensors
    #filepath = 'new/tests/11_sensors/test_sensors_01.json'

    # 10_effects
    #filepath = 'new/tests/10_effects/test_fx_01.json'

    # 09_projectiles
    #filepath = 'new/tests/09_projectiles/test_projectile_score_generation.json'
    #filepath = 'new/tests/09_projectiles/test_projectile_generation.json'
    #filepath = 'new/tests/09_projectiles/test_projectile_damage.json'
    #filepath = 'new/tests/09_projectiles/test_projectile_collision.json'

    # 08_arm_ammo
    #filepath = 'new/tests/08_arm_ammo/test_arm_ammo_01.json'

    # 07_arm_weapon
    #filepath = 'new/tests/07_arm_weapon/test_arm_weapon_01.json'

    # 06_teleportation
    #filepath = 'new/tests/06_teleportation/test_teleportation_02.json'
    #filepath = 'new/tests/06_teleportation/test_teleportation_01.json'

    # 05_pickup
    #filepath = 'new/tests/05_pickup/test_pickup_01.json'

    # 04_collisions
    #filepath = 'new/tests/04_collisions/test_collisions_05.yaml'
    #filepath = 'new/tests/04_collisions/test_collisions_05.json'
    #filepath = 'new/tests/04_collisions/test_collisions_04.json'
    #filepath = 'new/tests/04_collisions/test_collisions_03.json'
    #filepath = 'new/tests/04_collisions/test_collisions_02.json'
    #filepath = 'new/tests/04_collisions/test_collisions_01.json'

    # 03_animations
    #filepath = 'new/tests/03_animations/test_weapon_animations.json'
    #filepath = 'new/tests/03_animations/test_animations_01.json'

    # 02_commands
    #filepath = 'new/tests/02_commands/test_commands_02.json'
    #filepath = 'new/tests/02_commands/test_commands_01.json'

    # 01_movements
    #filepath = 'new/tests/01_movements/test_movement_10.json'
    #filepath = 'new/tests/01_movements/test_movement_09.json'
    #filepath = 'new/tests/01_movements/test_movement_08.json'
    #filepath = 'new/tests/01_movements/test_movement_07.json'
    #filepath = 'new/tests/01_movements/test_movement_06.json'
    #filepath = 'new/tests/01_movements/test_movement_05.json'
    #filepath = 'new/tests/01_movements/test_movement_04.json'
    #filepath = 'new/tests/01_movements/test_movement_03.json'
    #filepath = 'new/tests/01_movements/test_movement_02.json'
    #filepath = 'new/tests/01_movements/test_movement_01.json'

    # 00_render
    #filepath = 'new/tests/00_render/test_render_02.json'
    #filepath = 'new/tests/00_render/test_render_01.json'


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
