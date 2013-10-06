import ldap
import site
import Cookie
import cookielib

site.addsitedir('/srv/http/wsgi')
import library
import goconfig


def application(environ, start_response):

  # Set default "empty page" text.
  body = ["<p>Nothing here.</p>"]

  # If the page was requested via POST, that means the URL-input 
  # form was submitted. Scan over the input data, parse it, validate
  # it, and then finally connect to the DB and store it. Then output.
  if environ["REQUEST_METHOD"] == "POST":
    
    # Grab user data, cut off non-relevant fields.
    data = environ['wsgi.input']
    data = library.parse_post_data( data )
    
    # Determine the user credentials to authenticate.
    usr = data['usr']
    psw = data['pass']
    bind = 'uid='+usr+',ou=people,o=gmu.edu'
    
    success = False # authentication success

    # Try to talk with the LDAP server.
    ldap.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    try:
      ld = ldap.initialize( goconfig.ldap_domain )
      result = ld.simple_bind_s( bind, psw )
      if result is not None:
        success = True
    except ldap.INVALID_CREDENTIALS:
      pass
    except ldap.INAPPROPRIATE_AUTH:
      pass
    except ldap.NO_SUCH_OBJECT:
      pass
    
    if( success ):
      # create a hashed cookie
      cookie = library.generate_cookie(usr)
      cookie_value = cookie["user"].OutputString()
      hash_value = cookie["user"].value
      
      # unregister the user, in case they're already in
      library.deactivate_user( hash_value )
      # register the hashed user with the SQL database
      library.activate_user( hash_value )
      
      # push the cookie to the user and redirect
      status = '303 See Other'
      response_headers = [('Set-Cookie', cookie_value),
                          ('Location', '/'),
                          ('Content-type', 'text/plain')]
      start_response(status, response_headers)
      return [ str(cookie) ]
    else:
      body = ["<p>Error: invalid username or password.</p>"]
  
  # Read and store in memory the header and footer sections 
  # of the page display.
  f = open(goconfig.doc_root + "/site_data/top.part", "r")
  top_part = f.read()
  f.close()
  
  f = open(goconfig.doc_root + "/site_data/bottom.part", "r")
  bottom_part = f.read()
  f.close()
  
  # Construct the HTML output using the wrapper and body data.
  body = ''.join( body )
  response = top_part + body + bottom_part
  
  # Do web-stuff
  status = '200 OK'
  response_headers = [('Content-type', 'text/html'),
                      ('Content-Length', str(len(response)))]
  start_response(status, response_headers)
  
  return [response]
