import smtplib
import requests 
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from datetime import date



#get indeed job url
def get_url(job_title, location):
    template = 'https://www.indeed.com/jobs?q={}&l={}&fromage=7'
    url = template.format(job_title, location)
    return url


#reading email settings and the job search string and location from a text file
def read_text_file():  
    global  Email_Address 
    global  Email_Password 
    global  Email_smtp 
    global  Email_port 
    global  Receiver_email
    global  search_job_title
    global  search_job_location
     
     
    filepath =  Path("job_email_settings.txt")
    if filepath.exists():
        with open(filepath) as fp:
         line = fp.readlines() 
    
         Email_Address = line[0].strip()
         Email_Password =  line[1].strip()
         Email_smtp =  line[2].strip()
         Email_port =  line[3].strip()
         Receiver_email = line[4].strip()
         search_job_title = line[5].strip() 
         search_job_location = line[6].strip() 


#email jobs retrieved from indeed
def job_send_email(email_html): 
    
    today = date.today()
    d2 = today.strftime("%B %d, %Y")
    Email_Subject = 'Indeed Jobs for today - ' +  d2

    with smtplib.SMTP(Email_smtp, Email_port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(Email_Address, Email_Password)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Email_Subject
        msg['From'] = Email_Address
        msg['To'] = Receiver_email
    

        Send_Email_Html = MIMEText(email_html, 'html')
        msg.attach(Send_Email_Html)
     
        try:
           smtp.sendmail(Email_Address, Receiver_email, msg.as_string())
           print ('email sent')
           smtp.quit()
        except (Exception) as sendmail_err:  
           print (sendmail_err)



#converting the list of jobs retrieved from indeed to partial html format
def get_job_search(card):
    
    atag = card.h2.a
    indeed_job_title = atag.get('title')
    job_url = 'https://www.indeed.com' + atag.get('href')
    company = card.find('span','company').text.strip()
    job_location = card.find('div', 'recJobLoc').get('data-rc-loc')
    job_summary = card.find('div', 'summary').text.strip()
    post_date = card.find('span','date').text.strip()
 
    
    strz = ( """              
                <p style="font-size: 1.2em;"> <strong style="padding: 0 5px;">Job Title: </strong>""" +  indeed_job_title +
                """<br style="font-size: 1.2em;"> <strong style="padding: 0 5px;">Company: </strong>""" + company +
                """<br style="font-size: 1.2em;"> <strong style="padding: 0 5px;">Location: </strong>""" + job_location +
                """<br style="font-size: 1.2em;"> <strong style="padding: 0 5px;">Summary: </strong>""" + job_summary +
                """<br style="font-size: 1.2em;"> <strong style="padding: 0 5px;">Date: </strong>""" + post_date +
                """<br style="font-size: 1.2em;"> <strong style="padding: 0 5px;">URL: </strong> <a href="""+job_url+""">Click Here</a>"""
                """<br>
                 <br>
                </p>
    """)

    return (strz)



#converting the list of jobs retrieved from indeed to full html format
def full_job_html(html_string): 
        str1 = ""  
        for ele in html_string:  
            str1 += ele   
 
        strz = ( """<html>
          <head></head>
          <body>
            <p>Hello There, <br>
              Jobs for today <br> <br>""" 
              
              + str1 +
               
          """</body>
        </html>""")
        
        return (strz)



#main method 
def main(job_title, location):
    records = []
    url = get_url(job_title, location)
    
    #extract the job data 
    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'html.parser')
        cards = soup.find_all('div', 'jobsearch-SerpJobCard')
        
        for card in cards: 
            record = get_job_search(card)
            records.append(record)
    
        try :
         url  = 'https://www.indeed.com' +  soup.find('a', {'aria-label':'Next'}).get('href')
        except AttributeError: 
          break

    
    job_send_email (full_job_html(records))



read_text_file()
main(search_job_title, search_job_location)










