import requests
from bs4 import BeautifulSoup
import re

email = ""
password = ""
login_url = "https://www.dhiraagu.com.mv/ocs/login.aspx"
service_url = "https://www.dhiraagu.com.mv/ocs/service_details.aspx"
headers = {'Content-Type' : 'application/x-www-form-urlencoded; charset=utf-8',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'}

def login(session, email, password):
    payload = { 'rm' : 'rapPanel|imgbtn_Login',
            'rm_TSM' : '',
            '__EVENTTARGET' : 'imgbtn_Login',
            '__EVENTARGUMENT' : '',
            '__VIEWSTATE' : '',
            '__VIEWSTATEGENERATOR' : '',
            '__EVENTVALIDATION' : '',
            'radTxt_nama' : '',
            'radTxt_nama_ClientState': '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}',
            'radTxt_laluan' : '',
            'radTxt_laluan_ClientState' : '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}',
            'w_ClientState' : '',
            '__ASYNCPOST' : 'true',
            'RadAJAXControlID' : 'rap' }
    
    service_numbers = []
    
    try:
        html = session.get(login_url).text
    except:
        return
    
    soup = BeautifulSoup(html, 'html.parser')
    payload['__VIEWSTATE'] = soup.find_all('input')[1]['value']
    payload['__VIEWSTATEGENERATOR'] = soup.find_all('input')[2]['value']
    payload['__EVENTVALIDATION'] = soup.find_all('input')[3]['value']
    payload['radTxt_nama'] = email
    payload['radTxt_laluan'] = password
    response = session.post(login_url, headers=headers, data=payload)
    
    try:
        html = session.get(service_url).text
    except:
        return
    
    soup = BeautifulSoup(html, 'html.parser')
    for n in soup.find_all(class_="rcbItem")[1:]:
        service_numbers.append(n.text)
    
    instance = soup.find_all('input')[1:4]
    
    return response, service_numbers, instance
    
def service_details(session, instance, service_number):
    payload = { 'ctl00$RadScriptManager1' : 'ctl00$ContentPlaceHolder1$ctl00$ContentPlaceHolder1$RAPPanel|ctl00$ContentPlaceHolder1$radcb_ServiceNo',
                'ctl00_RadScriptManager1_TSM' : '',
                '__EVENTTARGET' : 'ctl00$ContentPlaceHolder1$radcb_ServiceNo',
                '__EVENTARGUMENT' : '{"Command":"Select","Index":1}',
                '__VIEWSTATE' : '',
                '__VIEWSTATEGENERATOR' : '',
                '__EVENTVALIDATION' : '',
                'ctl00$hf_mobile_BillType' : '',
                'ctl00$ContentPlaceHolder1$hf_cache': '',
                'ctl00$ContentPlaceHolder1$hf_hideBalanceInfo' : '',
                'ctl00$ContentPlaceHolder1$hf_usage_hourly' : '',
                'ctl00$ContentPlaceHolder1$hf_usage_daily' : '',
                'ctl00$ContentPlaceHolder1$hf_usage_monthly' : '',
                'ctl00$ContentPlaceHolder1$hf_usage_type' : '',
                'ctl00$ContentPlaceHolder1$hf_usage_service_no' : '',
                'ctl00$ContentPlaceHolder1$hf_usage_service_no_exist' : '',
                'ctl00$ContentPlaceHolder1$hf_graph' : '',
                'ctl00$ContentPlaceHolder1$radcb_ServiceNo' : '',
                'ctl00_ContentPlaceHolder1_radcb_ServiceNo_ClientState' : '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}',
                'ctl00$ContentPlaceHolder1$radtb_Feedback' : 'Enter your feedback here',
                'ctl00_ContentPlaceHolder1_radtb_Feedback_ClientState' : '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":"Enter your feedback here"}',
                'ctl00$ContentPlaceHolder1$RadCaptcha1$CaptchaTextBox' : '',
                'ctl00_ContentPlaceHolder1_RadCaptcha1_ClientState' : '',
                'ctl00$hf_BillType' : '',
                '__ASYNCPOST' : 'true',
                'RadAJAXControlID' : 'ctl00_ContentPlaceHolder1_RAP'}
    
    payload['__VIEWSTATE'] = instance[0].get('value')
    payload['__VIEWSTATEGENERATOR'] = instance[1].get('value')
    payload['__EVENTVALIDATION'] = instance[2].get('value')
    payload['ctl00$ContentPlaceHolder1$radcb_ServiceNo'] = service_number
    payload['ctl00_ContentPlaceHolder1_radcb_ServiceNo_ClientState'] = '{"logEntries":[],"value":"' + service_number + '","text":"' + service_number + '","enabled":true,"checkedIndices":[],"checkedItemsTextOverflows":false}'
    
    response = session.post(service_url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    details = {}
    
    details['serviceno'] = soup.find(id="ctl00_ContentPlaceHolder1_ltr_serviceno").text
    details['package'] = soup.find(id="ctl00_ContentPlaceHolder1_ltr_package").text
    details['status'] = soup.find(id="ctl00_ContentPlaceHolder1_div_status").text.strip()[8:]
    
    for i, d in enumerate(soup.find_all(class_=re.compile('^data\-box\-type\-[0-9]+')), start=1):
        details['data'+str(i)] = {}
        details['data'+str(i)]['type'] = d.find(class_="data-type").text
        details['data'+str(i)]['expiry'] = d.find(class_="data-expire").text[11:]
        details['data'+str(i)]['unit'], details['data'+str(i)]['used'], details['data'+str(i)]['total']= parse_data(d.find(class_="data-total").text)
        
    return response, details

def parse_data(text):
    if re.search(r'[MGT]B', text):
        unit = re.findall(r'[MGT]B', text)[0]
        used = re.findall(r'(\d+\.?\d*) [MGT]B', text)[0]
        total = re.findall(r'(\d+\.?\d*) [MGT]B', text)[-1]
    elif "min" in text:
        unit = "min"
        used = re.findall(r'(\d+) min', text)[0]
        total = re.findall(r'(\d+) min', text)[-1]
    elif "SMS" in text:
        unit = "SMS"
        if "left" in text:
            used = "0"
            total = total = re.findall(r'(\d+) SMS', text)[0]
        elif "used" in text:
            used = re.findall(r'(\d+) SMS', text)[0]
            total = re.findall(r'(\d+) SMS', text)[-1]
    
    return unit, used, total

