def initialize(register, module_name):
    '''Script registers itself at ScriptManager'''
    # Mandatory line
    register(fnc=condition_total_score_greater_than, alias=module_name)

def condition_total_score_greater_than(event, *args, **kwargs):
    '''Test if the total score of the player that is stored in the
    score event under 'total' parameter is greater than argument of
    this function 'score'.
    '''
    # Get the score that should be compared to score event total
    print(f'### Total from event {event.params["total"]} vs score as parameter {kwargs.get("score")}... returns {event.params["total"] > kwargs.get("score")}')
    return event.params["total"] > kwargs.get("score")
