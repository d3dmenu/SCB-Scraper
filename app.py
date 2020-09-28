# /**
#  * Nemo payment iControl for Python
#  * System transactions checker.
#  * Version 2.1
#  *
#  * Released under the MIT license.
#  *
#  * Copyright (c) 2020 Tinnapat Rattanatham

#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
#  documentation files (the "Software"), to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
#  to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#  The above copyright notice and this permission notice shall be included in all copies or substantial portions
#  of the Software.

#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
#  THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#  */

import os
import csv
import time         
import mysql.connector

from pathlib import Path
from getpass import getpass
from firebase import firebase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from urllib3.exceptions import HostChangedError

# base variable
url = "https://www.scbeasy.com/v1.4/site/presignon/index.asp"

# Current path from start up
path = str(Path(__file__).parent.absolute()) + "\\driver\\chromedriver.exe"

os.path.abspath(path)

# Driver chrome version 85.0.4183.121 (Official Build) (64-bit)

# Class database MYSQL
class config():
    def __init__(self, host, username, password, database, port):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = port

        # Connection to database
        self.db = mysql.connector.connect(
            host = self.host, 
            user = self.username, 
            password = self.password, 
            database = self.database
        )

        self.cursor = self.db.cursor()
    
    def db_Loadtransaction(self):
        self.cursor.execute("SELECT * FROM TRANSACTIONS")
        for i in self.cursor:
            print(i)
    
    def db_Insertdata(self, date, time, type, channel, detail, checkid, withdraw, deposit, balance):
        # conn.InsertData("02/08/2541", "03:50", "X2", "ATM", "Terminal No. F308/Cardless ATM", "", "-200.00", "", "+4,543.37")
        sql = ('''
            INSERT INTO Transactions (DATE, TIME, TYPE, CHANNEL, DETAIL, CHECKID, WITHDRAW, DEPOSIT, BALANCE) VALUES 
            ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")
        ''' % (date, time, type, channel, detail, checkid, withdraw, deposit, balance))

        self.cursor.execute(sql)
        self.db.commit()    
    

# Class payment
class payment():

    # Methid payment

    def __init__(self, path, url, user, passwd, mode):
        # path file
        self.path = path
        # target url
        self.url = url
        # information sign in to target website
        self.user = user
        self.passwd = passwd
        # web driver mode [Enabled / Disabled]
        self.mode = mode
        # Save to database
        self.data = []
        self.dict = {}

        # base element
        self.element = {"txtlogin": "//*[@id='LOGIN']", 
                        "txtpsasword": "//*[@id='LogIn']/table/tbody/tr[3]/td/label/input",
                        "btnsubmit": "//*[@id='lgin']", 
                        "Account": "//*[@id='Image3']",
                        "View": "//*[@id='DataProcess_SaCaGridView_SaCaView_LinkButton_0']",
                        "Dataprogress2": "//*[@id='DataProcess_Link2']",
                        "Dataprogress3": "//*[@id='DataProcess_Link3']", 
                        "Combobox": "//*[@id='DataProcess_ddlMonth",
                        "Table": "//*[@id='DataProcess_GridView']",
                        "Mainpage": "//*[@id='mainpage']",
                        "Back": "//*[@id='back']"}
    
    def Scrap_month(self, month, loadall=True):
        
        if self.mode:
            options = webdriver.ChromeOptions()
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--incognito")
            options.add_argument("--headless")
            self.driver = webdriver.Chrome(
                self.path, chrome_options=options
            )
        else:
            self.driver = webdriver.Chrome(self.path)
        
        # Start browser [chrome]
        self.driver.get(self.url)

        # [Event for target website]

        # Username
        self.driver.find_element_by_xpath(self.element["txtlogin"]).send_keys(self.user, Keys.TAB)
        # Password
        state = self.driver.find_element_by_xpath("//*[@id='LogIn']/table/tbody/tr[3]/td/label/input")
        state.send_keys(self.passwd)
        # Submit button
        self.driver.find_element_by_xpath(self.element["btnsubmit"]).click()
        # Account
        self.driver.find_element_by_xpath(self.element["Account"]).click()
        # View
        self.driver.find_element_by_xpath(self.element["View"]).click()
        # Dataprogress
        self.driver.find_element_by_xpath(self.element["Dataprogress3"]).click()


        # Select by text
        # select_fr.select_by_visible_text('กันยายน 2563')
    
        if loadall == False:

            # Combobox select transactions
            select_fr = Select(self.driver.find_element_by_xpath("//*[@id='DataProcess_ddlMonth']"))
            # Select by value
            select_fr.select_by_index(month)

            # Load data transactions
            rows = self.driver.find_elements_by_xpath("//*[@id='DataProcess_GridView']")
            pattern = ["Date", "Time", "Type", "Channel", "Detial", "CheckID", "WithDraw", "Deposit", "Balance"]
            for row in rows:
                temp = []
                columns = row.find_elements_by_css_selector("td") # check bv td tag

                for column in columns:
                    if len(temp) == 9: # Columns
                        self.data.append(temp)
                        temp = []
                    temp.append(column.text)
                    
            return self.data
        else:
            for m in range(1, 12):
                # Combobox select transactions
                select_fr = Select(self.driver.find_element_by_xpath("//*[@id='DataProcess_ddlMonth']"))
                # Select by value
                print(m)
                select_fr.select_by_index(m)

                # Load data transactions
                rows = self.driver.find_elements_by_xpath("//*[@id='DataProcess_GridView']")
                pattern = ["Date", "Time", "Type", "Channel", "Detial", "CheckID", "WithDraw", "Deposit", "Balance"]
                for row in rows:
                    temp = []
                    columns = row.find_elements_by_css_selector("td")

                    for column in columns:
                        if len(temp) == 9:
                            self.data.append(temp)
                            temp = []
                        temp.append(column.text)
            return self.data
    
    def Scrap_realtime(self):
        count = 0
        if self.mode:
            options = webdriver.ChromeOptions()
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--incognito")
            options.add_argument("--headless")
            self.driver = webdriver.Chrome(
                self.path, chrome_options=options
            )
        else:
            self.driver = webdriver.Chrome(self.path)
        
        # Start browser [chrome]
        self.driver.get(self.url)

        # [Event for target website]

        # Username
        self.driver.find_element_by_xpath(self.element["txtlogin"]).send_keys(self.user, Keys.TAB)
        # Password
        state = self.driver.find_element_by_xpath("//*[@id='LogIn']/table/tbody/tr[3]/td/label/input")
        state.send_keys(self.passwd)
        # Submit button
        self.driver.find_element_by_xpath(self.element["btnsubmit"]).click()
        # Account
        self.driver.find_element_by_xpath(self.element["Account"]).click()
        # View
        self.driver.find_element_by_xpath(self.element["View"]).click()
        # Dataprogress
        self.driver.find_element_by_xpath(self.element["Dataprogress2"]).click()

        # Load data transactions
        while True:
            rows = self.driver.find_elements_by_xpath("//*[@id='DataProcess_GridView']")
            pattern = ["Date", "Time", "Type", "Channel", "WithDraw", "Deposit", "Detial"]
            for row in rows:
                temp = []
                columns = row.find_elements_by_css_selector("td") # check td tag

                for column in columns:
                    if len(temp) == 7: # Columns
                        if temp not in self.data: self.data.append(temp)
                        temp = []
                    temp.append(column.text)

            if len(self.data) != count:
                count = len(self.data)
                print(self.data[-1])

            time.sleep(3)

            # https://www.scbeasy.com/online/easynet/page/err/err_post.aspx  # Back
            # https://www.scbeasy.com/online/easynet/page/err/err_session.aspx?err_code=9&lang= # Maximum session

            if self.driver.current_url == str("https://www.scbeasy.com/online/easynet/page/err/err_post.aspx"):
                try:
                    # Back
                    self.driver.find_element_by_xpath(self.element["Back"]).click()
                    # View
                    self.driver.find_element_by_xpath(self.element["View"]).click()
                    # Dataprogress
                    self.driver.find_element_by_xpath(self.element["Dataprogress2"]).click()
                except:
                    pass
            try:
                self.driver.find_element_by_xpath(self.element["Mainpage"]).click()
            except:
                pass
            self.driver.refresh()
                        

if __name__ == "__main__":

    # Authentication
    conn = config("localhost", "root", "123456", "nemo", "3306")

    scb_admin = input("Username: ")
    scb_password = getpass()

    # Object class variable
    sc = payment(path, url, scb_admin, scb_password, False)

    sc.Scrap_realtime()


    # # Download History Transactions
    # ts = sc.Scrap_month(2, True)
    # print(ts)

    # for idx in range(len(ts)):
    #     conn.db_Insertdata(ts[idx][0], ts[idx][1], ts[idx][2], ts[idx][3], ts[idx][4], ts[idx][5], ts[idx][6], ts[idx][7], ts[idx][8])
