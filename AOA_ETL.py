import requests
import json
from pyquery import PyQuery as pq
import pandas as pd
table = []
url = 'https://www.aoa.org/DrFinder/GetDrSearchResults'
headers = {'Content-Type': 'application/json'}
states = ["AK" ,"AL","AZ","AR","CA","CZ","CO","CT","DE","DC","FL","GA","GU","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","PR","RI","SC","SD","TN","TX","UT","VT","VI","VA","WA","WV","WI","WY"]
for state in states:
	data = {"query":{"FullName":"","City":"","State":state,"Zip":"","Distance":"200","Filters":{"PracticeServices":"","SpecialEmphasis":"","LanguagesSpoken":"","MaxResults":"2000"},"ProfilePageUrl":"healthy-eyes/find-a-doctor/doctor-profile","PracticeID":"","MemberID":""},"page":1}
	response = requests.post(url ,headers=headers, data=json.dumps(data))
	selector = pq(response.text)
	last_page = selector('[href="#doctor-card-list"]:contains("Last")').attr('data-page')
	print(state, last_page)
	for page in range(1,int(last_page)+1):
		print(f'{state} State --> page {page} out of {last_page}')
		data = {
		   "query":{
		      "FullName":"",
		      "City":"",
		      "State":state,
		      "Zip":"",
		      "Distance":"200",
		      "Filters":{
		         "PracticeServices":"",
		         "SpecialEmphasis":"",
		         "LanguagesSpoken":"",
		         "MaxResults":"2000"
		      },
		      "ProfilePageUrl":"healthy-eyes/find-a-doctor/doctor-profile",
		      "PracticeID":"",
		      "MemberID":""
		   },
		   "page":page,
		}
		

		response = requests.post(url ,headers=headers, data=json.dumps(data))
		selector = pq(response.text)
		for item in selector('.doctor-card').items():
			item_dict = {}
			item_dict['Dr Name'] = item('.doctor-card__details h5 a').text()
			item_dict['Practice Name'] = item('.doctor-card__details h5 + div').text()
			item_dict['Address1'] = item('.doctor-card__details div').eq(1).text()
			item_dict['Address2'] = item('.doctor-card__details div').eq(3).text()
			item_dict['Zip'] = item('.doctor-card__details div').eq(3).text().split(' ')[-1]
			item_dict['State'] = item('.doctor-card__details div').eq(3).text().split(' ')[-2]
			item_dict['City'] = item('.doctor-card__details div').eq(3).text().split(',')[0]
			item_dict['Phone number'] = item('.doctor-card__details div').eq(4).text()
			item_dict['Website'] = item('.doctor-card__links a:contains("Website")').attr('href')
			table.append(item_dict)
print('data extracted successfully!')

# Data Transformation  
df = pd.json_normalize(table)
df["Address"] = df[['Address1', 'Address2']].agg('-'.join, axis=1)
df.drop(['Address1','Address2'], axis=1, inplace=True)
df = df[['Dr Name', 'Practice Name', 'Address','City','State','Zip','Phone number','Website']]

df.to_csv('aoa.csv', index=False)