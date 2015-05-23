Taiga contrib FAS OpenID auth
=========================

The Taiga plugin for FAS (Fedora Account System) authentication.

Flow diagram
------------

Roughly, this is how it works

```
taiga-front             taiga-back         fedoauth
---------------------------------------------------

 add a FAS
  button
    |
    V
  click  -----ajax------> auth?
                           |
  hidden <----html---------*
form, auto
  submit -----POST-------------------------> auth?
                                               |
                   verify and store <---POST---*
                    user in the db
                           |
  verify <----302----------*
and update
the UI to
say welcome!
```

Installation
------------

### Taiga Back

In your Taiga back python virtualenv install the pip package `taiga-contrib-fas-openid-auth` with:

```bash
  pip install taiga-contrib-fas-openid-auth
```

Modify your settings/local.py and include the line:

```python
  INSTALLED_APPS += ["taiga_contrib_fas_openid_auth"]

  REST_FRAMEWORK = {
      # We monkey patch the rest_framework exception handler to allow us to do
      # the 302 redirects that we need to do for openid to finish.
      "EXCEPTION_HANDLER": "taiga_contrib_fas_openid_auth.services.exception_handler",
  }
```

### Taiga Front

Download in your `dist/js/` directory of Taiga front the `taiga-contrib-fas-openid-auth` compiled code:

```bash
  cd dist/js
  wget "https://raw.githubusercontent.com/taigaio/taiga-contrib-fas-openid-auth/$(pip show taiga-contrib-fas-openid-auth | awk '/^Version: /{print $2}')/front/dist/fas_openid_auth.js"
```

Download in your `dist/images/contrib` directory of Taiga front the `taiga-contrib-fas-openid-auth` Fedora icon:

```bash
  cd dist/images/contrib
  wget "https://raw.githubusercontent.com/taigaio/taiga-contrib-fas-openid-auth/$(pip show taiga-contrib-fas-openid-auth | awk '/^Version: /{print $2}')/front/images/contrib/fedora-logo.png"
```

Include in your dist/js/conf.json in the contribPlugins list the value `"/js/fas_openid_auth.js"`:

```json
...
    "contribPlugins": ["/js/fas_openid_auth.js"]
...
```
