import cfscrape
from bs4 import BeautifulSoup
import requests
import json

url = "https://www.pikiran-rakyat.com/"

# headers = {
#     'user-agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
# }
# req = scraper.get(url, headers=headers)


# Using this because my ip got blocked by cloudflare
scraper = cfscrape.create_scraper()

# List to store the extracted data
data_json = []

req = scraper.get(url)

soup = BeautifulSoup(req.text, 'html.parser')

section = soup.find('section', class_='most mt2 clearfix')

# Check if section exist
if section:
    #Find all most popular item in section
    items = section.find_all('div', class_='most__item')
    
    for item in items:
        most_right = item.find('div', class_='most__right')
        titles = item.find('h2', class_='most__title').text
        most_link = most_right.find('a', class_='most__link')

        #Check the item link and get the href
        if most_link:
            link_url = most_link['href']

            link_req = scraper.get(link_url)

            link_soup = BeautifulSoup(link_req.text, 'html.parser')

            # Find the article content within the link
            link_content = link_soup.find('article', class_='read__content clearfix')

            # Extract text from paragraphs in the article content
            link_p = link_content.find_all('p')
            paragraphs = [p.get_text(strip=True) for p in link_p]
            link_content_text = ' '.join(paragraphs)

            # Find the paging content within the link
            paging_content = link_soup.find('div', class_='paging paging--article clearfix')

            # Check if the article has a paging
            if paging_content:

                pages = paging_content.find_all('div', class_='paging__item')

                # Loop through each page
                for page in pages:
                    page_link = page.find('a', class_='paging__link')
                    page_url = page_link['href']
                    
                    # Check if the page URL is the first page or not
                    if page_url == "#":
                        
                        # Remove the title 'Pikiran Rakyat -' in every first of the article content
                        link_content_text = link_content_text[16:]

                        # Create a dictionary with extracted data
                        item_json ={
                            'title' : titles,
                            'content' :link_content_text,
                            'page': page_link.text,
                            'url' : link_req.url
                        }

                        # Append the dictionary to the data list
                        data_json.append(item_json)

                        # Write the data to JSON
                        with open('output.json', 'w', encoding='utf-8') as json_file:
                            json.dump(data_json, json_file, ensure_ascii=False, indent=2)
                    else:
                        # Go to the next page
                        next_req = scraper.get(page_url)
                        next_soup = BeautifulSoup(next_req.text, 'html.parser')

                        next_link_content = next_soup.find('article', class_='read__content clearfix')

                        # Extract text from paragraphs in the article content
                        next_link_p = next_link_content.find_all('p')
                        next_paragraphs = [p.get_text(strip=True) for p in next_link_content]
                        next_link_content_text = ' '.join(next_paragraphs)

                        # Create a dictionary with extracted data
                        item_json ={
                            'title' : titles,
                            'content' :next_link_content_text,
                            'page': page_link.text,
                            'url' : next_req.url
                        }

                        # Append the dictionary to the data list
                        data_json.append(item_json)

                        # Write the data to JSON
                        with open('output.json', 'w', encoding='utf-8') as json_file:
                            json.dump(data_json, json_file, ensure_ascii=False, indent=2)
        else:
            print("Link not found in item.")

else:
    print("Section not found.")

print("Success!")