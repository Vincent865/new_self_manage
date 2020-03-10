function SwitchSystemController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;
    this.isTestSuccess = false;
   
    this.pRabFlow = "#"+this.elementId + "_rabFlow";
    this.pBtnFlowSwitch = "#" + this.elementId + "_btnFlowSwitch";

    this.pDevChecktime = "#"+this.elementId + "_devChecktime";
    this.pBtnDevSwitch = "#" + this.elementId + "_btnDevSwitch";
}

SwitchSystemController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_SWITCH), {
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

SwitchSystemController.prototype.initControls = function(){
    try {
        var parent = this;

        this.getDevStatus();
        $(this.pBtnFlowSwitch).on("click", function (event) {
            parent.setFlowSwitch();
        });
        this.getFlowSwitchStatus();
        $(this.pBtnDevSwitch).on("click", function (event) {
            parent.setDevChecktime();
        });
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

SwitchSystemController.prototype.load = function (info) {
    try {
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.load() - Unable to load: " + err.message);
    }
}

SwitchSystemController.prototype.getFlowSwitchStatus = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_FLOW_SWITCH;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.action) != "undefined") {
                switch (result.action){
                    case 1:
                        parent.pViewHandle.find(parent.pRabFlow).prop("checked", true);
                        break;
                    case 0:
                        parent.pViewHandle.find(parent.pRabFlow).prop("checked", false);
                        break;
                    default:
                        parent.pViewHandle.find(parent.pRabFlow).prop("checked", false);
                        break;
                }
            }
            else {
                layer.alert("获取流量告警开关信息失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - SwitchSystemController.getFlowSwitchStatus() - Unable to get the device remote status: " + err.message);
    }
}

SwitchSystemController.prototype.setFlowSwitch = function () {
    var parent = this;
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var FlowStatus = $(this.pRabFlow).prop("checked") ? "1" : "0";
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_FLOW_SWITCH;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {action:parseInt(FlowStatus)});
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
                layer.alert("流量告警开关设置失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        parent.getSwitchStatus();
        console.error("ERROR - SwitchSystemController.setSwitch() - Unable to get the device remote status: " + err.message);
    }
}

SwitchSystemController.prototype.getDevStatus = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEV_STATUS;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.check_time) != "undefined") {
                $(parent.pDevChecktime).val(result.check_time);
            }
            else {
                layer.alert("获取资产告警周期信息失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - SwitchSystemController.getDevStatus() - Unable to get the device remote status: " + err.message);
    }
}

SwitchSystemController.prototype.setDevChecktime = function () {
    var parent = this;
    try {
        var Checktime = $(parent.pDevChecktime).val();
        if(Checktime<1||Checktime>60){
            $(parent.pDevChecktime).val('');
            layer.alert("资产告警检测时间周期范围1-60分钟", { icon: 5 });
            return false;
        }
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEV_STATUS;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {check_time:parseInt(Checktime)});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
            parent.getDevStatus();
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert(result.msg, { icon: 6 });
                        break;
                    case 0:
                        layer.alert(result.msg, { icon: 2 });
                        parent.getDevStatus();
                        break;
                    default:
                        layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                        parent.getDevStatus();
                        break;
                }
            }
            else {
                layer.alert("获取资产告警周期信息失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        parent.getDevStatus();
        console.error("ERROR - SwitchSystemController.setDevChecktime() - Unable to get the device remote status: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.SwitchSystemController", SwitchSystemController);
