import random
import math
import site
import MySQLdb
import Cookie
import cookielib
import hashlib

site.addsitedir('/srv/http/wsgi')
import goconfig

# Determine if a user is appropriately validated through LDAP.
def user_logged_in( environ ):
  cookie = Cookie.SimpleCookie()
  
  # if the environment contains a cookie, check it out
  if environ.has_key('HTTP_COOKIE'):
    if cookie.has_key('user'):
      # load the cookie we found
      cookie.load(environ['HTTP_COOKIE']);
      user_hash = cookie['user'].value
      # see if it's in the database
      mdb,cursor = connect_to_mysql()
      cursor.execute("""SELECT count(*) FROM `%s` WHERE `user_hash`='%s';""" % 
        (goconfig.sql_usr_table, user_hash) )
      ((num_rows,),) = cursor.fetchall()
      
      mdb.commit()
      mdb.close()
      
      return num_rows > 0
      
  
  return False


# Log in a user by placing a cookie on their machine and entering
# the related hash in a SQL database.
def generate_cookie( user ):
  hashed_value = hashlib.sha512( user + goconfig.hash_salt ).hexdigest()
  cookie = Cookie.SimpleCookie()
  cookie["user"] = hashed_value
  cookie["user"]["expires"] = ""
  cookie["user"]["path"] = "/"
  return cookie


# Register the user in the table of active users.
def activate_user( hash_value ):
  mdb,cursor = connect_to_mysql()
  cursor.execute( """INSERT INTO `%s` (user_hash) VALUES ('%s');""" %
    (goconfig.sql_usr_table, hash_value) )
  mdb.commit()
  mdb.close()


# Unregister the user in the table of active users.
def deactivate_user( hash_value ):
  mdb, cursor = connect_to_mysql()
  cursor.execute( """DELETE FROM `%s` WHERE `user_hash`='%s';""" %
    (goconfig.sql_usr_table, hash_value) )
  mdb.commit()
  mdb.close()


# Connect to a mySQL database and return a pointer to that database.
def connect_to_mysql():
  # Connect to and choose the database.
  mdb = MySQLdb.connect(
    goconfig.sql_domain,
    goconfig.sql_usr,
    goconfig.sql_pasw,
    goconfig.sql_db )
  cursor = mdb.cursor()
  
  # If we need to create the urls table, then construct it.
  cursor.execute("""CREATE TABLE IF NOT EXISTS %s(
  id INT NOT NULL AUTO_INCREMENT, 
  PRIMARY KEY(id), 
  longurl VARCHAR(100), 
  shorturl VARCHAR(100),
  clicks INT(10))""" % goconfig.sql_url_table)

  cursor.execute("""CREATE TABLE IF NOT EXISTS %s(
  id INT NOT NULL AUTO_INCREMENT, 
  PRIMARY KEY(id), 
  user_hash VARCHAR(500))""" % goconfig.sql_usr_table)
  
  return mdb, cursor


# Given a dictionary and a set of relevant entries, this procedure 
# removes all irrelevant entries, effectively trimming the noise level
def trim_noise( dictionary, relevant_keys ):
  marked_for_removal = []
  
  for key in dictionary:
    if key not in relevant_keys:
      marked_for_removal.append( key )
  for item in marked_for_removal:
    del dictionary[item]


# Parse post data submitted to this function. That is, split it up as a
# dictionary and return that readable dictionary.
def parse_post_data( post_data ):
  delimiter = "&"
  subdelimiter = "="
  
  # read stream to a list
  data = post_data.read()
  
  if len( data ) > 0:
    
    # create a dictionary as {field:val, field:val, ... }
    data = dict( item.split(subdelimiter) for item in data.split( delimiter ) )
    
    # return the dictionary of data
    return data
  
  # if there is no data, return an empty result
  return None


# Generate a random short url from a list of possible characters
# and the minimum allowed length.
def generate_short_url( long_url ):
  decimal = 10
  encoding = 62
  
  # determine the range of possible values (set by goconfig.min_url_len)
  min_val = encoding ** (goconfig.min_url_len - 1)
  max_val = (encoding ** goconfig.min_url_len) - 1
  
  # generate the short url (some val between min and max)
  value = random.randint( min_val, max_val )
  
  # Encode the short url value in the most appropriate base.
  short = []
  
  # define the list of possible characters
  charlist = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
  
  while value > 0:
    short.append(charlist[ int(value % encoding) ])
    value = math.floor( value / encoding )
  
  return ''.join( short )


# This function should return true if the specified short_url
# already exists in the mySQL database. This prevents overlapping.
def short_url_exists( short_url ):
  mdb, cursor = connect_to_mysql()
  output = cursor.execute( 
  """ SELECT * from """ + goconfig.sql_url_table +
  """ WHERE shorturl = %s """, (short_url))
  output = True if output > 0 else False
  mdb.commit()
  mdb.close()
  return output


# Inserts a short-url, long-url pairing into the database.
def register_url( longurl, shorturl ):
  mdb, cursor = connect_to_mysql()
  cursor.execute("""INSERT INTO `%s`(`id`, `longurl`, `shorturl`, `clicks`) VALUES
  (NULL, '%s', '%s', '0')""" % (goconfig.sql_url_table, longurl, shorturl))
  mdb.commit()
  mdb.close()
