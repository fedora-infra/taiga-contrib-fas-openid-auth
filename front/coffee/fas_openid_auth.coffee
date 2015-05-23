@.taigaContribPlugins = @.taigaContribPlugins or []

fasOpenIDAuthInfo = {
    slug: "fas-openid-auth"
    name: "FAS Auth"
    type: "auth"
    module: "taigaContrib.fasOpenIDAuth"
    template: "contrib/fas_openid_auth"
}

@.taigaContribPlugins.push(fasOpenIDAuthInfo)

module = angular.module('taigaContrib.fasOpenIDAuth', [])

ID_PROVIDER = "https://id.fedoraproject.org"

FASOpenIDLoginButtonDirective = ($window, $params, $location, $config, $events, $confirm, $auth, $navUrls, $loader) ->
    # Login or registar a user with his/her fas account.
    #
    # Example:
    #     tg-fas-openid-login-button()
    #
    # Requirements:
    #   - ...

    link = ($scope, $el, $attrs) ->
        clientId = $config.get("fasOpenIDClientId", null)

        loginOnSuccess = (response) ->
            if $params.next and $params.next != $navUrls.resolve("login")
                nextUrl = $params.next
            else
                nextUrl = $navUrls.resolve("home")

            $events.setupConnection()

            $location.search("next", null)
            $location.search("token", null)
            $location.search("state", null)
            $location.search("code", null)
            $location.path(nextUrl)

        loginOnError = (response) ->
            $location.search("state", null)
            $location.search("code", null)
            $loader.pageLoaded()

            if response.data.error_message
                $confirm.notify("light-error", response.data.error_message )
            else
                $confirm.notify("light-error",
                        "Our Panda Squad wasn't able to log you in via FAS.")

        loginWithFASOpenIDAccount = ->
            type = $params.state
            code = $params.code
            token = $params.token

            return if not (type == "fas-openid" and code)
            $loader.start()

            data = {code: code, token: token}
            $auth.login(data, type).then(loginOnSuccess, loginOnError)

        loginWithFASOpenIDAccount()

        $el.on "click", ".button-auth", (event) ->
            $.ajax({
              url: '/api/v1/auth',
              method: 'POST',
              data: {type: 'fas-openid'},
              success: (data) ->
                # THIS IS CRAZY TALK
                form = $(data.form);
                $('body').append(form);
                form.submit();
              error: (data) ->
                console.log('failure');
                console.log(data);
            });

        $scope.$on "$destroy", ->
            $el.off()

    return {
        link: link
        restrict: "EA"
        template: ""
    }

module.directive("tgFasOpenidLoginButton", [
    "$window", '$routeParams', "$tgLocation", "$tgConfig", "$tgEvents",
   "$tgConfirm", "$tgAuth", "$tgNavUrls", "tgLoader",
   FASOpenIDLoginButtonDirective])
