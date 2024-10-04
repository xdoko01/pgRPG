import os

'''Help script for generationg entity json files from model json files'''

# Specity the directory with the subdirectories containing models
os.chdir('c://Users//otakar//OneDrive//Personal//Python//pyRPG//pyrpg//resources//models//generic//wearable//male//torso')

# Parse through directories only
dirs = (dir for dir in os.listdir() if os.path.isdir(dir))
for dir in dirs:
	
	# Switch to the directory
	os.chdir(dir)

	# Parse through files only
	files = (file for file in os.listdir() if os.path.isfile(file) and file.split(".")[-1] == 'json')
	for file in files:
		print(f' Creating file: {dir + "_" + file}')

		# Creates a new file
		with open('../' + dir + '_' + file, 'w') as fp:
			fp.write("""{
	"id" : "wearable_male_torso_""" + dir + "_" + file.split('.')[0] + """_model",
	"templates" : ["model/wearable/male/torso"],
	"components" : [
		{"type" : "renderable_model:RenderableModel", "params" : {"model" : "generic/wearable/male/torso/""" + dir + "/" + file + """}}
	]
}""")
	# Return back
	os.chdir('..')

""" Version for directories without subdirectories"""
''' 
os.chdir('c://Users//otakar//OneDrive//Personal//Python//pyRPG//pyrpg//resources//models//generic//wearable//male//belt')

# Parse through files only
files = (file for file in os.listdir() if os.path.isfile(file) and file.split(".")[-1] == 'json')
for file in files:
	print(f' Creating file: {file}')

	# Creates a new file
	with open('../' + file, 'w') as fp:
		fp.write("""{
	"id" : "wearable_male_belt_""" + file.split('.')[0] + """_model",
	"templates" : ["model/wearable/female/belt"],
	"components" : [
		{"type" : "renderable_model:RenderableModel", "params" : {"model" : "generic/wearable/male/belt/""" + file + """}}
	]
}""")
'''