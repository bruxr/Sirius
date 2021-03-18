import requests
from datetime import datetime
from dateutil.parser import parse
from bs4 import BeautifulSoup

def get_jinio_parcel(code):
    """Retrieve details about a parcel carried by Jinio"""
    
    url = f'https://jinio.com.ph/tracker?tracking_no={code}'
    params = { 'c': 'app' }
    headers = { 'C_JX': 'response' }
    res = requests.post(data=params, headers=headers, url=url)
    
    if ('Tracking No. doesn\'t exist!' in res.text):
        raise RuntimeError(f'Jinio parcel does not exist')

    data = {}
    for item in res.json()['c_js']:
        if 'i' in item:
            data[item['i']] = item['c']
    
    now = datetime.now()
    start_date = parse(data['estimatedFromDate'] + ' ' + str(now.year))
    end_date = parse(data['estimatedToDate'] + ' ' + str(now.year))

    if start_date > end_date:
        end_date = parse(data['estimatedToDate'] + ' ' + str(now.year - 1))

    result = {}
    result['start'] = start_date
    result['end'] = end_date

    result['tracking'] = []
    soup = BeautifulSoup(data['tracker_log_list'], 'html.parser')
    nodes = soup.find_all('li', class_='columns')
    for node in nodes:
        date_nodes = node.find_all('div', class_='node')
        if (len(date_nodes) == 0):
            continue

        date = parse(date_nodes[0].get_text() + ' ' + str(now.year))
        if start_date > date:
            date = parse(date_nodes[0].get_text() + ' ' + str(now.year - 1))
        
        info_text = ': '.join(str(node).split('<br/>')[1:]).replace('</li>', '')
        result['tracking'].append({
            'date': date,
            'message': info_text,
        })

    return result
