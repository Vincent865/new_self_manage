function RemoteDeviceController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.controller = controller;
    this.isRedirect = true;
    this.isRebootSuccess = true;
    this.isResetSuccess = true;

    this.pRabRemoteIP = "#"+this.elementId + "_rabRemoteIP";
    this.pDivRemoteIP = "#" + this.elementId + "_divRemoteIP";
    this.pTxtRemoteIP = "#" + this.elementId + "_txtRemoteIP";
    this.pTxtRemoteIP6 = "#" + this.elementId + "_txtRemoteIP6";
    this.pBtnAddRemoteIP = "#" + this.elementId + "_btnAddRemoteIP";
    this.pTxtDeviceLogoutDateTime = "#" + this.elementId + "_txtDeviceLogoutDateTime";
    this.pTxtDeviceLogintTimes = "#" + this.elementId + "_txtDeviceLogintTimes";
    this.pBtnLoginSetting = "#" + this.elementId + "_btnLoginSetting";
}

RemoteDeviceController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.DEVICE_REMOTE), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - RemoteDeviceController.init() - Unable to initialize: " + err.message);
    }
}

RemoteDeviceController.prototype.initControls = function () {
    try {
        var parent = this;

        this.pViewHandle.find(this.pRabRemoteIP).on("click", function () {
            parent.updateDeviceRemote();
        });

        this.pViewHandle.find(this.pBtnLoginSetting).on("click", function (event) {
            parent.updateDeviceLoginInfo();
            return false;
        });

        this.pViewHandle.find(this.pBtnAddRemoteIP).on("click", function () {
            parent.addRemoteIP();
        });

        this.pViewHandle.find(this.pTxtDeviceLogoutDateTime).on("keyup", function () {
            $(this).val($(this).val().replace(/\D/g, '0'));
        });

        this.pViewHandle.find(this.pTxtDeviceLogintTimes).on("keyup", function () {
            $(this).val($(this).val().replace(/\D/g, '0'));
        });

        this.pViewHandle.find(this.pTxtDeviceLogoutDateTime).on("change", function () {
            var logoutDatetime = $(this).val();
            if (parseInt(logoutDatetime) < 5 || parseInt(logoutDatetime) > 60) {
                parent.pViewHandle.find(parent.pTxtDeviceLogoutDateTime).parent().find(".Validform_checktip").addClass("Validform_wrong").css("color", "#ff0000").text("登出时间请确认在5-60分钟");
            }
            else {
                parent.pViewHandle.find(parent.pTxtDeviceLogoutDateTime).parent().find(".Validform_checktip").removeClass("Validform_wrong").css("color", "").text("");
            }
        });
        this.pViewHandle.find(this.pTxtDeviceLogintTimes).on("change", function () {
            var loginTimes = $(this).val();
            if (parseInt(loginTimes) < 5 || parseInt(loginTimes) > 10) {
                parent.pViewHandle.find(parent.pTxtDeviceLogintTimes).parent().find(".Validform_checktip").addClass("Validform_wrong").css("color", "#ff0000").text("登录次数请确认在5-10次");
                return false;
            }
            else {
                parent.pViewHandle.find(parent.pTxtDeviceLogintTimes).parent().find(".Validform_checktip").removeClass("Validform_wrong").css("color", "").text("");
            }
        });
    }
    catch (err) {
        console.error("ERROR - RemoteDeviceController.initControls() - Unable to initialize control: " + err.message);
    }
}

RemoteDeviceController.prototype.load = function () {
    try {
        this.getDeviceRemote();
        this.getLoginInfo();
    }
    catch (err) {
        console.error("ERROR - RemoteDeviceController.load() - Unable to load: " + err.message);
    }
}

RemoteDeviceController.prototype.getDeviceRemote = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_REMOTE;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.isRemoteCtl) != "undefined") {
                switch (result.isRemoteCtl){
                    case 1:
                        parent.pViewHandle.find(parent.pRabRemoteIP).prop("checked", true);
                        parent.pViewHandle.find(parent.pTxtRemoteIP).val(result.ipv4);
                        parent.pViewHandle.find(parent.pTxtRemoteIP6).val(result.ipv6);
                        parent.pViewHandle.find(parent.pDivRemoteIP).show();
                        parent.pViewHandle.find(parent.pBtnAddRemoteIP).show();
                        break;
                    default:
                        parent.pViewHandle.find(parent.pRabRemoteIP).prop("checked", false);
                        parent.pViewHandle.find(parent.pDivRemoteIP).hide();
                        parent.pViewHandle.find(parent.pBtnAddRemoteIP).hide();
                        break;
                } 
            }
            else {
                layer.alert("获取远程登录IP控制状态失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - RemoteDeviceController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

RemoteDeviceController.prototype.updateDeviceRemote = function () {
    var parent = this;
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var remoteStaus = $(this.pRabRemoteIP).prop("checked") ? "1" : "0";
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_DEVICE_REMOTE;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {flag:remoteStaus});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
            parent.getDeviceRemote();
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        if (remoteStaus == 1) {
                            parent.pViewHandle.find(parent.pBtnAddRemoteIP).show();
                            parent.pViewHandle.find(parent.pDivRemoteIP).show();
                        }
                        else {
                            parent.pViewHandle.find(parent.pBtnAddRemoteIP).hide();
                            parent.pViewHandle.find(parent.pDivRemoteIP).hide();
                        }
                        break;
                    default:
                        parent.getDeviceRemote();
                        break;
                }
            }
            else {
                layer.alert("更新远程登录设置失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        parent.getDeviceRemote();
        console.error("ERROR - RemoteDeviceController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

RemoteDeviceController.prototype.addRemoteIP = function () {
    var parent = this;
    var ip = $.trim($(this.pTxtRemoteIP).val())||"";
    var ip6 = $.trim($(this.pTxtRemoteIP6).val())||"";
    if (!Validation.validateComplexIP(ip)&&!ip6) {
        layer.alert("请输入正确有效的IP", { icon: 5 });
        return false;
    }
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        layer.confirm("请确认已经加入本机IP到远程访问列表",{
            title:"提示",
            btn:["确定","取消"], 
            btn1: function (index,layero) {
                var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].ADD_DEVICE_REMOTE_IP;
                var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { ipv4:ip,ipv6:ip6});
                promise.fail(function (jqXHR, textStatus, err) {
                    console.log(textStatus + " - " + err.message);
                    layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                    layer.close(loadIndex);
                });
                promise.done(function (result) {
                    if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                        switch (result.status) {
                            case 1:
                                layer.alert("添加远程控制IP成功", { icon: 6 });
                                break;
                            default:
                                layer.alert(result.msg, { icon: 5 });
                                break;
                        }
                    }
                    else {
                        layer.alert("重启失败", { icon: 5 });
                    }
                    layer.close(loadIndex);
                });
            },
            btn2: function () {
                layer.close(loadIndex);
            }
        });
        layer.close(loadIndex);
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - RemoteDeviceController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

RemoteDeviceController.prototype.getLoginInfo = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_LOGIN_INFO;
        var promise = URLManager.getInstance().ajaxCall(link, { username: "admin" });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined") {
                parent.pViewHandle.find(parent.pTxtDeviceLogoutDateTime).val(result.logoutTime);
                parent.pViewHandle.find(parent.pTxtDeviceLogintTimes).val(result.loginAttemptCount);
            }
            else {
                layer.alert("获取失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - BasicDeviceController.getLoginInfo() - Unable to get device login setting: " + err.message);
    }
}

RemoteDeviceController.prototype.updateDeviceLoginInfo = function () {
    var parent = this;
    var logoutDatetime = $.trim(parent.pViewHandle.find(this.pTxtDeviceLogoutDateTime).val());
    var loginTimes = $.trim(parent.pViewHandle.find(this.pTxtDeviceLogintTimes).val());
    var passwordLevel = "2";
    var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_DEVICE_LOGIN_SETTING;
    if (logoutDatetime == "") {
        layer.alert("请输入强制登出时间", { icon: 5 });
        return;
    }
    if (loginTimes == "") {
        layer.alert("请输入尝试登陆次数", { icon: 5 });
        return;
    }
    if ((parseInt(logoutDatetime) < 5 || parseInt(logoutDatetime) > 60) || (parseInt(loginTimes) < 5 || parseInt(loginTimes) > 10)) {
        layer.alert("登出时间请确认在5-60分钟,登录次数请确认在5-10次否则会导致无法登录", { icon: 5 });
        return;
    }
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var para = {
            logoutMinute: logoutDatetime,
            tryLogTimes: loginTimes,
            safeLevel: passwordLevel
        };
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST",para);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != null && result.status == "1") {
                AuthManager.getInstance().setSessionTimeMin(logoutDatetime);
                layer.alert("登录安全设置成功", { icon: 6 });
            }
            else {
                layer.alert("登录安全设置失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - BasicDeviceController.updateDeviceLoginInfo() - Unable to update login setting: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.device.RemoteDeviceController", RemoteDeviceController);