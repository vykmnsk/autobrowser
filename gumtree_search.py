from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from chromedriver import chromedriver_path
import time


def main(driver):
    """
    Yarra Area - Richmond
    Hobsons Bay Area
    Whitehorse Area
    Banyule Area
    Kingston Area
    Bayside Area
    """

    areastxt = """
    Yarra Area - Richmond
    Hobsons Bay Area
    Whitehorse Area
    Banyule Area
    Kingston Area
    Bayside Area
    """

    areastxt = areastxt.strip()
    menu_areas = [
        line.split('-')
        for line in areastxt.split('\n') if line]
    menu_vic = ['Victoria']
    menu_melb = ['Melbourne Region', 'show more']

    ### RUN ###
    driver.implicitly_wait(20)
    driver.get('http://www.gumtree.com.au/')
    driver.find_element_by_link_text('Property for Rent').click()
    navigateMenu(driver, menu_vic)
    setMinMax(driver, 250, 340)
    # time.sleep(8)

    for menu_area in menu_areas:
        navigateMenu(driver, menu_melb)
        navigateMenu(driver, menu_area)
        sort(driver, by='Cheapest')
        time.sleep(5)
        #paginate(driver, 100)
        items = read_items(driver)
        print_items(driver, menu_area, sorted(items))

    print_end()

    driver.close()


def navigateMenu(driver, menu):
    for m in menu:
        places = find_places_box(driver)
        time.sleep(3)
        places.find_element_by_link_text(m.strip()).click()


def find_places_box(driver):
    menuboxes = driver.find_elements_by_css_selector('ul.srp-nav-attr-list')
    if len(menuboxes) < 4:
        # time.sleep(5)
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
    try:
        driver = webdriver.Chrome(chromedriver_path)
        main(driver)
    finally:
        driver.close()
