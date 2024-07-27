import os
import json
import requests
from bs4 import BeautifulSoup
import openai
from dotenv import load_dotenv
import re
from flask import Flask, jsonify


class Event:
    def __init__(self, source_url, name,location,time,start_date,end_date, description):
        self.source_url = source_url
        self.name = name
        self.location = location
        self.time=time
        self.start_date=start_date
        self.end_date=end_date
        self.description=description
    def __hash__(self):
        # Define a custom hash function
        return hash((self.source_url, self.name, self.location,self.time,self.start_date,self.end_date,self.description))

    def __eq__(self, other):
        # Ensure the equality check considers the same attributes as the hash function
        return (self.source_url, self.name, self.location,self.time,self.start_date,self.end_date,self.description) == (other.source_url, other.name, other.location,other.time,other.start_date,other.end_date,other.description)

    def to_dict(self):
        return {
            'source_url': self.source_url,
            'name': self.name,
            'location': self.location,
            'time': self.time,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'description':self.description
        }


# Set OpenAI API key 
#openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to interact with OpenAI's GPT-3.5 model for chat completions with tools
def openai_platform_code(html_content, tools):
    # Call OpenAI's ChatCompletion API with tools
    openai.api_key = ''

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'system', 'content': "Please ensure that all the following properties are required and provided: [source_url], [name], [location], [time], [start_date], [end_date], [description]"},
            {"role": "user", "content": html_content}
        ],
        tools=tools,
        tool_choice="auto",
    )
    return response


# function to call with openai
def extract_events_data(events):
  print("Extracted events Data")
  print(events)

  for event in events:
    print(event['source_url'])
    print(event['name'])
    print(event['location'])  
    print(event['time'])
    print(event['start_date'])
    print(event['end_date'])
    print(event['description'])
    print("---")
  return {
    'status': 'saved' 
  }



# Function to extract event information through OpenAI
def extract_information_through_openai(html_content):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "extract_events_data",
                "description": "This function extracts essential details about an event from a given source URL using AI.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "events":{
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    "source_url": {
                                        "type": "string",
                                        "description": "The URL of the webpage from which event information is to be extracted."
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "The official title or name of the event."
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "The venue or place where the event will take place. This can include the street address, zone, room number, or hall number."
                                    },
                                    "time": {
                                        "type": "string",
                                        "description": "The specific start and end time of the event, if available. Include both the start and end times in a clear format, such as '10:00 AM - 12:00 PM'. If only one time is available (e.g., a single time slot), provide that time."
                                    },
                                    "start_date": {
                                        "type": "string",
                                        "description": "The commencement date of the event."
                                    },
                                    "end_date": {
                                        "type": "string",
                                        "description": "The concluding date of the event."
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "The concluding description of the event."
                                    }
                                }
                            }
                        }
                    },
                    "required": ["source_url", "name", "location", "time", "start_date", "end_date", "description"]
                }
            }
        }
    ]
     #while structure used to ensure that openai return a correct response containing relevent data

    # Send the HTML content to OpenAI to extract information
    response = openai_platform_code(html_content, tools)
    #print('response message=',response)
    response_message = response['choices'][0]['message']['tool_calls'][0]['function']['arguments']
    #this code used to convert the message from response from string to json structure
    jsonEvents=json.loads(response_message)

    

    events=[]
    #this code to extract and print events' details from the obtained events with json structure
    if list(jsonEvents['events'][0].values())==['', '', '', '', '', '', ''] or 'events' not in jsonEvents.keys():
       raise Exception("Unrecognized scraped urls")
    else:
        
        i = 1
        for event in jsonEvents['events']:
            new_event=Event(event['source_url'],event['name'],event['location'],event['time'],event['start_date'],event['end_date'],event['description'])
            events.append(new_event.to_dict())
            i += 1
        
      
    return events

# Function to get URLs
def getURLs():
    urls = []  # List of Dictionaries, each one contains info about a different website
    urls.append({'base_url':'https://visitqatar.com/intl-en/events-calendar/all-events','pagination':'?page=','nb_pages':0,'tag':'div','class':'cmp-event-listing__result'})
##    urls.append({'base_url':'https://www.iloveqatar.net/events','pagination':'/p','nb_pages':1,'tag':'div','class':'article-block _events'})
##    urls.append({'base_url':'https://www.marhaba.qa/events','pagination':'/photo/page/','nb_pages':2,'tag':'div','class':'tribe-events-single-event-title'})
##    urls.append({'base_url':'https://www.qatartourism.com/en/business-events/calendar-of-business-events','pagination':'','nb_pages':0,'tag':'li','class':'cmp-event-list__item'})
##    urls.append({'base_url':'https://www.qf.org.qa/events','pagination':'','nb_pages':0,'tag':'div','class':'card__wrapper'})
##    urls.append({'base_url':'https://10times.com/events','pagination':'','nb_pages':0,'tag':'tr','class':'row py-2 mx-0 mb-3 bg-white deep-shadow event-card event_1053694 '})
##    urls.append({'base_url':'https://allevents.in/doha/all','pagination':'?page=','nb_pages':2,'tag':'li','class':'event-card event-card-link'})
##    urls.append({'base_url':'https://www.eventbrite.com/d/online/all-events/','pagination':'','nb_pages':0,'tag':'div','class':'Stack_root__1ksk7'})
    return urls

# Function to get events
def getEvents(url, tag, css_class):
    # Send a GET request to the URL
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"}
    response = requests.get(url, headers=headers)
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find all the events
    events = soup.find_all(tag, class_=css_class)
    return events

# Function to scrape a single page based on a tag and class according to page structure inspection
def scrape_page(url, tag, css_class):
    print('Scraped url: ',url, '\n')
    # Get the events
    events = getEvents(url, tag, css_class)
    return events

# Function to scrape all pages of a site
def scrape_all_pages(site):
    all_data = []
    base_url = site['base_url']
    pagination = site['pagination']
    
    if site['nb_pages'] == 0:
        all_data.append(scrape_page(base_url, site['tag'], site['class']))
    else:
        all_data.append(scrape_page(base_url, site['tag'], site['class']))
        for page_number in range(2, site['nb_pages'] + 1):
            url = f"{base_url}{pagination}{page_number}"
            page_data = scrape_page(url, site['tag'], site['class'])
            if page_data is None:
                break
            all_data.extend(page_data)
    return all_data

# Function to scrape all sites
def scrapeAllSites(sites):
    print('Scraping websites: Tarted...')
    allHTMLdata = []
    for site in sites:
        html_data = scrape_all_pages(site)
        allHTMLdata.extend(html_data)
    print('Scraping websites: Finished.')
    return allHTMLdata

# Function to clean HTML 
def remove_style_and_class(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    
    for img_tag in soup.find_all('img'):
        img_tag.decompose()
 
    # Iterate over all tags in the HTML
    for tag in soup.find_all(True):  # True finds all tags
        if 'style' in tag.attrs:
            del tag.attrs['style']
        if 'class' in tag.attrs:
            del tag.attrs['class']
        if 'alt' in tag.attrs:
            del tag.attrs['alt']
        if 'sizes' in tag.attrs:
            del tag.attrs['sizes']
        if 'src' in tag.attrs:
            del tag.attrs['src']
        if 'for' in tag.attrs:
            del tag.attrs['for']
        if 'type' in tag.attrs:
            del tag.attrs['type']
        if 'height' in tag.attrs:
            del tag.attrs['height']
        if 'id' in tag.attrs:
            del tag.attrs['id']
            
    # to delete new lines        
    cleaned_html = str(soup).replace('\n', '')
    # Remove more than two successive spaces
    cleaned_html = re.sub(r'\s{2,}', ' ', cleaned_html)
    return cleaned_html

def html_to_events_json_list(events_html_list):
    event_info=[]
    for event_html in events_html_list:
        cleaned_event_html=remove_style_and_class(str(event_html))
        #prompt added to ensure that openai will return all the requested fields
        prompt="""
        Extract the following events details from the given HTML content:
        - source_url
        - name
        - location
        - time: is in hours not date format
        - start_date
        - end_date
        - description

        HTML Content:"""+ cleaned_event_html + """ Response format:
        {'events':[{
            'source_url': '',
            'name": '',
            'location': '',
            'time':'2pm',
            'start_date':'',
            'end_date':'',
            'description':''
        }]}

        Make sure to include all the required properties in the response and time properties in time not date ended with am or pm only."""
        event_info.extend(extract_information_through_openai(prompt))

        json_event_info = json.dumps(event_info, indent=4)

        save_events_to_json_file(json_event_info)
        
    return event_info

def save_events_to_json_file(events):
    with open('events.json', 'w') as file:
        file.write(events)
        
app = Flask(__name__)

@app.route('/api/getEvents', methods=['GET'])
def get_getEvents():
    try:
        result = html_to_events_json_list(scrapeAllSites(getURLs()))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
        



