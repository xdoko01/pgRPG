from threading import Thread

class ProgressBar():
    '''Class implementing the progress bar'''

    def __init__(self, header="Loading", text="") -> None:

        self.total = None
        self.progress: int
        self.header = header
        self.text = text
        self.finished: bool

    def __enter__(self):
        self.progress = 0
        self.finished = False

        Thread(target=self.run).start()

        return self.update
 
    def __exit__(self, *args):
        self.finished=True # effectivelly finishes the Thread


    def update(self, iter):
        '''Set values for rendering of progress bar. It is called from different
        places of the code. The reference to this particular function is passed to
        those parts of the code that manage loading of the resources.'''

        if self.progress == 0: #First call of the update function

            try:
                self.total = len(iter)
            except TypeError: # is not iterator but for example generator
                self.total = None

        for i in iter:
            self.progress += 1
            yield i

    def run(self):
        '''Displays progress screen (running in separate thread)'''

        while not self.finished:

            progress = int(self.progress/self.total*100) if self.total else '?'
            print(f'{self.header} - {self.text} ... {self.progress} / {self.total} ... {progress}%')


if __name__ == '__main__':

    # process_aliases is Iterator
    processors_aliases = list(range(150))
    with ProgressBar('Processing Iterator') as progress:

        for processor in progress(processors_aliases):
            print(processor)

    # process_aliases is Generator
    processors_aliases = range(150)
    with ProgressBar('Processing generator') as progress:

        for n, processor in progress(enumerate(processors_aliases)):
            print(f'{n} - {processor}')

