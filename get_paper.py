import os
import sys
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
from threading import Lock, Thread

total = []
lock = Lock()

# crawl setting
key_words = ['key-value', 'kv', 'lsm', 'log-structured', 'learned index']
conference_list = ['PPoPP', 'FAST', 'DAC', 'HPCA', 'MICRO', 'SC', 'ASPLOS', 'ISCA', 'USENIX', 'DATE', 'SIGMOD', 'CODES', 'ICDE', 'SIGIR', 'KDD', 'CIKM', 'ICDM', 'EDBT', 'CIDR', 'ICDCS']
# number is the latest volume
journal_list = [['tcad', 42], ['tpds', 34], ['tc', 72], ['tos', 18], ['tods', 47], ['tkde', 35], ['tois', 40], ['pvldb', 16]]
# start year and final year of conferences
start_year = 2018
final_year = 2022
# volumes of journals
vols = 5


def main():
    # get(key_words, conference_list, 2018, 2022, journal_list, 5)

    # support thread
    threads = []
    part_conf_len = len(conference_list) // 3
    part_jour_len = len(journal_list) // 3
    for i in range(0, 3):
        conf_range = conference_list[i * part_conf_len : (i + 1) * part_conf_len]
        jour_range = journal_list[i * part_jour_len : (i + 1) * part_jour_len]
        threads.append(Thread(target=get, args=(conf_range, start_year, final_year, jour_range, vols, )))
        threads[-1].start()
    conf_range = []
    jour_range = []
    if 3 * part_conf_len < len(conference_list):
        conf_range = conference_list[3 * part_conf_len : len(conference_list)]
    if 3 * part_jour_len < len(journal_list):
        jour_range = journal_list[3 * part_jour_len : len(journal_list)]
    if conf_range or jour_range:
        threads.append(Thread(target=get, args=(conf_range, start_year, final_year, jour_range, vols, )))
        threads[-1].start()

    for thread in threads:
        thread.join()
    
    print('FILTERING')
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


def get(conference_list, year_begin, year_end, journal_list, volume_forward):
    global total
    part = []
    for conf_name in conference_list:
        year = year_begin
        while year <= year_end:
            try:
                papers = getConference(conf_name.lower(), year)
            except Exception as e:
                print(e)
                year += 1
                continue
            for paper in papers:
                part.append(paper)
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
            for paper in papers:
                part.append(paper)
            volume += 1

    lock.acquire()
    total.extend(part)
    lock.release()


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


if __name__ == '__main__':
    main()
    print('END')
