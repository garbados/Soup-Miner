"""
generic functions to help spider.py's parser get and deal with data
"""

from BeautifulSoup import BeautifulSoup
import urllib2

# calendar for converting string months to their numerical equivalents
month = {'Jan':1,
	'Feb':2,
	'Mar':3,
	'Apr':4,
	'May':5,
	'Jun':6,
	'Jul':7,
	'Aug':8,
	'Sep':9,
	'Oct':10,
	'Nov':11,
	'Dec':12,
	'January':1,
	'February':2,
	'March':3,
	'April':4,
	'May':5,
	'June':6,
	'July':7,
	'August':8,
	'September':9,
	'October':10,
	'November':11,
	'December':12}
	

def soupify(url):
	"""
	Returns a BeautifulSoup object from the string url.
	Also checks for redirects. If redirected, returns None.
	"""
	assert type(url) is str
	contents = urllib2.urlopen(url)
	# check for redirect
	if url == contents.geturl():
		return BeautifulSoup(contents.read())
	else:
		return None
		
def getID(url,regex=None):
	"""
	Gets numeric (integer) ID from a string url.
	If regex == None, ID is assumed to be the section of the url following the last '/'
	regex = [start,end] example: [blah.com,blog] -> blah.com/<ID>/blog
	getID constructs a regular expression from [start,end]
	"""
	assert type(url) is str or type(url) is unicode
	if regex:
		assert type(regex) is list and len(regex) is 2
		# regex directs us to collect the ID from a more sophisticated place, like blah.com/<ID>/blog
		# construct a regular expression from the arguments supplied through regex
		regex = regex[0] + "/(?P<ID>.*)/" + regex[1]
		return re.search(regex,url).group('ID')
	else:
		i = url.rfind('/')+1
		return url[i:]
