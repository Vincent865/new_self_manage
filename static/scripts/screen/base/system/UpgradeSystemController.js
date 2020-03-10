function UpgradeSystemController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;
    this.controller = controller;

    this.pBtnUpload = "#" + this.elementId + "_btnUpload";
    this.pFileUpload = "#" + this.elementId + "_fileUpload";
    this.pFormUpload = "#" + this.elementId + "_formUpload";
    this.pBtnUpgrade = "#" + this.elementId + "_btnUpgrade";
    this.pErrUpload = "#" + this.elementId + "_errUpload";
}

UpgradeSystemController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_UPGRADE), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - UpgradeSystemController.init() - Unable to initialize: " + err.message);
    }
}

UpgradeSystemController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pBtnUpgrade).on("click", function () {
            var fileName = $.trim($(parent.pFileUpload).val());
            if (fileName != "") {
                var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 3).toLowerCase();
                if (fieExtension == "bin" || fieExtension == "tgz") {
                    $(parent.pErrUpload).html(fileName);
                    parent.checkUpgradedSpace(function () {
                        parent.upgradeDevice();
                    });
                }
                else {
                    layer.alert("文件格式不对！", { icon: 5 });
                    $(parent.pErrUpload).html("文件格式不对");
                }
            }
            else {
                layer.alert("选择上传文件！", { icon: 5 });
                $(parent.pErrUpload).html("选择上传文件");
            }
            return false;
        });

        $(this.pFileUpload).on("change", function () {
            var fileName = $.trim($(this).val());
            if (fileName != "") {
                var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 3).toLowerCase();
                if (fieExtension == "bin") {
                    $(parent.pErrUpload).html(fileName);
                }
                else {
                    $(parent.pErrUpload).html("文件格式不对");
                }
            }
            else {
                $(parent.pErrUpload).html("选择上传文件");
            }
        });
    }
    catch (err) {
        console.error("ERROR - UpgradeSystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

UpgradeSystemController.prototype.load = function () {
    try {

        this.pViewHandle.find("#loginuser").val(AuthManager.getInstance().getUserName());
    }
    catch (err) {
        console.error("ERROR - UpgradeSystemController.load() - Unable to load: " + err.message);
    }
}

UpgradeSystemController.prototype.gotoPage = function () {
    if (this.isRedirect == true) {
        window.location.replace(APPCONFIG[APPCONFIG.PRODUCT].LOGIN_URL);
    }
}

UpgradeSystemController.prototype.checkUpgradedSpace = function (callback) {
    var loadIndex;
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].CHECK_UPGRADED_FILESIZE;
        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1) {
                callback();
            }
            else {
                layer.alert("磁盘空间不够，无法升级", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - UpgradeSystemController.checkUpgradedSpace() - Unable to check space: " + err.message);
    }
}

UpgradeSystemController.prototype.upgradeDevice = function () {
    var layerIndex;
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPGRADE_DEVICE;
        layerIndex = layer.msg("正在升级，请稍后登录...", {
            time: 600000,
            shade: [0.5, '#fff']
        }, function () {
            parent.gotoPage();
        });
        $(this.pFormUpload).ajaxSubmit({
            type: 'POST',
            url: link,
            success: function (result) {
                result = $.parseJSON(result);
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 0:
                            parent.isRedirect = false;
                            layer.alert("升级失败", { icon: 5 }); break;
                        case 2:
                            parent.isRedirect = false;
                            layer.alert("升级磁盘空间不足", { icon: 5 }); break;
                        default: $(parent.pErrUpload).html("");
                            break;
                    }
                }
                else {
                    parent.isRedirect = false;
                    layer.alert("升级失败", { icon: 5 });
                }
                $(parent.pFileUpload).val("");
            },
            error: function (XmlHttpRequest, textStatus, errorThrown) {
                $(parent.pFileUpload).val("");
            }
        });
    }
    catch (err) {
        this.isRedirect = false;
        layer.close(layerIndex);
        console.error("ERROR - UpgradeSystemController.upgradeDevice() - Unable to upgrade device: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.UpgradeSystemController", UpgradeSystemController);