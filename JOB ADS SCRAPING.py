# -*- coding: utf-8 -*-
"""
Created on Thu May 30 14:16:30 2024

@author: ADMIN
"""

import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# Function to scrape Indeed for data analyst and data science jobs in Kenya
def scrape_indeed_jobs():
    url = "https://www.indeed.com/jobs?q=data+analyst+or+data+scientist&l=Kenya&fromage=30"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []

    for job_card in soup.find_all('div', class_='jobsearch-SerpJobCard'):
        title = job_card.find('a', class_='jobtitle').text.strip()
        company = job_card.find('span', class_='company').text.strip()
        location = job_card.find('div', class_='location').text.strip()
        date_posted = job_card.find('span', class_='date').text.strip()

        if '30+' not in date_posted:  # Filter out jobs older than 30 days
            job_url = "https://www.indeed.com" + job_card.find('a', class_='jobtitle')['href']
            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'date_posted': date_posted,
                'url': job_url
            })

    return jobs

# Function to scrape LinkedIn for data analyst and data science jobs in Kenya
def scrape_linkedin_jobs():
    url = "https://www.linkedin.com/jobs/search?keywords=Data%20Analyst%20or%20Data%20Scientist&location=Kenya&f_TPR=r2592000&position=1&pageNum=0"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []

    for job_card in soup.find_all('li', class_='result-card job-result-card result-card--with-hover-state'):
        title = job_card.find('h3', class_='result-card__title').text.strip()
        company = job_card.find('h4', class_='result-card__subtitle').text.strip()
        location = job_card.find('span', class_='job-result-card__location').text.strip()
        date_posted = job_card.find('time')['datetime']
        date_posted = datetime.strptime(date_posted, "%Y-%m-%d").date()

        if datetime.now().date() - date_posted <= timedelta(days=30):
            job_url = job_card.find('a', class_='result-card__full-card-link')['href']
            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'date_posted': date_posted.strftime("%Y-%m-%d"),
                'url': job_url
            })

    return jobs

# Function to send email with job listings
def send_email(job_listings, recipient_email):
    sender_email = "youremail@example.com"
    sender_password = "yourpassword"

    message = MIMEMultipart("alternative")
    message["Subject"] = "New Data Analyst/Data Science Jobs in Kenya"
    message["From"] = sender_email
    message["To"] = recipient_email

    html_content = "<h1>New Job Listings</h1>"
    for job in job_listings:
        html_content += f"<p><b>{job['title']}</b><br>{job['company']} - {job['location']}<br>{job['date_posted']}<br><a href='{job['url']}'>Apply here</a></p><hr>"

    message.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    indeed_jobs = scrape_indeed_jobs()
    linkedin_jobs = scrape_linkedin_jobs()
    all_jobs = indeed_jobs + linkedin_jobs

    if all_jobs:
        send_email(all_jobs, "recipient@example.com")
    else:
        print("No new job listings found.")
