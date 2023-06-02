Aggiornamento sito:
Il gioco è disponibile online su: http://pdsmattermost.ddns.net:8000/home/



# Backend [Django]
## Prerequisiti
1. Installare pip
  - Linux `python3 -m pip install --user --upgrade pip`
  - Windows `py -m pip install --upgrade pip`

2. Installare Virtualenv
  - Linux `python3 -m pip install --user virtualenv`
  - Windows `py -m pip install --user virtualenv`

3. Creare l'ambiente virtuale
  - Linux `python3 -m venv venv` oppure `python3 -m venv venv/bin/activate`
  - Windows `py -m venv env`

4. Attivare l'ambiente virtuale
  - Linux `source venv/venv`
  - Windows `.\venv\Scripts\activate`

5. Installare le dipendenze
  - Linux `python3 -m pip install -r requirements.txt`
  - Windows `py -m pip install -r requirements.txt`

6. Installare Redis
  - `https://redis.io/docs/getting-started/installation/`


## Procedure
1. Avviare Redis
  - `https://tableplus.com/blog/2018/10/how-to-start-stop-restart-redis.html`

2. Avvio django server
  - Linux `python3 manage.py runserver`
  - Windows `py manage.py runserver`
