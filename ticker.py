# Coinmarketcap ticker
#
# App to gather data from coinmarketcap for selected cryptocurrency...
# ... and presented it as small neat bar, which can be placed anywhere on screen and stopped by right click.
# Daniel Czerniawski 06.01.2022

import locale
import pprint
import PySimpleGUI as sg
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json



def get_data(slug):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        # 'start': '1',
        # 'id': '5350',
        # 'limit': '5000',
        'slug': slug,
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '',  #  <------- PUT YOUR API KEY here!!
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        k = list(data['data'].keys())
        #pprint.pprint(data['data'].g)
        pprint.pprint(data['data'])
        #pprint.pprint(data['data']['5350']['quote']['USD']['price'])
        rank = data['data'][k[0]]['cmc_rank']
        price = data['data'][k[0]]['quote']['USD']['price']

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    return round(price, 6), rank

if __name__ == '__main__':
    # Read coinmarketcap URL from file "url.txt" in working directory
    # eg. https://coinmarketcap.com/currencies/ethereum/
    # Url can be selected among all available crypto in coinmarketcap
    locale.setlocale(locale.LC_ALL, 'en_US')
    f = open("url.txt", "r")
    slug = f.read()
    f.close()

    # Get screen size
    w, h = sg.Window.get_screen_size()

    # Read data from provided url, parse it and put into variable
    #print(get_data(slug))

    text1 = slug.upper() + ": "
    text2 = "$" + str(get_data(slug)[0])
    text3 = " #" + str(get_data(slug)[1])
    #text3 = " Watching: " + re.sub("\\D", "", data[2].text.strip())
    #text4 = "Mcap: $" + locale.format_string("%d", int(re.sub("\\D", "", data[5].text.strip())), grouping=True)

    # Set layout for window
    # Just simple one line without any buttons
    layout = [
        [sg.Text(text1, key='currency_name', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#333333'),
         sg.Text(text2, key='price', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#333333'),
         sg.Text(text3, key='coinmarketcap_position', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#333333')]
    ]

    # Put window on top of the screen
    # No title bar, always on top
    # Right mouse click to close app
    window = sg.Window("Coinmarketcap ticker", layout, location=(w/2-100,0), no_titlebar=True, keep_on_top=True, grab_anywhere=True, margins=(0,0), finalize=True)
    window['currency_name'].bind('<Button-3>', '+RIGHT CLICK+')
    window['price'].bind('<Button-3>', '+RIGHT CLICK+')
    window['coinmarketcap_position'].bind('<Button-3>', '+RIGHT CLICK+')

    data = get_data(slug)
    last_price = get_data(slug)[0]
    last_pos = get_data(slug)[1]


    # Main loop
    while True:

        event, values = window.read(timeout=30000)

        text1 = get_data(slug)[0]
        text2 = " #" + str(get_data(slug)[1])

        window['price'].update(text1)
        window['coinmarketcap_position'].update(text2)


        #Change color to red if price is lower and to green if price is higher

        if int(last_price) < get_data(slug)[0]:
            window['price'].update(text_color='#55FF55')
        if int(last_price) > get_data(slug)[0]:
            window['coinmarketcap_position'].update(text_color='#FF5555')

        # Change color to red if position is lower and to green if price is higher
        if int(last_pos) < get_data(slug)[1]:
            window['price'].update(text_color='#FF5555')
        if int(last_pos) > get_data(slug)[1]:
            window['coinmarketcap_position'].update(text_color='#55FF55')



        last_price = get_data(slug)[0]
        last_pos = get_data(slug)[1]

        if event == "currency_name+RIGHT CLICK+" or event == "price+RIGHT CLICK+" or event == "coinmarketcap_position+RIGHT CLICK+" or event == sg.WIN_CLOSED:
            break


    window.close()
