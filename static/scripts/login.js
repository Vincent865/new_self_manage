function isPinCodeAction(){
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].IS_PIN_ACTION;
        $.ajax({
            type: 'GET',
            url: link,
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            //data: JSON.stringify({ username: username, pw: password,pin: pin }),
            success: function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    if (result.status == 1) {
                        $(".input-login").eq(2).show();
                        $(".loginbox").css({"height": "305px"});
                    } else {
                        $(".input-login").eq(2).hide();
                        $(".loginbox").css({"height": "250px"});
                    }
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                $(".log_text").text("系统服务忙，请稍后重试！");
                console.error("ERROR - initializeLoginScreen() - Unable to retrieve URL: " + link + ". " + errorThrown);
                return false;
            }
        });
        return;
    }
    catch (err) {
        console.error("ERROR - isPinCodeAction() - Can not initialize: " + err.message);
    }
}

function initializeLoginScreen() {
    try {
        //validate user
        jQuery.support.cors = true;
        var username = $.trim($("#login_txtUserName").val().replace(/[\/<>()]/g,''));
        var password = $.trim($("#login_txtUserPassword").val());
        var pin = $.trim($("#login_txtUserPin").val());
        if (username.length < 4 || username.length > 25) {
            $(".log_text").text("用户名必须为4-25个字符，以字母开头");
            return false;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].CHECK_USER;
        $(".log_text").text("正在验证，请稍等...");
        $.ajax({
            type: 'POST',
            url: link,
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({ username: username, pw: password, pin: pin }),
            success: function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 0://账号不存在
                            $(".log_text").text("您输入的账号与密码不匹配，请确认正确性");
                            break;
                        case 3://账号密码错误
                            $(".log_text").text("您输入的账号与密码不匹配！你还有"+ result.msg +"次输入机会！");
                            break;
                        case 1://账号被锁定
                            $(".log_text").text("账号已经被锁定，请稍后再试");
                            break;
                        case -1://账号密码错误
                            $(".log_text").text("该帐号已登陆，请下线后重试！");
                            break;
                        case 2://登录成功
                            if(typeof (result.login_info) == "undefined")
                            {
                                $(".log_text").text("系统服务忙，请稍后重试！");
                                break;
                            }
                            result.login_info.runmode = "ips";
                            LocalStorageManager.getInstance().init();
                            LocalStorageManager.getInstance().setProperty(APPCONFIG.LOGIN_RESPONSE, LocalStorageManager.serialize(result.login_info));
                            window.location.replace(APPCONFIG[APPCONFIG.PRODUCT].HOMEPAGE_URL);
                            break;
                        case 4://密码超出时效
                            if(typeof (result.login_info) == "undefined")
                            {
                                $(".log_text").text("系统服务忙，请稍后重试！");
                                break;
                            }
                            result.login_info.runmode = "ips";
                            LocalStorageManager.getInstance().init();
                            LocalStorageManager.getInstance().setProperty(APPCONFIG.LOGIN_RESPONSE, LocalStorageManager.serialize(result.login_info));
                            window.location.replace(APPCONFIG[APPCONFIG.PRODUCT].HOMEPAGE_URL);
                            break;
                        case 6:
                        case 7://PIN码错误
                            $(".log_text").text(result.msg+"！你还有"+ result.times +"次输入机会！");
                            break;
                        default:
                            $(".log_text").text("系统服务忙，请稍后重试！");
                            break;
                    }
                }
                else {
                    $(".log_text").text("系统服务忙，请稍后重试！");
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                $(".log_text").text("系统服务忙，请稍后重试！");
                console.error("ERROR - initializeLoginScreen() - Unable to retrieve URL: " + link + ". " + errorThrown);
                return false;
            }
        });
        return;
    }
    catch (err) {
        console.error("ERROR - initializeLoginScreen() - Can not initialize: " + err.message);
    }
}