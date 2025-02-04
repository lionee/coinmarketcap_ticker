# Coinmarketcap ticker
#
# App to gather data from coinmarketcap for selected cryptocurrency...
# ... and presented it as small neat bar, which can be placed anywhere on screen and stopped by right click.
# Daniel Czerniawski 06.01.2022


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
        amount = float(config['DEFAULT']['amount'])
        background_colour_default = config['DEFAULT']['background_color_default']
        font_colour_default = config['DEFAULT']['font_color_default']
        font_colour_better = config['DEFAULT']['font_color_better']
        font_colour_worse = config['DEFAULT']['font_color_worse']

    except (KeyError, ValueError, FileNotFoundError) as e:
        print(f"Configuration error: {e}")
        exit(1)

    text1, text2, text3, text4 = "", "Connecting ...", "", ""

    # Set layout for window
    # Just simple one line without any buttons
    layout = [
        [sg.Text(text1, key='currency_name', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#'+str(background_colour_default)),
         sg.Text(text2, key='price', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#'+str(background_colour_default)),
         sg.Text(text3, key='coinmarketcap_position', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#'+str(background_colour_default)),
         sg.Text(text4, key='current_amount_value', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#'+str(background_colour_default))]
    ]
    # Get screen size
    w, h = sg.Window.get_screen_size()

    # Put window on top of the screen in middle
    # No title bar, always on top
    # Right mouse click to close app
    window = sg.Window("Coinmarketcap ticker", layout, location=(w/2-100,0), no_titlebar=True, keep_on_top=True, grab_anywhere=True, margins=(0,0), finalize=True)
    window['currency_name'].bind('<Button-3>', '+RIGHT CLICK+')
    window['price'].bind('<Button-3>', '+RIGHT CLICK+')
    window['coinmarketcap_position'].bind('<Button-3>', '+RIGHT CLICK+')
    window['current_amount_value'].bind('<Button-3>', '+RIGHT CLICK+')

    event, values = window.read(timeout=1000)

    # Main loop
    while True:
        try:
            data = get_data(slug)
            current_price, current_pos = data
        except:
            window['price'].update(text_color='#'+str(font_colour_worse))
            window['coinmarketcap_position'].update(text_color='#'+str(font_colour_worse))
            data = ("Cannot connect", "to coinmarketcap API!")
            last_price, last_pos = data
            current_price, current_pos = data
            text1 = ""
            text2 = last_price
            text3 = last_pos
            text4 = ""
            pass
        else:
            text1 = slug.upper() + ": "
            text2 = "$" + str(current_price)
            text3 = " #" + str(current_pos)
            if int(amount) != 0:
                #print(amount)
                current_amount_value = round(float(amount) * float(current_price), 2)
                text4 = " $" + str(current_amount_value)
            else:
                text4 = ""
        window['currency_name'].update(text1)
        window['price'].update(text2)
        window['coinmarketcap_position'].update(text3)
        window['current_amount_value'].update(text4)


        try:
            switch_colors(last_price, current_price, window['price'])
            switch_colors(current_pos, last_pos, window['coinmarketcap_position']) #Here we do opposite way - green if lower
            switch_colors(last_value, current_amount_value, window['current_amount_value'])
        except:
            pass



        last_price = current_price
        last_pos = current_pos
        last_value = current_amount_value


        if event == "currency_name+RIGHT CLICK+" or event == "price+RIGHT CLICK+" or event == "coinmarketcap_position+RIGHT CLICK+" or event == "current_amount_value+RIGHT CLICK+" or event == sg.WIN_CLOSED:
            break
        event, values = window.read(timeout=refresh_rate)

    window.close()
