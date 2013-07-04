# 人人Python SDK

Renrenpy 是人人 API 的一个第三方 Python SDK 。使用 OAuth 2 验证并提供了 API
的调用方法。

## OAuth2.0

首先在[人人开放平台](http://dev.renren.com)上申请开发者账户并新建应用。 SDK
需要应用的 App Key 和 Key Secret 。 SDK 还需要一个授权后重定向地址。

```python
from renren import APIClient
    
APP_KEY = "YOUR_APP_KEY"            # app key
APP_SECRET = "YOUR_APP_SECRET"      # app secret
REDIRECT_URI = "YOUR_REDIRECT_URI"  # redirect uri
```

然后用如下方式获取授权地址：

```python
client = APIClient(app_key=YOUR_APP_KEY, app_secret=YOUR_APP_SECRET,
                   redirect_uri=YOUR_REDIRECT_URI)
url = client.get_authorize_url()    # redirect the user to `url'
```

`get_authorize_url(scope=None, force_relogin=False)` 有两个额外参数。 scope
是应用权限列表，默认为人人默认的应用权限。可以自行添加，如
`["status_update", "photo_upload", "read_user_status"]` 。 若将 `force_relogin` 设为 `True` ，则授权页会强制用户重新登录。

授权完毕后，用户将会被转至 `YOUR_REDIRECT_URI` 。请求中有参数
`code=AUTHORIZATION_CODE` 。之后可以用 `AUTHORIZATION_CODE` 换取 access
token 。

```python
r = client.request_access_token(AUTHORIZATION_CODE)
access_token = r["access_token"]  # access token
client.set_access_token(access_token)
```

至此授权完毕。之后可以用 API client 来调用 API 。

## 调用 API

API 可在[人人 API 文档](http://wiki.dev.renren.com/wiki/API)中找到。 SDK 中的 APIClient 类对所有 API 提供了同名方法。通用参数(`v`, `access_token`, `call_id`)及 `method` 参数均由APIClient提供， `format` 参数默认为 `JSON` 。调用时只需提供其它必需参数。

例如：

```python
print client.users.getInfo()
print client.users.getLoggedInUser()
print client.users.getVisitors()
print client.friends.search(name=u"成龙")
print client.status.set(status="test")
print client.status.gets()
```

SDK 也支持上传照片 (photos.upload)

```python
f = open("test.png", "rb")
r = client.photos.upload(upload=f)
f.close()  # you need to do this manually
```

注意 `upload` 参数必须是个 file-like 对象。


# Renrenpy

A Python SDK for Renren open platform which provides OAuth 2 authentication and API wrapper. 

Inspired from [Sinaweibopy](https://github.com/michaelliao/sinaweibopy).

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
client.set_access_token(access_token)
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

Notice that the `upload` parameter only accepts file-like objects.
