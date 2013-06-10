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
    timetext = timetext.replace('m', '').replace('s', '')
    timenums = timetext.split()
    mins, secs = timenums
    secs = 60 * int(mins) + int(secs)
    return secs


def main(browser):
    browser.implicitly_wait(15)
    endtime_el = browser.find_element_by_css_selector("span.vi-tm-left")
    endtime_text = endtime_el.text
    secsleft_calced = calc_secs_left(endtime_text)
    hibernate_secs = secsleft_calced - cfg.hibernate_until
    if hibernate_secs > cfg.hibernate_min:
        browser.close()
        print "too long until %s, will hibernate for %d secs" \
            % (endtime_text, hibernate_secs)
        time.sleep(hibernate_secs)

    for _ in xrange(100):
        browser.get(cfg.url)
        timeleft_text = browser.find_element_by_css_selector("span.tmlHt").text
        secs_left_shown = parse_mins_secs_left(timeleft_text)
        print 'secs_left_shown=', secs_left_shown
        secs_left = min(secs_left_shown, secsleft_calced)
        if secs_left <= cfb.bid_when_left:
            print 'Bid!!!'
            break
        else:
            waitfor = secs_left / 2
            print "waiting for: ", waitfor
            time.sleep(waitfor)
            print 'waiting for %d' % waitfor


if __name__ == '__main__':
    browser = webdriver.Firefox()
    browser.implicitly_wait(15)
    try:
        main(browser)
    finally:
        browser.close()
