function ProtocolController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.controller = controller;

    this.pRabModbus = "#" + this.elementId + "_rabModbus";
    this.pRabOpcda = "#" + this.elementId + "_rabOpcda";
    this.pRabIec104 = "#" + this.elementId + "_rabIec104";
    this.pRabDnp3 = "#" + this.elementId + "_rabDnp3";
    this.pRabMms = "#" + this.elementId + "_rabMms";
    this.pRabS7 = "#" + this.elementId + "_rabS7";
    this.pRabProfinetio = "#" + this.elementId + "_rabProfinetio";
    this.pRabGoose = "#" + this.elementId + "_rabGoose";
    this.pRabSv = "#" + this.elementId + "_rabSv";
    this.pRabEnip = "#" + this.elementId + "_rabEnip";
    this.pRabOpcua = "#" + this.elementId + "_rabOpcua";
    this.pRabPnrtdcp = "#" + this.elementId + "_rabPnrtdcp";
    this.pRabSnmp = "#" + this.elementId + "_rabSnmp";
    //this.pRabFocas = "#"+this.elementId + "_rabFocas";
    this.pRabOracle = "#" + this.elementId + "_rabOracle";
    this.pRabFtp = "#" + this.elementId + "_rabFtp";
    this.pRabTelnet = "#" + this.elementId + "_rabTelnet";
    this.pRabHttp = "#" + this.elementId + "_rabHttp";
    this.pRabPop3 = "#" + this.elementId + "_rabPop3";
    this.pRabSmtp = "#" + this.elementId + "_rabSmtp";
    this.pRabSip = "#" + this.elementId + "_rabSip";
    this.pRabSqlserver = "#" + this.elementId + "_rabSqlserver";
    this.pTdProtocol = "." + this.elementId + "_tdProtocol";

    this.pBtnSave = "#" + this.elementId + "_btnSave";
    this.pBtnReset = "#" + this.elementId + "_btnReset";
    this.pBtnEnableAll = "#" + this.elementId + "_btnEnableAll";
    this.pBtnDisableAll = "#" + this.elementId + "_btnDisableAll";
}

ProtocolController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_AUDITSTRATEGY_PROTOCOL), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - ProtocolDeviceController.init() - Unable to initialize: " + err.message);
    }
}

ProtocolController.prototype.initControls = function () {
    try {
        var parent = this;

        this.pViewHandle.find(this.pBtnEnableAll).on("click", function () {
            parent.enableDeviceProtocol();
        });

        this.pViewHandle.find(this.pBtnDisableAll).on("click", function () {
            parent.disableDeviceProtocol();
        });

        this.pViewHandle.find(this.pBtnSave).on("click", function () {
            parent.updateDeviceProtocol();
        });

        this.pViewHandle.find(this.pBtnReset).on("click", function () {
            parent.getDeviceProtocol();
        });
    }
    catch (err) {
        console.error("ERROR - ProtocolDeviceController.initControls() - Unable to initialize control: " + err.message);
    }
}

ProtocolController.prototype.load = function () {
    try {
        var parent = this;
        this.getProtocol(function () {
            parent.getDeviceProtocol();
        });
    }
    catch (err) {
        console.error("ERROR - ProtocolDeviceController.load() - Unable to load: " + err.message);
    }
}

ProtocolController.prototype.getProtocol = function (callback) {
    try {
        var protocolArray = $.grep(Constants.PROTOCOL_LIST[APPCONFIG.PRODUCT],function(item){
            return item.show;
        });
        var html = "",tr={},tr1={},cur,cur1;
        if (typeof (protocolArray) != "undefined" && protocolArray.length > 0) {
            var indusProto=[],normalProto=[];
            for (var i = 0; i < protocolArray.length; i++) {
                if(protocolArray[i].key=='ftp'||protocolArray[i].key=='telnet'||protocolArray[i].key=='snmp'||protocolArray[i].key=='http'||protocolArray[i].key=='smtp'||protocolArray[i].key=='pop3'||protocolArray[i].key=='oracle'||protocolArray[i].key=='sqlserver'){
                    normalProto.push(protocolArray[i]);
                }else{
                    indusProto.push(protocolArray[i]);
                }
            }
            for (var i = 0; i < indusProto.length; i++) {
                if(!(i%2)){
                    tr1[i]=$('<tr></tr>');
                    $(this.pViewHandle).find(this.pTdProtocol + ">tbody.gk").append(tr1[i]);
                    cur1=tr1[i];
                }
                cur1.append("<td>" + indusProto[i].name + "</td>"+'<td><span class="btn-on-box">'
                    +'<input type="checkbox" class="btn-on" data-key="' + indusProto[i].key + '" id="rab' + indusProto[i].key + '" />'
                    +'<label for="rab' + indusProto[i].key + '"></label>'+'</span></td>');
            }
            for (var i = 0; i < normalProto.length; i++) {
                if(!(i%2)){
                    tr[i]=$('<tr></tr>');
                    $(this.pViewHandle).find(this.pTdProtocol + ">tbody.ct").append(tr[i]);
                    cur=tr[i];
                }
                cur.append("<td>" + normalProto[i].name + "</td>"+'<td><span class="btn-on-box">'
                    +'<input type="checkbox" class="btn-on" data-key="' + normalProto[i].key + '" id="rab' + normalProto[i].key + '" />'
                    +'<label for="rab' + normalProto[i].key + '"></label>'+'</span></td>');
            }
            indusProto.length%2?cur1.append('<td></td><td></td>'):'';
            normalProto.length%2?cur.append('<td></td><td></td>'):'';
            callback();
        }
        else {
            html = "<tr><td colspan='3'>暂无数据</td></tr>";
            $(this.pViewHandle).find(this.pTdProtocol + ">tbody").html(html);
        }
    }
    catch (err) {
        console.error("ERROR - ProtocolDeviceController.getProtocol() - Unable to get all protocol: " + err.message);
    }
}

ProtocolController.prototype.getDeviceProtocol = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PROTOCOL_SWITCH;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                var protocolArray = Constants.PROTOCOL_LIST[APPCONFIG.PRODUCT];
                for (var i = 0; i < protocolArray.length; i++) {
                    parent.pViewHandle.find("input[data-key='" + protocolArray[i].key + "']").prop("checked", result.switch[protocolArray[i].key] == 1 ? true : false);
                }
            }
            else {
                layer.alert("获取协议开关状态失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - ProtocolDeviceController.getDeviceProtocol() - Unable to get the protocol switch status: " + err.message);
    }
}

ProtocolController.prototype.updateDeviceProtocol = function () {
    var parent = this;
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var para = {};
        var protocolArray = Constants.PROTOCOL_LIST[APPCONFIG.PRODUCT];
        for (var i = 0; i < protocolArray.length; i++) {
            para[protocolArray[i].key] = this.pViewHandle.find("input[data-key='" + protocolArray[i].key + "']").prop("checked") ? "1" : "0";
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_PROTOCOL_SWITCH;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", para);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert("更新协议开关状态成功", { icon: 6 });
                        break;
                    default:
                        layer.alert("更新协议开关状态失败", { icon: 5 });
                        break;
                }
            }
            else {
                layer.alert("更新协议开关状态失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - ProtocolController.updateDeviceProtocol() - Unable to update the protocol switch status: " + err.message);
    }
}

ProtocolController.prototype.enableDeviceProtocol = function () {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_PROTOCOL_SWITCH;
        var para = {};
        var protocolArray = Constants.PROTOCOL_LIST[APPCONFIG.PRODUCT];
        for (var i = 0; i < protocolArray.length; i++) {
            para[protocolArray[i].key] = "1";
        }
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", para);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.pViewHandle.find("input[data-key]").prop("checked", true);
                        layer.alert("启用所有协议开关成功", { icon: 6 });
                        break;
                    default:
                        layer.alert("启用所有协议开关失败", { icon: 5 });
                        break;
                }
            }
            else {
                layer.alert("启用所有协议开关失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - ProtocolDeviceController.enableDeviceProtocol() - Unable to enable all the protocol switch status: " + err.message);
    }
}

ProtocolController.prototype.disableDeviceProtocol = function () {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_PROTOCOL_SWITCH;
        var para = {};
        var protocolArray = Constants.PROTOCOL_LIST[APPCONFIG.PRODUCT];
        for (var i = 0; i < protocolArray.length; i++) {
            para[protocolArray[i].key] = "0";
        }
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", para);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.pViewHandle.find("input[data-key]").prop("checked", false);
                        layer.alert("禁用所有协议开关成功", { icon: 6 });
                        break;
                    default:
                        layer.alert("禁用所有协议开关失败", { icon: 5 });
                        break;
                }
            }
            else {
                layer.alert("禁用所有协议开关失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - ProtocolController.disableDeviceProtocol() - Unable to disable all the protocol switch status: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.auditstrategy.ProtocolController", ProtocolController);
