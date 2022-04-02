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

from email.errors import NonPrintableDefect
import sys, getopt # for processing of cli arguments

def main(argv):
    '''Run the game using the CLI arguments'''

    console = True
    filepath = 'new/tests/04_collisions/new_test_01.json'
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
