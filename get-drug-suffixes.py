import requests
from bs4 import BeautifulSoup

url = "https://denalirx.com/drug-prefix-root-and-suffix/"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
drug_suffixes = []
for row in soup.find_all('tr'):
    # get only first td
    for cell in row.find_all('td'):
        drug_suffixes.append(cell.text.split(';')[0].replace('-', ''))
        break
# remove -, split ; and get only first word
# remove duplicates
drug_suffixes = list(set(drug_suffixes))
print(drug_suffixes)
