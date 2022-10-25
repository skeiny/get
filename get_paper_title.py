import os
import sys
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError


def main():
    # config
    key_words = ['learned index', 'learned', 'index', 'LSM', 'KV', 'secondary', 'correlation', 'database']
    conference_list = ['DAC', 'DATE', 'usenix', 'HPCA', 'FAST', 'SIGMOD', 'VLDB', 'ICDE', 'codes']
    # number is the latest volume
    journal_list = [['tcad', 41], ['tpds', 33], ['tc', 71], ['tos', 18]]

    # the last number is the volume num
    get(key_words, conference_list, 2018, 2022, journal_list, 5)


def get(key_words, conference_list, year_begin, year_end, journal_list, volume_forward):
    total = []
    for conf_name in conference_list:
        year = year_begin
        while year <= year_end:
            try:
                papers = getConference(conf_name.lower(), year)
            except Exception as e:
                print(e)
                year += 1
                continue
            for i in papers:
                total.append(i)
            year += 1

    for journal in journal_list:
        volume = journal[1] - volume_forward + 1
        while volume <= journal[1]:
            try:
                papers = getJournals(journal[0].lower(), volume)
            except Exception as e:
                print(e)
                volume += 1
                continue
            for i in papers:
                total.append(i)
            volume += 1

    df = pd.DataFrame(total)
    for idx, r in df.iterrows():
        save = False
        for word in key_words:
            if word.lower() in r["title"].lower():
                print(r["title"])
                save = True
                break
        if not save:
            df.drop(idx, inplace=True)

    # output
    if not os.path.exists(os.path.abspath(os.path.dirname(sys.argv[0]) + "/result")):
        os.makedirs(os.path.abspath(os.path.dirname(sys.argv[0]) + "/result"))
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0]) + "/result"))
    filename = datetime.datetime.now().strftime('%Y-%m-%d %H.%M') + ".csv"
    if os.path.exists(filename):
        os.remove(filename)
    df.to_csv(filename, index=False, encoding='utf_8_sig')


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
            paper["conference"] = name
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
            paper["journal"] = name
            # paper["auth_url"] = auth_urls
            papers.append(paper)
    return papers


# run here
main()
