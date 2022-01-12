# Coinmarketcap ticker
#
# App to gather data from coinmarketcap for selected cryptocurrency...
# ... and presented it as small neat bar, which can be placed anywhere on screen and stopped by right click.
# Daniel Czerniawski 06.01.2022

import requests, re, locale
from bs4 import BeautifulSoup
import PySimpleGUI as sg

def get_data(url):
    response = requests.get(url, headers={'Cache-Control': 'no-cache'})
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("div", class_="namePill")
    price = soup.find_all("div", class_="priceValue")
    mc = soup.find_all("div", class_="statsValue")

    results.extend(price)
    results.extend(mc[0])
    return results

if __name__ == '__main__':
    # Read coinmarketcap URL from file "url.txt" in working directory
    # eg. https://coinmarketcap.com/currencies/ethereum/
    # Url can be selected among all available crypto in coinmarketcap
    locale.setlocale(locale.LC_ALL, 'en_US')
    f = open("url.txt", "r")
    url = f.read()
    f.close()

    # Get screen size
    w, h = sg.Window.get_screen_size()

    # Read data from provided url, parse it and put into variable

    data = get_data(url)


    text1 = data[4].text.strip()
    text2 = " #" + re.sub("\D", "", data[0].text.strip())
    text3 = " Watching: " + re.sub("\D", "", data[2].text.strip())
    text4 = "Mcap: $" + locale.format_string("%d", int(re.sub("\D", "", data[5].text.strip())), grouping=True)

    # Set layout for window
    # Just simple one line without any buttons
    layout = [
        [sg.Text(text1, key='text1', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#333333'),
         sg.Text(text2, key='text2', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#333333'),
         sg.Text(text3, key='text3', pad=(0, 0), font=('Arial', 10, 'bold'), background_color='#333333')]
    ]

    # Put window on top of the screen
    # No title bar, always on top
    # Right mouse click to close app
    window = sg.Window("Coinmarketcap ticker", layout, location=(w/2-100,0), no_titlebar=True, keep_on_top=True, grab_anywhere=True, margins=(0,0), finalize=True)
    window['text1'].bind('<Button-3>', '+RIGHT CLICK+')
    window['text2'].bind('<Button-3>', '+RIGHT CLICK+')
    window['text3'].bind('<Button-3>', '+RIGHT CLICK+')

    data = get_data(url)
    last_price = re.sub("\D", "", data[4].text.strip())
    last_pos = re.sub("\D", "", data[0].text.strip())
    last_mcap = re.sub("\D", "", data[5].text.strip())

    # Main loop
    while True:

        event, values = window.read(timeout=10000)
        data = get_data(url)
        text1 = data[4].text.strip()
        text2 = " #" + re.sub("\D","",data[0].text.strip())
        text3 = " Watching: " + re.sub("\D","",data[2].text.strip())
        text4 = "Mcap: $" + locale.format_string("%d", int(re.sub("\D", "", data[5].text.strip())), grouping=True)
        window['text1'].update(text1)
        window['text2'].update(text2)
        window['text3'].update(text4)

        # Change color to red if price is lower and to green if price is higher
        if int(last_price) < int(re.sub("\D","",data[4].text.strip())):
            window['text1'].update(text_color='#55FF55')
        if int(last_price) > int(re.sub("\D", "", data[4].text.strip())):
            window['text1'].update(text_color='#FF5555')

        # Change color to red if position is lower and to green if price is higher
        if int(last_pos) < int(re.sub("\D","",data[0].text.strip())):
            window['text2'].update(text_color='#FF5555')
        if int(last_pos) > int(re.sub("\D", "", data[0].text.strip())):
            window['text2'].update(text_color='#55FF55')

        # Change color to red if marketcap is lower and to green if market cap is higher
        if int(last_mcap) < int(re.sub("\D", "", data[5].text.strip())):
            window['text3'].update(text_color='#FF5555')
        if int(last_mcap) > int(re.sub("\D", "", data[5].text.strip())):
            window['text3'].update(text_color='#55FF55')


        last_price = re.sub("\D", "", data[4].text.strip())
        last_pos = re.sub("\D", "", data[0].text.strip())
        last_mcap = re.sub("\D", "", data[5].text.strip())
        if event == "text1+RIGHT CLICK+" or event == "text2+RIGHT CLICK+" or event == "text3+RIGHT CLICK+" or event == sg.WIN_CLOSED:
            break


    window.close()
