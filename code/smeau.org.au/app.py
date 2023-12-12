import requests
from bs4 import BeautifulSoup
import pandas
import os, json 

homeURL = 'https://www.bbb.org/search?find_country=USA&find_latlng=40.762801%2C-73.977818&find_loc=New%20York%2C%20NY&find_type=Category&sort=Distance&find_text='
txtPath = './links.txt'
csvsPath = './csvs'
if not os.path.exists(csvsPath):
    os.mkdir(csvsPath)

baseUrl = 'https://www.smea.org.au'
url = baseUrl + '/wapi/widget'


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}
filename = csvsPath + "/Companies_smea.org.au.csv"
def getLinks() :
    isEnd = True
    pageNum = 194
    while isEnd :
        
        data = {
            'dc_id': 1,
            'header_type': 'html',
            'request_type': 'POST',
            'currentPage': pageNum,
            'dataType': 10,
            'queryString': '',
            'profId': '',
            'servId': 'null',
            'countryId': '',
            'stateId': '',
            'cityId': '',
            'levId': '',
            'profsPost': {"new_filename":"search_results"},
            'widget_name': 'Add-On - Bootstrap Theme - Search - Lazy Loader',
        }
        

        # Send POST request with JSON data
        response = requests.post(url, data=data)

        if response.status_code == 200:
            initSoup = BeautifulSoup(response.text, "html.parser")
            results = initSoup.find_all('a', class_="center-block")
            if len(results) > 0 :
                for x in results :
                    # links.append(x['href'])
                    try:
                        with open(txtPath) as f:
                            linksList = f.readlines()
                            linksList = [v.strip() for v in linksList if v.strip() != '']
                    except: linksList = []
                    
                    if x['href'] not in linksList:
                        with open(txtPath, 'a') as fi:
                            fi.write(f"{x['href']}\n")
                print(f'Data has been appended: {pageNum}')
            
        else:
            isEnd = False
        pageNum = pageNum + 1                        
                                        

def getLeads():
    rows = []
    linksList = []
    with open(txtPath) as f:
        linksList = f.readlines()
    
    if len(linksList) > 0:
        for reUrl in linksList : 
            companyName, location, website, startDate, employees, typeEntity, alterNames, managers, addContactInfo, socialURL, category, phoneNum = '', '', '', '', '', '', [], [], {}, {}, [], ''
            try:
                detailPage = requests.get(baseUrl + reUrl.strip(), headers=headers, allow_redirects=True)
            except:
                if len(rows) > 0 :
                    data = pandas.DataFrame(rows) 
                    data.to_csv(filename, index=False, encoding='utf-8-sig')
                    rows = []
                    print('Successfully created csv file')
            # detailPage = requests.get(baseUrl + results[7]['href'])
            detailSoup = BeautifulSoup(detailPage.content, "html.parser")
            dataDivs = detailSoup.find_all('div', class_="col-sm-4 bold")
            socialDiv = detailSoup.find('div', class_="col-sm-4 bold xs-bmargin")
            for s in dataDivs:
                if s.text.strip() == 'Company Name':
                    companyName = s.find_next('div').text.strip()
                if s.text.strip() == 'Website':
                    website = s.find_next('div').text.strip()
                if s.text.strip() == 'Phone Number':
                    phoneNum = s.find_next('div').find('u').text.strip()
                if s.text.strip() == 'Location':
                    locationCon = s.find_next('div').contents
                    for x in range(0, len(locationCon)):
                        if str(locationCon[x]) == "<br/>" or str(locationCon[x]) == "\n" or str(locationCon[x]) == ", ":
                            continue
                        elif "<span>" in str(locationCon[x]) :
                            location = location + str(locationCon[x]).split(">")[1].split("<")[0] + ", "
                        else :
                            location = location + str(locationCon[x])
                    
            if socialDiv != None :
                socialLinks = socialDiv.find_next('div').find_all('a')
                for link in socialLinks:
                    socialURL[link['class'][1]] = link['href']
            print([companyName, location.strip(), phoneNum, website, socialURL ])
            if companyName != '' :
                rows.append({
                    'Company': companyName,
                    'Website': website,
                    'Industry': typeEntity,
                    'Employees': employees,
                    'Annual revenue': '',
                    'Total funding': '',
                    'Company phone': phoneNum,
                    'Company Address': location.strip(),
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
            del linksList[0]

            with open(txtPath, 'w') as file:
                file.writelines(linksList) 
        if len(rows) > 0 :
            data = pandas.DataFrame(rows) 
            data.to_csv(filename, index=False, encoding='utf-8-sig')
            rows = []
            print('Successfully created csv file')
    else :
        print('Error')

#             
# getLinks()
getLeads()
print("Sucessfully scraping...")


 
        

