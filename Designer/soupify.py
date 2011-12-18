"""
generic functions to help spider.py's parser get and deal with data
"""

import BeautifulSoup, urllib2

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
	

def soupify(url,model):
	"""
	Gets html from string url
	Passes html through strainer rules contained in dict model
	Feeds strainer results back into model
	If we got redirected during the search, return redirected url
	Else, return model with strainer results
	"""
	assert type(url) is str and type(model) is dict
	contents = urllib2.urlopen(url)
	# check for redirect
	if url == contents.geturl():
		# if no redirect, run soup through strainers
		for k,v in model.iteritems():
			try:
				if v:
					strainer = BeautifulSoup.SoupStrainer(v[0],attrs=v[1])
					model[k] = BeautifulSoup.BeautifulSoup(contents,strainer)
			except KeyError:
				print k, v
		return model
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
		regex = regex[0] + "/(?P<id>.*)/" + regex[1]
		return re.search(regex,url).group('id')
	else:
		i = url.rfind('/')+1
		return url[i:]
