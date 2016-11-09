angular.module("templates").run(["$templateCache",function($templateCache){$templateCache.put("/plugins/fas-openid-auth/fas_openid_auth.html",'\n<div tg-fas-openid-login-button="tg-fas-openid-login-button"><a href="" title="Enter with your FAS account" class="button button-auth"><img src="/plugins/fas-openid-auth/images/contrib/fedora-logo.png"/><span>Login with FAS</span></a></div>')}]),function(){var FASOpenIDLoginButtonDirective,module;module=angular.module("taigaContrib.fasOpenIDAuth",[]),FASOpenIDLoginButtonDirective=function($window,$params,$location,$config,$events,$confirm,$auth,$navUrls,$loader){var link;return link=function($scope,$el,$attrs){var loginWithFASOpenIDAccount;return loginWithFASOpenIDAccount=function(){var data,nextUrl,scrub,token,type,user;if(type=$params.type,token=$params.token,"fas-openid"===type&&"undefined"!=typeof token)return $loader.start(),$auth.removeToken(),data=_.clone($params,!1),user=$auth.model.make_model("users",data),$auth.setToken(user.auth_token),$auth.setUser(user),$events.setupConnection(),nextUrl=$params.next&&$params.next!==$navUrls.resolve("login")?$params.next:$navUrls.resolve("home"),scrub=function(i,name){return $location.search(name,null)},$.each(["next","token","state","id","username","default_timezone","bio","type","default_language","is_active","photo","auth_token","big_photo","email","color","full_name_display","full_name"],scrub),$location.path(nextUrl)},loginWithFASOpenIDAccount(),$el.on("click",".button-auth",function(event){return $.ajax({url:"/api/v1/auth",method:"POST",data:{type:"fas-openid"},success:function(data){var form;return form=$(data.form),$("body").append(form),form.submit()},error:function(data){return console.log("failure"),console.log(data)}})}),$scope.$on("$destroy",function(){return $el.off()})},$(".login-form fieldset:nth-child(-n+3)").hide(),$(".login-text").hide(),{link:link,restrict:"EA",template:""}},module.directive("tgFasOpenidLoginButton",["$window","$routeParams","$tgLocation","$tgConfig","$tgEvents","$tgConfirm","$tgAuth","$tgNavUrls","tgLoader",FASOpenIDLoginButtonDirective])}.call(this);