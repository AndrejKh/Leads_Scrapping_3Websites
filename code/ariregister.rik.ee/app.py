from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import pandas
import os, json

keysPath = './keywords.txt'
linksPath = './links.txt'
csvsPath = '../../leads/ariregister.rik.ee'
if not os.path.exists(csvsPath):
    os.mkdir(csvsPath)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}
baseUrl = 'https://ariregister.rik.ee'
startUrl = "https://ariregister.rik.ee/eng/"

def startScraping(URL):
    listPage = requests.get(URL, headers=headers)
    # Use BeautifulSoup to parse the redirected page source
    soup = BeautifulSoup(listPage.content, 'html.parser')
    tbody = soup.find("tbody")
    if tbody != None :
        trs = tbody.find_all('tr')
        for row in trs:
            company, address, email, phone, capital = '', '', '', '', ''
            link = row.find('td').find('a')['href']
            # link = trs[2].find('td').find('a')['href']
            try:
                with open(linksPath) as f:
                    linksList = f.readlines()
                    linksList = [v.strip() for v in linksList if v.strip() != '']
            except: linksList = []
            
            if link not in linksList:
                with open(linksPath, 'a') as fi:
                    fi.write(f"{link}\n")
                driver = webdriver.Chrome()
                driver.get(baseUrl + link)
                # detailPage = requests.get(baseUrl + link)
                detailSoup = BeautifulSoup(driver.page_source, 'html.parser')
                company = detailSoup.find('div', class_='header-name-print')
                if company != None:
                    company = company.text.strip().splitlines()[0]
                    divs = detailSoup.find_all('div', class_="row mt-4")
                    for div in divs :
                        label = div.find('div')
                        if(label.text.strip() == 'Address'):
                            address = label.find_next('div').text.strip().split("Open map")[0]
                        if(label.text.strip() == 'E-mail address'):
                            email = label.find_next('div').text.strip()
                        if(label.text.strip() == 'Mobile phone'):
                            phone = label.find_next('div').text.strip()
                        if(label.text.strip() == 'Capital'):
                            text = label.find_next('div').text.strip()        
                            if 'Capital is' in text :
                                capital = text.split("Capital is")[1].split('€')[0] + "€"
                    print(company, address, email, phone, capital)
                    rows.append({
                        'Company': company,
                        'Email address': email,
                        'Phone number': phone,
                        'Location': address,
                        '# Employees': '',
                        'Industry & Keywords': '',
                        'Buying Intent': '',
                        'Technologies': '',
                        'Revenue': '',
                        'Funding': '',
                        'Job Postings': '',
                    })
                else:
                    driver.quit()
                    continue
                driver.quit()
            else :
                continue
    pagination = soup.find('ul', class_="pagination")
    if pagination != None :
        next = pagination.find_all('a', class_="page-link")[-1]
        if next.text.strip() == 'Next':
            startScraping(baseUrl + next['href'])

# Set up the WebDriver (use the appropriate driver for your browser)

with open(keysPath) as f:
    keywords = f.readlines()
    keywords = [v.strip().lower() for v in keywords if v.strip() != '']

for key in keywords :
    # Navigate to the initial page
    filenames = [filename.split("(")[0] for filename in os.listdir(csvsPath) if os.path.isfile(os.path.join(csvsPath, filename))]

    csvFileName = f'Companies_{key}_'
    
    if csvFileName not in filenames:
        driver = webdriver.Chrome()
        driver.get(startUrl)

        # Find the search bar and submit the for
        wait = WebDriverWait(driver, 10)
        search_bar = wait.until(EC.presence_of_element_located((By.ID, "company_search")))
        search_bar.send_keys(key)
        search_bar.send_keys(Keys.RETURN)

        # Wait for the redirection to complete (you may need to adjust the sleep time or use WebDriverWait)
        time.sleep(3)

        # Get the redirected page source
        redirectedUrl = driver.current_url

        # Close the browser
        driver.quit()

        rows = []
        startScraping(redirectedUrl)
        if len(rows) > 0:
            csvFileName = f'{csvFileName}({len(rows)}).csv'
            data = pandas.DataFrame(rows) 
            data.to_csv(csvsPath + "/" + csvFileName, index=False, encoding='utf-8-sig')
            print(f"Successfully created csv file - {csvFileName}")

            continue
    else :
        print("Skipped:", key)
print("Successfully finished scrapping.")


