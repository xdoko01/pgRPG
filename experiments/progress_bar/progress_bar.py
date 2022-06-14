''' I need to call function from different places, that will inform the 
progress bar how far it is and what should be generated on the screen.
'''

class ProgressBarManager():
	def __init__(self):
		self.progress = 0
		self.text = ''
		self.finished = False

	def update(self, progress, text, finished=False):
		self.progress = progress
		self.text = text
		self.finished = finished

	def draw(self):
		while not self.finished:
			print(f'Progress: {self.progress}, text: {self.text}')


if __name__ == '__main__':
	
	progress_bar = ProgressBarManager()

	import time
	from threading import Thread

	t = Thread(target=progress_bar.draw)
	t.start()
	progress_bar.update(25, 'Loading something')
	time.sleep(2)
	progress_bar.update(50, 'Loading something else')
	time.sleep(2)
	progress_bar.update(190, 'Loading something else', finished=True)

