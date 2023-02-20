from pprint import pprint

map = [
    ['X', '', '', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', '', '', '']
]

class Vect:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Step:
    frm: Vect
    to: Vect
    iter: int = 0

    def __init__(self, frm, to: Vect, iter: int):
        self.frm = frm
        self.to = to
        self.iter = iter

dirs = [[1,0], [-1,0], [0,1], [0,-1]]


def find_path(map, step_list: list, target: Vect) -> list:
    '''Find the path on the map and return
    it as a list of lists.
    '''


    while step_list:

        # Pop from the front of the queue
        step = step_list.pop(0)

        # If we have reached the target then end
        if step.to.x == target.x and step.to.y == target.y:

            map[step.to.y][step.to.x] = step.iter

            print(f'GOAL REACHED IN {step.iter}')

            print(f'Step to [{step.to.x}, {step.to.y}]')

            previous_step = step.frm
            while previous_step is not None:
                print(f'previous step {previous_step}, [{previous_step.to.x}, {previous_step.to.y}]')
                previous_step = previous_step.frm
            return

        else:
            

            # Mark as visited
            map[step.to.y][step.to.x] = step.iter
            print(f'Marking [{step.to.y}, {step.to.x}] as visited from [{step.frm.to.y if step.frm is not None else ""}, {step.frm.to.x if step.frm is not None else ""}]')
            pprint(map)
            input()

            # Add to the list for visiting, if there is no obstacle
            for dir in dirs:

                # Get the coordinates of the neighbour
                next_x, next_y = step.to.x + dir[0], step.to.y + dir[1]

                # If not out of bounds, continue
                if 0 <= next_x <= len(map[0]) and 0 <= next_y <= len(map):
                    next_step = Vect(next_x, next_y)

                    # If there is no obstacle, continue
                    if map[next_step.y][next_step.x] == '':
                        map[step.to.y][step.to.x] = step.iter+1
                        step_list.append(Step(frm=step, to=next_step, iter=step.iter+1))



if __name__ == "__main__":
    start = Vect(0,0)
    start_step = Step(frm=None, to=start, iter=0)
    target = Vect(5,5)

    find_path(map=map, step_list=[start_step], target=target)

    print(map)
