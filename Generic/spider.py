# Write your models and mining code here!
import soupify, datetime, re

# Enter your models here!
model = {
	# like this!
	#'field_name':''	# what field_name will store
	'url':'',			# URL retrieved
	'error':'',			# Did the spider run into an error?
	'ID':'',			# Profile ID
	'user':'',			# Username
	'name':'',			# Real name
	'gender':'',		# User's stated gender, if any
	'age':'',			# Age
	'joinDate':'',		# Date joined
	'extrDate':'',		# Date of data extraction
	'numDesSco':'',		# Number of designs scored
	'numScoPri':'',		# Number of designs scored that we later printed
	'isPrinted':'',		# Have any of the author's designs been printed?
	'avgSco':'',		# Average score given by the designer
	'url':'',			# Designer's external homepage
	'aim':''}			# Designer's AIM handle

def parse(url,model=model):
	data = soupify.soupify(url)
	# mine your data here!
	model['url'] = url
	model['ID'] = soupify.getID(url)
	model['extrDate'] = datetime.date.today().isoformat()
	# check for redirect:
	if not data:
		model['error'] = 'Redirected'
		return model
	else:
		try:
			# format arguments en masse as {'model.key':['tag',{'attr':'value','attr':'value',...}],...}
			userData = {'user':['a',{"class":"orange nou"}],
				'name':['span',{"class":"fn"}],
				'url':['a',{'rel':'nofollow me'}],
				'aim':['a',{'rel':'me','class':'url'}],
				'isPrinted':['a',{'href':'/alumniclub'}]}
			# process arguments en masse
			for k,v in userData.iteritems():
				model[k] = data.findAll(v[0],v[1])
				# if no data was returned, do nothing. Else, grab data contents.
				if model[k]:
					model[k] = model[k][0].contents[0]
			# field-specific post-processing
			# convert isPrinted to boolean: if we gathered alumniclub data, user has been printed. Else, not.
			if model['isPrinted']:
				model['isPrinted'] = True
			else:
				model['isPrinted'] = False
			# use regex to parse unmarked string for data we want. send data as {'model.key':'regex',...}
			userData = data.findAll('span',{"style":"font-size:12px;"})[0].contents[2]
			# 'data' will mark the group we need.
			userRegex = {'age': 'is a (?P<data>.*) year',
				'numDesSco':'scored (?P<data>.*) submissions',
				'numScoPri':'helping (?P<data>.*) designs',
				'avgSco':'of (?P<data>.*), helping',
				'joinDate':'since (?P<data>.*), has',
				'gender':'(?P<data>girl|boy)'}
			for k,v in userRegex.iteritems():
				v = re.search(v,userData)
				if v:
					model[k] = v.group('data')
				else:
					model[k] = u''
			# field-specific post-processing
			# eliminate commas, turning "1,000" into "1000"
			for i in ['numDesSco','numScoPri']:
				if model[i]:
					model[i] = model[i].replace(',','')
			# convert age into timedelta, and subtract it from today to get an approximate birth date
			if model['age']:
				model['age'] = (datetime.datetime.today() - datetime.timedelta(float(model['age'])*365.25)).isoformat()
			# convert joinDate to a datetime object
			if model['joinDate']:
				date = model['joinDate'].replace(',','').split(' ')
				date[0] = soupify.month[date[0]]
				model['joinDate'] = datetime.date(int(date[2]),date[0],int(date[1])).isoformat()
			# convert from unicode so the resultant csv isn't full of u''
			model['avgSco'] = float(model['avgSco'])
			for k in model.keys():
				if type(model[k]) is unicode:
					model[k] = str(model[k].encode('ascii','ignore'))
			return model
		except:
			model['issue'] = 'Issues'
			print model['ID']
			raise
			return model
