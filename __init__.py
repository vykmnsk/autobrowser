import os
from selenium import webdriver


chromedriver_path = "/Users/bear/dev/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver_path
driver = webdriver.Chrome(chromedriver_path)
