__author__ = "Zhijing Jin"
__copyright__ = "Copyright 2020, Zhijing Jin"
__credits__ = ["git@github.com:shunk031/TedScraper.git"]
__license__ = "MIT"
__version__ = "1.0"
__email__ = "zhijing.jin@connect.hku.hk"
__status__ = "Production"

'''
website is https://www.ted.com/participate/translate/our-languages
stats of previous dump is http://www.cs.jhu.edu/~kevinduh/a/multitarget-tedtalks/stats.txt
similar datasets is https://github.com/saranyan/TED-Talks, https://www.kaggle.com/rounakbanik/ted-talks, https://data.world/owentemple/ted-talks-complete-list
some rss listing of website links is http://www.ted.com/talks/rss, http://feeds.feedburner.com/TedtalksHD?fmt=xml
'''

import os
import re
import time
import json

from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError

try:
    from bs4 import BeautifulSoup
    from lxml import etree
    from tqdm import tqdm
    import efficiency
except ImportError:
    os.system('pip install bs4 tqdm efficiency')


class TEDTalkDownloader:
    BASE_URL = "https://www.ted.com/talks"

    def __init__(self, language='en', transcript_file='ted_transcripts.json',
                 raw_file='ted_raw.json'):
        self.language = language
        self.transcript_file = transcript_file
        self.raw_file = raw_file
        self.all_links = []
        self.all_webpages = {}
        self.all_transcripts = {}

    def get_all_transcripts(self, read_existing_file: bool = False,
                            max_webpages: int = None, links: list = None,
                            max_link_pages: int = 200, wait: int = 10) -> None:
        from tqdm import tqdm
        from efficiency.function import flatten_list

        if not read_existing_file:
            self.get_all_webpages(max_webpages=max_webpages, links=links,
                                  max_link_pages=max_link_pages, wait=wait)
        else:
            with open(self.raw_file) as f:
                data = json.load(f)
                self.all_webpages = data['all_transcripts']
                self.all_links = data['all_links']

        for link, webpage in tqdm(self.all_webpages.items(), desc='Parsing HTML'):
            transcript = self._get_transcript_from_webpage(webpage)
            self.all_transcripts[link] = transcript

        sents = flatten_list(self.all_transcripts.values())
        print('[Info] Saved {} links, {} transcripts, and {} sentences to "{}"'
              .format(len(self.all_links), len(self.all_transcripts),
                      len(sents), self.transcript_file))
        self._save_json(only_transcripts=True)

    def get_all_webpages(self, max_webpages: int = None,
                         links: list = None, max_link_pages: int = 200,
                         wait: int = 10, auto_save: bool = True) -> dict:
        '''
        Get the transcripts of all talks
        :param  (list) links: list of links that you want to crawl the websites of
                (int) max_link_pages: max number of pages that you want to crawl the links out of
                (int) wait: the waiting time between each two website visit requests
                    (to avoid anti-scraping scripts from TED)
                (bool) auto_save: whether to automatically save the outputs
        :return: (dict) all_talk_transcripts:
                a dict of {url: html webpage}
        '''
        from tqdm import tqdm

        if links is None:
            self.get_all_links(max_pages=max_link_pages, wait=wait)
        else:
            self.all_links = links

        self.all_webpages = {}
        pbar = tqdm(self.all_links[:max_webpages])
        for atl in pbar:
            tr_url = self._get_transcript_url(atl, self.language)
            self.target_url = tr_url

            tr_soup = self._make_soup(tr_url)
            if tr_soup is not None:
                self.all_webpages[atl] = tr_soup.__repr__()
                if auto_save: self._save_json()
                pbar.set_description(
                    'Retrieving Webpages'.format(len(self.all_webpages)))

            time.sleep(wait)

        return self.all_webpages

    def get_all_links(self, max_pages=200, wait=10):
        '''
        Get the links of all talks

        :return: list of string
        '''
        from tqdm import tqdm

        url_templ = 'https://www.ted.com/talks?sort=newest&language=' \
                    + self.language + '&page={}'

        pbar = tqdm(range(1, max_pages + 1))
        for page_id in pbar:

            target_url = url_templ.format(page_id)
            soup = self._make_soup(target_url)
            if soup is None:
                print('[Info] {} links gathered. Invalid link: {}'.format(
                    len(self.all_links), target_url))
                break
            talk_links = self._get_links_from_soup(soup)
            self.all_links.extend(talk_links)
            pbar.set_description(
                'Retrieved {} links'.format(len(self.all_links)))

            self._save_json()
            time.sleep(wait)

        return self.all_links

    def get_remaining_webpages(self):
        from efficiency.log import fwrite
        from efficiency.function import flatten_list

        with open(self.raw_file) as f:
            data = json.load(f)
        links = data['all_links']
        webpages = data['all_webpages']
        links = flatten_list(links)

        if set(webpages.keys()) != set(links):

            new_links = set(links) - set(data['all_transcripts'].keys())
            self.save_file = 'ted_tmp.json'
            new_webpages = self.get_all_webpages(list(new_links),
                                                 auto_save=False)
            webpages.update(new_webpages)
            data['all_webpages'] = {l: webpages[l] for l in links}
            if set(data['all_webpages'].keys()) == set(links):
                fwrite(json.dumps(data, indent=4), self.raw_file)

    def _save_json(self, only_transcripts=False):
        import json
        from efficiency.log import fwrite

        if only_transcripts:
            data = self.all_transcripts
            file = self.transcript_file
        else:
            data = {
                'all_links': self.all_links,
                'all_webpages': self.all_webpages,
            }
            file = self.raw_file
        fwrite(json.dumps(data, indent=4), file, verbose=False)

    @staticmethod
    def _make_soup(url):
        """
        Return BeautifulSoup instance from URL

        :param str url:
        :rtype: bs4.BeautifulSoup
        """
        try:
            with urlopen(url) as res:
                # print("[DEBUG] in make_soup() : Found: {}".format(url))
                html = res.read()

        except HTTPError as e:
            print("[Error] in make_soup() : Raise HTTPError exception:")
            print("[Error] URL: {} {}".format(url, e))
            return None

        return BeautifulSoup(html, "lxml")

    @staticmethod
    def _get_transcript_url(s, lang="en"):
        """
        Get a link from talk link to transcript
        """
        r1 = "?language=" + lang
        r2 = "/transcript?language=" + lang

        is_match = re.match(".*(\?language=).*", s)
        if is_match:
            t_url = s.replace(r1, r2)
        else:
            t_url = s + r2

        return t_url

    @staticmethod
    def _get_talk_addresses(soup):
        """
        Find the talk link address from talk page
        """
        return soup.find("h4", {"class": "h9"}).find("a").attrs['href']

    def _get_links_from_soup(self, ta_soup):
        """
        Get the link to each talk from the current talk list,
        and return a list of the link
        """
        talk_links = ta_soup.find_all("div", {"class": "talk-link"})
        talk_addresses = [self._get_talk_addresses(tl) for tl in talk_links]
        talk_addresses_full = [urljoin(self.BASE_URL, ta)
                               for ta in talk_addresses]
        return talk_addresses_full

    @staticmethod
    def _get_transcript_from_webpage(webpage, return_list_of_sents=True):
        from lxml import etree
        from efficiency.nlp import NLP

        text_div_head = '<div class="Grid Grid--with-gutter d:f@md p-b:4"'

        if text_div_head not in webpage:
            print('[Error] The webpage does not contain a TED transcript.')
            return ''

        html = etree.HTML(webpage)
        text_elems = html.xpath(
            '//div[@class="Grid Grid--with-gutter d:f@md p-b:4"]//p')
        paras = [i.text for i in text_elems]

        nlp = NLP()
        all_sents = []
        for para in paras:
            words = para.split()
            words = [w for w in words if w]
            text = ' '.join(words)
            sents = nlp.sent_tokenize(text)
            all_sents.extend(sents)
        if return_list_of_sents:
            return all_sents
        else:
            return ' '.join(all_sents)


def main():
    language = 'de'
    language = 'ro'
    language = 'en'
    downloader = TEDTalkDownloader(language)
    links = [
        "https://www.ted.com/talks/edward_tenner_the_paradox_of_efficiency?language=en",
        "https://www.ted.com/talks/alex_gendler_why_doesn_t_the_leaning_tower_of_pisa_fall_over?language=en",
    ]
    downloader.get_all_transcripts(links=links)
    downloader.get_all_transcripts()


if __name__ == '__main__':
    main()
