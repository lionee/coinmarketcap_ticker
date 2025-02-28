# Coinmarketcap ticker
#
# App to gather data from coinmarketcap for selected cryptocurrency...
# ... and presented it as small neat bar, which can be placed anywhere on screen and stopped by right click.
# Daniel Czerniawski 06.01.2022
import time

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
        rank = data['data'][k[0]]['cmc_rank']
        price = data['data'][k[0]]['quote']['USD']['price']

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return round(price, 6), rank

def switch_colors(last, current, field):
    try:
        if float(last) < float(current):
            field.update(text_color='#'+str(font_colour_better))
        elif float(last) > float(current):
            field.update(text_color='#'+str(font_colour_worse))
        elif float(last) == float(current):
            field.update(text_color='#'+str(font_colour_default))
    except:
        pass


if __name__ == '__main__':
    # Read config from config.cfg
    # Put your API-KEY there
    config = configparser.ConfigParser()
    try:
        config.read('config.cfg')
        api_key = config['DEFAULT']['api_key']
        slug = config['DEFAULT']['currency']
        refresh_rate = config['DEFAULT']['refresh_rate']
        amount = config['DEFAULT']['amount']
        background_colour_default = config['DEFAULT']['background_color_default']
        font_size = config['DEFAULT']['font_size']
        font_colour_default = config['DEFAULT']['font_color_default']
        font_colour_better = config['DEFAULT']['font_color_better']
        font_colour_worse = config['DEFAULT']['font_color_worse']

    except (KeyError, ValueError, FileNotFoundError) as e:
        print(f"Configuration error: {e}")
        exit(1)


    slugs = [x.strip() for x in slug.split(',')]
    slugs_amounts = [x.strip() for x in amount.split(',')]

    text1, text2, text3, text4 = "", "Connecting ...", "", ""
    rows = []
    layout = []
    last_price = last_pos = last_value = []

    my_new_theme = {'BACKGROUND': '#'+background_colour_default,
                    'TEXT': '#'+font_colour_default,
                    'INPUT': '#c7e78b',
                    'TEXT_INPUT': '#000000',
                    'SCROLL': '#c7e78b',
                    'BUTTON': ('white', '#709053'),
                    'PROGRESS': ('#01826B', '#D0D0D0'),
                    'BORDER': 0,
                    'SLIDER_DEPTH': 0,
                    'PROGRESS_DEPTH': 0}
    sg.theme_add_new('CoinmarketcapTickerTheme', my_new_theme)

    # Switch your theme to use the newly added one.
    sg.theme('CoinmarketcapTickerTheme')

    for x in range(len(slugs)):

        rows.append([
         sg.Text(text1, key='currency_name_'+slugs[x], pad=(0, 0), font=('Arial', font_size, 'bold'), background_color='#'+str(background_colour_default)),
         sg.Text(text2, key='price_'+slugs[x], pad=(0, 0), font=('Arial', font_size, 'bold'), background_color='#'+str(background_colour_default)),
         sg.Text(text3, key='coinmarketcap_position_'+slugs[x], pad=(0, 0), font=('Arial', font_size, 'bold'), background_color='#'+str(background_colour_default)),
         sg.Text(text4, key='current_amount_value_'+slugs[x], pad=(0, 0), font=('Arial', font_size, 'bold'), background_color='#'+str(background_colour_default))
        ])

        last_price.append(0)
        last_pos.append(0)
        last_value.append(0)
    layout = ([rows])
    #layout.append(rows)
    print(layout)


    # Get screen size
    w, h = sg.Window.get_screen_size()

    # Put window on top of the screen in middle
    # No title bar, always on top
    # Right mouse click to close app
    window = sg.Window("Coinmarketcap ticker", layout, location=(w/2-100,0), no_titlebar=True, keep_on_top=True, grab_anywhere=True, margins=(0,0), finalize=True)
    window['currency_name_'+slugs[x]].bind('<Button-3>', '+RIGHT CLICK+')
    window['price_'+slugs[x]].bind('<Button-3>', '+RIGHT CLICK+')
    window['coinmarketcap_position_'+slugs[x]].bind('<Button-3>', '+RIGHT CLICK+')
    window['current_amount_value_'+slugs[x]].bind('<Button-3>', '+RIGHT CLICK+')

    event, values = window.read(timeout=5)

    # Main loop
    while True:
        for x in range(len(slugs)):   # Iterating through all slugs defined in config.cfg

            try:
                data = get_data(slugs[x])
                current_price, current_pos = data

            except:
                window['price_'+slugs[x]].update(text_color='#'+str(font_colour_worse))
                window['coinmarketcap_position_'+slugs[x]].update(text_color='#'+str(font_colour_worse))
                data = ("Cannot connect", "to coinmarketcap API!")
                last_price, last_pos = data
                current_price, current_pos = data
                text1 = ""
                text2 = last_price[x]
                text3 = last_pos[x]
                text4 = ""
                pass
            else:
                text1 = slugs[x].upper() + ": "
                text2 = "$" + str(current_price)
                text3 = " #" + str(current_pos)
                if float(slugs_amounts[x]) != 0:
                    #print(amount)
                    current_amount_value = round(float(slugs_amounts[x]) * float(current_price), 2)
                    text4 = " $" + str(current_amount_value)
                else:
                    text4 = ""
            window['currency_name_'+slugs[x]].update(text1)
            window['price_'+slugs[x]].update(text2)
            window['coinmarketcap_position_'+slugs[x]].update(text3)
            window['current_amount_value_'+slugs[x]].update(text4)


            try:
                switch_colors(last_price[x], current_price, window['price_'+slugs[x]])
                switch_colors(current_pos, last_pos[x], window['coinmarketcap_position_'+slugs[x]])
                switch_colors(last_value[x], current_amount_value, window['current_amount_value_'+slugs[x]])
            except:
                pass

            last_price[x] = current_price
            last_pos[x] = current_pos
            last_value[x] = current_amount_value

            if (event == "currency_name_"+slugs[x]+"+RIGHT CLICK+" or
                    event == "price_"+slugs[x]+"+RIGHT CLICK+" or
                    event == "coinmarketcap_position_"+slugs[x]+"+RIGHT CLICK+" or
                    event == "current_amount_value_"+slugs[x]+"+RIGHT CLICK+" or
                    event == sg.WIN_CLOSED):
                window.close()
                exit(0)


        event, values = window.read(timeout=refresh_rate)

    window.close()
