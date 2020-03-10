function UkeyController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pUkeyForm = "#" + this.elementId + "_UkeyForm";
    this.pRabOpenUkey = "#"+this.elementId + "_rabOpenUkey";
    this.pBtnOpenUkey = "#" + this.elementId + "_btnOpenUkey";
    this.pNewPassword1 = "#" + this.elementId + "_newPassword1";
    this.pNewPassword = "#" + this.elementId + "_newPassword";
    this.pOldUserPassword = "#" + this.elementId + "_oldPassword";
    this.pChangePINPwd = "#" + this.elementId + "_changePINPwd";
}

UkeyController.prototype.init = function () {
    try {
        var parent = this;

        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.UKEY_EDIT), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - UkeyController.init() - Unable to initialize: " + err.message);
    }
}

UkeyController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pUkeyForm).Validform({
            tiptype: function (msg, o, cssctl) {
                if (!o.obj.is("form")) {
                    //页面上不存在提示信息的标签时，自动创建;
                    if (o.obj.parent().find(".Validform_checktip").length == 0) {
                        o.obj.parent().append("<span class='Validform_checktip' />");
                        o.obj.parent().next().find(".Validform_checktip").remove();
                    }
                    var objtip = o.obj.parent().find(".Validform_checktip");
                    cssctl(objtip, o.type);
                    objtip.text(o.obj.parent().find("input").attr("errormsg"));
                }
            }
        });
        $(this.pNewPassword1).on("change", function () {
            var newPassword = $(parent.pNewPassword).val();
            var newPassword1 = $(parent.pNewPassword1).val();
            if (newPassword != newPassword1) {
                $(parent.pNewPassword1).parent().find(".Validform_checktip").css("color", "#ff0000").addClass("Validform_wrong").text("两次输入的密码不一致");
            }else {
                $(parent.pNewPassword1).parent().find(".Validform_checktip").removeClass("Validform_wrong").css("color", "").text("");
                console.log(1)
            }
        });
        $(this.pChangePINPwd).on("click", function () {
            var newPassword = $(parent.pNewPassword).val();
            var newPassword1 = $(parent.pNewPassword1).val();
            var oldPassword = $(parent.pOldUserPassword).val();
            if (newPassword != newPassword1) {
                $(parent.pNewPassword1).parent().find(".Validform_checktip").addClass("Validform_wrong").css("color", "#ff0000").text("两次输入的密码不一致");
                return false;
            }
            else {
                $(parent.pNewPassword1).parent().find(".Validform_checktip").removeClass("Validform_wrong").css("color", "").text("");
                if (!Validation.validatePin(newPassword)) {
                    layer.alert("密码必须由字母、数字、特殊字符(@,!,#)组成，长度8位", { icon: 5 });
                    return false;
                }
                parent.changePinPassword(newPassword,oldPassword);
                return false;
            }
        });
        this.pViewHandle.find(this.pBtnOpenUkey).on("click", function () {
            parent.updatePinStatus();
        });
    }
    catch (err) {
        console.error("ERROR - UkeyController.initControls() - Unable to initialize control: " + err.message);
    }
}

UkeyController.prototype.load = function () {
    try {
        this.getPinStatus();
    }
    catch (err) {
        console.error("ERROR - UkeyController.load() - Unable to load: " + err.message);
    }
}
UkeyController.prototype.getPinStatus = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].PIN_STATUS;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status)
                {
                    case 1:
                        parent.pViewHandle.find(parent.pRabOpenUkey).prop("checked", true);
                        break;
                    default:
                        parent.pViewHandle.find(parent.pRabOpenUkey).prop("checked", false);
                        break;
                }
            }
            else {
                layer.alert("获取Ukey认证状态失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - UkeyController.getPinStatus() - Unable to get the device remote status: " + err.message);
    }
}
UkeyController.prototype.updatePinStatus = function () {
    var parent = this;
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var pinStaus = $(this.pRabOpenUkey).prop("checked") ? "1" : "0";
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].PIN_STATUS;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {enable:pinStaus});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
            parent.getPinStatus();
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        if(pinStaus==1)
                            layer.alert("Ukey认证已开启", { icon: 6 });
                        else
                            layer.alert("Ukey认证已关闭", { icon: 6 });
                        break;
                    default:
                        layer.alert("Ukey认证状态更新失败", { icon: 5 });
                        parent.getPinStatus();
                        break;
                }
            }
            else {
                layer.alert("Ukey认证状态更新失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - UkeyController.updatePinStatus() - Unable to get the device remote status: " + err.message);
    }
}
UkeyController.prototype.changePinPassword = function (pwd,oldPwd) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].CHANGE_PIN_PWD;
        var data = {
            newpwd: pwd,
            oldpwd: oldPwd
        };
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            return false;
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert("修改PIN码成功", { icon: 6 });
                        $(parent.pNewPassword).val(''),$(parent.pNewPassword1).val(''),$(parent.pOldUserPassword).val('');
                        break;
                    default:
                        layer.alert(result.msg, { icon: 5 }); break;
                        break;
                }
            }
            else {
                layer.alert("修改PIN码失败", { icon: 5 });
            }
            layer.close(loadIndex);
            return false;
        });
    }
    catch (err) {
        console.error("ERROR - UkeyController.changePinPassword() - Unable to change password for user: " + err.message);
        return false;
    }
}

ContentFactory.assignToPackage("tdhx.base.user.UkeyController", UkeyController);

