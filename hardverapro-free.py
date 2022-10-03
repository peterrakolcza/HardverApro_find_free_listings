"""
A Simple Script for Extracting Data from a Webpage 
This script allows the user to extract the free items from HardverApró.
"""

# libraries
import urllib.request
from bs4 import BeautifulSoup
import csv
from progress.bar import Bar

# Base and starting URL
base_url = 'https://hardverapro.hu'
url = '/aprok/keres.php?search_exac=0&search_title=0&buying=0&noiced=1&offset=0'

free_items = []
free_items_links = []

# Finding the last section
request = urllib.request.Request (base_url + url)
content = urllib.request.urlopen(request)
parse = BeautifulSoup(content, 'html.parser')
last_section = parse.find('a', {'title' : 'Utolsó blokk'})['href']
last_section = last_section.split("offset=")
last_section = int(last_section[1])

bar = Bar('Scanning and processing page', max=(last_section / 50))

# Processing
while url != None:

    # Fetching the html
    request = urllib.request.Request (base_url + url)
    content = urllib.request.urlopen(request)

    # Parsing the html 
    parse = BeautifulSoup(content, 'html.parser')

    price = parse.find_all("div", class_="uad-price")
    count = 0
    for row in price:
        if row.text == "Ingyenes":
            parent = row.parent
            parent = parent.parent
            link = parent.findChildren("a", recursive="False")
            link = link[0]["href"]
            link = link.strip()
            title = parent.find_all("div", class_="uad-title")
            title = title[0].text.strip()
            
            # Check is not necessary, but I will leave it here for future upgrades of the script
            if title not in free_items:
                free_items.append(title)
                free_items_links.append(link)

    # Trying to locate the next section
    try:
        url = parse.find('a', {'title' : 'Következő blokk'})['href']
        bar.next()
    except TypeError:
        url = None

# Writing extracted data in a csv file
with open('free_items.csv', 'a') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(['Title','Link'])
    for col1,col2 in zip(free_items, free_items_links):
        writer.writerow([col1, col2])

bar.finish()