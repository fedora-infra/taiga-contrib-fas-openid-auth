
module = angular.module('taigaContrib.fasOpenIDAuth', [])

FASOpenIDLoginButtonDirective = ($window, $params, $location, $config, $events, $confirm, $auth, $navUrls, $loader) ->
    # Login or registar a user with his/her fas account.
    #
    # Example:
    #     tg-fas-openid-login-button()
    #
    # Requirements:
    #   - ...

    link = ($scope, $el, $attrs) ->

        loginWithFASOpenIDAccount = ->
            type = $params.type
            token = $params.token

            return if not (type == "fas-openid")
            return if typeof token is 'undefined'

            $loader.start()

            # Let's do this ourselves
            $auth.removeToken();
            data = _.clone($params, false);
            user = $auth.model.make_model("users", data);
            $auth.setToken(user.auth_token);
            $auth.setUser(user);

            $events.setupConnection()

            if $params.next and $params.next != $navUrls.resolve("login")
                nextUrl = $params.next
            else
                nextUrl = $navUrls.resolve("home")

            scrub = (i, name) ->
                $location.search(name, null)

            $.each(['next', 'token', 'state', 'id', 'username', 'default_timezone', 'bio', 'type', 'default_language', 'is_active', 'photo', 'auth_token', 'big_photo', 'email', 'color', 'full_name_display', 'full_name'], scrub);

            $location.path(nextUrl)

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

    # Hide the original login form :D
    # This is definitely not tha angular way of doing things, but ¯\_(ツ)_/¯
    $('.login-form fieldset:nth-child(-n+3)').hide();
    $('.login-text').hide();

    return {
        link: link
        restrict: "EA"
        template: ""
    }

module.directive("tgFasOpenidLoginButton", [
    "$window", '$routeParams', "$tgLocation", "$tgConfig", "$tgEvents",
   "$tgConfirm", "$tgAuth", "$tgNavUrls", "tgLoader",
   FASOpenIDLoginButtonDirective])
