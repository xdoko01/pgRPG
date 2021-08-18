import esper

class PosComp:
	def __init__(self):
		self.desc = 'I am Position Component'

class RenModComp:
	def __init__(self):
		self.desc = 'I am RenderableModel Component'

class MovComp:
	def __init__(self):
		self.desc = 'I am Movable Component'

class FlagDoMoveComp:
	def __init__(self):
		self.desc = 'I am FlagDoMove Component'

class FlagDoAttackComp:
	def __init__(self):
		self.desc = 'I am FlagDoAttack Component'

class IsDeadComp:
	def __init__(self):
		self.desc = 'I am IsDead Component'


if __name__ == '__main__':
	world = esper.World(timed=False)

	pos_comp_1 = PosComp()
	pos_comp_2 = PosComp()
	pos_comp_3 = PosComp()
	pos_comp_4 = PosComp()

	ren_mod_comp_1 = RenModComp()
	ren_mod_comp_2 = RenModComp()
	ren_mod_comp_3 = RenModComp()
	ren_mod_comp_4 = RenModComp()

	mov_comp_1 = MovComp()
	mov_comp_2 = MovComp()
	mov_comp_3 = MovComp()
	mov_comp_4 = MovComp()

	flag_do_move_comp_1 = FlagDoMoveComp()
	flag_do_move_comp_2 = FlagDoMoveComp()
	flag_do_move_comp_3 = FlagDoMoveComp()
	flag_do_move_comp_4 = FlagDoMoveComp()

	flag_do_attack_comp_1 = FlagDoAttackComp()
	flag_do_attack_comp_2 = FlagDoAttackComp()
	flag_do_attack_comp_3 = FlagDoAttackComp()
	flag_do_attack_comp_4 = FlagDoAttackComp()

	e1 = world.create_entity(pos_comp_1, 	ren_mod_comp_1, mov_comp_1, flag_do_move_comp_1)
	e2 = world.create_entity(				ren_mod_comp_2, mov_comp_2, flag_do_move_comp_2, flag_do_attack_comp_2)
	e3 = world.create_entity(				ren_mod_comp_3, mov_comp_3, flag_do_move_comp_3)
	e4 = world.create_entity(pos_comp_4,	ren_mod_comp_4, mov_comp_4)


	# Get all components for entity
	print(f'Components for e1 are: {world.components_for_entity(e1)}')

	# Get all entities that have PosComp
	print('*** Get all entities that have PosComp')
	for ent, pos in world.get_component(PosComp):
		print(f'Entity: {ent}, Component: {pos}')

	# Get all entities that have PosComp and FlagDoAttactComp
	print('*** Get all entities that have PosComp and FlagDoAttactComp')
	for ent, (pos, attack) in world.get_components(PosComp, FlagDoAttackComp):
		print(f'Entity: {ent}, Component: {pos}, Component: {attack}')

	# Get all entities that have PosComp, RenModComp  and do not have FlagDoAttactComp
	print('*** Get all entities that have PosComp, RenModComp and do not have FlagDoAttactComp')
	for ent, (pos, ren_mod) in world.get_components_ex(PosComp, RenModComp, exclude=FlagDoAttackComp):
		print(f'Entity: {ent}, Component: {pos}, Component: {ren_mod}')

	# Get all entities that have PosComp, RenModComp  and do not have FlagDoAttactComp, FlagDoMoveComp
	print('*** Get all entities that have PosComp, RenModComp and do not have FlagDoAttactComp, FlagDoMoveComp')
	for ent, (pos, ren_mod) in world.get_components_exs(include=(PosComp, RenModComp), exclude=(FlagDoAttackComp, FlagDoMoveComp)):
		print(f'Entity: {ent}, Component: {pos}, Component: {ren_mod}')

	# Get all entities that have RenModComp, MovComp and do not have FlagDoAttactComp, FlagDoMoveComp
	print('*** Get all entities that have RenModComp, MovComp and do not have FlagDoAttactComp, FlagDoMoveComp')
	for ent, (mov, ren_mod) in world.get_components_exs(include=(MovComp, RenModComp), exclude=(FlagDoAttackComp, FlagDoMoveComp, IsDeadComp)):
		print(f'Entity: {ent}, Component: {mov}, Component: {ren_mod}')
