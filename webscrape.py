import csv
import requests
from bs4 import BeautifulSoup
from decimal import *
from random import randint

url = "https://www.athletic.net/CrossCountry/Results/Meet.aspx?Meet=119954&show=all"
r = requests.get(url)

soup = BeautifulSoup(r.content, 'html.parser')
if soup.title is not None:

	meetName = str(soup.title.string)
	meetName = meetName.replace('\n','').replace('\t','').replace('\r','').replace('/','_')

	meetDetails = soup.find_all('div', {"class" : "meetDetails"})
	eventDate = meetDetails[0].next.text
	eventSeason = 'Winter'
	if 'Dec' in eventDate or 'Jan' in eventDate or 'Feb' in eventDate:
		eventSeason = 'Winter'
	elif 'Mar' in eventDate or 'Apr' in eventDate or 'May' in eventDate:
		eventSeason = 'Spring'
	elif 'Jun' in eventDate or 'Jul' in eventDate or 'Aug' in eventDate:
		eventSeason = 'Summer'
	else:
		eventSeason = 'Fall'

	eventLocation = meetDetails[0].next.next.next.next.next.text

	with open('races.csv', 'wb') as csvfile:
		fieldnames_races = ['id', 'date', 'location', 'season', 'bg', 'race_name', 'distance', 'type', 'score', 'place', 'teams']
		writer_races = csv.DictWriter(csvfile, fieldnames=fieldnames_races)
		writer_races.writeheader()

		with open('performances.csv', 'wb') as csvfile:
			fieldnames_performances = ['id', 'ram', 'race', 'race_time', 'depth', 'place', 'grade', 'season', 'meet_team_rank']
			writer_performances = csv.DictWriter(csvfile, fieldnames=fieldnames_performances)
			writer_performances.writeheader()

			for resultSection in soup.find_all('div', {"class" : "tab-pane"}):

				for event in resultSection.find_all('h3', {"class" : "mTop5"}):

					# Event Class Name - MensResults or WomensResults
					eventClassName = str(event.text)
					eventGender = 'b'
					if "Women" in eventClassName:
						eventGender = 'g'

					eventType = 'unknown'
					eventPlace = 'unknown'
					eventScore = 'unknown'
					eventDistanceMiles = 0

					individualRamGenderDepth = 1

					for eventSummary in resultSection.find_all('table', {"class" : "DataTable HLData table table-hover"}):

						for eventSubSummary in resultSection.find_all('tbody', {"class" : "DivBody"}):

							# Team Event Type
							eventFullType = 'unknown'
							for teamEventTypeSecion in eventSubSummary.find_all('tr', {"class" : "DivHeader"}):
								for eventFullTypeRecord in teamEventTypeSecion.find_all('h4', {"class" : ""}):
									eventFullType = eventFullTypeRecord.text
									if "Junior Varsity" in eventFullType:
										eventType = 'jv'
									elif "Varsity" in eventFullType:
										eventType = 'v'
									else:
										eventType = 'mix'

									eventDistanceMiles = Decimal(eventFullType.split(" ")[0].replace("," , "")) / Decimal(1600)

							numberResults = 0

							# Team Scores
							for teamScoreSecion in eventSubSummary.find_all('tr', {"class" : "ts_Cont"}):

								for eventResult in teamScoreSecion.find_all('tr', {"class" : "ts"}):
									numberResults += 1
									if "Ingraham" in eventResult.text:
										results = eventResult.text.split(".Ingraham")
										eventPlace = results[0]
										eventScore = results[1]

							race_id = randint(10000000, 99999999)

							# Write Race Data
							writer_races.writerow({'id' : race_id, 'date' : eventDate, 'location' : eventLocation, 'season': eventSeason, 'bg' : eventGender, 'race_name' : eventFullType, 'distance' : str(eventDistanceMiles), 'type' : eventType, 'score' : eventScore, 'place' : eventPlace, 'teams' : numberResults})	

							# Individual Scores
							individualRamDepth = 1
							for individualResult in eventSubSummary.find_all('tr', {"class" : ""}):
								if not "Official Team Scores" in individualResult.text and "Ingraham" in individualResult.text:

									# Parse Text Value: 1.11Ian Stiehl19:05.83Ingraham which is Place.GradeNameTimeSchool
									individualPlace = individualResult.next.text.replace(".", "")
									individualGrade = individualResult.next.next.next.text
									individualName = individualResult.next.next.next.next.next.text
									individualTime = individualResult.next.next.next.next.next.next.next.text
									
									individual_id = randint(10000000, 99999999)

									writer_performances.writerow({'id' : individual_id, 'ram' : individualName, 'race' : eventFullType, 'race_time' : individualTime, 'depth' : individualRamDepth, 'place' : individualPlace, 'grade' : individualGrade, 'season' : eventSeason, 'meet_team_rank' : individualRamGenderDepth})
									individualRamDepth += 1
									individualRamGenderDepth += 1
	

