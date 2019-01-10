# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 00:50:41 2018

@author: aumale
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
import os

def getAPIkey(file='./data/nyt_api.key') :
    """
    Get New York Times API key from a file
    
    Parameters
    ----------
    file : str
        Full designated path of the key file
    
    Returns
    -------
    str
        String of API key
    """
    try:
        with open(file) as fp:
            key = fp.read().strip()
            return key
    except Exception as e:
        print(e)


def searchNYTimes(api_key='', query='', fq='', 
                   fields='', sort='', begin_date='YYYYMMDD', 
                   end_date='YYYYMMDD', page=-1,):
    """
    Search New York times for articles through provided API.
    
    Parameters
    ----------
    api_key : str
        NYtimes API key string
    query : str
        Search query term. Search is performed on the article body, headline and byline.
    fq : str
        Filtered search query using standard Lucene syntax.
        The filter query can be specified with or without a limiting field: label.
        See Filtering Your Search for more information about filtering
    begin_date : str
        Format: YYYYMMDD
        Restricts responses to results with publication dates of the date specified or later."
    end_date : str
        Format: YYYYMMDD
        Restricts responses to results with publication dates of the date specified or earlier.
    sort : str
        By default, search results are sorted by their relevance to the query term (q). Use the sort parameter to sort by pub_date.
        Allowed values are:
            > newest
            > oldest
    fields : string
        Comma-delimited list of fields (no limit)
        Limits the fields returned in your search results. By default (unless you include an fl list in your request), 
        the following fields are returned: snippet, lead_paragraph, abstract, print_page, blog, source, multimedia, 
        headline, keywords, pub_date, document_type, news_desk, byline, type_of_material, _id, word_count
    page : int
        The value of page corresponds to a set of 10 results (it does not indicate the starting number of the result set). 
        For example, page=0 corresponds to records 0-9. To return records 10-19, set page to 1, not 10.

    Returns
    -------
    dict
        Dictionary representation of json object
    """
    # hardcoded link to article search api json object
    api_search_url= 'https://api.nytimes.com/svc/search/v2/articlesearch.json'

    assert len(query) > 0, 'Query string is empty'
    
    fl_items = ['web_url',
        'snippet',
        'lead_paragraph',
        'abstract',
        'print_page',
        'blog',
        'source',
        'multimedia',
        'headline',
        'keywords',
        'pub_date',
        'document_type',
        'news_desk',
        'byline',
        'type_of_material',
        '_id',
        'word_count']
    
    search_param={'api-key':api_key,
                  'q':query }
    
    if len(fq) > 0 :
        search_param['fq'] = fq
        
    if len(fields) > 0:
        if set(fields).issubset(fl_items) :
            search_param['fl'] = fields
        else:
            print('Enter valid field values')
            return None
    if len(sort) > 0:
        if sort == 'newest' | sort == 'oldest':
            search_param['sort'] = sort
    
    if begin_date != 'YYYYMMDD':
        if int(begin_date[4:6]) > 0 & int(begin_date[4:6]) <= 12:
            if int(begin_date[6:9]) > 0 & int(begin_date[6:9]) <= 31:
                search_param['begin_date'] = begin_date
                
    if end_date != 'YYYYMMDD':
        if int(begin_date[4:6]) > 0 & int(begin_date[4:6]) <= 12:
            if int(begin_date[6:9]) > 0 & int(begin_date[6:9]) <= 31:
                search_param['end_date'] = end_date
    
    if page >= 0:
        search_param['page'] = page
    
    try:
        resp = requests.get(url=api_search_url,params=search_param)
        response_json = resp.json()
        resp.close()
    except Exception as e:
        print(e)
    if(response_json != None):
        return response_json
        

class NYTapiResponseWrapper:
    """Python Wrapper class for the json object returned by NYtimes API"""
    def __init__(self, response_json = {}):
        """
        Constructor of Wrapper class
        Parameters
        ----------
        response_json : dict
            response json object from API
        """
        if len(response_json.keys()) > 0:
            self.status = response_json['status']
            self.copyright = response_json['copyright']
            self._response = response_json['response']
            self._parseResponse(self._response)
    
    def parseJSON(self, response_json = {} ):
        """
        Parser function to parse json object if Wrapper is not initialized with a json
        
        Parameters
        ----------
        response_json : dict
            response json object from API
        """
        self.status = response_json['status']
        self.copyright = response_json['copyright']
        self._response = response_json['response']
        self._parseResponse(self._response)

    def _parseResponse(self, response):
        self._docs = response['docs']
        self._meta = response['meta']
        self._parseDocs(self._docs)
    
    def _parseDocs(self, docs):
        self.docs = []
        i = 0
        for doc_item in docs:
            i += 1
            self.docs.append(Doc(doc = doc_item))
        
        
class Doc:
    def __init__(self, doc = {}):
        self._id = doc['_id']
        self.blog             = doc['blog']
        self.document_type    = doc['document_type']
        self.headline         = doc['headline']
        self.keywords         = doc['keywords']
        self.multimedia       = doc['multimedia']
        self.score            = doc['score']
        self.snippet          = doc['snippet']
        self.type_of_material = doc['type_of_material']
        self.web_url          = doc['web_url']
        self.word_count       = doc['word_count']


def getPageByURL(URL = ''):
    try:
        resp = requests.get(url=URL)
        soup = BeautifulSoup(resp.text, 'html.parser')
        resp.close()
        return soup
    except Exception as e:
        print(e)

        
def saveArticleText(headline, textParasSoup, filename):
    try:
        with open(filename, 'w') as fp:
            fp.write(headline)
            for para in textParasSoup:
                fp.write(para.text)
    except Exception as e:
        print(e)


def getArticlesInMass(api_key='', query='', fq='', 
                   fields='', sort='', begin_date='YYYYMMDD', 
                   end_date='YYYYMMDD', page_count = 1, write_to_file=False, 
                      filename='./data/Articles/ArticleList.json'):
    """
    Get multiple pageset of articles instead of 1
    
    Parameters
    ----------
    page_count : int
        number of pageset giving 10 articles for each count, i.e. page_count of i will give i*10 articles
    write_to_file : boolean
        Write obtained article list to a file
    filename : str
        Name of file if write_to_file is True
    Remainig params are same as searchNYTimes function
    
    Returns
    -------
    list
        list of all the articles obtained from API
    """
    article_list = []
    for page in range(0,page_count):
        resp = searchNYTimes(api_key=api_key, query=query, fq=fq, fields=fields,sort=sort,
                             begin_date=begin_date,end_date=end_date, page=page)
        resp_ob = NYTapiResponseWrapper(resp)
        if len(resp_ob.docs) <= 0 : 
            break
        for doc_item in resp_ob.docs:
            article = {'id':doc_item._id,'headline':doc_item.headline['main'], 'url':doc_item.web_url, 'downloaded':'N'}
            article_list.append(article)
        time.sleep(1)
    if write_to_file:
        with open(filename, 'w') as file:
            json.dump(article_list, file)
    return article_list


def groupByCategories(article_list=[]):
    """
    Group articles into article categories

    Category is obtained from the http link in below format:
    1(https://www.nytimes.com/2018/05/04/) 2(movies) 3(/sandra-bullock-mindy-kaling-oceans-8.html)

    2 gives the category
    
    Parameters
    ----------
    article_list : list
        List of Articles 
        
    Returns
    -------
    dict
        Dictionary of articles where key is category and value is list of articles    
    """
    groupedArticles = {}
    for article in article_list:
        url = article['url']
        # split the url into 3 parts
        # eg. 1(https://www.nytimes.com/2018/05/04/) 2(movies) 3(/sandra-bullock-mindy-kaling-oceans-8.html)
        reg_ex = r"([a-zA-Z0-9\.\-_/:]*/[0-9]{4}/[0-9]{2}/[0-9]{2}/)([a-zA-Z0-9]+)(/[a-zA-Z\-\.]*)"
        category = re.split(reg_ex, url)[2]
        if not category in groupedArticles:
            groupedArticles[category] = [article]
        else: 
            groupedArticles[category].append(article)
    return groupedArticles


def getArticleListByCategory(category='business', api_key='', begin_date='YYYYMMDD', 
                   end_date='YYYYMMDD', page_count = 0):
    """
    Returns article of a specific category
    """
    return getArticlesInMass(api_key=api_key, fq='web_url:*'+category+'*',page_count=page_count)
    

def downloadAllArticles(article_list, grouped=False, parentDirectory='./data/NYT-articles/'):
    
    """
    Download all the articles in the article list/dict to a individual article file.
        
    Parameters
    ----------
    article_list : list/dict
        A list or dict of articles
    grouped : boolean
        if grouped is True a dictionary of grouped articles is expceted in article_list
        else a list of articles
    parentDirectory : str
        Path of parent directory where articles files are saved by article id file name
    
    """
    if len(article_list) <1:
        return None
    if not grouped:
        if type(article_list) == list:
            total_articles_written = _downloadArticles(article_list, directory = parentDirectory)
        else:
            print('Error: List Expected '+type(article_list).__name__+' found')
            return None
    else:
        if type(article_list) == dict:
            total_articles_written = 0
            for category in article_list.keys():
                articles_written = _downloadArticles(article_list[category], directory=parentDirectory + category+'/')
                total_articles_written += articles_written
        else: 
            print('Error: Dict expected '+type(article_list).__name__+' found')
            return None
    return total_articles_written


def _downloadArticles(article_list=[], directory='./'):
    if len(article_list) <1:
        return None
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    articles_written = 0
    for article in article_list:
        article_soup = getPageByURL(URL = article['url']) 
        paras = article_soup.find_all('p')
        article_text = ''
        for para in paras:
            if 'class' in para.attrs: 
                p_class = ' '.join(para.attrs['class'])
                if 'css-1' in p_class and ' e2' in p_class or 'story' in p_class: 
                    article_text += para.text +'\n'
        try:
            with open(directory + article['id'], 'w', encoding='utf-8') as file:
                file.write(article['headline']+ '\n')
                file.write(article_text)
                time.sleep(1)
                articles_written += 1
        except Exception as e:
            print(e)
        finally:
            # future: write the article list to file once done or occurance of an excecption
            pass
    return articles_written