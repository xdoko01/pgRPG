# EVAL & EXEC - one dangerous way to evaluate conditions and do actions

b = "player"
a = "other"
finished = True


condition = 'b == "player" and a != "other"'

result = eval(condition)

if result:
	print("Condition " + condition + " fulfiled.")
	action = exec('finished = False')
	print(finished)


# Without EVAL - To evaluate condition, use custom made function
and_conditions = [(a,"other"), (b, "player")]

def check_and_condition(cond):
	result = True
	for i in cond:
		result = result and (i[0] == i[1])
	return result

print(check_and_condition(and_conditions))

# More complicated and powerfull function ... https://stackoverflow.com/questions/17752163/how-to-check-conditions-stored-as-strings-do-i-need-a-parser

