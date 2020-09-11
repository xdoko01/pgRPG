''' Module implementing loop command
'''

def cmd_loop(*args, **kwargs):
    ''' Loop command - uses information stored in brain about actual number of loops
    '''
    iterations = kwargs.get("iterations", 0)
    brain = kwargs.get("brain", None)

    # Increase counter
    brain.loop_counter += 1

    if iterations > brain.loop_counter:
        # Throw exception - iteration has not finished
        return -1
    else:
        # Reset the looper
        brain.loop_counter = 0
        # Do not throw exception, looping has finished
        return 0
