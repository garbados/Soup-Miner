"""
SaMarDaMin Data Mining Library
"""
import urllib2, cPickle
from types import FunctionType

def listID(url,iterations,start=0):
	"""
	Yields a URL list in the form of url + integer[start:end] as a generator
	url example: "http://www.google.com/"
	"""
	assert type(url) is str
	end = start+iterations
	for i in range(start,end):
		yield url + str(i)
		
def dataIDs(f,iterations=None,start=None):
	"""
	Unpickle the data file and use its values to construct a list of IDs
	Remember, the values contained in data are:
		url				the url to which IDs are appended
		last			the last ID checked
		iterations		how many iterations to run
	"""
	with open(f,'r') as f:
		data = cPickle.load(f)
	if iterations:
		data['iterations'] = iterations
	if not start:
		start = data['last']
	with open(f,'w') as f:
		cPickle.dump(data,f)
	return iterIDs(data['url'],data['iterations'],start)
			
def addError(error,errfile):
	"""
	Given an error-producing ID as 'error', determine what to do with it from the spider's data file.
	If data['error'] is store, we append it to the errors file.
	If data['error'] is ignore, we do nothing.
	"""
	with open(errfile,'r') as f:
		data = cPickle.load(f)
	data.append(error)
	with open(errfile,'w') as f:
		cPickle.dump(data,f)
			
def getMissing(results,missing):
	"""
	Given two files -- results and missing -- traverse the former to...
	1.) Find the highest ID traversed.
	2.) Use range(highest) and the existing IDs to determine which IDs are missing
	3.) Append this list of missing IDs to the pickled file 'missing'
	"""
	# get results
	with open(results,'r') as f:
		data = cPickle.load(f)
	# create list of all IDs we should have
	m = range(max(data))
	# remove all the IDs we do have
	for item in data:
		del m[m.index(item)]
	# write remaining IDs to 'missing'
	with open(missing,'w') as f:
		cPickle.dump(m,f)
	
def searchHTML(html,start,end):
	"""
	Given string HTML, returns everything between the start and end strings.
	Returns None if either start or end isn't found.
	"""
	assert type(html) is str
	i = html.find(start)
	if i != -1: i += len(start)
	j = html.find(end)
	if i != -1 and j != -1:
		return html[start:end]
	else:
		return None
		
class idMiner(url,model,parse,errfile='errors'):
	"""
	Takes a single URL ending in a numeric ID,
	uses the 'parse' function to pull data from the HTML,
	and shove it into the model dict.
	If we encounter errors, they're appended to the error file.
	"""
	assert type(url) is str
	assert type(model) is dict
	assert type(parse) is FunctionType
	try:
		# get URL
		model['ID'] = url[url.rfind('/')+1:]
		u = urllib2.urlopen(url)
		model['url'] = u.geturl()
		# check for validity. Did we get redirected?
		if model['url'] is not url:
			# if we got redirected, return spider and quit
			return model
		else:
			model = parse(u.read(),model)
			return model
	except:
		# issues
		model['error'] = True
		addError(model,errfile)
		return model
