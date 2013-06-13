from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from datetime import datetime
import ebaybidder_cfg as cfg
from dbg import set_trace
import time
import re


def calc_secs_left(endtime_text):
    endtime_str = endtime_text.replace('(', '').replace(' AEST)', '')
    endtime = datetime.strptime(endtime_str, "%d %b, %Y %H:%M:%S")
    timeleft = endtime - datetime.today()
    secsleft = timeleft.total_seconds()
    return secsleft


def parse_time_text(timetext):
    matches = re.split('[d|h|m|s]', timetext)
    nums = [int(m.strip()) for m in matches if m]
    padded = []
    for _ in range(len('dhms') - len(nums)):
        padded.append(0)
    padded.extend(nums)
    return padded


def convert2secs(time_pieces):
    total_secs = 0
    for pair in zip([24*60*60, 60*60, 60, 1], time_pieces):
        total_secs += pair[0] * pair[1]
    return total_secs


def read_calc_verify_timeleft():
    endtime_el = browser.find_element_by_css_selector("span.vi-tm-left")
    endtime_text = endtime_el.text
    secsleft_calced = calc_secs_left(endtime_text)
    print 'secsleft_calced=', secsleft_calced

    timeleft_text = browser.find_element_by_css_selector("span.tmlHt").text
    time_pieces = parse_time_text(timeleft_text)
    secsleft_shown = convert2secs(time_pieces)
    print 'secsleft_shown=', secsleft_shown

    assert abs(secsleft_calced - secsleft_shown) < 100, \
        'time left shown and calculated mismath!'
    return min(secsleft_calced, secsleft_shown), endtime_text


def read_price():
    price_el = browser.find_element_by_id('w1-15-_bidPrice')
    price_text = price_el.text.strip()
    m = re.search('.+\$(\d+\.\d\d)', price_text)
    if m:
        price = float(m.groups()[0])
        print 'current price: %s:' % price_text
    else:
        print 'could not parse the price: %s' % price_text
        price = -1
    return price


def bid(browser, maxbid):
    bidbox = browser.find_element_by_id('MaxBidId')
    bidbutton = browser.find_element_by_id('bidBtn_btn')
    bidbox.send_keys(str(maxbid))
    bidbutton.click()
    # bidbox2 = browser.find_element_by_id('w1-24-_enter_val')
    bidbox2 = browser.find_element_by_css_selector("div.maxbidinput input[type='text']")
    # bidbutton2 = browser.find_element_by_id('w1-24-_place_btn')
    bidbutton2 = browser.find_element_by_css_selector("table.btnLnk input[type='button']")
    bidbox2.send_keys(str(maxbid))
    bidbutton2.click()
    set_trace()


def main(browser):
    browser.get(cfg.url)
    secsleft, endtime_text = read_calc_verify_timeleft()
    hibernate_secs = secsleft - cfg.hibernate_until
    if hibernate_secs > cfg.hibernate_min:
        print "too long until %s, will hibernate for %d mins" \
            % (endtime_text, hibernate_secs / 60)
        time.sleep(hibernate_secs)
        print "waking up!"
        browser.get(cfg.url)
        secsleft, endtime_text = read_calc_verify_timeleft()

    for _ in xrange(100):
        secsleft_calced = calc_secs_left(endtime_text)
        secs2bid = secsleft_calced - cfg.bid_when_left
        # TODO check, print current price
        price = read_price()
        maxprice = float(cfg.maxbid)
        if price > maxprice:
            print 'current price=%.2f is already higher that max bid=%.2f' \
                % (price, maxprice)

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
    finally:
        browser.close()
