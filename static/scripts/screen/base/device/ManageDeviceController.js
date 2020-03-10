function ManageDeviceController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.controller = controller;
    this.isRedirect = true;

    this.pRabMode = this.elementId + "_rabMode";
    this.pRabMode1 = "#" + this.elementId + "_rabMode1";
    this.pRabMode2 = "#" + this.elementId + "_rabMode2";
    this.pBtnMode = "#" + this.elementId + "_btnMode";
    this.pDivMode = "#" + this.elementId + "_divMode";
    this.ptxtModeIP = "#" + this.elementId + "_txtModeIP";
    this.pRabSelfMode = this.elementId + "_rabSelfMode";
    this.pRabSelfMode1 = "#" + this.elementId + "_rabSelfMode1";
    this.pRabSelfMode2 = "#" + this.elementId + "_rabSelfMode2";
    this.pRabAuditMode = this.elementId + "_rabAuditMode";
    this.pRabAuditMode1 = "#" + this.elementId + "_rabAuditMode1";
    this.pRabAuditMode2 = "#" + this.elementId + "_rabAuditMode2";
    this.pBtnAuditMode = "#" + this.elementId + "_btnAuditMode";
}

ManageDeviceController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.DEVICE_MANAGE), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - ManageDeviceController.init() - Unable to initialize: " + err.message);
    }
}

ManageDeviceController.prototype.initControls = function () {
    try {
        var parent = this;

        parent.pViewHandle.find(this.pBtnMode).on("click", function () {
            parent.changeDeviceMode();
        });

        parent.pViewHandle.find(this.pBtnAuditMode).on("click", function () {
            parent.changeFunctionMode();
        });

        parent.pViewHandle.find("input[name='" + this.pRabMode + "']").on("click", function () {
            if ($(this).val() == "0") {
                parent.pViewHandle.find(parent.pDivMode).show();
                parent.pViewHandle.find(parent.ptxtModeIP).attr("disabled", "disabled");
            }
            else {
                parent.pViewHandle.find(parent.pDivMode).hide();
            }
        });

        parent.pViewHandle.find("input[name='" + this.pRabSelfMode + "']").on("click", function () {
            if ($(this).val() == "1") {
                parent.pViewHandle.find(parent.ptxtModeIP).attr("disabled", "disabled");
            }
            else {
                parent.pViewHandle.find(parent.ptxtModeIP).removeAttr("disabled");
            }
        });
    }
    catch (err) {
        console.error("ERROR - ManageDeviceController.initControls() - Unable to initialize control: " + err.message);
    }
}

ManageDeviceController.prototype.load = function () {
    try {
        this.getDeviceMode();
    }
    catch (err) {
        console.error("ERROR - ManageDeviceController.load() - Unable to load: " + err.message);
    }
}

ManageDeviceController.prototype.getDeviceMode = function () {
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
        console.error("ERROR - ManageDeviceController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

ManageDeviceController.prototype.changeDeviceMode = function () {
    try {
        var parent = this;
        var mode = parent.pViewHandle.find("input:radio[name='" + this.pRabMode + "']:checked").val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].CHANGE_DEVICE_MODE;
        var para = {
            controlMode: mode,
            mwip: "",
            dhcp:""
        };
        if (mode == 0) {
            var isSelf = parent.pViewHandle.find("input:radio[name='" + this.pRabSelfMode + "']:checked").val();
            para.dhcp = isSelf;
            if (isSelf != "1") {
                para.mwip = $.trim(parent.pViewHandle.find(this.ptxtModeIP).val());
                if (!Validation.validateIP($.trim(parent.pViewHandle.find(this.ptxtModeIP).val()))) {
                    layer.alert("请输入有效的IP", { icon: 5 });
                    return false;
                }
            }
        }
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST",para);
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
        console.error("ERROR - ManageDeviceController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.device.ManageDeviceController", ManageDeviceController);