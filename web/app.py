from flask import Flask, render_template
import threading
import csv
import time
import urllib.request
from bs4 import BeautifulSoup
app = Flask(__name__)

def update_items():
    while True:
        # Base and starting URL
        base_url = 'https://hardverapro.hu'
        url = '/aprok/keres.php?search_exac=0&search_title=0&buying=0&noiced=1&offset=0'

        free_items = []
        free_items_links = []
        free_items_imgs = []


        # Processing
        while url != None:
            # Fetching the html
            request = urllib.request.Request (base_url + url)
            content = urllib.request.urlopen(request)

            # Parsing the html 
            parse = BeautifulSoup(content, 'html.parser')

            price = parse.find_all("div", class_="uad-price")
            
            for row in price:
                if row.text == "Ingyenes":
                    parent = row.parent
                    parent = parent.parent
                    link = parent.findChildren("a", recursive="False")
                    link = link[0]["href"]
                    link = link.strip()
                    title = parent.find_all("div", class_="uad-title")
                    title = title[0].text.strip()

                    parent = parent.parent
                    img = parent.findChildren("img", recursive="False")
                    img = "https:" + img[0]["src"]
                    
                    free_items.append(title)
                    free_items_links.append(link)
                    free_items_imgs.append(img)

            # Trying to locate the next section
            try:
                url = parse.find('a', {'title' : 'Következő blokk'})['href']
            except TypeError:
                url = None

        # Writing extracted data in a csv file
        with open('free_items.csv', 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            for col1,col2,col3 in zip(free_items, free_items_links, free_items_imgs):
                writer.writerow([col1, col2, col3])
        
        print("Updated the CSV file at: " + time.ctime())
        time.sleep(60 * 60 * 12)

@app.route('/')
def list_free_items():
    items = []
    with open('free_items.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_counter = 0
        for row in csv_reader:
            items.append( [ line_counter, row[0], row[1], row[2] ] )
            line_counter = line_counter + 1

    return render_template('index.html', items=items)



if __name__ == "__main__":
    update_items = threading.Thread(target=update_items, daemon=True, name="Updater")
    update_items.start()
    app.run()