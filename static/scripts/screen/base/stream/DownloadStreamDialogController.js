function DownloadStreamDialogController(controller,viewHandle, elementId,data) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.pController = controller;
    this.data = data;

    this.pLblIP = "#" + this.elementId + "_lblIP";
    this.pLblProtocol = "#" + this.elementId + "_lblProtocol";
    this.pLblMac = "#" + this.elementId + "_lblMac";
    this.pLblDatetime = "#" + this.elementId + "_lblDatetime";
    this.pLblPort = "#" + this.elementId + "_lblPort";
    this.pTxtSessionExtraPwd = "#" + this.elementId + "_session_txtExtraPwd";
    this.pBtnSessionDownload = "#" + this.elementId + "_session_btnDownload";
}

DownloadStreamDialogController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.STREAM_DOWNLOAD_DIALOG), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - DownloadStreamDialogController.init() - Unable to initialize: " + err.message);
    }
}

DownloadStreamDialogController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pBtnSessionDownload).on("click", function () {
            parent.downloadFile(parent.data[8]);
        });
    }
    catch (err) {
        console.error("ERROR - DownloadStreamDialogController.initControls() - Unable to initialize control: " + err.message);
    }
}

DownloadStreamDialogController.prototype.load = function () {
    try {
        /*base data*/
        $(this.pLblDatetime).text(this.data[6]);
        $(this.pLblIP).text(this.data[0] + "<=>" + this.data[1]);
        $(this.pLblMac).text(this.data[2] + "<=>" + this.data[3]);
        $(this.pLblProtocol).text(this.data[7]);
        $(this.pLblPort).text(this.data[4] + "<=>" + this.data[5]);
    }
    catch (err) {
        console.error("ERROR - DownloadStreamDialogController.load() - Unable to load: " + err.message);
    }
}

DownloadStreamDialogController.prototype.downloadFile = function (file) {
    var parent = this;
    try {
        var pwd = $.trim($(this.pTxtSessionExtraPwd).val());
        if (pwd == "") {
            layer.alert("密码不能为空", { icon: 5 });
            return false;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].EXPORT_STREAM_FILEPATH + "?passwd=" + pwd + "&file=" + file;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_STREAM_FILE_FOLDER_PATH + result.filename);
                        break;
                    default: layer.alert("无法下载", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("无法下载", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - DownloadStreamDialogController.downloadFile() - Unable to download file: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.stream.DownloadStreamDialogController", DownloadStreamDialogController);