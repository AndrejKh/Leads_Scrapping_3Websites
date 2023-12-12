import requests
from bs4 import BeautifulSoup
import pandas
import os, random 

homeURL = 'https://www.bbb.org/search?find_country=USA&find_latlng=40.762801%2C-73.977818&find_loc=New%20York%2C%20NY&find_type=Category&sort=Distance&find_text='
homeURL1 = 'https://www.bbb.org/search?find_country=CAN&find_latlng=45.539172%2C-73.593974&find_loc=Montreal%2C%20QC&find_type=Category&sort=Distance&find_text='
homeURL2 = 'https://www.bbb.org/search?find_country=MEX&find_latlng=19.301041%2C-98.337902&find_loc=De%20Mexico%2C%20TLA&find_type=Category&sort=Distance&find_text='

csvsPath = './csvs'
if not os.path.exists(csvsPath):
    os.mkdir(csvsPath)

Cates = [
    'Home Improvement',
    'Restaurants',
    'Auto Repair',
    'General Contractor',
    'Furniture Stores',
    'Dry Cleaners',
    'Jewelry Stores',
    'Real Estate',
    'Clothing',
    'Lawyers'
]

def Start(URL) :
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    rows = []
    
    for cate in Cates:
        url = URL + cate.replace(" ", "%20")
        filename = csvsPath + '/MEX_companies_' + cate + '_from_bbb.org.csv'
        initPage = requests.get(url+"&page=1", headers=headers)
        initSoup = BeautifulSoup(initPage.content, "html.parser")
        if initSoup.find('nav', class_="bds-pagination") == None:
            print('Empty')
            continue
        else:
            navigations = initSoup.find('nav', class_="bds-pagination").find_all('li')
            lastNav = int(navigations[len(navigations) - 1].find('a').text.strip().split(" ")[1])
            for i in range(1, lastNav + 1):
                sub = url+"&page="+str(i)
                subPage = requests.get(sub, headers=headers)
                subSoup = BeautifulSoup(subPage.content, "html.parser")
                if subSoup.find('div', class_="stack stack-space-20") == None :
                    print('No results')
                    continue
                else :
                    resultDiv = subSoup.find('div', class_="stack stack-space-20")
                    results = resultDiv.find_all('div', class_="result-item-ab")
                    for addr in results:
                        # durl = addr.find('a', class_="text-blue-medium")['href']+'/details'
                        durl = addr.find('a', class_="text-blue-medium")['href']+'/detalles'
                        companyName, location, website, startDate, employees, typeEntity, alterNames, managers, addContactInfo, socialURL, category, phoneNum = '', '', '', '', '', '', [], [], {}, {}, [], ''
                        detailPage = requests.get(durl, headers=headers)
                        detailSoup = BeautifulSoup(detailPage.content, "html.parser")
                        print(durl)
                        if detailSoup.find('h1', class_="bds-h3") == None:
                            print('skipped.')
                            continue
                        else:
                            companyName = detailSoup.find('h1', class_="bds-h3").text.strip().split(" for ")[1]
                            contactInfo = detailSoup.find('div', class_='dtm-contact')
                            location = contactInfo.find('address').text.strip()
                            if contactInfo.find('a', class_='dtm-url') != None:
                                website = contactInfo.find('a', class_='dtm-url')['href']
                            if contactInfo.find('a', class_='dtm-phone') != None:
                                phoneNum = contactInfo.find('a', class_='dtm-phone').text.strip()
                            
                            infoDts = detailSoup.find_all('dt')
                            
                            for s in infoDts:
                                if s.text.strip() == 'Business Started:':
                                    startDate = s.find_next('dd').text.strip()
                                if s.text.strip() == 'Number of Employees:':
                                    employees = s.find_next('dd').text.strip()
                                if s.text.strip() == 'Type of Entity:':
                                    typeEntity = s.find_next('dd').text.strip()
                                if s.text.strip() == 'Alternate Business Name':
                                    alts = s.find_next('dd').find_all('li')
                                    for aln in alts:
                                        alterNames.append(aln.text.strip())
                                if s.text.strip() == 'Business Management':
                                    alts = s.find_next('dd').find_all('li')
                                    for aln in alts:
                                        managers.append(aln.text.strip())
                                if s.text.strip() == 'Additional Contact Information':
                                    alts = s.find_next('dd').find_all('div', class_='')
                                    for aln in alts:
                                        iname = aln.find('p').text.strip()
                                        ilis = aln.find_all('li')
                                        values = []
                                        for ili in ilis:
                                            if ili.find('span') == None:
                                                values.append(ili.find('a').text.strip())
                                            else:
                                                values.append(ili.find('span').text.strip())
                                        addContactInfo[iname] = values
                                if s.text.strip() == 'Social Media':
                                    alts = s.find_next('dd').find_all('a')
                                    for aln in alts:
                                        socialURL[aln.text.strip()] = aln['href']
                                if s.text.strip() == 'Business Categories':
                                    alts = s.find_next('dd').find_all('a')
                                    for aln in alts:
                                        category.append(aln.text.strip())
                                
                            rows.append({
                                'Company': companyName,
                                'Website': website,
                                'Industry': typeEntity,
                                'Employees': employees,
                                'Annual revenue': '',
                                'Total funding': '',
                                'Company phone': phoneNum,
                                'Company Address': location,
                                # 'Company linkedin url': 
                                # 'Company street':
                                # 'Company city':
                                # 'Company postal code':
                                # 'Company state':
                                'Company country': '',
                                'Company founded date': startDate,
                                'Alter names': alterNames,
                                'Managers': managers,
                                'Addtional Contact Info': addContactInfo,
                                'Company Social Urls': socialURL,
                                'Category': category
                                })
                                    
            if len(rows) > 0 :
                data = pandas.DataFrame(rows) 
                data.to_csv(filename, index=False, encoding='utf-8-sig')
                
                print('Successfully created csv file')
Start(homeURL2)
print("Sucessfully scraping...")

 

 
        

