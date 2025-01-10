# This program simply tests some regex patterns for phone numbers
import re
import requests
from bs4 import BeautifulSoup

companyUrl = ''
# Old regex without negative look-ahead
#phonePattern = r"\+1\s?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
phonePattern = r"(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999)\+1\s?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|(?!\+?1?[-. ]?\(?123\)?[-. ]?456[-. ]?7890|\+?1?[-. ]?\(?999\)?[-. ]?999[-. ]?9999)\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}"
contactButtonPattern = r"\bContact(?: Us)?\b"
numberList = []

def main():
    # Look for phone numbers on main page
    # If nothing, look for a button with text "Contact" or "Contact Us"
    # Follow the url for the contact button and re-run the phone number search from there
    global companyUrl 
    companyUrl = 'https://idsfulfillment.com/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
    response = requests.get(companyUrl, headers=headers)
    #print(response.text)

    # Look for the phone number within the response
    searchForPhone(response.text)

    # After first search for phones, if blank numberList, look for contact button
    if len(numberList) == 0:
        # Parse the HTML content of the response
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Make a list of all link elements with href
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            # Find the contact button if it exists
            if link(text=re.compile(contactButtonPattern)):
                if 'http' in link['href']:
                    companyUrl = link['href']
                else:
                    companyUrl += link['href']

                print('link: ' + link['href'])
                response = requests.get(companyUrl, headers=headers)
                # Look for the phone number within the response
                searchForPhone(response.text)



# Method to search for phone number within the given html
def searchForPhone(htmlText):
    print("Looking for phone numbers at: " + companyUrl)
    #print("\n\n\n\n")
    #print(htmlText)
    # One possible issue is a very 'modern' website had 3174750960 listed as the phone number
    # Could we add a check for an html element whose TEXT matches this format as well?
    matches = re.findall(phonePattern, htmlText)
    for number in matches:
        if (number not in numberList):
            numberList.append(number)
            
    print(numberList)


if __name__ == '__main__':
    main()