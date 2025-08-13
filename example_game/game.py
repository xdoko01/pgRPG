
"""
python example_game/game.py -f UI/test_button_pressed.jsonc
python example_game/game.py -h
"""
# Bring pyrpg package onto the path
import sys, os
from pathlib import Path

pyrpg_path = "../pyrpg"
sys.path.append(os.path.abspath(Path(pyrpg_path)))

def main(config_file: str, scene_file: str=None) -> None:
    """Run the game using the CLI arguments."""

    print(f"Starting with the following arguments: {scene_file=}, {config_file=}")

    # Load the framework using all the configs
    import pyrpg
    pyrpg.init(config_file=config_file, scene_file=scene_file)

if __name__ == "__main__":

    scene_file = None
    config_file = "example_game/config.jsonc"

    # Empty
    #scene_file = "empty.jsonc"

    # UI
    #scene_file = "UI/test_button_pressed.jsonc"

    # Games
    #scene_file = "games/kill_all/kill_all_level01.jsonc" # MUST BE REDONE BTREES
    #scene_file = "games/sokoban/sokoban_new_level02.jsonc"
    #scene_file = "games/sokoban/sokoban_new_level01.jsonc"    
    #scene_file = "games/sokoban/sokoban_new.jsonc"            
    #scene_file = "games/sokoban/sokoban.jsonc"                
    #scene_file = "games/collect_coins/collect_coins.jsonc"

    # 12_ai
    #scene_file = "tests/12_ai/test_entity_seen.jsonc" # old, does not work, fix it
    #scene_file = "tests/12_ai/move_between_2_points.jsonc"
    #scene_file = "tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear_using_template.jsonc"
    #scene_file = "tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear_using_events.jsonc"
    #scene_file = "tests/12_ai/guard_fight_back_if_ambushed_and_attack_on_sight_or_hear.jsonc"
    #scene_file = "tests/12_ai/guard_and_fight_back_if_ambushed_using_events.jsonc"
    #scene_file = "tests/12_ai/guard_and_fight_back_if_ambushed.jsonc"
    #scene_file = "tests/12_ai/guard_and_attack_on_sight.jsonc"

    #scene_file = "tests/12_ai/simple/test_damaged.jsonc"
    #scene_file = "tests/12_ai/simple/test_bb_value.jsonc"
    #scene_file = "tests/12_ai/simple/do_parallel.jsonc"
    #scene_file = "tests/12_ai/simple/move_between_checkpoints.jsonc"
    #scene_file = "tests/12_ai/simple/move_to_vect.jsonc"
    #scene_file = "tests/12_ai/simple/move_to_target.jsonc"
    #scene_file = "tests/12_ai/simple/move_to.jsonc"

    #scene_file = "tests/12_ai/simple/attack.jsonc"
    #scene_file = "tests/12_ai/simple/face_target.jsonc"
    #scene_file = "tests/12_ai/simple/move_to_pos_target_vect.jsonc"
    #scene_file = "tests/12_ai/simple/move_to_pos_target.jsonc"
    #scene_file = "tests/12_ai/simple/move_to_pos_tile_vect.jsonc"
    #scene_file = "tests/12_ai/simple/move_to_pos_px_vect.jsonc"
    #scene_file = "tests/12_ai/simple/move_to_pos_tile.jsonc"
    #scene_file = "tests/12_ai/simple/move_to_pos_px.jsonc"

    # 11_sensors
    #scene_file = "tests/11_sensors/test_sensors_01.jsonc"
    
    # 10_effects
    #scene_file = "tests/10_effects/test_fx_01.jsonc"

    # 09_projectiles
    #scene_file = "tests/09_projectiles/test_projectile_score_generation.jsonc"
    #scene_file = "tests/09_projectiles/test_projectile_generation.jsonc"
    #scene_file = "tests/09_projectiles/test_projectile_damage.jsonc"
    #scene_file = "tests/09_projectiles/test_projectile_collision.jsonc"

    # 08_arm_ammo
    #scene_file = "tests/08_arm_ammo/test_arm_ammo_01"

    # 07_arm_weapon
    scene_file = "tests/07_arm_weapon/test_arm_weapon_01"

    # 06_teleportation
    #scene_file = "tests/06_teleportation/test_teleportation_02"
    #scene_file = "tests/06_teleportation/test_teleportation_01"

    # 05_pickup
    #scene_file = "tests/05_pickup/test_pickup_02.jsonc"
    #scene_file = "tests/05_pickup/test_pickup_01.jsonc"

    # 04_collisions
    #scene_file = "tests/04_collisions/test_collisions_05.yaml"
    #scene_file = "tests/04_collisions/test_collisions_05.jsonc"
    #scene_file = "tests/04_collisions/test_collisions_04.jsonc"
    #scene_file = "tests/04_collisions/test_collisions_03.jsonc"
    #scene_file = "tests/04_collisions/test_collisions_02.jsonc"
    #scene_file = "tests/04_collisions/test_collisions_01.jsonc"

    # 03_animations
    #scene_file = "tests/03_animations/test_weapon_animations.jsonc"
    #scene_file = "tests/03_animations/test_animations_01.jsonc"

    # 02_commands
    #scene_file = "tests/02_commands/test_commands_03.jsonc"
    #scene_file = "tests/02_commands/test_commands_02.jsonc"
    #scene_file = "tests/02_commands/test_commands_01.jsonc"
    #scene_file = "tests/02_commands/play_commands_03.jsonc"
    #scene_file = "tests/02_commands/play_commands_02.jsonc"
    #scene_file = "tests/02_commands/play_commands_01.jsonc"
    #scene_file = "tests/02_commands/record_commands.jsonc"

    # 01_movements
    #scene_file = "tests/01_movements/test_controls_12"
    #scene_file = "tests/01_movements/test_movement_11.jsonc"
    #scene_file = "tests/01_movements/test_movement_10.jsonc"
    #scene_file = "tests/01_movements/test_movement_09.jsonc"
    #scene_file = "tests/01_movements/test_movement_08.jsonc"
    #scene_file = "tests/01_movements/test_movement_07.jsonc"
    #scene_file = "tests/01_movements/test_movement_06.jsonc"
    #scene_file = "tests/01_movements/test_movement_05.jsonc"
    #scene_file = "tests/01_movements/test_movement_04.jsonc"
    #scene_file = "tests/01_movements/test_movement_03.jsonc"
    #scene_file = "tests/01_movements/test_movement_02.jsonc"
    #scene_file = "tests/01_movements/test_movement_01.jsonc"

    # 00_render
    #scene_file = "tests/00_render/test_render_02.jsonc"
    #scene_file = "tests/00_render/test_render_01.jsonc"

    # Parse the CLI for config and scene file
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-f", "--file", help="Load particular scene file.The path must be relative to QUEST_PATH defined in configuration.",type=str)
    parser.add_argument("-c", "--config", help="Load particular configuration file.", type=str)
    args = parser.parse_args()

    main(config_file=args.config or config_file, scene_file=args.file or scene_file)