import sys, json, re, codecs, urllib.parse
import requests as req
from datetime import datetime
from pyquery import PyQuery as pq

from .models import Tweet, TweetCriteria

class Exporter(object):

    def __init__(self, criteria = None, filename = 'tweets_gathered.csv'):
        file_extension = '.'.split(filename)[-1]

        if not file_extension == '.csv':
            self.filename = 'tweets_gathered.csv'
        else:
            self.filename = filename

        self.output = codecs.open(self.filename, 'w+', 'utf-8')

        if not criteria:
            criteria = [
                'date', 'retweets',
                'favorites', 'text',
                'mentions', 'hashtags', 'permalink'
            ]

        criteria_string = ','.join(criteria)

        self.output.write(criteria_string)

    def output_to_file(self, tweets):
        for tweet in tweets:
            format = '\n%s,%s,%s,%s,%s,%s, %s'
            self.output.write((format % \
            (tweet.date_fromtimestamp.strftime('%Y-%m-%d'),\
            tweet.retweets, tweet.favorites, tweet.text,\
            tweet.mentions,tweet.hashtags, tweet.permalink)))
        self.output.flush();
        # print ('%d tweets added to file' % len(tweets))

    def close(self):
        self.output.close()

class Scraper(object):

    def __init__(self):
        pass

    @staticmethod
    def set_headers(data, language, refresh_cursor):
        url = 'https://twitter.com/i/search/timeline?f=realtime&q=%s&src=typd'\
                + '&%smax_position=%s'
        url = url % (urllib.parse.quote(data), language, refresh_cursor)
        headers = {
            'Host': 'twitter.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': url,
            'Connection': 'keep-alive'
        }

        return url, headers

    @staticmethod
    def get_tweets(tweet_criteria, buffer = None, buffer_length = 100):
        active = True
        refresh_cursor = ''
        mentions = re.compile('(@\\w*)')
        hashtags = re.compile('(#\\w*)')
        results = []
        results_to_append = []

        if tweet_criteria.max_tweets <= 0:
            return

        while active:
            json = Scraper.get_json_response(tweet_criteria, refresh_cursor)

            if not json or len(json['items_html'].strip()) == 0:
                break

            refresh_cursor = json['min_position']
            tweets = pq(json['items_html'])('div .js-stream-tweet')

            if len(tweets) == 0:
                break

            for tweetHTML in tweets:
                _ = pq(tweetHTML)


                text = re.sub(r'\s+', ' ', _('p.js-tweet-text').text()\
                        .replace('# ', '#').replace('@ ', '@').replace(',', ''))
                retweet_id = 'span.ProfileTweet-action--retweet '\
                            + 'span.ProfileTweet-actionCount'
                retweets = int(_(retweet_id).attr('data-tweet-stat-count')\
                            .replace(',', ''))
                favorites_id = 'span.ProfileTweet-action--favorite '\
                            + 'span.ProfileTweet-actionCount'
                favorites = int(_(favorites_id).attr('data-tweet-stat-count')\
                            .replace(',', ''))
                href = 'https://twitter.com' + _.attr('data-permalink-path')
                raw_date_ms =  int(_('span.js-short-timestamp')\
                                .attr('data-time'))
                tweet_date = _('span._timestamp .js-short-timestamp').text()

                urls = []
                for link in _('a'):
                    try:
                        urls.append(link.attrib['data-expanded-url'])
                    except:
                        pass

                tweet = Tweet()
                tweet.text = text
                tweet.date = tweet_date
                tweet.raw_date_ms = raw_date_ms
                tweet.date_fromtimestamp = datetime.fromtimestamp(raw_date_ms)
                tweet.formatted_raw_date = datetime.fromtimestamp(raw_date_ms)\
                                            .strftime('%a %b %d %X +0000 %Y')
                tweet.permalink = href
                tweet.retweets = retweets
                tweet.favorites = favorites
                tweet.urls = ','.join(urls)
                tweet.mentions = ' '.join(mentions.findall(tweet.text))
                tweet.hashtags = ' '.join(hashtags.findall(tweet.text))

                results.append(tweet)
                results_to_append.append(tweet)

                if buffer and len(results_to_append) >= buffer_length:
                    buffer(results_to_append)
                    results_to_append = []

                if len(results) >= tweet_criteria.max_tweets:
                    active = False
                    break

        if buffer and len(results_to_append) > 0:
            buffer(results_to_append)

        return results

    @staticmethod
    def get_json_response(tweet_criteria, refresh_cursor):
        data = ''

        if hasattr(tweet_criteria, 'username'):
            data += ' from:' + tweet_criteria.username

        if hasattr(tweet_criteria, 'since'):
            data += ' since:' + tweet_criteria.since

        if hasattr(tweet_criteria, 'until'):
            data += ' until:' + tweet_criteria.until

        if hasattr(tweet_criteria, 'query'):
            data += ' ' + tweet_criteria.query
        else:
            print('No query placed.')
            return

        if hasattr(tweet_criteria, 'language'):
            language = 'lang=' + tweet_criteria.language + '&'
        else:
            language = 'lang=en-US&'

        url, headers = Scraper.set_headers(data, language, refresh_cursor)

        try:
            r = req.get(url, headers=headers)
        except:
            text = 'Twitter weird response. Try to see on browser:'\
                    +'https://twitter.com/search?q=%s&src=typd'
            print(text % urllib.parse.quote(url))
            print('Unexpected error:', sys.exc_info()[0])
            sys.exit()
            return

        return r.json()
