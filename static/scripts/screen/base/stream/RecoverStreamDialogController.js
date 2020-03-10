function RecoverStreamDialogController(controller,viewHandle, elementId,data) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.pController = controller;
    this.data = data;

    this.pLblIP = "#" + this.elementId + "_lblIP";
    this.pLblProtocol = "#" + this.elementId + "_lblProtocol";
    this.pLblMac = "#" + this.elementId + "_lblMac";
    this.pLblDatetime = "#" + this.elementId + "_lblDatetime";
    this.pLblPort = "#" + this.elementId + "_lblPort";
    this.pTabSession = "#" + this.elementId + "_tabSession";
    this.pTabSessionHolder = "#" + this.elementId + "_tabSessionHolder";
    this.pTabFile = "#" + this.elementId + "_tabFile";
    this.pTabFileHolder = "#" + this.elementId + "_tabFileHolder";
    this.pTxtSessionExtraPwd = "#" + this.elementId + "_session_txtExtraPwd";
    this.pBtnSessionDownload = "#" + this.elementId + "_session_btnDownload";
    this.pTxtSessionContent = "#" + this.elementId + "_session_txtContent";
    this.pTxtFileExtraPwd = "#" + this.elementId + "_file_txtExtraPwd";
    this.pBtnFileRefresh = "#" + this.elementId + "_file_btnRefresh";
    this.pTdFileList = "#" + this.elementId + "_file_tdFileList";
    this.pLblFileTotal = "#" + this.elementId + "_file_lblFileTotal";
    this.pPagerContent = "#" + this.elementId + "_file_pagerContent";

    this.pager = null;
    this.currentTabId = "";
    this.currentTabHolder = null;
}

RecoverStreamDialogController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.STREAM_RECOVER_DIALOG), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - RecoverStreamDialogController.init() - Unable to initialize: " + err.message);
    }
}

RecoverStreamDialogController.prototype.initControls = function () {
    try {
        var parent = this;

        //tab click event
        this.pViewHandle.find(".tabtitle>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.pTabSession:
                    parent.currentTabHolder = $(parent.pTabSessionHolder);
                    break;
                case parent.pTabFile:
                    parent.currentTabHolder = $(parent.pTabFileHolder);
                    parent.selectFiles(1);
                    break;
            }
            parent.pViewHandle.find(".tabtitle>ul>li").removeClass("hit");
            $(this).addClass("hit");
            parent.pViewHandle.find(".tabmiantxt").css("display", "none");
            parent.pViewHandle.find(parent.currentTabHolder).css("display", "block");
        });
        this.pViewHandle.find(".tabtitle>ul>li").eq(0).click();

        $(this.pBtnSessionDownload).on("click", function () {
            parent.downloadSession();
        });

        $(this.pBtnFileRefresh).on("click", function () {
            parent.pager = null;
            parent.selectFiles(1);
        });
    }
    catch (err) {
        console.error("ERROR - RecoverStreamDialogController.initControls() - Unable to initialize control: " + err.message);
    }
}

RecoverStreamDialogController.prototype.load = function () {
    try {
        /*base data*/
        $(this.pLblDatetime).text(this.data[6]);
        $(this.pLblIP).text(this.data[0] + "<=>" + this.data[1]);
        $(this.pLblMac).text(this.data[2] + "<=>" + this.data[3]);
        $(this.pLblProtocol).text(this.data[7]);
        $(this.pLblPort).text(this.data[4] + "<=>" + this.data[5]);
        this.getSession();
    }
    catch (err) {
        console.error("ERROR - RecoverStreamDialogController.load() - Unable to load: " + err.message);
    }
}

RecoverStreamDialogController.prototype.selectFiles = function (pageIndex) {
    var html = "";
    html += '<tr class="title">';
    html += '<td class="address" style="width:60%;">文件名</td>';
    html += '<td class="address" style="width:20%;">时间</td>';
    html += '<td style="width:20%;">状态</td>';
    html += '</tr>';
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_STREAM_FILE_DETAIL +"?sessionid="+this.data[9]+ "&page=" + pageIndex;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='3'>暂无数据</td></tr>";
            $(parent.pTdFileList).html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.filelist) != "undefined") {
                if (result.filelist.length > 0) {
                    for (var i = 0; i < result.filelist.length; i++) {
                        html += "<tr>";
                        html += "<td style='width:60%;text-align:left;padding-left:10px;'>" + result.filelist[i][1] + "</td>";
                        html += "<td style='width:20%;'>" + result.filelist[i][0] + "</td>";
                        html += "<td style='width:20%;'><button class='details' data-key='" + result.filelist[i][2] + "'>下载</button></td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='3'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='3'>暂无数据</td></tr>";
            }
            //if (typeof (result.total) != "undefined") {
            //    $(parent.pLblFileTotal).text(result.total);
            //}
            $(parent.pTdFileList).html(html);
            layer.close(loadIndex);

            $(parent.pTdFileList).find("button").on("click", function (stream) {
                var src = $(this).attr("data-key");
                parent.downloadFile(src);
            });

            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.selectFiles(pageIndex);
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER2);
            }

        });
    }
    catch (err) {
        html += "<tr><td colspan='3'>暂无数据</td></tr>";
        $(this.pTdFileList).html(html);
        console.error("ERROR - RecoverStreamController.selectStreams() - Unable to search safe streams via filter: " + err.message);
    }
}

RecoverStreamDialogController.prototype.getSession = function (pageIndex) {
    var parent = this;
    try {
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_STREAM_SESSION_DETAIL + "?sessionid="+this.data[9];
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.data) != "undefined") {
                $(parent.pTxtSessionContent).html("<pre>"+result.data+"</pre>");
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - RecoverStreamController.selectStreams() - Unable to search safe streams via filter: " + err.message);
    }
}

RecoverStreamDialogController.prototype.downloadSession = function () {
    var parent = this;
    try {
        var pwd = $.trim($(this.pTxtSessionExtraPwd).val());
        if (pwd == "")
        {
            layer.alert("密码不能为空", { icon: 5 });
            return false;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].EXPORT_STREAM_FILEPATH + "?passwd=" + pwd + "&file=" + this.data[8];
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
        console.error("ERROR - RecoverStreamController.downloadSession() - Unable to download file: " + err.message);
    }
}

RecoverStreamDialogController.prototype.downloadFile = function (file) {
    var parent = this;
    try {
        var pwd = $.trim($(this.pTxtFileExtraPwd).val());
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
        console.error("ERROR - RecoverStreamController.downloadSession() - Unable to download file: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.stream.RecoverStreamDialogController", RecoverStreamDialogController);