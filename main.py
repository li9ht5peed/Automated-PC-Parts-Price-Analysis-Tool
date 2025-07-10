from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# geckodriver_path = "C:\geckodriver"
# browser = webdriver.Firefox(geckodriver_path)
browser = webdriver.Firefox()

browser.get("http://www.python.org")
assert "Python" in browser.title

event_times = browser.find_elements(By.CSS_SELECTOR, ".event-widget div ul li time")
event_names = browser.find_elements(By.CSS_SELECTOR, ".event-widget div ul li a")
# for time in event_times:
#     print(time.text)

# events = {event_time.text: event_name.text for event_time, event_name in zip(event_times, event_names)}
# events = {"time": event_time.text, "name": event_name.text for event_time, event_name in zip(event_times, event_names)}
events = {}
for index in range(len(event_times)):
    events[index] = {
        "time": event_times[index].text,
        "name": event_names[index].text
    }
print(events)

browser.quit()
