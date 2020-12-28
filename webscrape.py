import csv
import requests
from bs4 import BeautifulSoup

url = "https://www.athletic.net/CrossCountry/Results/Meet.aspx?Meet=119954&show=all"
r = requests.get(url)

soup = BeautifulSoup(r.content, 'html.parser')
if soup.title is not None:

	meetName = str(soup.title.string)
	meetName = meetName.replace('\n','').replace('\t','').replace('\r','').replace('/','_')

	file_name = "meet-" + str(meetName) + (".txt")
	text_file = open(file_name, "w")
	text_file.write("Meet Name: %s\n" % meetName)

	for resultSection in soup.find_all('div', {"class" : "tab-pane"}):

		for event in resultSection.find_all('h3', {"class" : "mTop5"}):
			eventClassName = str(event.text)
			eventClassName = eventClassName.replace('\n','').replace('\t','').replace('\r','').replace(' ','')
			text_file.write("\nEvent Class Name: %s\n" % eventClassName)

			for eventSummary in resultSection.find_all('table', {"class" : "DataTable HLData table table-hover"}):

				for eventSubSummary in resultSection.find_all('tbody', {"class" : "DivBody"}):

					# Team Event Type
					for teamEventTypeSecion in eventSubSummary.find_all('tr', {"class" : "DivHeader"}):
						for eventType in teamEventTypeSecion.find_all('h4', {"class" : ""}):
							text_file.write("\nTeam Type Name: %s\n" % eventType.text)

					numberResults = 0

					# Team Scores
					for teamScoreSecion in eventSubSummary.find_all('tr', {"class" : "ts_Cont"}):

						for eventResult in teamScoreSecion.find_all('tr', {"class" : "ts"}):
							numberResults += 1
							if "Ingraham" in eventResult.text:
								text_file.write("Team Result: %s\n" % eventResult.text)

						text_file.write("Total Team Results: %s\n\n" % numberResults)

					# Individual Scores
					for individualResult in eventSubSummary.find_all('tr', {"class" : ""}):
						if not "Official Team Scores" in individualResult.text and "Ingraham" in individualResult.text:
							text_file.write("Individual Result: %s\n" % individualResult.text)


#		for event in soup.find_all('table', {"class" : "DataTable HLData table table-hover"}):
#			for event_name in event.find_all('h5', {"class" : "bold"}):
#				text_file.write("Event: %s " % str(event_name.contents[0]))
#			for event_time in event.find_all('a', {"class" : " PR"}):
#				text_file.write("Time: %s\n" % str(event_time.contents[0]))
	
	text_file.close()

