# Newyork-Times-Datacollect
Collect articles from NYtimes through [NYTimes api]("https://developer.nytimes.com/")

## Requirements:
- [Python 3.6]("https://www.python.org/downloads/release/python-360/")
- [Beautiful Soup 4]("https://www.crummy.com/software/BeautifulSoup/")
- [Requests]("http://docs.python-requests.org/en/master/")

## Usage

Get articles in a json 
```python
apikey = getAPIkey(file='./API-key.txt')

article_json = searchNYTimes(api_key=apikey, query='football')
```


Get bulk articles in a list
```python
articles = getArticlesInMass(api_key=apikey, query='football', page_count=5)
```