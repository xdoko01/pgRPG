from ex_proc_class import ExampleProcessor

to_create = { 'name' : 'ExampleProcessor', 'params' : ['ex_fnc']}
to_create_2= { 'name' : 'ExampleProcessor', 'params' : {'ex_fnc' : 'ex_fnc'}}

processors = {
	'ExampleProcessor' : ExampleProcessor
}

def ex_fnc():
	print(f'Executed.')
	return 0

def _create_processor(name, params):
	return name(params)

def _create_processor_args(name, params):
	return name(**params)

def _create_processor_json(proc):
	return processors.get(proc.get('name'))(*[globals()[param] for param in proc.get('params')])

def _create_processor_json_2(proc):
	if isinstance(proc.get('params'), dict):
		return processors.get(proc.get('name'))(**{k : globals()[v] for k, v in proc.get('params').items()})
	elif isinstance(proc.get('params'), list):
		return processors.get(proc.get('name'))(*[globals()[param] for param in proc.get('params')])
	else:
		return processors.get(proc.get('name'))(globals()[proc.get('params')])

parameters = {
	'ex_fnc' : ex_fnc
}

if __name__ == '__main__':

	c = _create_processor(ExampleProcessor, ex_fnc)
	c.process()

	d = _create_processor_args(ExampleProcessor, {'ex_fnc' : ex_fnc})
	d.process()

	e = _create_processor_json(to_create)
	e.process()

	e = _create_processor_json_2(to_create_2)
	e.process()
