function DebugDiagnosisController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.controller = controller;

    this.pLblDebugDatetime = "#" + this.elementId + "_lblDebugDatetime";
    this.pLblDebugResult = "#" + this.elementId + "_lblDebugResult";
    this.pLblDebugFolder = "#" + this.elementId + "_lblDebugFolder";
    this.pBtnDebugRecovery = "#" + this.elementId + "_btnDebugRecovery";
    this.pBtnDebugExport = "#" + this.elementId + "_btnDebugExport";
    this.pDdlTest = "#" + this.elementId + "_ddlTest";
    this.download_path = "";
}

DebugDiagnosisController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.DIAGNOSIS_DEBUG), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - DebugDiagnosisController.init() - Unable to initialize: " + err.message);
    }
}

DebugDiagnosisController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pBtnDebugRecovery).on("click", function (event) {
            parent.recoveryDebugInformation();
        });

        $(this.pBtnDebugExport).on("click", function () {
            parent.exportDebugInformation();
        });
    }
    catch (err) {
        console.error("ERROR - DebugDiagnosisController.initControls() - Unable to initialize control: " + err.message);
    }
}

DebugDiagnosisController.prototype.load = function () {
    try {
        this.getDebugInformation();
    }
    catch (err) {
        console.error("ERROR - DebugDiagnosisController.load() - Unable to load: " + err.message);
    }
}

DebugDiagnosisController.prototype.getDebugInformation = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEBUG_INFO;
        var loadIndex = layer.load(2);
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined"&& result.status== 1) {
                $(parent.pLblDebugDatetime).text(result.timestamp == "" ? "无" : result.timestamp);
                $(parent.pLblDebugResult).text(result.timestamp == "" ? "无" :result.collectstatus == 1 ? "成功" : "失败");
                $(parent.pLblDebugFolder).text(result.filename == "" ? "无" : result.filename);
                parent.download_path = result.rel_file;
            }
            else {
                layer.alert("获取调试信息收集失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - DebugDiagnosisController.getDebugInformation() - Unable to get the debug information: " + err.message);
    }
}

DebugDiagnosisController.prototype.recoveryDebugInformation = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].RECOVERY_DEBUG_INFO;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1) {
                $(parent.pLblDebugDatetime).text(result.timestamp == "" ? "无" : result.timestamp);
                $(parent.pLblDebugResult).text(result.collectstatus == 1 ? "成功" : "失败");
                $(parent.pLblDebugFolder).text(result.filename == "" ? "无" : result.filename);
                parent.download_path = result.rel_file;
            }
            else {
                layer.alert("收集信息失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - DebugDiagnosisController.getDeviceRemote() - Unable to recovery the debug information: " + err.message);
    }
}

DebugDiagnosisController.prototype.exportDebugInformation = function () {
    try {
        var parent = this;
        if (parent.download_path != "") {
            window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEBUG_INFO_PATH +parent.download_path);
        }
        else {
            layer.alert("文件不存在，无法导出调试信息", { icon: 5 });
        }
    }
    catch (err) {
        console.error("ERROR - DebugDiagnosisController.exportDebugInformation() - Unable to export the debug information: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.diagnosis.DebugDiagnosisController", DebugDiagnosisController);