'''
    Experiment to understand sys.stdio functionality.
    Eventually, I am trying to create custom class that
    will feed input instead of stdio

    What is sys.stdio?
    A file object able to read and write str objects. 
    Often, a text file actually accesses a byte-oriented 
    datastream and handles the text encoding automatically. 
    Examples of text files are files opened in text mode 
    ('r' or 'w'), sys.stdin, sys.stdout, and instances 
    of io.StringIO.

'''

# Example 1 /Takes data from the pipe and feeds it to program that prints it with the stars
'''
import sys

for line in sys.stdin:
    print('**' + line + '**')
'''

# Example 2/ Take a small class and substitute sys.stdin
import sys

class CustomStdIn():
    ''' Class has only readline method that tells stdin
        what to return upon input request.
    '''

    def readline(self):
        ''' Input always returns Sample text
        '''
        text = 'Sample text'
        return str(text)

'''
# Do backup of the original stdin
backup = sys.stdin

# Overwrite the original with new that is always feeding Sample text
sys.stdin = CustomStdIn()

# Upon interactive input, always feeds Sample text automatically
a = input('Write anythig:')
print(a)

for line in sys.stdin:
    print(line)
'''

import pygame

print(pygame.font.get_fonts())



