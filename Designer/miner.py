"""
SaMarDaMin Data Mining Library
Deals with storing, reading, and modifying results data
Gets data by running spider.py functions
Pushes/pulls data from results.dat
"""
import sys, urllib2, cPickle, spider, threading, Queue
from optparse import OptionParser

# file constants
_SETTINGS = 'settings.txt'
_RESULTS = 'results.dat'

# SETTINGS FUNCTIONS
def getSettings(settings):
	"""
	Using string settings, open its corresponding file
	and parse its contents into a dict that we then return
	"""
	with open(settings,'r') as f:
		# use eval() because we live on the edge
		return eval(f.read().replace('\n',''))
	
def setSettings(s,f):
	"""
	Using dict s and filename f, write s into f in a human-readable format.
	Remember that settings are supposed to be editable by hand.
	"""
	assert type(s) is dict and type(f) is str
	settings = getSettings(f)
	for k,v in s.iteritems():
		if type(settings[k]) is str:
			settings[k] = '\''+v+'\''
		else:
			settings[k] = v
	with open(f,'w') as f:
		f.write('{')
		f.writelines('\''+k+'\' : '+str(v)+',\n' for k,v in settings.iteritems())
		f.seek(-2,2)
		f.write('}')
		
def getIDs(settings):
	"""
	Uses dict settings to create a list of IDs to parse
	Returns a list of IDs
	"""
	assert type(settings) is dict
	a = settings['last']
	b = a + settings['iterations']
	for ID in xrange(a,b):
		yield ID
	
def constructURLs(settings,idList):
	"""
	Uses settings['url'] from dict settings and iter idList
	to return a list of string urls for parsing
	"""
	assert type(settings) is dict
	url = settings['url']
	return [url.replace('<id>',str(ID)) for ID in idList]

def iterateLast(settings):
	"""
	Using string settings, open its corresponding file
	and increase 'last' by 'iterations'
	then write back the file
	"""
	data = getSettings(settings)
	data['last'] += data['iterations']
	setSettings(data,settings)
	
def validateSettings(settings):
	"""
	settings should really have a couple basic key:value pairs. If it doesn't, bad things happen.
	This checks and, if necessary, repairs settings without deleting custom additions.
	"""
	data = getSettings(settings)
	if 'url' not in data.keys():
		data['url'] = ''
	for item in ['last','iterations']:
		if item not in data.keys():
			data[item] = 1
	for item in ['debug','missing']:
		if item not in data.keys():
			data[item] = False
	setSettings(data,settings)
	
# RESULTS FUNCTIONS
def readData(f):
	"""
	Given filename f, open file f and parse its contents back into their dict format
	Return a list of these dicts.
	"""
	assert type(f) is str
	with open(f,'r') as f:
		# insert newlines, then split at them. results don't contain them naturally.
		data = f.read().replace('}{','}\n{').split('\n')
	results = []
	for line in data: results.append(eval(line))
	return results

def appendData(data,f):
	"""
	Given dict data and filename f, open file f and append data.
	"""
	assert type(data) is dict and type(f) is str
	with open(f,'a') as f:
		f.write(str(data))
	
def getMissing(results):
	"""
	Given string 'results', open its file and:
	1.) Find the highest ID traversed.
	2.) Use range(highest) and the existing IDs to determine which IDs are missing
	3.) Return the missing IDs as a list
	NOTE: assumes results file stores IDs in manners that can be turned to integers easily.
	"""
	data = readData(results)
	IDs = []
	for item in data:
		IDs.append(int(item['ID']))
	# yield missing IDs
	for ID in xrange(max(IDs)):
		if ID not in IDs:
			yield ID
	
def getErrors(results):
	"""
	Given string 'results', open its file and returns a list of all IDs marked as having issues.
	Ignores errors from redirects.
	"""
	data = readData(results)
	for item in data:
		if item['error'] is 'Issues':
			yield item['ID']
	
def removeDupes(results):
	"""
	Given string results, parse its file, 
	remove all duplicates IDs (favoring more recent results), 
	and write the modified results back to file
	"""
	pass
	
def toCSV(results):
	"""
	Given string results, convert its contents into an equivalent CSV
	and return the csv construct.
	"""
	pass
	
# MINER FUNCTIONS
def gather(q,urls):
	"""
	Parses each url in list urls and puts the item in queue q.
	"""
	for url in urls:
		miner = spider.spider()
		q.put(miner.parse(url),True)
		
def append(q,results):
	"""
	Appends each item in queue q to filename results.
	"""
	while True:
		try:
			q.get(True,1)
		except Queue.Empty:
			break
		
def mine(settings,results):
	"""
	Converts string settings to its corresponding file
	and uses the data in it to construct a list of IDs to parse
	Then, sicks spider.py on that list
	And appends the results to string results' corresponding file
	"""
	assert type(settings) is str and type(results) is str
	settings = getSettings(settings)
	if not settings['debug'] and not settings['missing']:
		idList = getIDs(settings)
	else:
		idList =[]
		if settings['debug']:
			idList.append(getErrors(results))
		if settings['missing']:
			idList.append(getMissing(results))
	# gather data serially -- that is, one ID at a time. Performance suffers while we wait for the server.
	#miner(constructURLs(settings,idList),results)
	# multi-threaded processing cordoned off until i can figure out how the hell to make it work without duplicity
	urls = constructURLs(settings,idList)
	threads = 3 # number of threads
	q = Queue.Queue()
	urlList = [urls[i::threads] for i in xrange(threads)]
	for urls in urlList:
		t = threading.Thread(target=gather,args=(q,urls))
		t.start()
	t = threading.Thread(target=append,args=(q,results))
	t.start()
		
# MAIN FUNCTIONS
def main(args=sys.argv):
	# set up options
	parser = OptionParser()
	parser.add_option("-u","--url",
		dest="url",
		help="Set the base url to URL. Don't forget to include <id>!",
		metavar="URL")
	parser.add_option("-l","--last",
		dest="last",
		help="Set the last-parsed ID to LAST_ID",
		metavar="LAST_ID")
	parser.add_option("-i","--iterations",
		dest="iterations",
		help="Set the number of iterations to ITERATIONS",
		metavar="ITERATIONS")
	parser.add_option("-d","--debug",
		dest="debug",
		help="Set debug to 1 (True) or 0 (False)",
		metavar="ZERO_OR_ONE")
	parser.add_option("-m","--missing",
		dest="missing",
		help="Set missing to 1 (True) or 0 (False)",
		metavar="ZERO_OR_ONE")
	(options, args) = parser.parse_args()
	# parse options
	settings = {}
	if options.url: settings['url'] = options.url
	if options.last: settings['last'] = options.last
	if options.iterations: settings['iterations'] = options.iterations
	if options.debug:
		if options.debug is 0:
			settings['debug'] = False
		elif options.debug is 1:
			settings['debug'] = True
	if options.missing:
		if options.missing is 0:
			settings['missing'] = False
		elif options.missing is 1:
			settings['missing'] = True
	if settings:
		setSettings(settings,_SETTINGS)
	# run miner
	mine(_SETTINGS,_RESULTS)
	# when miner completes, if we didn't debug or check missing, iterate settings
	if not options.debug and not options.missing:
		iterateLast(_SETTINGS)
	
# run miner.py to activate the whole mess!
if __name__ == '__main__': 
	main()
