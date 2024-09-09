''' Function json_logic is aiming to evaluate logical expressions written 
in JSON.

In pyRPG it is used for example to evaluate prerequisities of quest processors.
'''

from functools import reduce

def get_var(data: dict, key):
	try:
		result = data[key]
	except (KeyError, TypeError, ValueError):
		return None
	else:
		return result

OPERATORS = {
	# Condition operators - true/false
	"ONEOF" : lambda *args: args.count(True) == 1,
	"ALLOF": lambda *args: reduce(lambda a, b: a and b, args),
	"ANYOF": lambda *args: reduce(lambda a, b: a or b, args),
	"AND": lambda *args: reduce(lambda a, b: a and b, args),
	"OR": lambda *args: reduce(lambda a, b: a or b, args),
	"IN": lambda item, list: item in list,

	"==": lambda *args: reduce(lambda a, b: a==b, args),
	"!=": lambda *args: reduce(lambda a, b: a!=b, args),
	">": lambda a, b: a>b,
	">=": lambda a, b: a>=b,
	"<": lambda a, b: a<b,
	"<=": lambda a, b: a<=b,

	# Non-condition operators
	"LIST": lambda list: None, # for returning list other than from data dict
	"VAR": lambda var: None,
	"IF": lambda cond, act: None,
	"SEQ": lambda *args: None,
	# Other
	"SCRIPT": lambda: None
}

def json_logic(expr, value_fnc=lambda value: value, script_fnc=lambda *args: None, data: dict={}):
	''' Evaluate expression given by 'expr'. Single expression is
	evaluated using 'fnc' and complex expressions are evaluated
	using operators.

	expr: the expression
	value_fnc: function that should be executed on literal (simple expression)
	script_fnc: function that should be executed on SCRIPT operator ["SCRIPT", "new.dialog", {}]
	TODO data: dictionary with data that are used in the expression - google jsonLogic
	'''

	#print(f'JSON_LOGIC: {expr=}, {value_fnc=}, {script_fnc=}, {data=}')

	assert isinstance(data, dict), f'Data must be a dictionary'

	# If the expression item is not a list - single expression for evaluation
	if not isinstance(expr, list):
		return value_fnc(expr)

	# If the expression is a list - evaluate recursivelly
	elif isinstance(expr, list):

		try:
			# Operation that we want to perform
			operator = expr[0].upper()
		except IndexError:
			# if the list is empty, return True
			return True
		except AttributeError:
			raise ValueError(f'Cannot evaluate the following expression: {expr}')

		# In case of unknown operator
		if operator not in OPERATORS:
			raise ValueError(f'Not supported logical operator: "{operator}".')
		
		# Process the expression recursivelly
		else:

			if operator == 'LIST':
				return value_fnc(expr[1])

			if operator == 'VAR':
				return get_var(data, expr[1])
			
			if operator == 'IF':
				return json_logic(expr=expr[2], value_fnc=value_fnc, script_fnc=script_fnc, data=data) if json_logic(expr=expr[1], value_fnc=value_fnc, script_fnc=script_fnc, data=data) else None

			if operator == 'SCRIPT':
				return script_fnc(*expr[1:])

			# Evaluate all the arguments recursivelly into the list of values
			values = [json_logic(expr=e, value_fnc=value_fnc, script_fnc=script_fnc, data=data) for e in  expr[1:]]

			#print(f'JSON_LOGIC: {values=}')

			# Use the operator and apply it on values using function defined in OPERATORS
			return OPERATORS[operator](*values)

if __name__ == '__main__':

	data = {"param1" : 10, "param2": "Hello", "param3": 0, "param_list": [1,2,3,4,10]}
	#expression = ["AND", "1==1", ["OR", "1==2", "1==1"]]
	#expression = ["and", "1==1", "1==1", "1==1", "2==3"]
	#expression = ["oneOf", "1==1", "1==1", "1==1", "2==3"]
	expression = ["oneOf", "1==1", "1==5", "1==1", "2==3"]
	expression = ['and', "True"]
	expression = 'True'
	expression = []
	expression = ["==", ["var", "param1"], 10] # True
	expression = ["==", ["var", "param2"], "Hello"] # True
	#expression = ["IF", ["==", ["var", "param1"], 10], "print('hello')"] # print('hello')
	#expression = ["SEQ", "print('hello')", "print('hello')", "print('hello again')"] # None
	#expression = ["IF", ["==", ["var", "param1"], 10], ["SEQ", "print('hello')", "print('hello')", "print('hello again')"]]
	expression = [
	"IF", 
		["==", ["var", "param1"], 10], 
		["SEQ", 
			["SCRIPT", "script.name.1", "script.args.1"], 
			["IF", 
				["ONEOF",
					["!=", ["var", "param2"], "Hello"],
					["!=", ["var", "param1"], 10]
				],
				["SEQ",
					["SCRIPT", "script.name.2", "script.args.2"],
					["SCRIPT", "script.name.3", "script.args.3"]
				]
			],
			["SCRIPT", "script.name.4", "script.args.4"]
		]
	]
	expression = ["==", ["VAR", "param3"], 0]

	expression = ["IN", 5, ["VAR", "param_list"]]
	
	expression = ["IN", ["VAR", "param1"], ["VAR", "param_list"]]

	#expression = ["IN", ["VAR", "param1"], [1,2,3,4,5,6,7,8,9,10]] # not supported now
	#expression = [1,2,3,4,5,6,7,8,9,10] # not supported now
	expression = ["VAR", "param1"]	#ok
	expression = ["VAR", "param_list"] #ok
	expression = ["VAR", [1,2,3]]  #returns None because it is not in data

	expression = ["LIST", [1,2,3]]  #returns the list that is not part of data!!!
	expression = ["IN", ["VAR", "param1"], ["LIST", [1,2,3,10]] ] # works



	print(f'Evaluating expression {expression} \n')
	print(f'Final result is {json_logic(expr=expression, value_fnc=lambda x: x, script_fnc=lambda *args: print(*args), data=data)}')