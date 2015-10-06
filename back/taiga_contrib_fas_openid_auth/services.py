# Copyright (C) 2014 Andrey Antukh <niwi@niwi.be>
# Copyright (C) 2014 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2015 Ralph Bean <rbean@redhat.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import urllib.parse

from django.db import transaction as tx
from django.apps import apps

from taiga.auth.services import send_register_email
from taiga.auth.services import make_auth_response_data
from taiga.auth.signals import user_registered as user_registered_signal

# Are we interested in any groups for this?  How about this for now?
groups = ['sysadmin-releng', 'sysadmin-main']

@tx.atomic
def fas_register(username, full_name, email):
    """
    Register a new user from FAS.

    This can raise `exc.IntegrityError` exceptions in
    case of conflics found.

    :returns: User
    """

    auth_data_model = apps.get_model("users", "AuthData")
    user_model = apps.get_model("users", "User")

    try:
        # Github user association exist?
        auth_data = auth_data_model.objects.get(key="fas-openid", value=username)
        user = auth_data.user
    except auth_data_model.DoesNotExist:
        try:
            # Is a user with the same email as the FAS user?
            user = user_model.objects.get(email=email)
            auth_data_model.objects.create(user=user, key="fas-openid", value=username, extra={})
        except user_model.DoesNotExist:
            # Create a new user
            user = user_model.objects.create(email=email,
                                             username=username,
                                             full_name=full_name)
            auth_data_model.objects.create(user=user, key="fas-openid", value=username, extra={})

            send_register_email(user)
            user_registered_signal.send(sender=user.__class__, user=user)

    return user


import taiga.base.exceptions
import django.http
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied


class SneakyRedirectException(taiga.base.exceptions.BaseException):
    def __init__(self, url, *args, **kwargs):
        super(SneakyRedirectException, self).__init__(*args, **kwargs)
        self.url = url


def exception_handler(exc):
    # This is a copy and paste of taiga.base.exceptions.exception_handler
    # except we need to add a new kind of clause here for 302 redirects.

    # This first conditional is the only reason we override this.
    if isinstance(exc, SneakyRedirectException):
        return django.http.HttpResponseRedirect(exc.url)
    elif isinstance(exc, taiga.base.exceptions.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["X-Throttle-Wait-Seconds"] = "%d" % exc.wait

        detail = taiga.base.exceptions.format_exception(exc)
        return taiga.base.response.Response(detail, status=exc.status_code, headers=headers)

    elif isinstance(exc, django.http.Http404):
        return taiga.base.response.NotFound({'_error_message': str(exc)})

    elif isinstance(exc, DjangoPermissionDenied):
        return taiga.base.response.Forbidden({"_error_message": str(exc)})

    # Note: Unhandled exceptions will raise a 500 error.
    return None


def fas_openid_login_func(request):
    # Use this endpoint for two phases of the login
    # first for the redirect from RP to IP
    # second from the redirect from IP to RP
    if not 'openid.sreg.nickname' in request.DATA:
        return handle_initial_request(request)
    else:
        return handle_openid_request(request)


from openid.consumer import consumer
from openid.extensions import pape, sreg
from openid_cla import cla
from openid_teams import teams


def handle_openid_request(request):
    base_url = request.build_absolute_uri()
    oidconsumer = consumer.Consumer(request.session, None)
    params = {}
    for key, value in request.POST.items():
        params[key] = value
    for key, value in request.GET.items():
        params[key] = value
    info = oidconsumer.complete(params, base_url)
    display_identifier = info.getDisplayIdentifier()

    if info.status == consumer.FAILURE and display_identifier:
        print('FAILURE. display_identifier: %s' % display_identifier)
        sys.stdout.flush()
    elif info.status == consumer.CANCEL:
        print('OpenID request was cancelled')
        sys.stdout.flush()
        raise NotImplementedError()
        #if cancel_url:
        #    return flask.redirect(cancel_url)
    elif info.status == consumer.SUCCESS:
        sreg_resp = sreg.SRegResponse.fromSuccessResponse(info)

        if not sreg_resp:
            # If we have no basic info, be gone with them!
            raise NotImplementedError("Be gone with them")

        user = fas_register(username=sreg_resp.get('nickname'),
                            email=sreg_resp.get('email'),
                            full_name=sreg_resp.get('fullname'))

        data = make_auth_response_data(user)
        data['token'] = data['auth_token']  # ¯\_(ツ)_/¯
        data['type'] = 'fas-openid'

        #return_url = request.session['FAS_OPENID_RETURN_URL'] + "?" + urllib.parse.urlencode(data)
        return_url = request.build_absolute_uri('/login') + "?" + urllib.parse.urlencode(data)

        raise SneakyRedirectException(url=return_url)
    else:
        raise NotImplementedError('Strange state: %s' % info.status)


def handle_initial_request(request):

    groups = ['sysadmin-releng', 'sysadmin-main']
    session = {}
    oidconsumer = consumer.Consumer(session, None)
    try:
        req = oidconsumer.begin('https://id.stg.fedoraproject.org')
    except consumer.DiscoveryFailure:
        # VERY strange, as this means it could not discover an OpenID
        # endpoint at FAS_OPENID_ENDPOINT
        return 'discoveryfailure'
    if req is None:
        # Also very strange, as this means the discovered OpenID
        # endpoint is no OpenID endpoint
        return 'no-req'

    req.addExtension(sreg.SRegRequest(
        required=['nickname', 'fullname', 'email', 'timezone']))
    req.addExtension(pape.Request([]))
    req.addExtension(teams.TeamsRequest(requested=groups))
    req.addExtension(cla.CLARequest(
        requested=[cla.CLA_URI_FEDORA_DONE]))


    # Use the django HTTPRequest for this
    trust_root = request.build_absolute_uri('/')
    return_to = request.build_absolute_uri() + "?type=fas-openid"

    # Success or fail, redirect to the base.  ¯\_(ツ)_/¯
    return_url = cancel_url = request.build_absolute_uri('/')
    request.session['FAS_OPENID_RETURN_URL'] = return_url
    request.session['FAS_OPENID_CANCEL_URL'] = cancel_url

    # the django rest framework requires that we use the json route here
    return dict(form=req.htmlMarkup(trust_root, return_to,
        form_tag_attrs={'id': 'openid_message'}, immediate=False))
