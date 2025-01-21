import re
import tkinter as tk
import requests
from tkinter import filedialog
from tkinter import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from pandas import DataFrame
from datetime import datetime

baseURL = ''
searchURL = ''
# Old regex without negative look-ahead
#phonePattern = r"\+1\s?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
#phonePattern_include800s = r"(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999)\+1\s?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999)\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
#phonePattern_exclude_all_800s = r"(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999|\+1[-. ]?\(?8|\(?8)\+1\s?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999|\+1[-. ]?\(?8|\(?8)\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
phonePattern = r"(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999|\+1[-. ]?\(?8|\(?8)\+1\s?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999|\+1[-. ]?\(?8|\(?8)\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
# The following phone pattern only excludes phone numbers starting with 8 and two consecutive numbers
#phonePattern = r"(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999|\+1[-. ]?\(?8(\d)\1|\(?8(\d)\2)\+1\s?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999|\+1[-. ]?\(?8(\d)\1|\(?8(\d)\2)\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
#phonePattern = r"\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
#phonePattern = r"(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999|\+1[-. ]?\(?8(\d)\1|\(?8(\d)\2))(\(?\d{3}\)?)[-.\s]?(\d{3})[-.\s]?(\d{4})"
contactButtonPattern = r"(?i)\bContact(?: Us)?\b"
numberList = []
visitedSites = []
window = tk.Tk()
window.iconbitmap('icon_hd.ico')

class GUI:
    def __init__(self, name):
        self.name = name
        self.startTK()

    def startTK(self):
        # Create main window
        window.geometry("650x275")
        window.title("Company Search")

        # Create a label
        label = tk.Label(window, text="Enter the required info below, then press 'Search'", font='Helvetica 12 bold')
        label.place(relx=0.2, rely=0.1)

        # Create company entry label
        companyLabel = tk.Label(window, text="Company type")
        companyLabel.place(relx=0.25, rely=0.3)

        # Create company type entry box
        companyTypeEntry = tk.Entry(window, width=50)
        companyTypeEntry.place(relx=0.25, rely=0.4)

        # Create state entry label
        stateLabel = tk.Label(window, text="State abbreviation")
        stateLabel.place(relx=0.25, rely=0.5)

        # Create state to search in box
        stateEntry = tk.Entry(window, width=50)
        stateEntry.place(relx=0.25, rely=0.6)

        # Create a button
        button = tk.Button(window, text="Search", command=lambda: self.executeBBBSearch(companyTypeEntry.get(), stateEntry.get()))
        button.place(relx=0.46, rely=0.8)

        # Start the GUI
        window.mainloop()


    # Get user input
    def getUserInput(self, url):
        print("You entered: ", url)

    
    # This method retrieves company information from the BBB website
    def executeBBBSearch(self, companyType, state):
        
        pageNumber = 1
        name_array = []
        number_array = []
        address_array = []
        validSite = True
        while(pageNumber <= 5):
            print("Page number: " + str(pageNumber))
            # Web access setup
            options = Options()
            options.add_argument("--headless=new")
            # Is this what I need to get beautiful soup to work??
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
            options.add_argument(f'user-agent={user_agent}')
            dr = webdriver.Chrome(options=options)

            # Set the base URL for the search
            url = f"https://www.bbb.org/search?page={pageNumber}&sort=Relevance&touched=1&find_country=USA"
            if companyType != '':
                url += '&find_text=' + companyType.replace(' ', '%20')
            if state != '':
                url += '&filter_state=' + state

            # Try to access the site, if failure exit loop
            try:
                dr.get(url)
            except:
                break

            #with open("test.html", "w") as text_file:
            #    text_file.write(dr.page_source)
            #bs = BeautifulSoup(dr.page_source, "html.parser")
            divs = dr.find_elements(By.CLASS_NAME, 'result-card')

            for div in divs:
                try:
                    name = div.find_element(By.CLASS_NAME, 'result-business-name')
                    number = div.find_element(By.CLASS_NAME, 'text-black')
                    address = div.find_element(By.CSS_SELECTOR, 'p.bds-body.text-size-5.text-gray-70')
                    if (name.text not in name_array) and ('advertisement' not in name.text) and (name.text != '') and (number.text != '') and (address.text != ''):
                        name_array.append(name.text)
                        number_array.append(number.text)
                        try:
                            address_array.append(address.text.split("\n")[1])
                        except:
                            address_array.append(address.text)
                except:
                    print("There was an error")
                    print(div.text)
        
            # Increment page number
            pageNumber += 1

        # Set up excel sheet
        df = DataFrame({'Company Name': name_array, 'Phone Number': number_array, 'Address': address_array})
        with filedialog.asksaveasfile(mode='w', defaultextension='.xlsx') as file:
            df.to_excel(file.name)

        window.quit()


# ******** CODE BELOW HERE IS NOT BEING USED AT THE MOMENT ******************


    # Method to search for phone number within the given html
    def searchForPhone(self, htmlText, searchURL):
        print("Looking for phone numbers at: " + searchURL)

        # One possible issue is a very 'modern' website had 3174750960 listed as the phone number
        # Could we add a check for an html element whose TEXT matches this format as well?
        matches = re.findall(phonePattern, htmlText)
        print(matches)
        for number in matches:
            if (number not in numberList):

                numberList.append(number)
                
        print(numberList)
        


    # Look for phone numbers on main companypage
    # If nothing, look for a button with text "Contact" or "Contact Us"
    # Follow the url for the contact button and re-run the phone number search from there
    def executeSearch(self, url):

        # Remove trailing / from url before doing anything else
        if url[len(url) - 1] == "/":
           url = url[0:len(url)-1]

        # Set values
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
        global baseURL
        baseURL = url
        searchURL = url
        try:
            response = requests.get(url, headers=headers)
            #print(response.text)
        except:
            #pass
            return
        
        # Search for phone numbers within the base URL
        #for chunk in response.iter_content(chunk_size=1024):
        self.searchForPhone(response.text, baseURL)
        #self.searchForPhone(url, baseURL)
        

        # After first search for phones, if blank numberList, look for contact button
        if len(numberList) == 0:
            # Parse the HTML content of the response
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Make a list of all link elements with href
            all_links = soup.find_all('a', href=True)

            # Loop through all site links
            for link in all_links:
                # Find the contact button if it exists
                if link(text=re.compile(contactButtonPattern)):
                    if baseURL in link['href']:
                        # Set the search URL
                        searchURL = link['href']

                        # Ensure we haven't already visited this site
                        if searchURL not in visitedSites:
                            response = requests.get(searchURL, headers=headers)
                            # Look for the phone number within the response
                            self.searchForPhone(response.text, searchURL)

                        # Add full link and link minus base URL
                        visitedSites.append(searchURL)
                        visitedSites.append(searchURL.replace(baseURL, ""))
                    else:
                        # Append link to base URL
                        searchURL = baseURL + link['href']

                        # Ensure we haven't already visited this site
                        if link['href'] not in visitedSites:
                            response = requests.get(searchURL, headers=headers)
                            # Look for the phone number within the response
                            self.searchForPhone(response.text, searchURL)

                        # Add search URL to visited sites
                        visitedSites.append(searchURL)