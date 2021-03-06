import requests
import os
import yagmail
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import logging
import time


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
URL_TO_MONITOR=os.environ["URL_TO_MONITOR"]

def send_email(message):
    u_name=os.environ['SMTP_USERNAME']
    u_pass=os.environ['SMTP_PASSWORD']

    yag=yagmail.SMTP(u_name,u_pass)
    yag.send(os.environ['SMTP_RECIPIENT'],"web-monitor update",message)
   
def process_html(string):
    soup = BeautifulSoup(string, features="lxml")

    # make the html look good
    soup.prettify()

    # remove script tags
    for s in soup.select('script'):
        s.extract()

    # remove meta tags 
    for s in soup.select('meta'):
        s.extract()

    # convert to a string, remove '\r', and return
    return str(soup).replace('\r', '')

def webpage_check(): 
    """Returns true if the webpage was changed, otherwise false."""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
    response = requests.get(URL_TO_MONITOR, headers=headers)

    # create the previous_content.txt if it doesn't exist
    if not os.path.exists("previous_content.txt"):
        open("previous_content.txt", 'w+').close()
    
    filehandle = open("previous_content.txt", 'r', encoding='utf-8')
    previous_response_html = filehandle.read() 
    filehandle.close()

    processed_response_html = process_html(response.text)


    if processed_response_html == previous_response_html:
        return False
    else:
        filehandle = open("previous_content.txt", 'w', encoding='utf-8')
        filehandle.write(processed_response_html)
        filehandle.close()
        return True

def main():
    log = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    log.info("Running Website Monitor")
    while True:
        # try:
        if webpage_check():
            log.info("WEBPAGE WAS CHANGED.")
            send_email(f"PUPPIES!!!! {URL_TO_MONITOR}")
        else:
            log.info("Webpage was not changed.")
        # except:
        #     log.info("Error checking website.")
        time.sleep(3600)


if __name__ == "__main__":
    main()