//app.js, the entry point of the whole project
$(function () {
    try {
        LocalStorageManager.getInstance().init();
        AuthManager.getInstance().init();
        ScriptLoader.getInstance().includeModule(APPCONFIG.PRODUCT.toLowerCase(), function (done) {
            URLManager.getInstance().init();
            var authInfo=JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']);
            var auth_menu,featurecode=authInfo.lastLogin;
            mstat= $.md5(featurecode+1),ostat=$.md5(featurecode+3),astat=$.md5(featurecode+2);
            if(!authInfo['redirect']){
                switch(authInfo['authority']) {
                    case mstat:
                        auth_menu = Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_MENU_ADMIN;
                        break;
                    case astat:
                        auth_menu = Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_MENU_AUDIT;
                        break;
                    case ostat:
                        auth_menu = Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_MENU_OPERA;
                        break;
                }
            }else{
                auth_menu = Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_MENU_ADMIN;
            }
            gloTimer={};
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_HEADER,auth_menu,
                Constants.TEMPLATES.DEVICE_MODE,
                Constants.TEMPLATES.UTILITY_ERROR,
                Constants.TEMPLATES.UTILITY_PAGER1,
                Constants.TEMPLATES.UTILITY_PAGER2],
                function (templateResults) {
                    var locale = CookieManager.getCookieValue("AgentLanguage");
                    locale = (locale == null || locale == "" || locale == "null") ? APPCONFIG.DEFAULT_LOCALE : locale;
                    AuthManager.getInstance().init();
                    AuthManager.getInstance().isLoggedIn(function () {
                        new tdhx.base.utility.SessionTimeoutController().init();
                        renderUI();
                    }, function () {
                        AuthManager.getInstance().logOut();
                    });
                });
        });
    }
    catch (err) {
        console.error("ERROR - App.js document.ready() - Can not initialize KEA-C200: " + err.message);
    }
});

$(window).resize(function () {
    try {
    }
    catch (err) {
        console.error("ERROR - App.js window.resize() - Can not render UI: " + err.message);
    }
});


var headerController;
function renderUI() {
    try {
        //call header/menu controller to load main page via product serial number.
        var authInfo=JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']);
        headerController = new tdhx.index.HeaderController($(".header"));
        headerController.init();
        new tdhx.index.MenuController($(".nav")).init();
        if (AuthManager.getInstance().getMode() == 0) {//集中管理：单页面
            new tdhx.base.device.CentralizeDeviceController($("#viewContainer"), "device_centralize").init();
            $(".guide").css("visibility", "hidden");
            $(".guide").css("display", "none");
        }
        else {//自管理：多页面
            if(!authInfo['redirect']){
                switch(authInfo['authority']) {
                    case mstat:
                        View.getInstance().init(Constants.PageType.USER, "用户管理");
                        break;
                    case astat:
                        View.getInstance().init(Constants.PageType.LOG, "日志管理");
                        break;
                    case ostat:
                            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_LISENCE_STATUS;
                            var promise = URLManager.getInstance().ajaxCall(link);
                            promise.fail(function (jqXHR, textStatus, err) {
                                resolvedUnauthorize();
                                console.log(textStatus + " - " + err.message);
                            });
                            promise.done(function (result) {
                                if (result.status) {
                                    View.getInstance().init("HOME_DASHBOARD", "首页");
                                    license_expire=result.license_time,license_func=result.license_func;
                                }else{
                                    resolvedUnauthorize();
                                }
                            });
                            $('.nav').height($(window).height() - 72);
                        break;
                }
            }else{
                View.getInstance().init(Constants.PageType.USER, "用户管理");
            }
            function resolvedUnauthorize(){
                layer.alert('该产品未取得license授权', { icon: 4, btn: ['去授权'], closeBtn: 0 });
                license_expire = 0, license_func = 0;
                $('<div>').addClass('coverlayer').css({ width: '100%', height: '100%', backgroundColor: '#0e7171', opacity: 0.5, position: 'absolute', zIndex: 777, top: 0, left: 0 }).prependTo('.nav');
                $(window).resize(function(){$('.coverlayer').css({height:$('.nav-list').height()});});
                var overlayer = $(".nav-list>li").last();
                $(".nav-list>li .nav-title").removeClass("active");
                overlayer.find('>.nav-title').addClass('active');
                $(".second-nav-list>li").removeClass("on");
                overlayer.find('.second-nav li').eq(0).addClass("on");
                overlayer.find('.second-nav').show();
                $('.coverlayer').css({height:$('.nav-list').height()});
                View.getInstance().init("LISENCE_RIGHT", "授权");
            }
            $(".guide").css("visibility", "visible");
            $(".guide").css("display", "");
            $(".guide>div>p>a").on("click", function () {
                View.getInstance().init("HOME_DASHBOARD", "首页");
                new GuideController($("#guideContainer"), "guide_step1").init(Constants.TEMPLATES.UTILITY_GUIDE_STEP_START);
            });
            $(".guide>div>p").eq(0).on("click", function () {
                $("#guideContainer").html("");
                $(".second-nav").eq(3).slideDown(300);
                $(".nav-list li .nav-title").removeClass("active");
                $(".nav-list li .nav-title").eq(7).addClass("active");
                $(".nav-list>li").eq(7).find(".second-nav-list>li").eq(0).trigger("click");
            });
            $(".guide>div>p").eq(1).on("click", function () {
                $("#guideContainer").html("");
                $(".second-nav").eq(0).slideDown(300);
                $(".nav-list li .nav-title").removeClass("active");
                $(".nav-list li .nav-title").eq(3).addClass("active");
                $(".nav-list>li").eq(3).find(".second-nav-list>li").eq(0).trigger("click");
            });
        }
    }
    catch (err) {
        console.error("ERROR - App.js renderUI() - Can not render UI: " + err.message);
    }
}

function syncSysTime() {
    if (headerController != null && typeof (headerController) != "undefined") {
        //获取系统时间
        if (gloTimer.sysTimer != null) {
            clearInterval(gloTimer.sysTimer);
        }
        headerController.getSystemTime();
    }
}