import os
from flask import Flask,render_template,request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from selenium import webdriver
from apscheduler.schedulers.blocking import BlockingScheduler
import config

app = Flask(__name__)


def send_sms(message):
    print(message)
    url = 'https://www.fast2sms.com/dev/bulk'
    payload = "sender_id=FSTSMS&message={0}&language=english&route=p&numbers=9130050005".format(message)
    headers = {
    'authorization': config.authorization,
    'Content-Type': "application/x-www-form-urlencoded",
    'Cache-Control': "no-cache",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

def prod_detail():
        # driver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

        #make fake browser agent
        url = 'https://www.myntra.com/invictus-jacket'
        driver.get(url)
        driver.implicitly_wait(30)
        source = driver.page_source
        html = bs(source, 'html.parser')

        #perticular product link
        link = 'https://www.myntra.com/jackets/invictus/invictus-men-off-white-solid-bomber/5497974/buy'
        driver.get(link)
        pSource = driver.page_source
        html = bs(pSource, 'html.parser')
        all_prod = html.find_all('div', {'class':'pdp-price-info'})
        name = all_prod[0].find_all('h1')
        prod_name = name[1].text
        print(prod_name)

        #price
        price = all_prod[0].find_all('span')
        pr = price[0].text.split(' ')
        print(pr)

        #size
        size = html.find_all('button', {'class' : 'size-buttons-size-button-disabled size-buttons-size-button-default'})
        size1 = size[1].p.text
        print(size1)

        if (size1 == 'M'):
                print('Product is now available')
                message = ' Hello Ganesh The Product ' + prod_name + ' of size (M). Price Rs:' + pr[1] + ' is in Stock now please visit' + link
                send_sms(message)
        driver.close()


sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=0.166667)
def timed_job():
    print('This job is run every ten seconds.')
    prod_detail()

sched.start()

@app.route('/', methods=['GET'])
def signup():
    print('********************called**********************')

if __name__ == '__main__':
    sched.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

