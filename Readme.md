# Image-Scraper-kk

## Description
Extract image url from Instagram by POSTing the url in JSON format with a keyword, 'url'.
For example,
```
{"url": "https://www.instagram.com/P/faewfFEfdcna/fjiaof......"}
```
The 'kk' does not mean anything, that is only the name had been taken by someone else.

## Install

* Install packages using pip.

```
pip install -r requirements
```

* If using heroku, just run the following command, and you are good to go.
```
heroku local
```

* If not using heroku, you can run the app like this.
```
export FLASK_APP=image-scraper.py
flask run
```

