function ResetSystemController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;
    this.isRebootSuccess = true;
    this.isResetSuccess = true;

    this.pBtnRebootDevice = "#" + this.elementId + "_btnRebootDevice";
    this.pBtnResetDevice = "#" + this.elementId + "_btnResetDevice";

    this.pDeviceController = controller;
}

ResetSystemController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_RESET), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.init() - Unable to initialize: " + err.message);
    }
}

ResetSystemController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pBtnRebootDevice).on("click", function (event) {
            layer.open({
                type:1,
                title:'确认重启设备吗？',
                closeBtn:false,
                area:'300px',
                shade:0.8,
                btn:['确认','取消'],
                btnAlign:'c',
                yes:function(res){
                    layer.closeAll();
                    parent.rebootDevice();
                }
            });
        });

        $(this.pBtnResetDevice).on("click", function () {
            layer.open({
                type:1,
                title:'确认恢复出厂设置吗？',
                closeBtn:false,
                area:'300px',
                shade:0.8,
                btn:['确认','取消'],
                btnAlign:'c',
                yes:function(res){
                    layer.closeAll();
                    parent.resetDevice();
                }
            });
        });
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

ResetSystemController.prototype.load = function () {
    try {
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.load() - Unable to load: " + err.message);
    }
}

ResetSystemController.prototype.rebootDevice = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].REBOOT_DEVICE;
        var layerIndex = layer.msg("正在重启，请稍后登录...", {
            time:120000 ,
            shade: [0.5, '#fff']
        }, function () {
            if (parent.isRebootSuccess==true) {
                window.location.replace(APPCONFIG[APPCONFIG.PRODUCT].LOGIN_URL);
            }
        });
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            parent.isRebootSuccess = false;
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.isRebootSuccess = true;
                        break;
                    default:
                        parent.isRebootSuccess = false;
                        layer.alert("重启失败", { icon: 5 });
                        break;
                }
            }
            else {
                parent.isRebootSuccess = false;
                layer.alert("重启失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        this.isRebootSuccess = false;
        console.error("ERROR - ResetSystemController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

ResetSystemController.prototype.resetDevice = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].RESET_DEVICE;
        var layerIndex = layer.msg("正在恢复出厂设置，请稍后登录...", {
            time: 180000,
            shade: [0.5, '#fff']
        }, function () {
            if (parent.isResetSuccess == true) {
                window.location.replace(APPCONFIG[APPCONFIG.PRODUCT].LOGIN_URL);
            }
        });
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            parent.isResetSuccess = false;
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.isResetSuccess = true;
                        break;
                    default:
                        parent.isResetSuccess = false;
                        layer.alert("恢复出厂设置失败", { icon: 5 });
                        break;
                }
            }
            else {
                parent.isResetSuccess = false;
                layer.alert("恢复出厂设置失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        this.isResetSuccess = false;
        console.error("ERROR - ResetSystemController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.ResetSystemController", ResetSystemController);