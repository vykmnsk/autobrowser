from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from chromedriver import chromedriver_path
from selenium.webdriver.support.ui import WebDriverWait
import cfg
# from dbg import set_trace
import time


def main(driver):
    driver.implicitly_wait(15)
    wait = WebDriverWait(driver, 15)

    driver.get(cfg.url)
    driver.find_element_by_link_text(cfg.category).click()
    navigateMenu(driver, cfg.menu_vic)
    setMinMax(driver, 250, 340)

    def loaded(driver):
        el = driver.find_element_by_id('srch-area')
        srch_val = el.get_attribute('value')
        return srch_val == expected

    for menu_area in cfg.menu_areas:
        navigateMenu(driver, cfg.menu_melb)
        expected = cfg.menu_melb[0] + ', VIC'
        wait.until(loaded)

        navigateMenu(driver, menu_area)
        expected = menu_area[-1] + ', VIC'
        wait.until(loaded)

        sort(driver, by='Cheapest')
        wait.until(loaded)

        time.sleep(3)
        #paginate(driver, 100)
        items = read_items(driver)
        print_items(driver, menu_area, sorted(items))

    print_end()


def navigateMenu(driver, menu):
    for mitem in menu:
        mitem = mitem.strip()
        wait = WebDriverWait(driver, 10)
        places = wait.until(find_places_box, driver)
        places.find_element_by_link_text(mitem).click()


def find_places_box(driver):
    menuboxes = driver.find_elements_by_css_selector('ul.srp-nav-attr-list')
    if len(menuboxes) < 4:
        menuboxes = driver.find_elements_by_css_selector('ul.srp-nav-attr-list')
    return menuboxes[3]


def setMinMax(driver, min, max):
    driver.find_element_by_id('srp-nav-price-min').send_keys(min)
    driver.find_element_by_id('srp-nav-price-max').send_keys(max)
    driver.find_element_by_id('srp-nav-price-sbmt').click()


def sort(driver, by='Cheapest'):
    sortby = driver.find_element_by_id('sortingField-selector-input')
    sortby.send_keys(by)
    sortby.send_keys(Keys.RETURN)


def paginate(driver, results=100):
    results_per_page = driver.find_element_by_id('resultsperpage-select')
    results_per_page.send_keys(results)


def read_items(driver):
    rows = driver.find_elements_by_css_selector('ul#srchrslt-adtable li')
    items = []
    for row in rows:
        detail = read_detail(row)
        if excluded(detail):
            continue
        price = read_price(row)
        url = read_url(row)
        items.append((price, detail, url))
    return items


def read_detail(row):
    detail_el = row.find_element_by_css_selector('div.rs-ad-field.rs-ad-detail')
    try:
        detail_el.find_element_by_link_text('show more').click()
    except NoSuchElementException:
        pass
    return detail_el.text.encode('ascii', 'ignore')


def read_price(row):
    price_el = row.find_element_by_css_selector('div.rs-ad-field.rs-ad-price')
    price = price_el.text.replace('$', '').replace(',', '')
    price = price.split('.')[0]
    try:
        price = int(price)
    except ValueError:
        price = 999
    return price


def read_url(row):
    link = row.find_element_by_css_selector('a.rs-ad-title.h-elips')
    return link.get_attribute('href')


def excluded(detail):
    detail_norm = detail.lower()
    return (
        detail_norm.startswith('wanted')
        or 'office space' in detail_norm
        or 'studio' in detail_norm)


def print_items(driver, ma, items):
    print '\n==============================================='
    print ma
    print '==============================================='
    for price, detail, url in items:
        print '\n{0}\n{1}\n{2}'.format(price, detail, url)


def print_end():
    print '\n*************** END ****************************'


if __name__ == '__main__':
    # driver = webdriver.Chrome(chromedriver_path)
    driver = webdriver.Firefox()
    main(driver)
    driver.close()
