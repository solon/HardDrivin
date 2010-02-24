# TwitterService.py
#
import twitter, urllib2, simplejson, re
        
class TwitterService:
    def __init__(self):
        self.username = 'hardtestin'
        self.password = 'lkmkjn'
        self.api = twitter.Api(self.username, self.password)
        self.last_reply_id = 0
        self.last_tweet_id = 0
        self.search_uri = 'http://search.twitter.com/search.json?q='
        self.friendship_exists_uri = 'http://api.twitter.com/1/friendships/exists.json?user_a='+self.username+'&user_b='
        self.friendship_create_uri = 'http://api.twitter.com/1/friendships/create.json?screen_name='
        self.tweets = []
        self.following = []
    
    def update(self, message):
        status = self.api.PostUpdate(message)
        print status.text

    def get_replies(self):
        print "getting replies since id %d" % self.last_reply_id
        statuses = self.api.GetReplies(None, self.last_reply_id)
        for status in statuses:
            print status.text
        return statuses

    def search(self, params, trace=False):
        params = urllib2.quote(params)
        json = urllib2.urlopen(self.search_uri+params).read()
        results = simplejson.loads(json)['results']
        if (trace):
            self.trace_search_results(results)
        return results

    def trace_search_results(self, results):
        for r in results:
            print r['id'], r['text']

    def is_following(self, user):
        # check local cache first
        if user in self.following:
            return True
        else:
            # no match in cache so check online
            #json = urllib2.urlopen(self.friendship_exists_uri+user).read()
            #result = simplejson.loads(json)
            result = self.api.IsFollowing(user)
            if result: # update cache -- it's out of date
                self.following.append(user)
            return result

    def follow(self, user):
        if self.is_following(user):
            return True
        else:    
            success = self.api.CreateFriendship(user)
            if success:       
                self.following.append(user)
                print "now following " + user
            return success

    def get_new_tweets(self):
        return self.api.GetFriendsTimeline(self.username,since_id=self.last_tweet_id)
        
    def update_tweets(self):
        # save id's of tweets already seen, and don't show them again
        temp_tweet_id = 0
        tweets = self.get_new_tweets()
        newtweets = []
        for t in tweets:
            temp_tweet_id = max(temp_tweet_id, t.id)
            newtweets.append([t.id,t.user.name,t.text])
            
        self.last_tweet_id = max(self.last_tweet_id,temp_tweet_id)
        self.tweets = newtweets #.extend(self.tweets)
        
    def get_tweets(self):
        return self.tweets

    def show_tweets(self):
        map(print_tweet,self.tweets)
            
    def print_tweet(self,tweet):
        print "%d %s %s" % (tweet[0], tweet[1], tweet[2])
        
        
    def get_following(self):
        return self.following;
        
    def update_following(self):
        replies = self.get_replies()
        pattern = '@' + self.username + r"\sfollow\s@(\w{1,20})"
        p = re.compile(pattern, re.IGNORECASE)
        new_users = []
        temp_reply_id = 0
        for r in replies:
            temp_reply_id = max(temp_reply_id,r.id)
            m = p.match(r.text)
            if (m):
                u = m.group(1)
                if not self.is_following(u):
                    new_users.append(u)
                    
        print "%d new users to follow" % len(new_users)
        
        if new_users:    
            try:
                map(self.follow, new_users)
            except urllib2.HTTPError as e:
                print "Error updating follow list"
                print e
                return
            
        self.last_reply_id = max(self.last_reply_id, temp_reply_id) 
