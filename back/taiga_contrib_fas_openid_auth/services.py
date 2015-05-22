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

from django.db import transaction as tx
from django.apps import apps

from django.http import HttpResponseRedirect

from taiga.base.utils.slug import slugify_uniquely
from taiga.auth.services import send_register_email
from taiga.auth.services import make_auth_response_data, get_membership_by_token
from taiga.auth.signals import user_registered as user_registered_signal

from . import connector


@tx.atomic
def fas_register(username, full_name):
    """
    Register a new user from FAS.

    This can raise `exc.IntegrityError` exceptions in
    case of conflics found.

    :returns: User
    """
    raise NotImplementedError("gotta write this still.")

    #auth_data_model = apps.get_model("users", "AuthData")
    #user_model = apps.get_model("users", "User")

    #try:
    #    # Github user association exist?
    #    auth_data = auth_data_model.objects.get(key="github", value=github_id)
    #    user = auth_data.user
    #except auth_data_model.DoesNotExist:
    #    try:
    #        # Is a user with the same email as the github user?
    #        user = user_model.objects.get(email=email)
    #        auth_data_model.objects.create(user=user, key="github", value=github_id, extra={})
    #    except user_model.DoesNotExist:
    #        # Create a new user
    #        username_unique = slugify_uniquely(username, user_model, slugfield="username")
    #        user = user_model.objects.create(email=email,
    #                                         username=username_unique,
    #                                         full_name=full_name,
    #                                         bio=bio)
    #        auth_data_model.objects.create(user=user, key="github", value=github_id, extra={})

    #        send_register_email(user)
    #        user_registered_signal.send(sender=user.__class__, user=user)

    #if token:
    #    membership = get_membership_by_token(token)
    #    membership.user = user
    #    membership.save(update_fields=["user"])

    #return user


def fas_openid_login_func(request):
    # Use this endpoint for two phases of the login
    # first for the redirect from RP to IP
    # second from the redirect from IP to RP
    if True:
        return handle_initial_request(request)
    else:
        handle_openid_request(request)

    raise done

    code = request.DATA.get('code', None)
    token = request.DATA.get('token', None)

    email, user_info = connector.me(code)

    user = github_register(username=user_info.username,
                           email=email,
                           full_name=user_info.full_name,
                           github_id=user_info.id,
                           bio=user_info.bio,
                           token=token)
    data = make_auth_response_data(user)
    return data


import openid
from openid.consumer import consumer
from openid.fetchers import setDefaultFetcher, Urllib2Fetcher
from openid.extensions import pape, sreg
# Python2 only :(
#from openid_cla import cla
#from openid_teams import teams


def handle_openid_request(request):
    base_url = request.build_absolute_uri('/')
    oidconsumer = consumer.Consumer(request.session, None)
    info = oidconsumer.complete(request.GET, base_url)
    display_identifier = info.getDisplayIdentifier()

    if info.status == consumer.FAILURE and display_identifier:
        print('FAILURE. display_identifier: %s' % display_identifier)
        raise NotImplementedError()
    elif info.status == consumer.CANCEL:
        if cancel_url:
            return flask.redirect(cancel_url)
        print('OpenID request was cancelled')
        raise NotImplementedError()
    elif info.status == consumer.SUCCESS:
        sreg_resp = sreg.SRegResponse.fromSuccessResponse(info)
        pape_resp = pape.Response.fromSuccessResponse(info)
        teams_resp = teams.TeamsResponse.fromSuccessResponse(info)
        cla_resp = cla.CLAResponse.fromSuccessResponse(info)
        user = {'fullname': '', 'username': '', 'email': '',
                'timezone': '', 'cla_done': False, 'groups': []}
        if not sreg_resp:
            # If we have no basic info, be gone with them!
            raise NotImplementError("Be gone with them")
        user['username'] = sreg_resp.get('nickname')
        user['fullname'] = sreg_resp.get('fullname')
        user['email'] = sreg_resp.get('email')
        user['timezone'] = sreg_resp.get('timezone')
        if cla_resp:
            user['cla_done'] = cla.CLA_URI_FEDORA_DONE in cla_resp.clas
        if teams_resp:
            # The groups do not contain the cla_ groups
            user['groups'] = frozenset(teams_resp.teams)

        raise NotImplementedError("success!")
        flask.session['FLASK_FAS_OPENID_USER'] = user
        flask.session.modified = True
        if self.postlogin_func is not None:
            self._check_session()
            return self.postlogin_func(return_url)
        else:
            return flask.redirect(return_url)
    else:
        raise NotImplementedError('Strange state: %s' % info.status)


def handle_initial_request(request):
    session = {}
    oidconsumer = consumer.Consumer(session, None)
    try:
        req = oidconsumer.begin('https://id.fedoraproject.org')
    except consumer.DiscoveryFailure as exc:
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
    # Ignore teams and CLA stuff for now for py2/py3 reasons

    # Use the django HTTPRequest for this
    trust_root = request.build_absolute_uri('/')
    return_to = request.build_absolute_uri()

    # Success or fail, redirect to the base.  ¯\_(ツ)_/¯
    return_url = cancel_url = request.build_absolute_uri('/')
    request.session['FAS_OPENID_RETURN_URL'] = return_url
    request.session['FAS_OPENID_CANCEL_URL'] = cancel_url

    # the django rest framework requires that we use the json route here
    return dict(form=req.htmlMarkup( trust_root, return_to,
        form_tag_attrs={'id': 'openid_message'}, immediate=False))

