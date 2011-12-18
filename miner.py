"""
SaMarDaMin Data Mining Library
Deals with storing, reading, and modifying results data
Gets data by running spider.py functions
Pushes/pulls data from results.dat
"""
import sys, urllib2, cPickle, spider
from optparse import OptionParser


# SETTINGS FUNCTIONS
def getSettings(settings):
	"""
	Using string settings, open its corresponding file
	and parse its contents into a dict that we then return
	"""
	with open(settings,'r') as f:
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
	return range(a,b)
	
def constructURLs(settings,idList):
	"""
	Uses settings['url'] from dict settings and idList
	to return a list of string urls for parsing
	"""
	assert type(settings) is dict and type(idList) is list
	# one-line version, because I can: yield (settings['url'].replace('<id>',ID) for ID in idList)
	url = settings['url']
	for ID in idList:
		yield url.replace('<id>',str(ID))
		
def iterateLast(settings):
	"""
	Using string settings, open its corresponding file
	and increase 'last' by 'iterations'
	then write back the file
	"""
	data = getSettings(settings)
	data['last'] += data['iterations']
	setSettings(data,settings)
	
# RESULTS FUNCTIONS
def readData(f):
	"""
	Given filename f, open file f and parse its contents back into their dict format
	Return a list of these dicts.
	"""
	assert type(f) is str
	with open(f,'r') as f:
		data = f.readlines()
	results = []
	# use eval() because you're the classiest gent
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
	# create list of all IDs we should have
	missing = range(max(IDs))
	# remove all the IDs we do have
	for item in IDs:
		del missing[missing.index(item)]
	# return the subsequent list
	return missing
	
def getErrors(results):
	"""
	Given string 'results', open its file and returns a list of all IDs marked as having issues.
	Ignores errors from redirects.
	"""
	data = readData(results)
	errors = []
	for item in data:
		if item['error'] is 'Issues':
			errors.append(item['ID'])
	return errors
	
def removeDupes(results):
	"""
	Given string results, parse its file, 
	remove all duplicates IDs (favoring more recent results), 
	and write the modified results back to file
	"""
	pass
	
# MINER FUNCTION
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
	urls = constructURLs(settings,idList)
	for url in urls:
		data = spider.parse(url)
		appendData(data,results)
		
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
		setSettings(settings,'settings.txt') # TODO eliminate hardcoding of filenames
	# run miner
	print "Beginning miner..."
	mine('settings.txt','results.dat') # TODO eliminate hardcoding of filenames
	if not options.debug and not options.missing:
		iterateLast('settings.txt')
	print "Miner finished."
	
# run miner.py to activate the whole mess!
if __name__ == '__main__': 
	main()
