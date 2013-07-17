import os, sys, re, time
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import ebaybidder_cfg as cfg
from dbg import set_trace
from selenium.webdriver.support.ui import WebDriverWait



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


def time2secs(time_pieces):
    total_secs = 0
    for pair in zip([24*60*60, 60*60, 60, 1], time_pieces):
        total_secs += pair[0] * pair[1]
    return total_secs


def secs2time(total_secs):
    hrs = int(total_secs // 3600)
    mins = int(total_secs % 3600 // 60)
    secs = int(total_secs % 3600 % 60)
    return hrs, mins, secs


def verify_bidding_active():
    try:
        msgbox = browser.find_element_by_css_selector('div.msgPad span')
    except:
        return  # good, no message
    msg = msgbox.text
    print 'eBay message: {0}'.format(msg)
    if msg.lower().find('bidding has ended') >= 0:
        sys.exit(0)


def read_calc_verify_timeleft():
    endtime_el = browser.find_element_by_css_selector("span.vi-tm-left")
    endtime_text = endtime_el.text
    secsleft_calced = calc_secs_left(endtime_text)
    print 'secsleft_calced={:.1f}'.format(secsleft_calced)

    timeleft_text = browser.find_element_by_css_selector("span.tmlHt").text
    time_pieces = parse_time_text(timeleft_text)
    secsleft_shown = time2secs(time_pieces)
    print 'secsleft_shown=', secsleft_shown

    assert abs(secsleft_calced - secsleft_shown) < 100, \
        'time left shown and calculated mismath!'
    return min(secsleft_calced, secsleft_shown), endtime_text


def read_price():
    try:
        price_el = browser.find_element_by_css_selector(
            "div.actPanel span[itemprop='price']")
    except:
        print '!!! could not read current price'
    price_text = price_el.text.strip().replace(',', '')
    m = re.search(r'\d+\.\d\d', price_text)
    if m:
        price = float(m.group())
        print 'current price: {}:'.format(price)
    else:
        print '!!! could not parse price: {}'.format(price_text)
        price = -1
    return price


def login_info():
    usr = os.environ.get('EBAYUSR', None)
    pwd = os.environ.get('EBAYPWD', None)
    if not usr or not pwd:
        print 'CANNOT LOGIN: env vars EBAYUSR and/or EBAYPWD not set!'
    return usr, pwd


def login(browser, usr, pwd):
    print 'Logging in...'
    signin_link = browser.find_element_by_link_text('Sign in')
    signin_link.click()

    def login_form(browser):
        usr_textbox = browser.find_element_by_id('userid')
        pwd_textbox = browser.find_element_by_id('pass')
        sign_btn = browser.find_element_by_id('sgnBt')
        return usr_textbox, pwd_textbox, sign_btn

    wait = WebDriverWait(browser, 20)
    usr_textbox, pwd_textbox, sign_btn = wait.until(login_form)

    usr_textbox.send_keys(usr)
    pwd_textbox.send_keys(pwd)
    sign_btn.submit()
    print 'login info submitted.'
    return


def hibernate(secs):
    if secs > cfg.hibernate_minimum:
        print "hibernating for {}h {}m {}s...".format(*secs2time(secs))
        time.sleep(secs)
        print "waking up!"


def bid(browser, maxbid):
    print 'Bid {0}!!!'.format(maxbid)
    try:
        bid_box = browser.find_element_by_id('MaxBidId')
        bid_btn = browser.find_element_by_id('bidBtn_btn')
        bid_box.send_keys(str(maxbid))
        bid_btn.click()
        confirm_btn = browser.find_element_by_css_selector("table.btnLnk input[type='button']")
        confirm_btn.click()
    except Exception, e:
        print 'Exception happened: ', e
    else:
        print 'bid placed'
        print 'message: ', read_msg(browser)


def read_msg(browser):
    msg = ''
    try:
        msg_el = browser.find_element_by_css_selector('div.pb div.sm-t div')
        msg = msg_el.text
    except Exception, e:
        print 'could not read message coz: ', e
    return msg


def main(browser):
    browser.get(cfg.url)
    verify_bidding_active()
    usr, pwd = login_info()
    secsleft, endtime_text = read_calc_verify_timeleft()

    timeleft_text = '{}h {}m {}s'.format(*secs2time(secsleft))
    msg = 'All set! Will bid {} in {} {}'
    print msg.format(cfg.maxbid, timeleft_text, endtime_text)

    hibernate(secsleft - cfg.hibernate_until)

    browser.get(cfg.url)
    secsleft, endtime_text = read_calc_verify_timeleft()
    login(browser, usr, pwd)

    for _ in xrange(1000):
        secsleft_calced = calc_secs_left(endtime_text)
        secs2bid = secsleft_calced - cfg.bid_when_left
        price = read_price()
        if price > float(cfg.maxbid):
            warn = '!!! bid will fail: price={:.2f} > maxbid={:.2f}'
            print warn.format(price, cfg.maxbid)
        if secs2bid > 1:
            waitfor = secs2bid / 2
            print "{:.1f} until bid...".format(secs2bid)
            time.sleep(waitfor)
        else:
            bid(browser, cfg.maxbid)
            return

    sys.exit('Fatal error! loop is exhausted, perhaps indefinite...')


if __name__ == '__main__':
    browser = webdriver.Firefox()
    browser.implicitly_wait(15)
    try:
        main(browser)
        print 'Done.'
        set_trace()
    finally:
        browser.close()
