from flask import Flask, render_template, Response
import threading
import csv
import time
import urllib.request
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from flask_statistics import Statistics
from feedgen.feed import FeedGenerator
import re
app = Flask(__name__)

"""
#Statistics
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)

class Request(db.Model):
    __tablename__ = "request"

    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    response_time = db.Column(db.Float)
    date = db.Column(db.DateTime)
    method = db.Column(db.String)
    size = db.Column(db.Integer)
    status_code = db.Column(db.Integer)
    path = db.Column(db.String)
    user_agent = db.Column(db.String)
    remote_address = db.Column(db.String)
    exception = db.Column(db.String)
    referrer = db.Column(db.String)
    browser = db.Column(db.String)
    platform = db.Column(db.String)
    mimetype = db.Column(db.String)

db.create_all()

statistics = Statistics(app, db, Request)
"""

def update_items():
    try:
        while True:
            # Base and starting URL
            base_url = 'https://hardverapro.hu'
            url = '/aprok/keres.php?search_exac=0&search_title=0&buying=0&noiced=0&offset=0'

            free_items = []
            free_items_links = []
            free_items_imgs = []
            free_items_price = []
            isItFrozen = []

            new_free_items = []
            new_free_items_links = []
            new_free_items_imgs = []

            #Loading in the old items
            old_items = []
            with open('free_items.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_counter = 0
                for row in csv_reader:
                    if line_counter != 0:
                        old_items.append( row[1] )
                    line_counter = line_counter + 1


            # Processing
            while url != None:
                # Fetching the html
                request = urllib.request.Request (base_url + url)
                content = urllib.request.urlopen(request)

                # Parsing the html 
                parse = BeautifulSoup(content, 'html.parser')

                price = parse.find_all("div", class_="uad-price")
                
                for row in price:
                    if row.text == "Keresem":
                        continue
                    if row.text == "Csere" or row.text == "Ingyenes" or int(row.text.replace("Ft", "").replace(" ", "")) <= 3000:
                        parent = row.parent
                        parent = parent.parent
                        link = parent.findChildren("a", recursive="False")
                        link = link[0]["href"]
                        link = link.strip()
                        title = parent.find_all("div", class_="uad-title")
                        title = title[0].text.strip()
                        title = re.sub(r'[^\x00-\x7F]', ' ', title)

                        # Filter
                        filtered = [ "eladót", "adás-vétel", "keresünk", "áron", "előresorolt" ]
                        if any(x in title.lower() for x in filtered):
                            continue

                        parent = parent.parent
                        img = parent.findChildren("img", recursive="False")
                        img = "https:" + img[0]["src"]
                        
                        free_items.append(title)
                        free_items_links.append(link)
                        free_items_imgs.append(img)
                        free_items_price.append(row.text)
                        if parent.find('span', {'class': 'fas fa-snowflake fa-lg'}) != None:
                            isItFrozen.append(True)
                        else:
                            isItFrozen.append(False)

                        #Checking if item already existed before the previous run
                        if (link not in old_items) and (parent.find('span', {'class': 'fas fa-snowflake fa-lg'}) == None) and (row.text == "Ingyenes"):
                            new_free_items.append(title)
                            new_free_items_links.append(link)
                            new_free_items_imgs.append(img)

                # Trying to locate the next section
                try:
                    url = parse.find('a', {'title' : 'Következő blokk'})['href']
                except TypeError:
                    url = None

            # Writing extracted data in a csv file
            with open('free_items.csv', 'w', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                writer.writerow( [ time.ctime() ] )
                for col1,col2,col3,col4,col5 in zip(free_items, free_items_links, free_items_imgs, free_items_price, isItFrozen):
                    writer.writerow([col1, col2, col3, col4, col5])
            with open('new_free_items.csv', 'w', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                for col1,col2,col3 in zip(new_free_items, new_free_items_links, new_free_items_imgs):
                    writer.writerow([col1, col2, col3 ])
            
            print("Updated the CSV file at: " + time.ctime())
            
            time.sleep(60 * 60 * 6)

    except Exception as err:
        print("Unexpected ", err)

@app.route('/')
def list_free_items():
    items = []
    time = ""
    with open('free_items.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_counter = 0
        for row in csv_reader:
            if line_counter == 0:
                time = row[0]
            elif row[3] == "Ingyenes":
                items.append( [ line_counter, row[0], row[1], row[2], row[3], row[4] ] )
            line_counter = line_counter + 1

    return render_template('index.html', items=items, time=time)

@app.route('/swap')
def list_swap_items():
    items = []
    time = ""
    with open('free_items.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_counter = 0
        for row in csv_reader:
            if line_counter == 0:
                time = row[0]
            elif row[3] == "Csere":
                items.append( [ line_counter, row[0], row[1], row[2], row[3], row[4] ] )
            line_counter = line_counter + 1

    return render_template('index.html', items=items, time=time)

@app.route('/all')
def list_all_items():
    items = []
    time = ""
    with open('free_items.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_counter = 0
        for row in csv_reader:
            if line_counter == 0:
                time = row[0]
            else:
                items.append( [ line_counter, row[0], row[1], row[2], row[3], row[4] ] )
            line_counter = line_counter + 1

    return render_template('index.html', items=items, time=time)

@app.route('/price/<int:Price>')
def list_items(Price):
    items = []
    time = ""
    with open('free_items.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_counter = 0
        for row in csv_reader:
            if line_counter == 0:
                time = row[0]
            elif row[3] == "Csere":
                continue
            elif (row[3] == "Ingyenes") or (int(row[3].replace("Ft", "").replace(" ", "")) <= Price):
                items.append( [ line_counter, row[0], row[1], row[2], row[3], row[4] ] )
            line_counter = line_counter + 1

    return render_template('index.html', items=items, time=time)

@app.route('/rss')
def get_feed():
    feed = FeedGenerator()
    feed.title("Free Stuff on HardverApró")
    feed.description("This script allows the user to extract the free / very cheap items from HardverApró and view it in a browser. This page only shows free stuff. For every listing between free and 3000 Ft visit /all page or visit /price/'yourpricelimit' to filter the listings. Lastly, you can visit /swap.")
    feed.link({'href': "https://hardverapro.rakolcza.ml"})
    feed.load_extension('media')

    with open('new_free_items.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            entry = feed.add_entry()
            entry.title(row[0])
            entry.link({'href': row[1]})
            entry.media.thumbnail({'url': row[2]})
    return Response(feed.rss_str(), mimetype='application/rss+xml')


if __name__ == "__main__":
    update_items = threading.Thread(target=update_items, name="Updater")
    update_items.start()
    app.run(host='0.0.0.0')
