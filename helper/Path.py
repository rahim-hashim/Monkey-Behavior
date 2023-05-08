import os
import re

def extract_number(filename):
  number = re.findall('\d+', filename)  # find all sequences of digits in the filename string
  return number[0]  # return the first match

class Path:
	def __init__(self, ROOT, EXPERIMENT, TASK):

		# Data Paths
		self.data_path = os.path.join(ROOT, 'data')
		## Raw Data Path
		self.raw_data_path = os.path.join(self.data_path, 'raw', 'data_'+TASK)
		if os.path.exists(self.raw_data_path):
			print('Raw Data Path Exists: {}'.format(self.raw_data_path))
			print('  Number of Files  : {}'.format(len(os.listdir(self.raw_data_path))))
			# Get all .h5 files
			list_h5_files = [file for file in os.listdir(self.raw_data_path) if file.endswith('.h5')]
			# Get dates from file names
			dates = list(map(extract_number, list_h5_files))  # apply the extract_number function to each filename in the list
			print('  Earliest Date    : {}'.format(min(dates)))
			print('  Most Recent Date : {}'.format(max(dates)))
		else:
			print('Raw Data Path Does Not Exist: '.format(self.RAW_DATA_PATH))
		# Target Path
		self.target_path = os.path.join(ROOT, 'data', 'processed', 'processed_'+TASK)

		# Fractal Path
		self.fractal_path = os.path.join(self.data_path, '_fractals')

		# Figure Paths
		self.figure_path = os.path.join(ROOT, 'figures', TASK)

		# Tracker Path
		self.tracker_path = os.path.join(ROOT, 'docs', 'Tracker', 'Emotion')

		# Excel Path
		self.excel_path = os.path.join(self.tracker_path, 'Emotion_Tracker.xlsx')

		# Video Path
		self.video_path = ''
		list_tasks = os.listdir(os.path.join(ROOT, 'tasks', EXPERIMENT))
		task_folder = [task for task in list_tasks if TASK in task]
		if task_folder:
			if len(task_folder) > 1:
				print('Multiple task folders found for task: {}'.format(TASK))
				# ask user to select the task they want
				task_selected = input('Please select the task you want (i.e. 1, 2, 3...): ')
				for t_index, task in enumerate(task_folder):
					print('  {}: {}'.format(t_index+1, task))
				task_name = task_folder[int(task_selected)-1]
			else:
				task_name = task_folder[0]
			self.video_path = os.path.join(ROOT, 'tasks', EXPERIMENT, task_name, 'videos')
			print('Video Path Exists: {}'.format(self.video_path))
		else:
			print('No video folder found for task: {}'.format(TASK))

		# Raw Data Directory
		self.h5_pull()

	def h5_pull(self):
		"""Look for all .h5 extension files in directory"""
		print('Pulling \'.h5\' files...')
		raw_data_directory = os.listdir(self.raw_data_path)
		h5_filenames = [f for f in raw_data_directory if f[-3:] == '.h5']
		print('  Complete: {} \'.h5\' files pulled'.format(len(h5_filenames)))
		self.raw_data_directory = raw_data_directory