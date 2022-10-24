import os
import sys
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError


def main():
    ## config
    key_words = ["csd","computational"]
    conference_list = ["date",'dac','hpca','fast']
    journal_list = [["tcad",41]]


    if(True):
        loop_conference(conference_list, key_words, 2020, 2022)
    if(True):
        loop_journal(journal_list,key_words,3)

def loop_conference(conference_list, key_words, begin, end):
    # get
    total = []
    for conf_name in conference_list:
        year = begin
        while (year <= end):
            try:
                papers = getConference(conf_name.lower(), year)
            except Exception as e:
                print(e)
                break
            for i in papers:
                total.append(i)
            year += 1

    # filter
    df = pd.DataFrame(total)
    for idx, r in df.iterrows():
        save = False
        for word in key_words:
            if word.lower() in r["title"].lower():
                # print(r["title"])
                save = True
                break
        if not save:
            df.drop(idx, inplace=True)

    # output
    if not os.path.exists(os.path.abspath(os.path.dirname(sys.argv[0]) + "/result")):
        os.makedirs(os.path.abspath(os.path.dirname(sys.argv[0]) + "/result"))
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0]) + "/result"))
    filename = str(datetime.date.today()) + "_ConfResult_" + str(begin) + "~" + str(end)
    df.to_csv((filename + ".csv"), index=False, encoding='utf_8_sig')


def loop_journal(journal_list,key_words,loop):
    # get
    total = []
    for journal in journal_list:
        volume = journal[1] - loop + 1
        while (volume <= journal[1]):
            try:
                papers = getJournals(journal[0].lower(), volume)
            except Exception as e:
                print(e)
                break
            for i in papers:
                total.append(i)
            volume += 1

    # filter
    df = pd.DataFrame(total)
    for idx, r in df.iterrows():
        save = False
        for word in key_words:
            if word.lower() in r["title"].lower():
                # print(r["title"])
                save = True
                break
        if not save:
            df.drop(idx, inplace=True)

    # output
    if not os.path.exists(os.path.abspath(os.path.dirname(sys.argv[0]) + "/result")):
        os.makedirs(os.path.abspath(os.path.dirname(sys.argv[0]) + "/result"))
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0]) + "/result"))
    filename = str(datetime.date.today()) + "_JournalResult"
    df.to_csv((filename + ".csv"), index=False, encoding='utf_8_sig')


def getBsObj(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
        return None
    bsObj = BeautifulSoup(html, features="lxml")
    return bsObj


def getConference(name, year):
    url = "https://dblp.uni-trier.de/db/conf/" + name + "/" + name + str(year) + ".html"
    print(url)
    papers = []
    bsObj = getBsObj(url)
    themeList = bsObj.body.find("div", {"id": "main"}).findAll("ul", {"class": "publ-list"})
    for theme in themeList:
        itemList = theme.findAll("li", {"class": "entry inproceedings"})
        for item in itemList:
            paper = {}
            authors = item.cite.findAll("span", {"itemprop": "author"})
            auth_urls = [author.a["href"] for author in authors]
            authors = [author.a.span.get_text() for author in authors]
            paper["title"] = item.cite.find("span", {"class": "title"}).get_text()
            # paper["authors"] = authors
            paper["year"] = year
            paper["article"] = name
            # paper["auth_url"] = auth_urls
            papers.append(paper)
    return papers


def getJournals(name, volume):
    url = "https://dblp.uni-trier.de/db/journals/" + name + "/" + name + str(volume) + ".html"
    print(url)
    papers = []
    bsObj = getBsObj(url)
    themeList = bsObj.body.find("div", {"id": "main"}).findAll("ul", {"class": "publ-list"})
    for theme in themeList:
        itemList = theme.findAll("li", {"class": "entry article"})
        for item in itemList:
            paper = {}
            authors = item.cite.findAll("span", {"itemprop": "author"})
            auth_urls = [author.a["href"] for author in authors]
            authors = [author.a.span.get_text() for author in authors]
            paper["title"] = item.cite.find("span", {"class": "title"}).get_text()
            # paper["authors"] = authors
            paper["volume"] = volume
            paper["type"] = name
            # paper["auth_url"] = auth_urls
            papers.append(paper)
    return papers

# run here
main()