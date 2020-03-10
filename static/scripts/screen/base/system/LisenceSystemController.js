function LisenceSystemController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;

    this.pBtnDevCode = "#" + this.elementId + "_getDevCode";
    this.pCodeinfo = "#" + this.elementId + "_codeinfo";
    this.pInfoExpire = "#" + this.elementId + "_expires";
    this.pInfoFunc = "#" + this.elementId + "_func";
    
    this.pBtnUpload = "#" + this.elementId + "_btnUpload";
    this.pFileUpload = "#" + this.elementId + "_fileUpload";
    this.pFormUpload = "#" + this.elementId + "_formUpload";
    this.pBtnUpgrade = "#" + this.elementId + "_btnUpgrade";
    this.pErrUpload = "#" + this.elementId + "_errUpload";
}

LisenceSystemController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.LISENCE_RIGHT), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - LisenceSystemController.init() - Unable to initialize: " + err.message);
    }
}

LisenceSystemController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pBtnDevCode).on("click", function () {
            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_CODE;
            loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
            var promise = URLManager.getInstance().ajaxCall(link);
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                layer.close(loadIndex);
                layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            });
            promise.done(function (result) {
                if (result) {
                    parent.devCode=result.license_key;
                    $(parent.pCodeinfo).text(result.license_key);
                }
                else {
                    layer.alert('获取机器码失败！', { icon: 5 });
                }
                layer.close(loadIndex);
            });
        });

        $(this.pBtnUpgrade).on("click", function () {
            var fileName = $.trim($(parent.pFileUpload).val());
            if (fileName != "") {
                var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 3).toLowerCase();
                if (fieExtension!=='exe') {
                    if($(parent.pFileUpload)[0].files[0].size>512000){
                        layer.alert("文件大小限制512kb以内！", { icon: 5 });
                        $(parent.pErrUpload).html("请重新选择文件");
                    }else{
                        $(parent.pErrUpload).html(fileName);
                        parent.upgradeDevice();
                    }
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
                if (fieExtension!=='exe') {
                    if($(parent.pFileUpload)[0].files[0].size>512000){
                        layer.alert("文件大小限制512kb以内！", { icon: 5 });
                        $(parent.pErrUpload).html("请重新选择文件");
                    }else{
                        $(parent.pErrUpload).html(fileName);
                    }
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
        console.error("ERROR - LisenceSystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

LisenceSystemController.prototype.load = function () {
    try {
        this.pViewHandle.find("#loginuser").val(AuthManager.getInstance().getUserName());
        $(this.pInfoExpire).text(license_expire?'永久':'未授权');
        $(this.pInfoFunc).text(license_func?'全功能':'未授权');
    }
    catch (err) {
        console.error("ERROR - LisenceSystemController.load() - Unable to load: " + err.message);
    }
}


LisenceSystemController.prototype.checkUpgradedSpace = function (callback) {
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
        console.error("ERROR - LisenceSystemController.checkUpgradedSpace() - Unable to check space: " + err.message);
    }
}

LisenceSystemController.prototype.upgradeDevice = function () {
    var layerIndex;
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPLOAD_LICENSE_FILE;
        $(this.pFormUpload).ajaxSubmit({
            type: 'POST',
            url: link,
            success: function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 0:
                            layer.alert(result.msg, { icon: 5 }); break;
                        case 1:
                            layer.alert("license授权成功", { icon: 6 }); 
                            $(parent.pInfoExpire).text(result.license_time?'永久':'未授权');
                            $(parent.pInfoFunc).text(result.license_func?'全功能':'未授权');
                            location.replace('/templates/index.html');
                            break;
                        default: $(parent.pErrUpload).html("");
                            break;
                    }
                }
                else {
                    parent.isRedirect = false;
                    layer.alert("授权失败", { icon: 5 });
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
        console.error("ERROR - LisenceSystemController.upgradeDevice() - Unable to upgrade device: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.LisenceSystemController", LisenceSystemController);