# NTHSA Handler
import time
import datetime
from datetime import date
from datetime import datetime,timedelta
import requests
import json
import csv
from bs4 import BeautifulSoup

## NTHSA Class

class NTHSA:

    def __init__(self, nthsa_num):

        self.nthsa_num  = nthsa_num
        self.url =  "https://api.nhtsa.gov/recalls/campaignNumber?campaignNumber=" + nthsa_num
        self.json =  requests.get(self.url).json()["results"]


    # Setup Attributes, Used For Display Purposes


    def get_model_years(self):

        y_list = []
        for i in range(len(self.json)):
                # print(self.json[i]["ModelYear"])
                if self.json[i]["ModelYear"] not in y_list:
                    y_list.append(self.json[i]["ModelYear"])
        return y_list
    
    def get_models(self):

        m_list = []
        for i in range(len(self.json)):
                # print(self.json[i]["Model"])
                if self.json[i]["Model"] not in m_list:
                    m_list.append(self.json[i]["Model"])
        return m_list

    def get_makes(self):

        ma_list = []
        for i in range(len(self.json)):
                # print(self.json[i]["Make"])
                if self.json[i]["Make"] not in ma_list:
                    ma_list.append(self.json[i]["Make"])
        return ma_list

    def get_manufacturer(self):

        man_list = []
        for i in range(len(self.json)):
                # print(self.json[i]["Manufacturer"])
                if self.json[i]["Manufacturer"] not in man_list:
                    man_list.append(self.json[i]["Manufacturer"])
        return man_list
    
    def get_affected_units(self):
        au_list = []
        for i in range(len(self.json)):
                # print(self.json[i]["PotentialNumberofUnitsAffected"])
                if self.json[i]["PotentialNumberofUnitsAffected"] not in au_list:
                    au_list.append(self.json[i]["PotentialNumberofUnitsAffected"])
        return au_list

    def get_dates(self):
        rd_list = []
        for i in range(len(self.json)):
                # print(self.json[i]["ReportReceivedDate"])
                if datetime.strptime(self.json[i]["ReportReceivedDate"], "%d/%m/%Y").date() not in rd_list:
                    rd_list.append(datetime.strptime(self.json[i]["ReportReceivedDate"], "%d/%m/%Y").date())
        return rd_list   

    def __str__(self):

         summary = "NTHSA Number: " + self.nthsa_num + "\nReport Received: " + (",").join(str(e) for e in self.get_dates()) + "\nUnits Affected " + (",").join(str(e) for e in self.get_affected_units())  + "\nManufacturer: " +  (",").join(self.get_manufacturer()) + "\nModels: " + (",").join(self.get_models()) + "\nMakes: " + (",").join(self.get_makes()) + "\nModel Years: " + (",").join(self.get_model_years()) + "\nLink: " + self.url
         return summary


## Get Recalls Function
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()



def get_recalls(json_file,min_year,max_year,num_weeks):
    # initialize progress bar
    items = list(range(min_year,max_year))
    l = len(items)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    master_nthsa = {}

    pb = 0
    error_counts = 0
    for year in json_file:
        if int(year) >= min_year and int(year) <= max_year:
            time.sleep(0.1)
            printProgressBar(pb, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
            pb += 1
                # years
            # print("Getting Data for Year: ", year)
                # makes 
            for make in json_file[year]:
                    # print(make)

                    # models
                for model in json_file[year][make]:
                            
                    try:
                        # get recall data

                        url = "https://api.nhtsa.gov/recalls/recallsByVehicle?make=" + make + "&model=" + model  + "&modelYear=" + year
                        recalls = requests.get(url).json()["results"]
                        recall_date = recalls[0]["ReportReceivedDate"]
                        if datetime.strptime(recall_date, "%d/%m/%Y").date() >= (date.today() - timedelta(weeks = num_weeks)):
                        
                        
                        #print(date)
                        # nthsa num
                        
                            nthsa_num = recalls[0]["NHTSACampaignNumber"]
                        
                        # make call for nthsa num

                            url = "https://api.nhtsa.gov/recalls/campaignNumber?campaignNumber=" + nthsa_num
                        # nthsa_req = requests.get(url).json()["results"]

                            master_nthsa[nthsa_num] = NTHSA(str(nthsa_num))

                        # write to csv file
                        # fc.writerows(nthsa_req)
                            
                    except:
                        error_counts += 1

    print("Number of Errors: ",error_counts)
    return master_nthsa


def get_recent_recalls(master_nthsa,recall_thres = 1000):

    for nthsa_num in master_nthsa:
        dates = master_nthsa[nthsa_num].get_dates()
        if dates[0] >= date.today() - timedelta(weeks = 4):
            print("-----------------------")
            print(master_nthsa[nthsa_num])


def get_model_years():

    # model year
    model_year = requests.get("https://api.nhtsa.gov/products/vehicle/modelYears?issueType=r ").json()["results"]

    years = []
    for i in range(len(model_year)):
        years.append(model_year[i]["modelYear"])
    return years

def get_makes(years,min_year,max_year):

    master = {k: {} for k in years}
    items = list(range(len(master)))
    l = len(items)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    pb = 0

    for year in years:
        if (int(year) >= int(min_year)) & (int(year) <= int(max_year)):
            time.sleep(0.1)
            printProgressBar(pb, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
            pb += 1
            # url for each year
            url = "https://api.nhtsa.gov/products/vehicle/makes?modelYear="+ year + "&issueType=r"
            # makes for each year
            makes = requests.get(url).json()['results']

            # append all makes to master
            for i in range(len(makes)):
                make = makes[i]["make"]
                make_dict = dict()
                make_dict[make] = []
                try: 
                    master[year].update(make_dict)
                except:
                    print("error")
    return master


def get_models(master,min_year,max_year):
    
    items = list(range(len(master)))
    l = len(items)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    pb = 0

    for year in master.keys():
        if (int(year) >= int(min_year)) & (int(year) <= int(max_year)):
            time.sleep(0.1)
            printProgressBar(pb, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
            pb += 1
        
            makes = master[year]

            for make in makes:
                try:
                # get url
                    url = "https://api.nhtsa.gov/products/vehicle/models?modelYear="+ year + "&make=" + make + "&issueType=r"

                # get models from API
                    models = requests.get(url).json()["results"]

                # add to master
                    for i in range(len(models)):

                        year = models[i]["modelYear"]
                        make = models[i]["make"]
                        model = models[i]["model"]
                    
                        master[year][make].append(model)
                except:
                    print("error")

    return master


def get_recall_mapping(min_year,max_year): 
    
    years = get_model_years()
    

    print("Getting Makes")
    master = get_makes(years,min_year,max_year)
    
    print("Getting Models")
    master = get_models(master,min_year,max_year)
    

    with open('docs/mapping.json','w') as f:
        json.dump(master,f)
    print("Complete. File has been updated.")

def get_new_links(rss_feed):
    url = requests.get(rss_feed)
    soup = BeautifulSoup(url.content, "xml")

    entries = soup.find_all("entry")

    # Links to Call from
    links = []

    for entry in entries:
        title = entry.title.text
        date = entry.updated.text
        id  = entry.id.text

        links.append(id)

    return links

def get_first_recall_table(html_link):
    url = requests.get(html_link)
    # get doc
    doc = BeautifulSoup(url.text,"lxml")
    
    data = dict()

    # append data from table to dictionary
    trs = doc.find_all("tr")
    for tr in trs:
        ths = tr.find_all("th")
        tds = tr.find_all("td")
        for th in ths:
            for td in tds:
                data[th.text] = td.text
    return data


def get_canadian_recalls():
    links = get_new_links("https://wwwapps.tc.gc.ca/Saf-Sec-Sur/7/VRDB-BDRV/search-recherche/rss.aspx?lang=eng")

    master = {k: {} for k in links}
    for link in links:
        data = get_first_recall_table(link)
        master[link] = data
    
    return master

def get_recent_recalls_canadian(master,week_num = 2):

    for link in master:
        
        if datetime.strptime(master[link]["Recall Date"],"%Y-%m-%d").date() >= date.today() - timedelta(weeks = week_num):

            print("------------------------")
            print("Recall  Date: ",master[link]["Recall Date"])
            print("Issued By: ",master[link]["Issued by"])
            print("Units Affected: ",master[link]["Units Affected\xa0"])
            print("System: ", master[link]["System"])
            print("Link: ",link)
            

def find_canadian_recalls(week_num):

    master = get_canadian_recalls()

    get_recent_recalls_canadian(master,int(week_num))


