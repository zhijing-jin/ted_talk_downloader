# ted_talk_downloader (Python Package)

This is an easy-to-use Python package to download transcripts of TED talks. 

## Installation
**Method 1:** Clone this repo, and follow the instructions in [How To Run](#how-to-run) section.

**Method 2:** Pip install this package by 
```bash
pip install --upgrade git+git://github.com/zhijing-jin/ted_talk_downloader.git
```

**Method 3:** For research use (strictly not commercial), download [this dataset](http://bit.ly/ted-data-zhijing) of all the transcripts of TED talks.
 
The dataset contains all TED talks by Jan 9, 2020. Three lanuages are included, English, German, Romanian. 

Here are some statistics of this dataset:

- English: 3,799 transcripts, 450,326 sentences
- German: 2,625 talks, 338,117 sentences
- Romanian: 2,856 talks, 353,103 sentences
## How to Run

#### Function 1: Download the transcripts for specific talks.
```python
>>> from ted_talk_downloader import TEDTalkDownloader
>>> downloader = TEDTalkDownloader('en')
>>> links = [
             "https://www.ted.com/talks/edward_tenner_the_paradox_of_efficiency?language=en",
             "https://www.ted.com/talks/alex_gendler_why_doesn_t_the_leaning_tower_of_pisa_fall_over?language=en",
     ]
>>> downloader.get_all_transcripts(links=links)
Retrieving Webpages: 100%|███████| 2/2 [00:21<00:00, 11.06s/it]
Parsing HTML: 100%|██████████████| 2/2 [00:02<00:00,  1.97s/it]
[Info] Saved 2 links, 4 transcripts, and 190 sentences to "ted_transcripts.json"

# (1) for transcripts, check out the file `ted_transcripts.json`
# (2) for raw webpages, check out the file `ted_raw.json`
```
#### Function 2: (For Research Use Only) Download transcripts for all talks.
```python
>>> from ted_talk_downloader import TEDTalkDownloader
>>> downloader = TEDTalkDownloader('en')
>>> downloader.get_all_transcripts()
# (1) for transcripts, check out the file `ted_transcripts.json`
# (2) for raw webpages, check out the file `ted_raw.json`
```

## Contact
If you have any questions, feel free to check out the previous [Q&A](https://github.com/zhijing-jin/ted_talk_downloader/issues?utf8=%E2%9C%93&q=is%3Aissue), or raise a new GitHub issue.

In case of really urgent needs, contact the author [Zhijing Jin (Miss)](mailto:zhijing.jin@connect.hku.hk).
