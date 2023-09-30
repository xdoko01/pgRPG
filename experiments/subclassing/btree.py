class TreeNode:
    def __init__(self, name):
        self.name = name

    def process(self, blackboard):
        print(f'TreeNode print')

class Behavior(TreeNode):
    def __init__(self, name):
        super().__init__(name)
        print(f'+ Behavior __init__')

    def process(self, bb):
        super().process()
        print(f'and on top of that I have {bb}')

if __name__ == '__main__':
    action = Behavior('search')
    action.process()