# ***Telegram Crypto Server App***
Application multiuser developed to get information about cryptocurrency prices.

This app can be divided into three different parts: telegram alert system, google sheet data update system and website.

## Telegram Alert System
*Telegram Alert System* is created to notify cryptocurrency prices. With a multiuser system through *PopeBot Notifier* telegram bot, every user can define his own price notifications for each coin.

<img width="287" alt="2021-07-08_09h55_10" src="https://user-images.githubusercontent.com/72787344/124884512-a0de9500-dfd2-11eb-84e1-47d61c3f729c.png">

## Google Sheet Data Update System
This system is used to fill with cryptocurrency prices a google sheet. Given the name and the initial invested amount the system calculates maximums and minimums and different profits. You can also include tax and the final amount will be calculated automatically. Colours used at *Precio*, *Beneficio %* and *Beneficio* are automatically set depending on the data.

<img width="626" alt="2021-07-08_10h05_18" src="https://user-images.githubusercontent.com/72787344/124886419-81e10280-dfd4-11eb-872f-388e61d0ba9e.png">
 
 Unless you modify showed headers in the code (at gdrive folder) you must write headers as in the image.

## Website
Where we can watch different indicators to buy/sell coins and plots which show historic prices and moving averages.

![Firefox_Screenshot_2021-07-08T08-23-36 616Z](https://user-images.githubusercontent.com/72787344/124888678-9cb47680-dfd6-11eb-9dff-cc178bc55286.png)


## Run
There are two different ways to run this app:
- Launching *app.py* with python. You should go to folder application and run
```
$ pip install -r requirements.txt
$ python app.py
```
> App has been developed under python3.7, you can try to run it with all the versions you want but working is not assured.
- Running *docker-compose.yaml* file, which will create an *NGINX* server to serve the python app.
