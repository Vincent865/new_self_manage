function IptypeSystemController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;
    this.isTestSuccess = false;
    //this.isResetSuccess = true;
    this.regStatus="#" + this.elementId +'_connectStatus';
    this.serverIp="#" + this.elementId +'_serverIp';
    this.serverPort="#" + this.elementId +'_serverPort';

    this.pBtnTestStatus = "#" + this.elementId + "_btnTestStatus";
    this.pBtnConnectDevice = "#" + this.elementId + "_btnConnectDevice";

    this.pTip='#'+this.elementId+'_testTip';
    this.pDeviceController = controller;

    this.pRabIPV6 = "#"+this.elementId + "_rabIPV6";
    this.pBtnIPV6Switch = "#" + this.elementId + "_btnIPV6Switch";
}

IptypeSystemController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_IPTYPE), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        //this.load();
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.init() - Unable to initialize: " + err.message);
    }
}

IptypeSystemController.prototype.initControls = function(){
    try {
        var parent = this;

        this.getSwitchStatus();
        $(this.pBtnIPV6Switch).on("click", function (event) {
            parent.setSwitch();
        });
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

IptypeSystemController.prototype.load = function (info) {
    try {
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.load() - Unable to load: " + err.message);
    }
}

IptypeSystemController.prototype.getSwitchStatus = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_IPV6_SWITCH;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined"&& result.status==1 ) {
                switch (result.switch){
                    case 1:
                        parent.pViewHandle.find(parent.pRabIPV6).prop("checked", true);
                        break;
                    case 0:
                        parent.pViewHandle.find(parent.pRabIPV6).prop("checked", false);
                        break;
                    default:
                        parent.pViewHandle.find(parent.pRabIPV6).prop("checked", false);
                        break;
                }
            }
            else {
                layer.alert("获取IPV6功能开关信息失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - IptypeSystemController.getSwitchStatus() - Unable to get the device remote status: " + err.message);
    }
}

IptypeSystemController.prototype.setSwitch = function () {
    var parent = this;
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var ipv6Status = $(this.pRabIPV6).prop("checked") ? "1" : "0";
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_IPV6_SWITCH;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {switch:ipv6Status});
        console.log(ipv6Status);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
            parent.getSwitchStatus();
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert(result.msg, { icon: 6 });
                        break;
                    case 0:
                        layer.alert(result.msg, { icon: 2 });
                        parent.getSwitchStatus();
                        break;
                    default:
                        layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                        parent.getSwitchStatus();
                        break;
                }
            }
            else {
                layer.alert("IPV6功能开启失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        parent.getSwitchStatus();
        console.error("ERROR - IptypeSystemController.setSwitch() - Unable to get the device remote status: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.IptypeSystemController", IptypeSystemController);
