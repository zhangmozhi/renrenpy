# Renrenpy

A Python SDK for Renren open platform which provides OAuth 2 authentication and API wrapper. 

Inspired by [Sinaweibopy](https://github.com/michaelliao/sinaweibopy).

## OAuth2.0

After setting up your [Renren developer account](http://dev.renren.com) and
registering for an application, you will receive `YOUR_APP_KEY` and
`YOUR_APP_SECRET`, which are required for the SDK.  You also needs to provide `YOUR_REDIRECT_URI`

```python
from renren import APIClient
    
APP_KEY = "YOUR_APP_KEY"            # app key
APP_SECRET = "YOUR_APP_SECRET"      # app secret
REDIRECT_URI = "YOUR_REDIRECT_URI"  # redirect uri
```

Then redirect the user to the following authorization URL:

```python
client = APIClient(app_key=YOUR_APP_KEY, app_secret=YOUR_APP_SECRET,
                   redirect_uri=YOUR_REDIRECT_URI)
url = client.get_authorize_url()    # redirect the user to `url'
```

There are two additional keyword parameters for `get_authorize_url()`, 
`scope` and `force_relogin`.  `scope` is a list of additional permissions 
for your application, e.g. `["status_update", "photo_upload",
"read_user_status"]`.  When `force_relogin` is set to `True`, the 
user is forced to relogin to authorize.

After granting the privileges, the user will be redirected to
`YOUR_REDIRECT_URI`, with parameter `code=AUTHORIZATION_CODE`. 
You can get access token using `AUTHORIZATION_CODE`.

```python
r = client.request_access_token(AUTHORIZATION_CODE)
access_token = r["access_token"]  # access token
expires_in = r["expires_in"]      # token expires time
client.set_access_token(access_token, expires_in)
```

Now you can call Renren API using the API client.

## How to call a particular API

The APIs are listed at [Renren API Documentation]
(http://wiki.dev.renren.com/wiki/API).
You can call an API by calling an authorized API clients' attribute that
has the same name with the API.  The general parameters(`v`,
`access_token`, `call_id`) and `method` parameter are supplied by the API
client.  The `format` parameter is by default `JSON` as recommended by
Renren.

For example, 
```python
print client.users.getInfo()
print client.users.getLoggedInUser()
print client.users.getVisitors()
print client.friends.search(name=u"成龙")
print client.status.set(status="test")
print client.status.gets()
```

As for uploading pictures:

```python
f = open("test.png", "rb")
r = client.photos.upload(upload=f)
f.close()  # you need to do this manually
```

The upload parameter only accepts file-like objects.
