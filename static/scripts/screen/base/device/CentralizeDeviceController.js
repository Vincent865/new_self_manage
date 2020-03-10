function CentralizeDeviceController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;

    this.pFormIP = "#" + this.elementId + "_formIP";
    this.pLblDeviceTypeNo = "#" + this.elementId + "_lblDeviceTypeNo";
    this.pLblDeviceSerialNo = "#" + this.elementId + "_lblDeviceSerialNo";
    this.pLblDeviceVersion = "#" + this.elementId + "_lblDeviceVersion";
    this.pLblDeviceIP = "#" + this.elementId + "_lblDeviceIP";
    this.pTxtDeviceNewIP = "#" + this.elementId + "_txtDeviceNewIP";
    this.pTxtDeviceNewSubnet = "#" + this.elementId + "_txtDeviceNewSubnet";
    this.pTxtDeviceNewGateway = "#" + this.elementId + "_txtDeviceNewGateway";
    this.pBtnIPSetting = "#" + this.elementId + "_btnIPSetting";

    this.pRabMode = this.elementId + "_rabMode";
    this.pRabMode1 = "#" + this.elementId + "_rabMode1";
    this.pRabMode2 = "#" + this.elementId + "_rabMode2";
    this.pBtnMode = "#" + this.elementId + "_btnMode";
    this.pDivMode = "#" + this.elementId + "_divMode";
    this.ptxtModeIP = "#" + this.elementId + "_txtModeIP";
    this.pRabSelfMode = this.elementId + "_rabSelfMode";
    this.pRabSelfMode1 = "#" + this.elementId + "_rabSelfMode1";
    this.pRabSelfMode2 = "#" + this.elementId + "_rabSelfMode2";
}

CentralizeDeviceController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.DEVICE_MODE), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);
        $(".nav").width(0);
        $(".wrapper").width("100%");
        $(".wrapper").css("margin-left","0");
        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - CentralizeDeviceController.init() - Unable to initialize: " + err.message);
    }
}

CentralizeDeviceController.prototype.initControls = function () {
    try {
        var parent = this;

        this.pViewHandle.find(this.pFormIP).Validform({
            datatype: {
                "ip": function (gets, obj, curform, regxp) {
                    return Validation.validateIP(gets);
                },
                "subnet": function (gets, obj, curform, regxp) {
                    return Validation.validateSubnet(gets);
                }
            },
            tiptype: function (msg, o, cssctl) {
                if (!o.obj.is("form")) {
                    if (o.obj.parent().find(".Validform_checktip").length == 0) {
                        o.obj.parent().append("<span class='Validform_checktip' />");
                    }
                    var objtip = o.obj.parent().find(".Validform_checktip");
                    cssctl(objtip, o.type);
                    objtip.text(o.obj.attr("errormsg"));

                    return;
                }
            },
            beforeSubmit: function () { }
        });

        parent.pViewHandle.find(this.pBtnMode).on("click", function () {
            parent.changeDeviceMode();
        });

        this.pViewHandle.find("input[name='" + this.pRabMode + "']").on("click", function () {
            if ($(this).val() == "0") {
                parent.pViewHandle.find(parent.pDivMode).show();
                parent.pViewHandle.find(parent.ptxtModeIP).attr("disabled", "disabled");
            }
            else {
                parent.pViewHandle.find(parent.pDivMode).hide();
            }
        });

        this.pViewHandle.find("input[name='" + this.pRabSelfMode + "']").on("click", function () {
            if ($(this).val() == "1") {
                parent.pViewHandle.find(parent.ptxtModeIP).attr("disabled", "disabled");
            }
            else {
                parent.pViewHandle.find(parent.ptxtModeIP).removeAttr("disabled");
            }
        });

        this.pViewHandle.find(this.pBtnIPSetting).on("click", function (event) {
            parent.updateDeviceIP();
            return false;
        });

    }
    catch (err) {
        console.error("ERROR - CentralizeDeviceController.initControls() - Unable to initialize control: " + err.message);
    }
}

CentralizeDeviceController.prototype.load = function () {
    try {
        this.getDeviceInfo();
        this.getDeviceMode();
    }
    catch (err) {
        console.error("ERROR - CentralizeDeviceController.load() - Unable to load: " + err.message);
    }
}

CentralizeDeviceController.prototype.getDeviceInfo = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_INFO;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.dpiInfo) != null) {
                parent.pViewHandle.find(parent.pLblDeviceTypeNo).html(result.dpiInfo.product);
                parent.pViewHandle.find(parent.pLblDeviceSerialNo).html(result.dpiInfo.SN);
                parent.pViewHandle.find(parent.pLblDeviceVersion).html(result.dpiInfo.version);
                parent.pViewHandle.find(parent.pLblDeviceIP).html(result.dpiInfo.ip);
            }
        });
    }
    catch (err) {
        console.error("ERROR - CentralizeDeviceController.getDeviceInfo() - Unable to get device inforamtion: " + err.message);
    }
}

CentralizeDeviceController.prototype.getDeviceMode = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_MODE;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.curMode) != "undefined") {
                switch (result.curMode) {
                    case 1:
                        parent.pViewHandle.find(parent.pRabMode1).attr("checked", "checked");
                        parent.pViewHandle.find(parent.pDivMode).hide();
                        break;
                    default:
                        parent.pViewHandle.find(parent.pRabMode2).attr("checked", "checked");
                        parent.pViewHandle.find(parent.pDivMode).show();
                        switch (result.curDhcp) {
                            case 1:
                                parent.pViewHandle.find(parent.pRabSelfMode1).attr("checked", "checked");
                                parent.pViewHandle.find(parent.ptxtModeIP).attr("disabled", "disabled");
                                break;
                            default:
                                parent.pViewHandle.find(parent.pRabSelfMode2).attr("checked", "checked");
                                parent.pViewHandle.find(parent.ptxtModeIP).val(result.curMwIp);
                                parent.pViewHandle.find(parent.ptxtModeIP).removeAttr("disabled");
                                break;
                        }
                        break;
                }
            }
            else {
                layer.alert("获取管理模式失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - CentralizeDeviceController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

CentralizeDeviceController.prototype.updateDeviceIP = function () {
    try {
        var parent = this;
        var ip = $.trim($(this.pTxtDeviceNewIP).val());
        var subnet = $.trim($(this.pTxtDeviceNewSubnet).val());
        var gateway = $.trim($(this.pTxtDeviceNewGateway).val());
        if (!Validation.validateIP(ip) || !Validation.validateSubnet(subnet) || !Validation.validateIP(gateway)) {
            layer.alert("请输入有效的IP、子网掩码和网关", { icon: 5 });
            return false;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_DEVICE_IP;
        var promise = URLManager.getInstance().ajaxCall(link, {
            Newdpiip: ip,
            newdpimask: subnet,
            newdpigateway: gateway
        });
        layer.msg("正在跳转中...", {
            time: 10000,
            shade: [0.5, '#fff']
        }, function () {
            window.location.replace("https://" + ip + "/" + APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].LOGIN_URL);
        });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != null && result.status == "1") {
                layer.alert("IP设置成功", { icon: 6 }); k
            }
            else {
                layer.alert("IP设置失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - CentralizeDeviceController.updateDeviceIP() - Unable to update ip setting: " + err.message);
    }
}

CentralizeDeviceController.prototype.changeDeviceMode = function () {
    try {
        var parent = this;
        var mode = $("input:radio[name='" + this.pRabMode + "']:checked").val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].CHANGE_DEVICE_MODE;
        var para = {
            controlMode: mode,
            mwip: "",
            dhcp: ""
        };
        if (mode == 0) {
            var isSelf = $("input:radio[name='" + this.pRabSelfMode + "']:checked").val();
            para.dhcp = isSelf;
            if (isSelf != "1") {
                para.mwip = $.trim($(this.ptxtModeIP).val());
                if (!Validation.validateIP($.trim($(this.ptxtModeIP).val()))) {
                    layer.alert("请输入有效的IP", { icon: 5 });
                    return false;
                }
            }
        }
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", para);
        var layerIndex = layer.msg("正在切换模式，请稍后...", {
            time: 60000,
            shade: [0.5, '#fff']
        }, function () {
            if (parent.isRedirect == true) {
                window.location.replace(APPCONFIG[APPCONFIG.PRODUCT].LOGIN_URL);
            }
        });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            parent.isRedirect = false;
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result.selfManageInfo) != "undefined" && typeof (result.selfManageInfo) != "undefined" && typeof (result.selfManageInfo.status) != "undefined") {
                switch (result.selfManageInfo.status) {
                    case 1:
                        parent.isRedirect = true;
                        AuthManager.getInstance().setMode(mode);
                        break;
                    default:
                        parent.isRedirect = false;
                        layer.alert("管理模式切换失败", { icon: 5 });
                        break;
                }
            }
            else {
                parent.isRedirect = false;
                layer.alert("管理模式切换失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        this.isRedirect = false;
        console.error("ERROR - CentralizeDeviceController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.device.CentralizeDeviceController", CentralizeDeviceController);