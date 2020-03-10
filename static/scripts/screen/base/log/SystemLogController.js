function SystemLogController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.controller = controller;

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnExport = "#" + this.elementId + "_btnExport";
    this.pBtnSearch = "#" + this.elementId + "_btnSearch";
    this.pBtnFilter = "#" + this.elementId + "_btnFilter";
    this.pDivFilter = "#" + this.elementId + "_divFilter";

    this.pTxtLogContent = "#" + this.elementId + "_txtLogContent";
    this.pTxtStartDateTime = "#" + this.elementId + "_txtStartDateTime";
    this.pTxtEndDateTime = "#" + this.elementId + "_txtEndDateTime";

    this.pTdLogList = "#" + this.elementId + "_tdLogList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";

    this.pager = null;
    this.filter = {
        page: 1,
        status: "",
        level: "",
        content: "",
        starttime: "",
        endtime: ""
    };

}

SystemLogController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.LOG_SYSTEM), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - SystemLogController.init() - Unable to initialize: " + err.message);
    }
}

SystemLogController.prototype.initControls = function () {
    try {
        var parent = this;

        this.pViewHandle.find(this.pBtnRefresh).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectLogs();
        });

        this.pViewHandle.find(this.pBtnExport).on("click", function () {
            parent.exportLog();
        });

        this.pViewHandle.find(this.pBtnFilter).on("click", function () {
            parent.pViewHandle.find(parent.pTxtLogContent).val("");
            parent.pViewHandle.find(parent.pTxtStartDateTime).val("");
            parent.pViewHandle.find(parent.pTxtEndDateTime).val("");
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            parent.pViewHandle.find(parent.pDivFilter).toggle();
        });

        this.pViewHandle.find(this.pBtnSearch).on("click", function () {
            if (!Validation.validateSpecialChart($(parent.pTxtLogContent).val())) {
                $(parent.pTxtLogContent).val("");
                return;
            }
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectLogs();
        });

        this.pViewHandle.find(this.pTxtLogContent).on("change", function () {
            if (!Validation.validateSpecialChart($(parent.pTxtLogContent).val()))
            {
                $(parent.pTxtLogContent).val("");
            }
        });
    }
    catch (err) {
        console.error("ERROR - SystemLogController.initControls() - Unable to initialize control: " + err.message);
    }
}

SystemLogController.prototype.load = function () {
    try {
        this.selectLogs();
    }
    catch (err) {
        console.error("ERROR - SystemLogController.load() - Unable to load: " + err.message);
    }
}

SystemLogController.prototype.exportLog = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].EXPORT_SYS_EVENT;
        var loadIndex = layer.load(2);
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
                        window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].SYS_EVENT_FILEPATH + result.filename + '?loginuser=' + JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']).username);
                        break;
                    default: layer.alert("导出失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("导出失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - SystemLogController.exportEvent() - Unable to export all events: " + err.message);
    }
}

SystemLogController.prototype.selectLogs = function () {
    var parent = this;
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].SEARCH_SYS_EVENT;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='4'>暂无数据</td></tr>";;
            parent.pViewHandle.find(parent.pTdLogList + ">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>" + FormatterManager.formatToLocaleDateTime(result.rows[i][2]) + "</td>";
                        html += "<td>" + parent.formatLogLevel(result.rows[i][0]) + "</td>";
                        html += "<td>" + parent.formatLogType(result.rows[i][1]) + "</td>";
                        html += "<td>" + result.rows[i][3] + "</td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='4'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='4'>暂无数据</td></tr>";
            }
            if (typeof (result.total) != "undefined") {
                parent.controller.pViewHandle.find(parent.controller.pTotalSystemLog).text(result.total);
            }
            parent.pViewHandle.find(parent.pTdLogList + ">tbody").html(html);
            layer.close(loadIndex);

            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectLogs();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='4'>暂无数据</td></tr>";
        parent.pViewHandle.find(parent.pTdLogList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - SystemLogController.selectLogs() - Unable to search log: " + err.message);
    }
}

SystemLogController.prototype.formatLogLevel = function (status) {
    try {
        switch (status) {
            case 0: return "紧急";
            case 1: return "警告";
            case 2: return "严重";
            case 3: return "错误";
            case 4: return "警示";
            case 5: return "通知";
            case 6: return "信息";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - SystemLogController.formatLogLevel() - Unable to format LogLevel: " + err.message);
    }
}

SystemLogController.prototype.formatReadStatus = function (status) {
    try {
        switch (status) {
            case 1: return "已读";
            case 0: return "未读";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - SystemLogController.formatReadStatus() - Unable to format ReadStaus: " + err.message);
    }
}

SystemLogController.prototype.formatLogType = function (v) {
    try {
        switch (v) {
            case 1: return "设备状态";
            case 2: return "接口状态";
            case 3: return "系统状态";
            case 4: return "业务状态";
            case 5: return "bypass状态";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - SystemLogController.formatLogType() - Unable to format LogType: " + err.message);
    }
}

SystemLogController.prototype.formatFilter = function () {
    try {
        this.filter.content = $.trim($(this.pTxtLogContent).val());
        this.filter.starttime = $.trim($(this.pTxtStartDateTime).val());
        this.filter.endtime=$.trim($(this.pTxtEndDateTime).val());
    }
    catch (err) {
        console.error("ERROR - SystemLogController.formatFilter() - Unable to get filter for searching: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.log.SystemLogController", SystemLogController);