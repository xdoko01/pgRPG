'''
  PREREQ = ['new.collision_system:GenerateCollisionsProcessor']
  PREREQ = ["AND", 'new.collision_system:GenerateCollisionsProcessor', 'new.collision_system:GenerateCollisionsProcessor']
  PREREQ = ["OR", 'new.collision_system:GenerateCollisionsProcessor', 'new.collision_system:GenerateCollisionsProcessor']
  PREREQ = ["IF", "old.processor", "some.processor", "other.processor"]
'''

'''
1. Take the first item from the array.
2. test if the item is some keyword AND, OR
  2a. if no evaluate the first item and return the result
  2b. if yes, evaluate every item recursively and apply the condition

  var rules = { "and" : [
    {"<" : [ { "var" : "temp" }, 110 ]},
    {"==" : [ { "var" : "pie.filling" }, "apple" ] }
  ] };

  var data = { "temp" : 100, "pie" : { "filling" : "apple" } };

  jsonLogic.apply(rules, data);

'''
import functools

OPERATORS = {
	"AND" : lambda a, b: a and b,
	"OR" : lambda a, b: a or b,
	"XOR" : lambda a, b: a != b,
	"IF" : lambda a,b,c: b if a else c,
	">" : lambda a, b: a > b
}

def evaluate(expr, fnc=lambda x: x, data={}, operators={}) -> bool:
	''' Evaluate expression given by 'expr'. Single expression is
	evaluated using 'fnc' and complex expressions are evaluated
	using operators.

	expr: the expression
	fnc: function that should be executed on literal (simple expression)
	data: dictionary with data that are used in the expression - see jsonLogic above
	operators: list of operator functions
	'''

	# If the expression item is not a list - single expression for evaluation
	if not isinstance(expr, list):
		return fnc(expr)

	# If the expression is a list - evaluate recursivelly
	elif isinstance(expr, list):

		# In case of unknown operator
		if expr[0] not in operators:
			raise ValueError(f'Not supported logical operator: {expr[0]}.')
		# Process the expression
		else:

			# Evaluate all the arguments recursivelly
			result = map(lambda x: evaluate(expr=x, fnc=fnc, data=data, operators=operators), expr[1:])

			# Use the operator and apply it on arguments
			return functools.reduce(operators[expr[0]], result)



expression = ["AND", "1==1", ["OR", "1==2", "1==1"], [">", ["VAR","$num"], "10"]]
#expression = ["ONEOF", "1==1", "1==1", "1==1", "2==3"]
expression = ["IF", "1==1", "print('It is true')", "print('It is false')"]
data = { "$num" : "22"}

print(f'Evaluating expression {expression} \n')
print(f'Final result is {evaluate(expr=expression, fnc=eval, data=data, operators=OPERATORS)}')