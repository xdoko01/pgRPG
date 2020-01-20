import cmd
import code

from threading import Thread

class CommandLine(cmd.Cmd):
	''' A class to enable an interactive debug command line. Provides a full python shell to review
	and modify variables while the game is actively running.

	:param app: The tuxemon.Game object of the game itself.

	:type app: tuxemon.Game

	To include the command line in the game, simply add the following line under the
	initialization of the main game:

	>>> def __init__(self):
	...     self.cli = core.cli.CommandLine(self)
	'''

	def __init__(self, module=None):

		# Initiate the parent class
		cmd.Cmd.__init__(self)

		# Set up the command line prompt itself
		self.prompt = "pyRPG>> "
		self.intro = ('pyRPG CLI\nType "help", "copyright", "credits"'
					' or "license" for more information.')

		# Start the CLI in a separate thread
		self.module = module
		self.cmd_thread = Thread(target=self.cmdloop)
		self.cmd_thread.daemon = True
		self.cmd_thread.start()

	def do_python(self, line):
		"""Open a full python shell if "python" was typed in the command line. From here, you can
		look at and manipulate any variables in the application. This can be used to look at this
		instance's "self.module" variable which contains the game object (engine module)
		"""
		
		code.interact(local=locals())
