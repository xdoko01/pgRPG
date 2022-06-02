''' Function json_logic is aiming to evaluate logical expressions written 
in JSON.

In pyRPG it is used for example to evaluate prerequisities of quest processors.
'''

from functools import reduce

OPERATORS = {
	"ONEOF" : lambda *args: args.count(True) == 1,
	"ALLOF": lambda *args: reduce(lambda a,b: a and b, args),
	"ANYOF": lambda *args: reduce(lambda a,b: a or b, args),
	"AND": lambda *args: reduce(lambda a,b: a and b, args),
	"OR": lambda *args: reduce(lambda a,b: a or b, args)
}

def json_logic(expr, fnc=lambda x: x, data={}) -> bool:
	''' Evaluate expression given by 'expr'. Single expression is
	evaluated using 'fnc' and complex expressions are evaluated
	using operators.

	expr: the expression
	fnc: function that should be executed on literal (simple expression)
	TODO data: dictionary with data that are used in the expression - google jsonLogic
	'''

	# If the expression item is not a list - single expression for evaluation
	if not isinstance(expr, list):
		return fnc(expr)

	# If the expression is a list - evaluate recursivelly
	elif isinstance(expr, list):

		try:
			# Operation that we want to perform
			operator = expr[0].upper()
		except IndexError:
			# if the list is empty, return True
			return True

		# In case of unknown operator
		if operator not in OPERATORS:
			raise ValueError(f'Not supported logical operator: "{operator}".')
		
		# Process the expression recursivelly
		else:

			# Evaluate all the arguments recursivelly into the list of values
			values = [json_logic(expr=e, fnc=fnc, data=data) for e in  expr[1:]]

			# Use the operator and apply it on values using function defined in OPERATORS
			return OPERATORS[operator](*values)

if __name__ == '__main__':


	#expression = ["AND", "1==1", ["OR", "1==2", "1==1"]]
	#expression = ["and", "1==1", "1==1", "1==1", "2==3"]
	#expression = ["oneOf", "1==1", "1==1", "1==1", "2==3"]
	expression = ["oneOf", "1==1", "1==5", "1==1", "2==3"]
	expression = ['and', "True"]
	expression = 'True'
	expression = []


	print(f'Evaluating expression {expression} \n')
	print(f'Final result is {json_logic(expr=expression, fnc=eval)}')