#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import re
import math
import csv

driver = webdriver.Chrome()

# dictionary for different make of a cars from JP
# car_make_dict = {1: 'TOYOTA', 2: 'HONDA', 3: 'NISSAN', 4: 'MAZDA', 5: 'MITSUBISHI'}
car_make_dict = {5: 'MITSUBISHI', 4: 'MAZDA', 3: 'NISSAN', 2: 'HONDA', 1: 'TOYOTA'}


# DETAILED CSV
csv_detailed_file = open('beforward_toyota_detailed.csv', 'w', encoding='utf-8', newline='')
writer_detailed = csv.writer(csv_detailed_file)
writer_detailed.writerow(['Car Make','Location' ,'Chassis No', 'Version/Class', 'Model Code', 'Milleage', 'Engine Size (CC)', 'Engine Code', \
    'Drive','Steering','Transmission','External Color','Registration Year/Month', 'Fuel','Manufacture Year/Month','Price($)'])

# START FETCHING LINKS FOR EACH VEHICLE
# Get data from
# result_urls = ['https://www.beforward.jp/stocklist/from_stocklist=1/kmode=and/make={}/sortkey=n/view_cnt=100'.format(x) for x in car_make_dict.keys()]

result_urls = ['https://www.beforward.jp/stocklist/from_stocklist=1/kmode=and/make={}/mfg_year_from=2015/mfg_year_to=2019/sortkey=n/view_cnt=100'.format(x) for x in car_make_dict.keys()]

links_list = []
for url in result_urls:
    driver.get(url)

    # get cars of first page
    total_cars_raw = driver.find_element_by_xpath('//div[@class="results-hits"]').text
    totals_cars = int(''.join(re.findall('\d+', total_cars_raw)))
    print(totals_cars)


    index = 1
    cars_fetched = 0
    # links_list = []
    # price = 0
  
    # while index < 2:
    while True:
        index+=1

        try:
            wait_fetching = WebDriverWait(driver, 10)
            cars = wait_fetching.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="cars-box"]/table/tbody/tr/td[@class="make-model-td"]')))
            print(len(cars))
            cars_fetched+=len(cars)
        except:
            driver.refresh()
            continue

        if(cars_fetched < totals_cars):
            for car in cars:
                try:
                    price_offer = car.find_element_by_xpath('..//td/[@class="is-underoffer-td"]').text
                    continue
                except:
                    pass

                try:
                    title = car.find_element_by_xpath('.//span[@class="model-title"]').text
                    year = ''.join(re.findall('\d+', title))
                    year = year[:4]
                    print(title)
                    print('Year : '+ year)
                except:
                    pass
                
                link = ''
                try:
                    link = car.find_element_by_xpath('.//a').get_attribute("href") 
                    # if(int(year) >= 2015 & int(year) <= 2020):
                    links_list.append(link)
                except:
                    pass

            try:
                page_next_button = WebDriverWait(driver, 10)
                page_next = page_next_button.until(EC.element_to_be_clickable((By.XPATH,
                '//li/a[@class="pagination-next"]')))
                driver.execute_script("arguments[0].click();", page_next)
            except Exception as e:
                print(e)


        else:
            break

# END FETCHING LINKS FOR EACH VEHICLE

# -----------------------------------
print('-'*50)
print('Total Links:' + str(len(links_list)))
for l in links_list:
    print('Link: '+ l)

# -----------------------------------

# BEGIN EXTRACTING SPECIFICATIONS FOR EACH CAR COLLECTED EARLIER

# START FETCHING CAR SPECIFICATIONS FOR EACH LINK COLLECTED ABOVE
time.sleep(3)

counter = 0
while counter < len(links_list):
    print("Car {}".format(counter+1)) 
    print("Link: "+ links_list[counter])  

    driver.get(links_list[counter])
    counter += 1
    time.sleep(3)

    # get the car make
    try:
        car_make = driver.find_element_by_xpath('//div[@class="car-info-area cf"]/h1').text
        car_make = ''.join(re.findall('\D+', car_make))
    except:
        # counter += 1
        continue

    # get the price
    try:
        price = driver.find_element_by_xpath('//span[@class="ip-usd-price"]').text
        price = ''.join(re.findall('\d+', price))
    except:
        # counter += 1
        continue

    # Get all the rows on the specification table
    try:
        wait_fetch_rows = WebDriverWait(driver, 10)
        spec_rows = wait_fetch_rows.until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="cf"]/table/tbody/tr')))
        print('Number of headers in specification table: {}'.format(len(spec_rows)))
    except:
        # time.sleep(2)
        # driver.refresh()
        # counter += 1
        continue

    
    print('-'*50)
    row_dict = {}
    row_dict['car_make'] = car_make
    j = 0
    while(j < len(spec_rows)):
        try:
            th_values = spec_rows[j].find_elements_by_xpath('.//th')
            td_values = spec_rows[j].find_elements_by_xpath('.//td')
            if(len(th_values) >= 1):
                for k in range(len(th_values)):
                    th_value = ((spec_rows[j].find_elements_by_xpath('.//th')[k]).text).strip()
                    td_value = ((spec_rows[j].find_elements_by_xpath('.//td')[k]).text).strip()
                    
                    th_dimension = ''
                    if(th_value.find('Dimension') != -1):
                        th_dimension = th_value
                    temp = ['Ref No','Sub Ref No', 'Auction Grade', 'Max Loading Capacity', 'Weight', 'M3', 'Doors','Seats', th_dimension]
                    if (not(th_value in temp)):
                        if (len(td_value) > 0):
                            row_dict[th_value] = td_value
                        else:
                            row_dict[th_value] = 'N/A'
                        
                        print(th_value + ' : '+ td_value)
            j+=1
        except:
            pass
    print('Price : '+ price)
    print('-'*50)
    row_dict['Price'] = price
    writer_detailed.writerow(row_dict.values())
    # counter+=1


