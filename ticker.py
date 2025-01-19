# Coinmarketcap ticker
#
# App to gather data from coinmarketcap for selected cryptocurrency...
# ... and presented it as small neat bar, which can be placed anywhere on screen and stopped by right click.
# Daniel Czerniawski 06.01.2022

import locale
import PySimpleGUI as sg
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import configparser



def get_data(slug):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'slug': slug,
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        k = list(data['data'].keys())
        #pprint.pprint(data['data'])
        rank = data['data'][k[0]]['cmc_rank']
        price = data['data'][k[0]]['quote']['USD']['price']

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return round(price, 6), rank

if __name__ == '__main__':


    # Read config from config.cfg
    # Put your API-KEY there

    config = configparser.ConfigParser()
    try:
        config.read('config.cfg')
        api_key = config['DEFAULT']['api_key']
        slug = config['DEFAULT']['currency']
        refresh_rate = config['DEFAULT']['refresh_rate']
    except (KeyError, ValueError, FileNotFoundError) as e:
        print(f"Configuration error: {e}")
        exit(1)

    locale.setlocale(locale.LC_ALL, 'en_US')

    # Get screen size
    w, h = sg.Window.get_screen_size()

    text1 = slug.upper() + ": "
    text2 = "$" + str(get_data(slug)[0])
    text3 = " #" + str(get_data(slug)[1])

    # Set layout for window
    # Just simple one line without any buttons
    layout = [
        [sg.Text(text1, key='currency_name', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#333333'),
         sg.Text(text2, key='price', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#333333'),
         sg.Text(text3, key='coinmarketcap_position', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#333333')]
    ]

    # Put window on top of the screen in middle
    # No title bar, always on top
    # Right mouse click to close app
    window = sg.Window("Coinmarketcap ticker", layout, location=(w/2-100,0), no_titlebar=True, keep_on_top=True, grab_anywhere=True, margins=(0,0), finalize=True)
    window['currency_name'].bind('<Button-3>', '+RIGHT CLICK+')
    window['price'].bind('<Button-3>', '+RIGHT CLICK+')
    window['coinmarketcap_position'].bind('<Button-3>', '+RIGHT CLICK+')

    data = get_data(slug)
    last_price, last_pos = data



    # Main loop
    while True:

        event, values = window.read(timeout=refresh_rate)

        data = get_data(slug)
        current_price, current_pos = data

        text2 = "$" + str(current_price)
        text3 = " #" + str(current_pos)

        window['price'].update(text2)
        window['coinmarketcap_position'].update(text3)

        # Change color to red if price is lower and to green if price is higher
        if float(last_price) < float(current_price):
            window['price'].update(text_color='#55FF55')
        elif float(last_price) > float(current_price):
            window['price'].update(text_color='#FF5555')
        elif float(last_price) == float(current_price):
            window['price'].update(text_color='#EEEEEE')

        # Change color to red if position is lower and to green if price is higher
        if float(last_pos) < float(current_pos):
            window['coinmarketcap_position'].update(text_color='#FF5555')
        elif float(last_pos) > float(current_pos):
            window['coinmarketcap_position'].update(text_color='#55FF55')
        elif float(last_pos) == float(current_pos):
            window['coinmarketcap_position'].update(text_color='#EEEEEE')

        last_price = current_price
        last_pos = current_pos

        if event == "currency_name+RIGHT CLICK+" or event == "price+RIGHT CLICK+" or event == "coinmarketcap_position+RIGHT CLICK+" or event == sg.WIN_CLOSED:
            break


    window.close()
