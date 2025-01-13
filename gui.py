import re
import tkinter as tk
import requests
from bs4 import BeautifulSoup

companyUrl = ''
# Old regex without negative look-ahead
#phonePattern = r"\+1\s?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
#phonePattern_include800s = r"(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999)\+1\s?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999)\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
phonePattern = r"(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999|\+1[-. ]?\(?8|\(?8)\+1\s?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999|\+1[-. ]?\(?8|\(?8)\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
contactButtonPattern = r"(?i)\bContact(?: Us)?\b"
userURL = ''
numberList = []
visitedSites = []

class GUI:
    def __init__(self, name):
        self.name = name
        self.startTK()
    
    def greet(self):
        return "Hello, my name is " + self.name

    def startTK(self):
        # Create main window
        window = tk.Tk()
        window.geometry("500x200")
        window.title("Hello World")

        # Create a label
        label = tk.Label(window, text="Welcome. Enter the site to scrape below")
        label.pack(padx=200, pady=5)

        # Create entry box
        entry = tk.Entry(window, width=50)
        entry.pack(padx=10, pady=10)

        # Create a button
        button = tk.Button(window, text="Search", command=lambda: self.executeSearch(entry.get()))
        button.pack(padx=20, pady=20)

        # Start the GUI
        window.mainloop()

    # Get user input
    def getUserInput(self, url):
        print("You entered: ", url)


    # Look for phone numbers on main page
    # If nothing, look for a button with text "Contact" or "Contact Us"
    # Follow the url for the contact button and re-run the phone number search from there
    def executeSearch(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
        global companyUrl
        companyUrl = url
        response = requests.get(url, headers=headers)

        # Look for the phone number within the response
        self.searchForPhone(response.text)

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
                    if 'http' in link['href']:
                        companyUrl = link['href']
                    else:
                        companyUrl += link['href']

                    # Ensure we haven't already visited this site
                    if link['href'] not in visitedSites:
                        response = requests.get(companyUrl, headers=headers)
                        # Look for the phone number within the response
                        self.searchForPhone(response.text)

                    # Add site to list of searched sites
                    visitedSites.append(link['href'])
                    print(visitedSites)


    # Method to search for phone number within the given html
    def searchForPhone(self, htmlText):
        print("Looking for phone numbers at: " + companyUrl)

        # One possible issue is a very 'modern' website had 3174750960 listed as the phone number
        # Could we add a check for an html element whose TEXT matches this format as well?
        matches = re.findall(phonePattern, htmlText)
        for number in matches:
            if (number not in numberList):
                numberList.append(number)
                
        print(numberList)