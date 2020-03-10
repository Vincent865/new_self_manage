function BasicDeviceController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;
    this.controller = controller;

    this.pFormIP = "#" + this.elementId + "_formIP";
    this.pFormIP6 = "#" + this.elementId + "_formIP6";
    this.pLblDeviceTypeNo = "#" + this.elementId + "_lblDeviceTypeNo";
    this.pLblDeviceSerialNo = "#" + this.elementId + "_lblDeviceSerialNo";
    this.pLblDeviceVersion = "#" + this.elementId + "_lblDeviceVersion";
    this.pLblDeviceIP = "#" + this.elementId + "_lblDeviceIP";
    this.pTxtDeviceNewIP = "#" + this.elementId + "_txtDeviceNewIP";
    this.pTxtDeviceNewSubnet = "#" + this.elementId + "_txtDeviceNewSubnet";
    this.pTxtDeviceNewGateway = "#" + this.elementId + "_txtDeviceNewGateway";
    this.pBtnIPSetting = "#" + this.elementId + "_btnIPSetting";
    this.pFormIP6 = "#" + this.elementId + "_formIP6";
    this.pLblDeviceIP6 = "#" + this.elementId + "_lblDeviceIP6";
    this.pTxtDeviceNewIP6 = "#" + this.elementId + "_txtDeviceNewIP6";
    this.pTxtDeviceNewSubnet6 = "#" + this.elementId + "_txtDeviceNewSubnet6";
    this.pTxtDeviceNewGateway6 = "#" + this.elementId + "_txtDeviceNewGateway6";
    this.pBtnIP6Setting = "#" + this.elementId + "_btnIP6Setting";

    this.pFormDatetime = "#" + this.elementId + "_formDatetime";
    this.pRabDeviceDateTime1 = this.elementId + "_rabDeviceDateTime1";
    this.pRabDeviceDateTime2 = this.elementId + "_rabDeviceDateTime2";
    this.pRabDeviceDateTime = this.elementId + "_rabDeviceDateTime";
    this.pTxtDeviceDateTime3 = "#" + this.elementId + "_txtDeviceDateTime3";
    this.pTxtDeviceDateTime4 = "#" + this.elementId + "_txtDeviceDateTime4";

    this.pFormLogin = "#" + this.elementId + "_formLogin";
    this.pBtnDateTimeSetting = "#" + this.elementId + "_btnDateTimeSetting";
    this.pTxtDeviceLogoutDateTime = "#" + this.elementId + "_txtDeviceLogoutDateTime";
    this.pTxtDeviceLogintTimes = "#" + this.elementId + "_txtDeviceLogintTimes";

    this.pTxtPolicyAmount = "#" + this.elementId + "_txtPolicyAmount";
    this.pDdlPolicyDays = "#" + this.elementId + "_ddlPollicyDay";
    this.pBtnPolicySetting = "#" + this.elementId + "_btnPolicySetting";
    this.pRowSettings = ".row-setting";
}

BasicDeviceController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.DEVICE_BASIC), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - BasicDeviceController.init() - Unable to initialize: " + err.message);
    }
}

BasicDeviceController.prototype.initControls = function () {
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
        this.pViewHandle.find(this.pFormIP6).Validform({
            datatype: {
                "ip6": function (gets, obj, curform, regxp) {
                    return Validation.validateIPV6(gets);
                },
                "subnet6": function (gets, obj, curform, regxp) {
                    return (/^\d+$/.test(gets)&&(parseInt(gets)>=0&&gets<=128));
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

        this.pViewHandle.find(this.pFormDatetime).Validform({
            datatype: {
                "ip": function (gets, obj, curform, regxp) {
                    return Validation.validateIP(gets);
                }
            },
            tiptype: function (msg, o, cssctl) {
                if (!o.obj.is("form")) {
                    //页面上不存在提示信息的标签时，自动创建;
                    if (o.obj.parent().find(".Validform_checktip").length == 0) {
                        o.obj.parent().append("<span class='Validform_checktip' />");
                        o.obj.parent().next().find(".Validform_checktip").remove();
                    }
                    var objtip = o.obj.parent().find(".Validform_checktip");
                    cssctl(objtip, o.type);
                    objtip.text(o.obj.attr("errormsg"));

                    return false;
                }
            }
        });

        this.pViewHandle.find(".dxinput").on("change", function () {
            if (parent.pRabDeviceDateTime1 == $(this).attr("data-id")) {
                $(parent.pTxtDeviceDateTime3).removeAttr("disabled");
                $(parent.pTxtDeviceDateTime4).attr("disabled", "disabled");
            }
            else {
                $(parent.pTxtDeviceDateTime3).attr("disabled", "disabled");
                $(parent.pTxtDeviceDateTime4).removeAttr("disabled");
            }
        });

        this.pViewHandle.find(this.pBtnIPSetting).on("click", function (event) {
            parent.updateDeviceIP();
            return false;
        });

        this.pViewHandle.find(this.pBtnIP6Setting).on("click", function (event) {
            parent.updateDeviceIP6();
            return false;
        });

        this.pViewHandle.find(this.pBtnDateTimeSetting).on("click", function (event) {
            parent.updateDeviceDatetime();
            return false;
        });

        this.pViewHandle.find(this.pBtnPolicySetting).on("click", function (event) {
            parent.updateDeletePolicy();
            return false;
        });

        this.pViewHandle.find(this.pTxtPolicyAmount).on("keyup", function () {
            $(this).val($(this).val().replace(/\D/g, '0'));
        });
    }
    catch (err) {
        console.error("ERROR - BasicDeviceController.initControls() - Unable to initialize control: " + err.message);
    }
}

BasicDeviceController.prototype.load = function () {
    try {
        this.getDeviceInfo();
        this.getRemoteNTP();
        this.getDeletePolicy();
        var authInfo=JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']);
        if(authInfo['authority']==mstat) {
            $(this.pRowSettings).hide();
            $(this.pRowSettings).next().hide();
        }
    }
    catch (err) {
        console.error("ERROR - BasicDeviceController.load() - Unable to load: " + err.message);
    }
}

BasicDeviceController.prototype.getDeviceInfo = function () {
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
                parent.pViewHandle.find(parent.pLblDeviceIP6).html(result.dpiInfo.ip6);
            }
            else {
                layer.alert("获取失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - BasicDeviceController.getDeviceInfo() - Unable to get device inforamtion: " + err.message);
    }
}

BasicDeviceController.prototype.getRemoteNTP = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_NET;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.mode) != "undefined" && typeof (result.serverIp) != "undefined") {
                if (result.mode == 0) {//手动
                    parent.pViewHandle.find(parent.pTxtDeviceDateTime3).removeAttr("disabled", "disabled");
                    parent.pViewHandle.find(parent.pTxtDeviceDateTime4).attr("disabled", "disabled");
                }
                else {//自动
                    parent.pViewHandle.find("#" + parent.pRabDeviceDateTime2).attr("checked", "checked");
                    parent.pViewHandle.find(parent.pTxtDeviceDateTime3).attr("disabled", "disabled");
                    parent.pViewHandle.find(parent.pTxtDeviceDateTime4).removeAttr("disabled", "disabled");
                }
                parent.pViewHandle.find(parent.pTxtDeviceDateTime4).val(result.serverIp);
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

BasicDeviceController.prototype.getDeletePolicy = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_DELETE_POLICY;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.volumenthreshold) != "undefined" && typeof (result.dataperiod) != "undefined") {
                parent.pViewHandle.find(parent.pTxtPolicyAmount).val(result.volumenthreshold);
                parent.pViewHandle.find(parent.pDdlPolicyDays).val(result.dataperiod);
            }
            else {
                layer.alert("获取失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - BasicDeviceController.getDeletePolicy() - Unable to get delete policy login setting: " + err.message);
    }
}

BasicDeviceController.prototype.updateDeviceIP = function () {
    try {
        var parent = this;
        var ip = $.trim($(this.pTxtDeviceNewIP).val());
        var subnet = $.trim($(this.pTxtDeviceNewSubnet).val());
        var gateway = $.trim($(this.pTxtDeviceNewGateway).val());
        if (!Validation.validateIP(ip) || !Validation.validateSubnet(subnet) || !Validation.validateIP(gateway)) {
            layer.alert("请输入有效的IP、子网掩码和网关", { icon: 5 });
            return false;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_DEVICE_IP;
        var promise = URLManager.getInstance().ajaxCall(link,{
            Newdpiip:ip,
            newdpimask:subnet,
            newdpigateway:gateway
        });
        layer.msg("正在跳转中...", {
            time: 10000,
            shade: [0.5, '#fff']
        }, function () {
            window.location.replace("https://" + ip + "/" + APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].LOGIN_URL);
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
        console.error("ERROR - BasicDeviceController.updateDeviceIP() - Unable to update ip setting: " + err.message);
    }
}

BasicDeviceController.prototype.updateDeviceIP6 = function () {
    try {
        var parent = this;
        var ip = $.trim($(this.pTxtDeviceNewIP6).val());
        var subnet = $.trim($(this.pTxtDeviceNewSubnet6).val());
        var gateway = $.trim($(this.pTxtDeviceNewGateway6).val());
        if (!Validation.validateIPV6(ip) || (!/^\d+$/.test(subnet)||!(parseInt(subnet)>=0&&subnet<=128)) || !Validation.validateIPV6(gateway)) {
            layer.alert("请输入有效的IP、子网掩码和网关", { icon: 5 });
            return false;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_DEVICE_IP6;
        var promise = URLManager.getInstance().ajaxCall(link,{
            newdpiip6:ip,
            newdpiPrefix:subnet,
            newdpigateway:gateway
        });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != null && result.status == "1") {
                layer.msg("正在跳转中...", {
                    time: 10000,
                    shade: [0.5, '#fff']
                }, function () {
                    window.location.replace("https://[" + ip + "]/" + APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].LOGIN_URL);
                });
                layer.alert("IPV6设置成功", { icon: 6 });
            }
            else {
                layer.alert("IPV6设置失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - BasicDeviceController.updateDeviceIP6() - Unable to update ip setting: " + err.message);
    }
}

BasicDeviceController.prototype.updateDeviceDatetime = function () {
    try {
        var parent = this;
        var para={};
        var manualTime = $.trim(this.pViewHandle.find(this.pTxtDeviceDateTime3).val());
        var autoIP = $.trim(this.pViewHandle.find(this.pTxtDeviceDateTime4).val());
        var syncType = $("input:radio[name='" + this.pRabDeviceDateTime + "']:checked").val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_DEVICE_TIME_AUTO;
        if (syncType == 2) {
            if (!Validation.validateIP(autoIP)) {
                layer.alert("请输入有效的服务器IP", { icon: 5 });
                return false;
            }
            para.destIp=autoIP;
        }
        else {
            link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_DEVICE_TIME_MANUAL;
            if (!Validation.validateDateTime(manualTime)) {
                return false;
            }
             para.inputTime=manualTime;
        }
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link,para);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != null && result.status == "1") {
                syncSysTime();
                layer.alert("时间设置成功", { icon: 6 });
            }
            else {
                layer.alert("时间设置失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - BasicDeviceController.updateDeviceDatetime() - Unable to update datetime setting: " + err.message);
    }
}

BasicDeviceController.prototype.updateDeletePolicy = function () {
    try {
        var parent = this;
        var amount = $.trim($(this.pTxtPolicyAmount).val());
        if (amount > 100 || amount < 1) {
            layer.alert("空间上限设置错误", { icon: 5 });
            return false;
        }
        var days = $.trim($(this.pDdlPolicyDays).val());
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_DEVICE_DELETE_POLICY;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link,{volumenthreshold:amount,dataperiod:days});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1) {
                layer.alert("策略设置成功", { icon: 6 });
            }
            else {
                layer.alert("策略设置失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - BasicDeviceController.updateDeviceDatetime() - Unable to update datetime setting: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.device.BasicDeviceController", BasicDeviceController);