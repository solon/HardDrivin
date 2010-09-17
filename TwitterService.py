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
      print 'e: %s' % e
      print repr(e)
      exit(1)
      
    try:
      self.auth = tweepy.OAuthHandler(self.settings['consumer_key'], self.settings['consumer_secret'])
      self.auth.set_access_token(self.settings['access_key'], self.settings['access_secret'])
      self.api = tweepy.API(self.auth)
    except TweepError, e:
      print 'e: %s' % e
      print repr(e)
      exit(1)
    except Exception, e:
      print 'e: %s' % e
      print repr(e)
      exit(1)
    
    self.username = self.settings['username']
 
    self.last_reply_id = self.settings['last_reply_id']
    self.last_tweet_id = self.settings['last_tweet_id']
    self.last_hashtag_id = self.settings['last_hashtag_id']
    self.status_ids_already_handled = []
    self.tweets = []
    self.following = []
    self.timeout = 6
    self.search_hashtags = self.settings['hashtags']
    self.interface = OpenSoundControl.Client(self.settings['user_interface']['osc_recv_port'])
    self.display = OpenSoundControl.Client(self.settings['tweet_display']['osc_recv_port'])
    
    
  def start(self):
    
    '''
    if replies:
          for reply in replies:
              print reply.text
              self.interface.send("/@%s" % self.username, reply.text)
    '''
    
    debug_print("\nlistening...\n") 
    while True:
      #debug_print(".",; stdout.flush())
      
      debug_print(chr(176) + 'looking for new people to follow') 
      self.update_following()
      
      debug_print(chr(176) + 'looking for new tweets from followed users') 
      r = self.get_new_tweets()
      if r:
        self.handle_new_followed_tweets(r)
      
      debug_print(chr(176) + 'looking for tweets with hashtags ( %s )' % ", ".join(self.search_hashtags))
      for hashtag in self.search_hashtags:
        debug_print("searching for tweets with hashtag %s" % hashtag)
        r = self.search(hashtag, self.last_hashtag_id)
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
      print 'e: %s' % e
      print repr(e)
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
    #      print 'Can\'t reach server.', e.reason
    #  elif hasattr(e, 'code'):
    #      print 'Server couldn\'t fulfil request:', e.code  
      print 'Server couldn\'t fulfil request:', e.code
    return replies
    
  def search(self, terms, since_id_param):
    try:
      debug_print("searching for tweets with hashtag "+terms+" since id %d" % since_id_param)
      results = self.api.search(terms, since_id=since_id_param)
      self.trace_search_results(results)
      return results
    except TweepError, e:
      if hasattr(e, 'reason'):
          print 'Can\'t reach server.', e.reason
      elif hasattr(e, 'code'):
          print 'Server couldn\'t fulfil request:', e.code
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
            print 'Can\'t reach server.', e.reason
        elif hasattr(e, 'code'):
            print 'Server couldn\'t fulfil request:', e.code
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
            print 'Can\'t reach server.', e.reason
        elif hasattr(e, 'code'):
            print 'Server couldn\'t fulfil request:', e.code
      else:
        if success:     
          self.following.append(user)
          print chr(219) % 'following @' % user
    return success

  def get_new_tweets(self):
    try:
      debug_print("looking for new tweets from users since %d" % self.last_tweet_id)
      return self.api.friends_timeline(since_id=self.last_tweet_id)
    except TweepError, e:
      if hasattr(e, 'reason'):
          print 'Can\'t reach server.', e.reason
      elif hasattr(e, 'code'):
          print 'Server couldn\'t fulfil request:', e.code
      else:
        print 'e: %s' % e
        print repr(e)
      return False

  def update_tweets(self):
    # save id's of tweets already seen, and don't show them again
    temp_tweet_id = 0
    tweets = self.get_new_tweets()
    newtweets = []
    for t in tweets:
      debug_print("inside update_tweets, checking t.id=" + t.id)
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
    replies = False
    try:
      replies = self.api.mentions()
    except TweepError, e:
      print 'e: %s' % e
      print repr(e)
    except Exception, e:
      print 'e: %s' % e
      print repr(e)
 
    if (replies):
      pattern = '@' + self.username + r"\sfollow\s@(\w{1,20})"
      p = re.compile(pattern, re.IGNORECASE)
      new_users = []
      temp_reply_id = 0
      for r in replies:
        #debug_print("Checking reply: " + r.text)
        temp_reply_id = max(temp_reply_id,r.id)
        m = p.match(r.text)
        if (m):
          u = m.group(1)
          if not self.is_following(u):
            new_users.append(u)
      if new_users:  
        debug_print("%d new users added to follow" % len(new_users))
        try:
          map(self.follow, new_users)
        except urllib2.HTTPError as e:
          print "Error updating follow list"
          print e
          return        
      self.last_reply_id = max(self.last_reply_id, temp_reply_id) 
      
  def handle_new_followed_tweets(self, statuses):
    count = 0
    for s in statuses:
      debug_print("inside handle_new_followed_tweets, s.id = %d" % s.id)
      id = s.id
      if id not in self.status_ids_already_handled:
        self.status_ids_already_handled.append(id)
        if (count == 0): 
          debug_print("")
          
        user = s.user.screen_name.encode('ascii', 'ignore')
        text = s.text.encode('ascii', 'ignore')
        
        debug_print(chr(219) + "@%s\n" % user + chr(32) + text + "\n\n")
        self.interface.send('/tweet',[user, len(text), text])
        self.display.send('/tweet',[user, len(text), text])
        
        count = count + 1
        time.sleep(1.5)
        
  def handle_new_hashtag_tweets(self, hashtag, results):
    debug_print("handling hashtag tweets")
    temp_hashtag_id = 0
    count = 0
    for r in results:
      id = r.id
      if id not in self.status_ids_already_handled:
        self.status_ids_already_handled.append(id)
        if (count == 0): 
          debug_print("")
          
        user = r.from_user.encode('ascii', 'ignore')
        text = r.text.encode('ascii', 'ignore')
        
        debug_print(chr(177) + "@%s\n " % user + text + "\n\n")
        self.interface.send('/#%s' % hashtag,[user, len(text), text])
        self.display.send('/#%s' % hashtag,[user, len(text), text])
        
        temp_hashtag_id = max(temp_hashtag_id, id)
        self.last_hashtag_id = max(self.last_hashtag_id,temp_hashtag_id)
        
        count = count + 1
        time.sleep(0.5)
        
          
        
  def save_settings(self):
    debug_print("Saving settings...")
    try:
      stream = file('settings.yaml','w')
      yaml.dump(self.settings, stream)
      return True
    except Exception, e:
      print 'e: %s' % e
      print repr(e)
      return False

def debug_print(msg):
  if DEBUG:
    print msg
    
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
    
    DEBUG = True
    ts = TwitterService()
    ts.start()