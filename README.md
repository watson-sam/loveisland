# loveisland

## Install
1. Clone the repo: `git clone git@github.com:watson-sam/loveisland.git`
2. Run `make full`
3. Enjoy!

## Get Twitter Data
To scrape tweets we "bypass" the Twitter API and utilise code from the brilliant 
[GetOldTweets-python](https://github.com/Jefferson-Henrique/GetOldTweets-python) package.
This package hasn't been updated for a long time and to pull it and use natively is 
not ideal (given the number of outstanding PRs/lack of recent updates its fairly stale) so 
I have cloned some of the scripts and adapted as appropriate (these scripts can be found in 
the `pipeline.got3` folder).

Having fulling installed tweets can be scraped for a specific date range (defaults to today
(true at the time of writing however will cap at the end of the series + a week or so when the 
time comes)), alternatively supplying the argument `--yesterday` will return all relevant tweets 
from yesterday. 

As you will see below we use the American date formatting. 
```
python3 venv/bin/get_tweets.py --start_date 2019-06-26 --end_date 2019-06-27
```

## Processing Tweets
We do all the pre-processing of tweets in one go as to only need two versions of the full 
data (raw and processed), in this step we remove all references to "love island" (to try 
and reduce noise in the sentiment analysis), find the sentiment of each tweet and also tag
each tweet with any and all of the islanders it directly references. 
```
python3 venv/bin/preprocess.py --start_date 2019-06-26 --end_date 2019-06-27
```

## Notebooks




### Ideas
- N tweets per day of the week, time of day, date (done)
- N tweets per person -> trended (need to do "Tom" and "Tommy" differently) (done)
- Bigram and trigram analysis (can we pull out couples??)
- Topic models per day, week, all time 
- Most "influential people" (by likes / retweets)
- Sentiment per person (done)
- "Weighted" sentiment (n likes/retweets)
- n pictures ("pic.twitter.com") etc (done)