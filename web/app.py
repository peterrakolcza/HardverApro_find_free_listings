from flask import Flask, render_template
import threading
import csv
import time
import os.path
app = Flask(__name__)

@app.route('/')
def list_free_items():
    items = []
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../web_scraper/free_items.csv")
    with open('free_items.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_counter = 0
        for row in csv_reader:
            items.append( [ line_counter, row[0], row[1], row[2] ] )
            line_counter = line_counter + 1

    return render_template('index.html', items=items)



if __name__ == "__main__":
    app.run()