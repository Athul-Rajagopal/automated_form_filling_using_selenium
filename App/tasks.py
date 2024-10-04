from celery import Celery
from selenium_script import fill_form 

# Configure Celery with Redis as the message broker
app = Celery('form_filling_tasks', broker='redis://localhost:6379/0')

# Define the Celery task to fill the form using Selenium
@app.task
def fill_form_task(user_data):
    
    fill_form(user_data)