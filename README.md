# loveisland

## Install
1. Clone the repo: `git clone git@github.com:watson-sam/loveisland.git`
2. Run `make full`
3. Enjoy!

## Data Pipeline

### Get Twitter Data
To scrape tweets we "bypass" the Twitter API and utilise code from the brilliant 
[GetOldTweets-python](https://github.com/Jefferson-Henrique/GetOldTweets-python) package.
This package hasn't been updated for a long time and to pull it and use natively is 
not ideal (given the number of outstanding PRs/lack of recent updates it's fairly stale) so 
I have cloned some of the scripts and adapted as appropriate (these scripts can be found in 
the `pipeline.got3` folder).

Having fulling installed, tweets can be scraped for a specific date range by specifying the `--start_date` 
(defaults to a week before season 5 started) and `--end_date` (defaults to 2019-08-05 which is the day after "the reunion") 
alternatively supplying the argument `--yesterday` will return all relevant tweets from yesterday. 

As you can we use the American date formatting as python prefers this. 
```
python3 venv/bin/get_tweets.py --start_date 2019-06-25 --end_date 2019-06-26
```

### Processing Tweets
We do all the pre-processing of tweets in one go per day as we only need two versions of the full 
data (raw and processed), as well as cleaning the text as per the pipeline written up [here](https://medium.com/@watson.sam/100-my-type-on-paper-watching-love-island-via-data-analytics-part-2-fb76dbc87070),
in this step we also remove all references to "love island" (to try and reduce noise in the 
sentiment analysis), find the sentiment of each tweet and also tag each tweet with any and 
all of the islanders it directly references. 
```
python3 venv/bin/preprocess.py --start_date 2019-06-25 --end_date 2019-06-26
```

### Topic Models
Topic Models are calculated per day (ie the corpus is all scraped tweets sent on the same 
date), the script will save the features from "best fitted" model to quickly be able to 
interact with it after being run, also it will create a visual using the `pyLDAvis`
package and export as a HTML.
```
python3 venv/bin/get_topics.py --start_date 2019-06-25 --end_date 2019-06-26
```

### Final Aggregation 
To make the notebooks run a lot quicker and be generally less computing intensive, after collecting
all the data, we run the `src/agg_data.py` script which compiles the relevant data into a much more compact
and easy to use format.
```python3 loveisland/src/agg_data.py --start_date 2019-06-03 --end_date 2019-07-30```


Also in the `src/` folder is a script which scrapes wiki and makes compiling the `constants` a lot quicker.
 
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


- Devicive days (ie recoupling after casa amor) - distirbution per islander to see if two disrtinct gorups (for and against each isaldner)