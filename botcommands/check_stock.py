import requests
from prettytable import PrettyTable
import textwrap


urls = ['https://store.ui.com/us/en/pro/category/all-unifi-cloud-gateways/products/udr']


def is_product_sold_out(urls):
    status = []
    for url in urls:
        response = requests.get(url)
        if 'Sold Out' in response.text:
            status.append({'url': url, 'status': 'Sold Out'})
        else:
            status.append({'url': url, 'status': 'In Stock!'})
    return status


def is_product_not_sold_out(urls):
    # call the function
    url_status = is_product_sold_out(urls)

    # create a new pretty table
    table = PrettyTable()

    # set the field names
    table.field_names = ['URL', 'Status']

    # add rows
    for item in url_status:
        table.add_row([item['url'], item['status']])

    # set max width
    table.max_width = 25
    return table

