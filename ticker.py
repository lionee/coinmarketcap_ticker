# Coinmarketcap ticker
#
# App to gather data from coinmarketcap for selected cryptocurrency...
# ... and presented it as small neat bar, which can be placed anywhere on screen and stopped by right click.
# Daniel Czerniawski 06.01.2022

import requests, re
from bs4 import BeautifulSoup
import PySimpleGUI as sg

def get_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("div", class_="namePill")
    price = soup.find_all("div", class_="priceValue")
    results.extend(price)
    return results

if __name__ == '__main__':
    # Read coinmarketcap URL from file "url.txt" in working directory
    # eg. https://coinmarketcap.com/currencies/ethereum/
    # Url can be selected among all available crypto in coinmarketcap

    f = open("url.txt", "r")
    url = f.read()
    f.close()

    # Get screen size
    w, h = sg.Window.get_screen_size()

    # Read data from provided url, parse it and put into variable
    data = get_data(url)
    text = data[4].text.strip() + " #" + re.sub("\D", "", data[0].text.strip()) + "; Watching: " + re.sub("\D", "", data[2].text.strip())

    # Set layout for window
    # Just simple one line without any buttons
    layout = [
        [sg.Text(text, key='text1', pad=(0, 0), font=('Arial', 10, 'bold'))],
        #[sg.Button(".")]
    ]

    # Put window on top of the screen
    # No title bar, always on top
    # Right mouse click to close app
    window = sg.Window("Coinmarketcap ticker", layout, location=(w/2-100,0), no_titlebar=True, keep_on_top=True, grab_anywhere=True, margins=(0,0), finalize=True)
    window['text1'].bind('<Button-3>', '+RIGHT CLICK+')

    # Main loop
    while True:

        event, values = window.read(timeout=30000)
        data = get_data(url)
        text = data[4].text.strip() +" #" + re.sub("\D","",data[0].text.strip()) + "; Watching: " + re.sub("\D","",data[2].text.strip())
        window['text1'].update(text)
        print(event)
        if event == "text1+RIGHT CLICK+" or event == sg.WIN_CLOSED:
            break


    window.close()
