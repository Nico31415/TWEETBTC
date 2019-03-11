import sys, getopt, datetime
import os, csv

from scraper import controllers, models

def getTwitterData(start_date, end_date, max_per_day, hashtag, main_file = 'tweets_gathered.csv'):
    run = True
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    step = datetime.timedelta(days=1)

    while (start <= end):
        start_date = str(start.date())
        print("Processing: %s" % (start_date))
        end_date = str((start + step).date())
        tweet_criteria = models.TweetCriteria()
        tweet_criteria.since = start_date
        tweet_criteria.until = end_date
        tweet_criteria.query = hashtag
        tweet_criteria.max_tweets = int(max_per_day)

        exporter = controllers.Exporter()
        miner = controllers.Scraper()
        miner.get_tweets(tweet_criteria, buffer = exporter.output_to_file, buffer_length=int(max_per_day))
        exporter.close()

        with open('tweets_gathered.csv') as f:
          num_lines = sum(1 for line in f)
        if(num_lines > 1):
          if(run):
            fout = open(main_file, "w")
            for line in open("tweets_gathered.csv"):
              fout.write(line)
          else:
            fout=open(main_file,"a")
            f = open("tweets_gathered.csv")
            for line in f.readlines()[1:]:
              fout.write(line)
              f.close()
          fout.close()
          run = False

        start += step


getTwitterData('2016-01-01', '2019-01-01', 200, 'bitcoin')


    # except:
    #     text = 'Unexpected error. Please try again. For more information on'\
    #         + ' how to use this script, use the -help argument.'
    #     print(text)

# if __name__ == '__main__':
#     main(sys.argv[1:])
