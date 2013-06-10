from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import ebaybidder_cfg as cfg
from dbg import set_trace
import time


def calc_secs_left(endtime_text):
    endtime_str = endtime_text.replace('(', '').replace(' AEST)', '')
    endtime = datetime.strptime(endtime_str, "%d %b, %Y %H:%M:%S")
    timeleft = endtime - datetime.today()
    secsleft = timeleft.total_seconds()
    return secsleft


def parse_mins_secs_left(timetext):
    mins, secs = 0, 0
    timetext = timetext.replace('m', '').replace('s', '')
    timenums = timetext.split()
    if len(timenums) == 2:
        mins, secs = timenums
    elif len(timenums) == 1:
        secs = timenums[0]
    secs = 60 * int(mins) + int(secs)
    return secs


def bid(browser, maxbid):
    bidbox = browser.find_element_by_id('MaxBidId')
    bidbutton = browser.find_element_by_id('bidBtn_btn')
    bidbox.send_keys(str(maxbid))
    bidbutton.click()
    bidbox2 = browser.find_element_by_id('w1-28-_enter_val')
    bidbutton2 = browser.find_element_by_id('w1-28-_place_btn')
    bidbox2.send_keys(str(maxbid))
    bidbutton2.click()
    set_trace()

def main(browser):
    browser.get(cfg.url)
    endtime_el = browser.find_element_by_css_selector("span.vi-tm-left")
    endtime_text = endtime_el.text
    secsleft_calced = calc_secs_left(endtime_text)
    hibernate_secs = secsleft_calced - cfg.hibernate_until
    if hibernate_secs > cfg.hibernate_min:
        # browser.close()
        print "too long until %s, will hibernate for %d mins" \
            % (endtime_text, hibernate_secs / 60)
        time.sleep(hibernate_secs)
        print "waking up!"

    browser.get(cfg.url)
    for _ in xrange(100):
        timeleft_text = browser.find_element_by_css_selector("span.tmlHt").text
        secsleft_shown = parse_mins_secs_left(timeleft_text)
        secsleft_calced = calc_secs_left(endtime_text)
        print 'secsleft_shown=', secsleft_shown
        print 'secsleft_calced=', secsleft_calced
        secs_left = min(secsleft_shown, secsleft_calced)
        secs2bid = secs_left - cfg.bid_when_left
        if secs2bid < 2:
            print 'Bid!!!'
            bid(browser, cfg.maxbid)
            break
        else:
            waitfor = secs2bid / 2
            print "napping for: ", waitfor
            time.sleep(waitfor)


if __name__ == '__main__':
    browser = webdriver.Firefox()
    browser.implicitly_wait(15)
    try:
        main(browser)
    except:
        browser.close()
