
# TwitterService.py
# v3 : oAuth
#
import tweepy, urllib2, simplejson, re, time, threading, subprocess, OpenSoundControl, yaml, pprint
from sys import stdout
from tweepy.error import TweepError
    
class TwitterService:
  def __init__(self):

    try:
      f = open('settings.yaml')
      self.settings = yaml.load(f)
    except Exception, e:
      error_print( '!!! e: %s' % e )
      error_print( repr(e) )
      exit(1)
      
    try:
      self.auth = tweepy.OAuthHandler(self.settings['consumer_key'], self.settings['consumer_secret'])
      self.auth.set_access_token(self.settings['access_key'], self.settings['access_secret'])
      self.api = tweepy.API(self.auth)
    except TweepError, e:
      error_print( '!!! e: %s' % e )
      error_print( repr(e) )
      exit(1)
    except Exception, e:
      error_print( '!!! e: %s' % e )
      error_print( repr(e) )
      exit(1)
    
    self.username = self.settings['username']
 
    self.last_reply_id = self.settings['last_reply_id']
    self.last_tweet_id = self.settings['last_tweet_id']
    self.last_geo_id = self.settings['last_geo_id']    
    self.last_hashtag_id = self.settings['last_hashtag_id']
    self.status_ids_already_handled = []
    self.tweets = []
    self.following = []
    self.timeout = 6
    self.search_hashtags = self.settings['hashtags']
    self.geoparams = self.settings['geosearch']
    self.interface = OpenSoundControl.Client(self.settings['user_interface']['osc_recv_port'])
    self.display = OpenSoundControl.Client(self.settings['tweet_display']['osc_recv_port'])
    
    
  def start(self):
    
    debug_print("\nlistening...\n") 
    
    while True:
    
      #debug_print(".",; stdout.flush())
      
      # GET NEW FOLLOWS
      self.update_following()
      
      # GET NEW TWEETS FROM FOLLOWED USERS

      self.update_tweets()
      
      # GET NEW NEARBY TWEETS
      r = self.geo_search()
      if r:
        self.handle_new_geo_tweets(r)
      
      # GET NEW HASHTAG TWEETS
      for hashtag in self.search_hashtags:
        r = self.hashtag_search(hashtag)
        if r:
          self.handle_new_hashtag_tweets(hashtag,r)

      self.interface.send('/status','OK')
      
      self.settings_changed = False
      
      if (self.settings['last_reply_id'] < self.last_reply_id):
        self.settings['last_reply_id'] = self.last_reply_id
        self.settings_changed = True
      if (self.settings['last_tweet_id'] < self.last_tweet_id):
        self.settings['last_tweet_id'] = self.last_tweet_id
        self.settings_changed = True
      if (self.settings['last_geo_id'] < self.last_geo_id):
        self.settings['last_geo_id'] = self.last_geo_id
        self.settings_changed = True
      if (self.settings['last_hashtag_id'] < self.last_hashtag_id):
        self.settings['last_hashtag_id'] = self.last_hashtag_id
        self.settings_changed = True
      
      if (self.settings_changed):
        if (self.save_settings()):
          self.settings_changed = False
    
      time.sleep(self.timeout)
    
  def update(self, message):
    try:
      status = self.api.PostUpdate(message)
    except TweepError, e:
      error_print( '!!! e: %s' % e )
      error_print( repr(e) )
      status = False
      
    if (status):
      debug_print(status.text)
      
  def get_replies(self):
    debug_print("getting replies since id %d" % self.last_reply_id)
    replies = None
    
    try:
      replies = self.api.GetReplies(None, self.last_reply_id)
    except IOError, e:
    #  if hasattr(e, 'reason'):
    #      print '!!! Can\'t reach server.', e.reason
    #  elif hasattr(e, 'code'):
    #      print '!!! Server couldn\'t fulfil request:', e.code  
      error_print ('!!! Server couldn\'t fulfil request: %s' % e.code)
    return replies

  def geo_search(self):
    try:
      info_print('~~~ looking for tweets within %(radius)s of %(lat)s, %(lng)s' % self.geoparams)
      results = self.api.search(lang='en', geocode="%(lat)s,%(lng)s,%(radius)s" % self.geoparams)
      self.trace_search_results(results)
      return results
    except TweepError, e:
      if hasattr(e, 'reason'):
        error_print( '!!! Can\'t reach server. %s' % e.reason )
      elif hasattr(e, 'code'):
        error_print ('!!! Server couldn\'t fulfil request: %s' % e.code)
      return False
    
  def hashtag_search(self, terms):
    try:
      info_print("### searching for tweets with hashtag "+terms+" since id %d" % self.last_hashtag_id)
      results = self.api.search(terms, lang='en', since_id=self.last_hashtag_id)
      self.trace_search_results(results)
      return results
    except TweepError, e:
      if hasattr(e, 'reason'):
        error_print( '!!! Can\'t reach server. %s' % e.reason )
      elif hasattr(e, 'code'):
        error_print ('!!! Server couldn\'t fulfil request: %s' % e.code)
      return False

  def trace_search_results(self, results):
    for r in results:
      debug_print("%d " % r.id + r.text)

  def is_following(self, user):
    # check local cache first
    if user in self.following:
      return True
    else:
      # no match in cache so check online
      result = None
      try:
        result = self.api.exists_friendship(self.username, user)
      except TweepError, e:
        if hasattr(e, 'reason'):
          error_print( '!!! Can\'t reach server. %s' % e.reason )
        elif hasattr(e, 'code'):
          error_print ('!!! Server couldn\'t fulfil request: %s' % e.code)
      else:
        # everything is fine
        if result: # update cache -- it's out of date
          self.following.append(user)
      
      return result

  def follow(self, user):
    success = None
    if self.is_following(user):
      return True
    else:  
      try:
        success = self.api.create_friendship(user)
      except TweepError, e:
        if hasattr(e, 'reason'):
          error_print( '!!! Can\'t reach server. %s' % e.reason )
        elif hasattr(e, 'code'):
          error_print ('!!! Server couldn\'t fulfil request: %s' % e.code)
      else:
        if success:     
          self.following.append(user)
          info_print('+++ Now following @%s' % user)
    return success

  def get_new_tweets(self):
    try:
      #debug_print("*** looking for new tweets from users since id %d" % self.last_tweet_id)
      return self.api.friends_timeline(since_id=self.last_tweet_id)
    except TweepError, e:
      if hasattr(e, 'reason'):
        error_print( '!!! Can\'t reach server. %s' % e.reason )
      elif hasattr(e, 'code'):
        error_print ('!!! Server couldn\'t fulfil request: %s' % e.code)
      else:
        print '!!! e: %s' % e
        print repr(e)
      return False

  def update_tweets(self):
    info_print(">>> looking for new tweets from followed users since id %d" % self.last_tweet_id)    
    # save id's of tweets already seen, and don't show them again
    temp_tweet_id = 0
    tweets = self.get_new_tweets()
    newtweets = []
    if tweets:
      self.handle_new_followed_tweets(tweets)
      for t in tweets:
        #debug_print("inside update_tweets, checking t.id=" + t.id)
        temp_tweet_id = max(temp_tweet_id, t.id)
        newtweets.append([t.id,t.user.name,t.text])
      
    #print "last_tweet_id: %d " % self.last_tweet_id + "temp_tweet_id: %d" % temp_tweet_id  
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
    info_print('@@@ looking for new people to follow') 
    replies = False
    try:
      replies = self.api.mentions(since_id=self.last_reply_id)
    except TweepError, e:
      error_print( '!!! e: %s' % e )
      error_print( repr(e) )
    except Exception, e:
      print ( '!!! e: %s' % e )
      print ( repr(e) )
 
    if (replies):
      pattern = '@' + self.username + r"\sfollow\s@(\w{1,20})$"
      p = re.compile(pattern, re.IGNORECASE)
      new_users = []
      temp_reply_id = 0
      for r in replies:
        
        #debug_print("Checking reply: " + r.text)
        temp_reply_id = max(temp_reply_id,r.id)
        m = p.match(r.text)
        if (m):
          #debug_print("Found a follow command: " + r.text)
          u = m.group(1)
          try:
            # check it's actually a Twitter user
            if self.api.get_user(u):
              if not self.is_following(u):
                #debug_print("About to follow: " + u)
                new_users.append(u)
              else:
                debug_print("--- Already following @%s" % u)
          except TweepError, e:
            debug_print("!!! No user found: %s" % u)
            
      if new_users:  
        debug_print("%d new users added to follow" % len(new_users))
        try:
          map(self.follow, new_users)
        except urllib2.HTTPError as e:
          error_print("Error updating follow list")
          error_print(e)
          return        
      self.last_reply_id = max(self.last_reply_id, temp_reply_id) 
      
  def handle_new_followed_tweets(self, statuses):
    count = 0
    for s in statuses:
      #debug_print("inside handle_new_followed_tweets, s.id = %d" % s.id)
      id = s.id
      if id not in self.status_ids_already_handled:
        self.status_ids_already_handled.append(id)
        if (count == 0): 
          info_print("")
          
        user = s.user.screen_name.encode('ascii', 'ignore')
        text = s.text.encode('ascii', 'ignore')
        
        info_print(">>> @%s\n    %s\n" % (user, text))
        self.interface.send('/tweet',[user, len(text), text])
        self.display.send('/tweet',[user, len(text), text])
        
        count = count + 1
        time.sleep(2.25)
        
  def handle_new_hashtag_tweets(self, hashtag, results):
    debug_print("handling hashtag tweets")
    temp_hashtag_id = 0
    count = 0
    for r in results:
      id = r.id
      if id not in self.status_ids_already_handled:
        self.status_ids_already_handled.append(id)
        if (count == 0): 
          info_print("")
          
        user = r.from_user.encode('ascii', 'ignore')
        text = r.text.encode('ascii', 'ignore')
        
        info_print("### @%s\n    %s\n" % (user, text))
        self.interface.send('/tweet',[user, len(text), text])
        self.display.send('/tweet',[user, len(text), text])
        
        temp_hashtag_id = max(temp_hashtag_id, id)
        self.last_hashtag_id = max(self.last_hashtag_id,temp_hashtag_id)
        
        count = count + 1
        time.sleep(3)


  def handle_new_geo_tweets(self, results):
    debug_print("handling nearby tweets")
    temp_geo_id = 0
    count = 0
    for r in results:
      id = r.id
      if id not in self.status_ids_already_handled:
        self.status_ids_already_handled.append(id)
        if (count == 0): 
          info_print("")

        user = r.from_user.encode('ascii', 'ignore')
        text = r.text.encode('ascii', 'ignore')

        info_print("~~~ @%s\n    %s\n" % (user, text))
        self.interface.send('/tweet',[user, len(text), text])
        self.display.send('/tweet',[user, len(text), text])

        temp_geo_id = max(temp_geo_id, id)
        self.last_geo_id = max(self.last_geo_id,temp_geo_id)

        count = count + 1
        time.sleep(1.5)

                
  def save_settings(self):
    debug_print("Saving settings...")
    try:
      stream = file('settings.yaml','w')
      yaml.dump(self.settings, stream)
      return True
    except Exception, e:
      error_print( '!!! e: %s' % e )
      error_print( repr(e) )
      return False

def error_print(msg):
  if PRINT_ERROR:
    print msg.encode('ascii', 'ignore')

def debug_print(msg):
  if PRINT_DEBUG:
    print msg.encode('ascii', 'ignore')

def info_print(msg):
  if PRINT_INFO:
    print msg.encode('ascii', 'ignore')
    

if __name__ == "__main__":

    print ""
    print "    __ __             __  ___      _       _      _ "
    print "   / // /___ ________/ / / _ \____(_)_  __(_)___ ( )"
    print "  / _  // _ `/ __/ _  / / // / __/ /| |/ / // _ \|/ "
    print " /_//_/ \_,_/_/  \_,_/ /____/_/ /_/ |___/_//_//_/   "
    print ""
    print " ___       ___  ___ ___   __   __       ___  __   __       "
    print "  |  |  | |__  |__   |   /  ` /  \ |\ |  |  |__) /  \ |    "
    print "  |  |/\| |___ |___  |   \__, \__/ | \|  |  |  \ \__/ |___ " 
    print ""
    
    PRINT_ERROR = True
    PRINT_DEBUG = False
    PRINT_INFO = True
    
    ts = TwitterService()
    ts.start()
