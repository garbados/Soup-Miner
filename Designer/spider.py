# Write your models and mining code here!
import soupify, datetime, re

# Enter your models here!
class spider:
	def __init__(self,model={}):
		self.model = model
		userMadeModel = {
			# define your models like this:
			#'field_name':''		# what field_name will store. The '' here can be any initial value.
			'url': '',				# URL retrieved
			'ID':'',				# Profile ID
			'error':'',				# Did the spider run into an error?
			# the fields below are user-created and not part of the generic spider
			'user':['a',{"class":"orange nou"}],			# Username
			'name':['span',{"class":"fn"}],					# Real name
			'gender':[],									# User's stated gender, if any
			'age':['span',{"style":"font-size:12px;"}],		# Age; also initial strainer for much other user data
			'joinDate':[],									# Date joined
			'extrDate':[],									# Date of data extraction
			'numDesSco':[],									# Number of designs scored
			'numScoPri':[],									# Number of designs scored that we later printed
			'isPrinted':['a',{'href':'/alumniclub'}],		# Have any of the author's designs been printed?
			'avgSco':[],									# Average score given by the designer
			'extUrl':['a',{'rel':'nofollow me'}],			# Designer's external homepage
			'aim':['a',{'rel':'me','class':'url'}]}			# Designer's AIM handle
		# join model and userMadeModel into self.model
		self.model.update(userMadeModel)
	def parse(self,url):
		# mine your data here!
		# get data. Anything that requires no post-processing is collected here.
		model = soupify.soupify(url,self.model)
		# get some easy values
		model['url'] = url
		model['ID'] = soupify.getID(url)
		model['extrDate'] = datetime.date.today().isoformat()
		# check for redirect:
		if model['ID'] not in model['url']:
			model['error'] = 'Redirected'
			return model
		else:
			# if no redirect, commence post-processing
			try:
				# convert isPrinted to boolean: if we gathered alumniclub data, user has been printed. Else, not.
				if model['isPrinted']:
					model['isPrinted'] = True
				else:
					model['isPrinted'] = False
				# recall that 'age' stores the html containing data for several other fields
				if model['age']:
					if len(model['age'][0].contents) > 1:
						userData = model['age'][0].contents[2]
					else:
						userData = model['age'][0].contents[0]
				else:
					model['issue'] = "Empty"
					print "Empty results at ID "+model['ID']
					return model
				# use regex to parse that html for data we want. send data as {'model.key':'regex',...}
				# group 'data' will mark the group we need.
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
				# format returned values
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
				print "Successfully scraped ID "+model['ID']
				return model
			except:
				model['issue'] = 'Issues'
				print "Issues encountered at ID "+model['ID']
				raise
				return model
