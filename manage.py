"""
Master helper file for managing SaMarDaMin projects.
"""

import sys, os, cPickle
from shutil import rmtree
from optparse import OptionParser

def startProject(directory):
	"""
	Creates the basic files for a new mining project.
	directory = string name of new project
	
	startProject creates a new directory called 'directory', 
	and then sticks some files in it with basic directions.
	Files:
		spider.py
		data
	"""
	# directory must be a string
	assert type(directory) == type('')
	# create project directory
	try:
		os.mkdir(directory)
	except OSError:
		print directory,"already exists."
	# create spider.py
	with open(directory+'/spider.py','w') as f:
		f.write("""# Write your models and mining code here!
import miner

# Extend the spider's model by adding key:value pairs
model = {'ID':'',		# Numeric ID
	'url':'',			# URL retrieved
	'error':''}			# Did the spider run into an error?

def mine(url,spider=model):
	# get URL
	# parse data
	return spider
""")
	# create data
	with open(directory+'/data','w') as f:
		data = {'url':'',
			'last':0,
			'iterations':'1'}
		cPickle.dump(data,f)
	# copy miner.py into project directory, for encapsulation
	with open('miner.py','r') as original:
		with open(directory+'/miner.py','w') as new:
			new.write(original.read())
	# create misc storage files
	# "results" holds all results
	with open(directory+'/results','w') as f:
		data = []
		cPickle.dump(data,f)
	# "recent" holds the results from the last run
	with open(directory+'/recent','w') as f:
		data = []
		cPickle.dump(data,f)
	# "errors" holds all IDs where we encountered errors
	with open(directory+'/errors','w') as f:
		data = []
		cPickle.dump(data,f)
	# "missing" holds all IDs we skipped for whatever reason
	with open(directory+'/missing','w') as f:
		data = []
		cPickle.dump(data,f)

def resetProject(directory):
	"""
	Checks to see if the directory exists
	if no, exit
	else, deletes the existing directory
	and runs startProject on it.
	"""
	try:
		# try to list the directory's contents. If it doesn't exist, errors will happen.
		os.listdir(directory)
	except OSError:
		# directory doesn't exist.
		startProject(directory)
	else:
		# directory does exist
		rmtree(directory) # obliterate the directory
		startProject(directory)

def main(args=sys.argv):
	# set up options
	parser = OptionParser()
	parser.add_option("-s","--start",
		dest="start",
		help="Create a new project called PROJECT",
		metavar="PROJECT")
	parser.add_option("-r","--reset",
		dest="reset",
		help="Reset an existing project called PROJECT",
		metavar="PROJECT")
	(options, args) = parser.parse_args()
	# parse options
	if options.start: startProject(options.start)
	if options.reset: resetProject(options.reset)
	
if __name__ == "__main__":
	main()
