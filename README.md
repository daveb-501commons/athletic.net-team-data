# Setup
pip install beautifulsoup4

# athletic.net-data-retrieval-tool
A web scraper that uses the BeautifulSoup package to grabs athletes personal records for every event and write the data to individual text files 

Team URL Example: 
1) (From Google Sheet) https://www.athletic.net/CrossCountry/meet/119954/results
2) Click Mens Varsity: https://www.athletic.net/CrossCountry/meet/119954/results/481815 
3) Click Womens Varsity: https://www.athletic.net/CrossCountry/meet/119954/results/481817
4) Click Show All: https://www.athletic.net/CrossCountry/Results/Meet.aspx?Meet=119954&show=all 

Team Values Needed

Team Results
Team Name                           Place     Number of Teams
Men - 5,000 Meters Junior Varsity   1         7
Men - 5,000 Meters Varsity
Women - 5,000 Meters Varsity

Team Invididuals Needed per Team
Men - 5,000 Meters Junior Varsity
:
: (List all the individuals)
Place, Name, Time, School


Individual URL Exmaple:
https://www.athletic.net/CrossCountry/Athlete.aspx?AID=9411064

Working Example based on original code for Individual
https://www.athletic.net/TrackAndField/Athlete.aspx?AID=4018802#/L0

L=0    ; All
L=4    ; High School
