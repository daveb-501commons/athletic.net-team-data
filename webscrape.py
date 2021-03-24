"""Igraham Athletic Net Cross County Processing"""

def getRamId(first_name, last_name, season, grade, gender):

	import csv
	import pandas as pd
	import sys

	with open('rams.csv', 'rb') as ramsFileHandle:

		try:
			rams = pd.read_csv(ramsFileHandle)
		except:
			print('Unexpected error: ', sys.exc_info()[0])

		# Find rams Id
		ramId = 0
		ramIdMax = 0
		for indexRam, rowRam in rams.iterrows():
			
			if ramIdMax < int(rowRam['id']):
				ramIdMax = int(rowRam['id'])

			if rowRam['first_name'] == first_name and rowRam['last_name'] == last_name and int(rowRam['season']) == int(season):
				ramId = rowRam['id']
				break

	if ramId == 0:
		ramId = ramIdMax + 1

		current_season = int(season)
		grad_year = current_season + 1
		senior_season = current_season

		if grade == '9':
			grad_year = current_season + 4
			senior_season = current_season + 3

		if grade == '10':
			grad_year = current_season + 3
			senior_season = current_season + 2

		if grade == '11':
			grad_year = current_season + 2
			senior_season = current_season + 1

		with open('rams.csv', 'ab') as csvfile:
			fieldnames_rams = ['id', 'first_name', 'last_name', 'season', 'grade', 'mf', 'grad_year', 'senior_season']
			writer_rams = csv.DictWriter(csvfile, fieldnames=fieldnames_rams)
			writer_rams.writerow({'id' : ramId, 'first_name' : first_name, 'last_name' : last_name, 'season' : season, 'grade' : grade, 'mf' : gender, 'grad_year' : grad_year, 'senior_season' : senior_season})

	return ramId

def main():

	import csv
	import requests
	import pandas as pd
	from datetime import datetime
	from decimal import *
	from bs4 import BeautifulSoup

	# Setup Performance Table
	performance_columns = {'first_name', 'last_name', 'race', 'race_time', 'depth', 'place', 'grade', 'season'}
	performance_girls = pd.DataFrame(columns=performance_columns)
	performance_boys = pd.DataFrame(columns=performance_columns)

	# "https://www.athletic.net/CrossCountry/Results/Meet.aspx?Meet=119954&show=all"
	urls = ["https://www.athletic.net/CrossCountry/Results/Meet.aspx?Meet=189652&show=all"]
	for url in urls:

		r = requests.get(url)

		soup = BeautifulSoup(r.content, 'html.parser')
		if soup.title is not None:

			meetName = str(soup.title.string)
			meetName = meetName.replace('\n','').replace('\t','').replace('\r','').replace('/','_')

			meetDetails = soup.find_all('div', {"class" : "meetDetails"})

			eventDateString = meetDetails[0].next.text
			eventDate = datetime.strptime(eventDateString + ' 00:00:00', '%A, %B %d, %Y %H:%M:%S')
			eventSeason = eventDate.year

			# Special Case to treat Spring 2021 Season as 2020
			if eventSeason == 2021 and ('March' in eventDateString or 'April' in eventDateString):
				eventSeason = '2020'

			eventLocation = meetDetails[0].next.next.next.next.next.text
			race_id = 0

			with open('races.csv', 'wb') as csvfile:
				fieldnames_races = ['id', 'date', 'location', 'season', 'bg', 'race_name', 'distance', 'type', 'score', 'place', 'teams']
				writer_races = csv.DictWriter(csvfile, fieldnames=fieldnames_races)
				writer_races.writeheader()

				for resultSection in soup.find_all('div', {"class" : "tab-pane"}):

					for event in resultSection.find_all('h3', {"class" : "mTop5"}):

						# Event Class Name - MensResults or WomensResults
						eventClassName = str(event.text)
						eventGender = 'Boys'
						if "Women" in eventClassName:
							eventGender = 'Girls'

						eventType = 'unknown'
						eventPlace = 'unknown'
						eventScore = 'unknown'
						eventDistanceMiles = 0

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

								# Write Race Data
								race_id += 1
								writer_races.writerow({'id' : race_id, 'date' : eventDate.strftime('%Y-%m-%d'), 'location' : eventLocation, 'season': eventSeason, 'bg' : eventGender, 'race_name' : eventFullType, 'distance' : str(eventDistanceMiles), 'type' : eventType, 'score' : eventScore, 'place' : eventPlace, 'teams' : numberResults})	

								# Individual Scores
								individualRamDepth = 1
								for individualResult in eventSubSummary.find_all('tr', {"class" : ""}):
									if not "Official Team Scores" in individualResult.text and "Ingraham" in individualResult.text:

										# Parse Text Value: 1.11Ian Stiehl19:05.83Ingraham which is Place.GradeNameTimeSchool
										individualPlace = individualResult.next.text.replace(".", "")
										individualGrade = individualResult.next.next.next.text
			
										individualName = individualResult.next.next.next.next.next.text
										results = individualName.split(" ")
										individualFirstName = eventPlace = results[0]
										individualLastName = results[1]

										individualTime = individualResult.next.next.next.next.next.next.next.text
										
										new_row = {'first_name' : individualFirstName, 'last_name' : individualLastName, 'race' : race_id, 'race_time' : individualTime, 'depth' : individualRamDepth, 'place' : individualPlace, 'grade' : individualGrade, 'season' : eventSeason}

										if eventGender == 'Boys':						
											performance_boys = performance_boys.append(new_row, ignore_index=True)
										else:
											performance_girls = performance_girls.append(new_row, ignore_index=True)

										individualRamDepth += 1

			# Meet Performance Results across all the races
			performance_girls.sort_values(
				by='race_time',
				ascending=False)

			performance_boys.sort_values(
				by='race_time',
				ascending=False)

			performanceId = 1
			with open('performances.csv', 'wb') as csvfile:
				fieldnames_performances = ['id', 'ram', 'race', 'race_time', 'depth', 'place', 'grade', 'season', 'meet_team_rank']
				writer_performances = csv.DictWriter(csvfile, fieldnames=fieldnames_performances)
				writer_performances.writeheader()

				# Write out Girls
				for index, row in performance_girls.iterrows():

					ramId = getRamId(row['first_name'], row['last_name'], row['season'], row['grade'], 'F')
					writer_performances.writerow({'id' : performanceId, 'ram' : ramId, 'race' : row['race'], 'race_time' : row['race_time'], 'depth' : row['depth'], 'place' : row['place'], 'grade' : row['grade'], 'season' : row['season'], 'meet_team_rank' : index + 1})
					performanceId += 1

				# Write out Boys
				for index, row in performance_boys.iterrows():

					ramId = getRamId(row['first_name'], row['last_name'], row['season'], row['grade'], 'M')
					writer_performances.writerow({'id' : performanceId, 'ram' : ramId, 'race' : row['race'], 'race_time' : row['race_time'], 'depth' : row['depth'], 'place' : row['place'], 'grade' : row['grade'], 'season' : row['season'], 'meet_team_rank' : index + 1})
					performanceId += 1

if __name__ == "__main__":
    main()