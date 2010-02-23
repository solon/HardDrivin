'''
get replies
if reply.id is new
    update following list
get user timeline

'''

import twitter, urllib2, simplejson, re, serial
from threading import Timer

# variables

twitter_username = 'hardtestin'
twitter_password = 'lkmkjn'
twitter_api = twitter.Api(twitter_username, twitter_password)
twitter_last_reply_id = 0
twitter_last_tweet_id = 0
twitter_search_uri = 'http://search.twitter.com/search.json?q='
twitter_friendship_exists_uri = 'http://api.twitter.com/1/friendships/exists.json?user_a='+twitter_username+'&user_b='
twitter_friendship_create_uri = 'http://api.twitter.com/1/friendships/create.json?screen_name='
twitter_tweets = []
twitter_following = []

cars = {
    1: {'x-servo':1, 'y-servo':2},
    2: {'x-servo':3, 'y-servo':4},
    3: {'x-servo':5, 'y-servo':6}
}

directions = {
    'S':  {'x-servo-val':90, 'y-servo-val':90},
    'F':  {'x-servo-val':115, 'y-servo-val':90},
    'B':  {'x-servo-val':65, 'y-servo-val':90},
    'FL': {'x-servo-val':115, 'y-servo-val':70},
    'FR': {'x-servo-val':115, 'y-servo-val':100},
    'BL': {'x-servo-val':65, 'y-servo-val':100},
    'BR': {'x-servo-val':65, 'y-servo-val':70}
}

usbport = 'COM12'
ser = serial.Serial(usbport, 115200, timeout=1)

def update(message):
    status = twitter_api.PostUpdate(message)
    print status.text

def get_replies():
    print "getting replies since id %d" % twitter_last_reply_id
    statuses = twitter_api.GetReplies(None, twitter_last_reply_id)
    for status in statuses:
        print status.text
    return statuses

def search(params, trace=False):
    params = urllib2.quote(params)
    json = urllib2.urlopen(twitter_search_uri+params).read()
    results = simplejson.loads(json)['results']
    if (trace):
        trace_search_results(results)
    return results

def trace_search_results(results):
    for r in results:
        print r['id'], r['text']

def is_following(user):
    # check local cache first
    if user in twitter_following:
        return True
    else:
        # no match in cache so check online
        #json = urllib2.urlopen(twitter_friendship_exists_uri+user).read()
        #result = simplejson.loads(json)
        result = twitter_api.IsFollowing(user)
        if result: # update cache -- it's out of date
            twitter_following.append(user)
        return result

def follow(user):
    if is_following(user):
        return True
    else:    
        success = twitter_api.CreateFriendship(user)
        if success:       
            twitter_following.append(user)
            print "now following " + user
        return success

def get_new_tweets():
    return twitter_api.GetFriendsTimeline(twitter_username,since_id=twitter_last_tweet_id)
    
def update_tweets():
    # save id's of tweets already seen, and don't show them again
    temp_tweet_id = 0
    tweets = get_new_tweets()
    newtweets = []
    for t in tweets:
        temp_tweet_id = max(temp_tweet_id, t.id)
        newtweets.append([t.id,t.user.name,t.text])
        
    global twitter_last_tweet_id, twitter_tweets
    twitter_last_tweet_id = max(twitter_last_tweet_id,temp_tweet_id)
    twitter_tweets = newtweets #.extend(twitter_tweets)
    
def get_tweets():
    return twitter_tweets

def show_tweets():
    map(print_tweet,twitter_tweets)
        
def print_tweet(tweet):
    print "%d %s %s" % (tweet[0], tweet[1], tweet[2])
    
    
def get_following():
    return twitter_following;
    
def update_following():
    replies = get_replies()
    pattern = '@' + twitter_username + r"\sfollow\s@(\w{1,20})"
    p = re.compile(pattern, re.IGNORECASE)
    new_users = []
    temp_reply_id = 0
    for r in replies:
        temp_reply_id = max(temp_reply_id,r.id)
        m = p.match(r.text)
        if (m):
            u = m.group(1)
            if not is_following(u):
                new_users.append(u)
                
    print "%d new users to follow" % len(new_users)
    
    if new_users:    
        try:
            map(follow, new_users)
        except urllib2.HTTPError as e:
            print "Error updating follow list"
            print e
            return
            
    global twitter_last_reply_id
    twitter_last_reply_id = max(twitter_last_reply_id, temp_reply_id) 
        
def moveServo(servo, angle):
    '''Moves the specified servo to the supplied angle.

    Arguments:
        servo
          the servo number to command, an integer from 1-6
        angle
          the desired servo angle, an integer from 0 to 180

    (e.g.) >>> servo.move(2, 90)
           ... # "move servo #2 to 90 degrees"'''
    
    if (0 <= angle <= 180):
        ser.write(chr(255))
        ser.write(chr(servo))
        ser.write(chr(angle))
    else:
        print "Servo angle must be an integer between 0 and 180.\n"
    
    
def moveCar(car, direction, duration=500):
    xservo = cars[car]['x-servo']
    yservo = cars[car]['y-servo']
    xval = directions[direction]['x-servo-val']
    yval = directions[direction]['y-servo-val']
    
    # steer first...
    #print "xservo %d %d" % (xservo, xval)
    moveServo(xservo, xval)
    
    # then hit the gas!
    #print "yservo %d %d" % (yservo, yval)
    moveServo(yservo, yval)
    
    # stop the car after given duration
    #print "stopping after %d" % (duration)
    t = Timer(float(duration)/1000, stopCar, [car])
    t.start()
    
def stopCar(car):
    #print "stopping car %d" % car
    xservo = cars[car]['x-servo']
    yservo = cars[car]['y-servo']
    xcentre = directions['S']['x-servo-val']
    ycentre = directions['S']['y-servo-val']
    moveServo(yservo, ycentre)
    moveServo(xservo, xcentre)

if __name__ == "__main__":
    print "Hard Drivin' test script"
    
