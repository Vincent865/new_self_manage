function OperationLogController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.controller = controller;
    this.elementId = elementId;

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnExport = "#" + this.elementId + "_btnExport";
    this.pBtnSearch = "#" + this.elementId + "_btnSearch";
    this.pBtnFilter = "#" + this.elementId + "_btnFilter";
    this.pDivFilter = "#" + this.elementId + "_divFilter";

    this.pTxtUserName = "#" + this.elementId + "_txtUserName";
    this.pTxtIP = "#" + this.elementId + "_txtIP";
    this.pTxtExcuteCmd = "#" + this.elementId + "_txtExecuteCmd";
    this.pTxtStartDateTime = "#" + this.elementId + "_txtStartDateTime";
    this.pTxtEndDateTime = "#" + this.elementId + "_txtEndDateTime";
    this.pDdlExecuteStatus = "#" + this.elementId + "_ddlExecuteStatus";

    this.pTdLogList = "#" + this.elementId + "_tdLogList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotalLog = "#" + this.elementId + "_lblTotalLog";

    this.pager = null;
    this.filter = {
        page: 1,
        ip: "",
        oper: "",
        oper_result: "",
        user: "",
        starttime: "",
        endtime: ""
    };
}

OperationLogController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.LOG_OPERATION), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - OperationLogController.init() - Unable to initialize: " + err.message);
    }
}

OperationLogController.prototype.initControls = function () {
    try {
        var parent = this;

        this.pViewHandle.find(this.pBtnFilter).on("click", function () {
            parent.pViewHandle.find(parent.pTxtUserName).val("");
            parent.pViewHandle.find(parent.pTxtIP).val("");
            parent.pViewHandle.find(parent.pTxtExcuteCmd).val("");
            parent.pViewHandle.find(parent.pTxtStartDateTime).val("");
            parent.pViewHandle.find(parent.pTxtEndDateTime).val("");
            parent.pViewHandle.find(parent.pDdlExecuteStatus).val("");
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            parent.pViewHandle.find(parent.pDivFilter).toggle();
        });

        this.pViewHandle.find(this.pBtnExport).on("click", function () {
            parent.exportLog();
        });

        this.pViewHandle.find(this.pBtnRefresh).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectLogs();
        });

        this.pViewHandle.find(this.pBtnSearch).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectLogs();
        });
    }
    catch (err) {
        console.error("ERROR - OperationLogController.initControls() - Unable to initialize control: " + err.message);
    }
}

OperationLogController.prototype.load = function () {
    try {
        this.selectLogs();
    }
    catch (err) {
        console.error("ERROR - OperationLogController.load() - Unable to load: " + err.message);
    }
}

OperationLogController.prototype.exportLog = function () {
    try {
        var parent = this,dlTimer;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].EXPORT_OPER_LOG;
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
                        $('<iframe style="display:none;" src="'+APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].OPER_LOG_FILEPATH + result.filename + '?loginuser=' + JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']).username + '"></iframe>').insertAfter($(parent.pBtnExport));
                        clearTimeout(dlTimer);
                        dlTimer=setTimeout(function(){
                            $(parent.pBtnExport).next().remove();
                        },2000);
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
        console.error("ERROR - OperationLogController.exportLog() - Unable to export all events: " + err.message);
    }
}

OperationLogController.prototype.selectLogs = function () {
    var parent = this;
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].SEARCH_OPER_LOG_LIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST",this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='5'>暂无数据</td></tr>";
            parent.pViewHandle.find(parent.pTdLogList+">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>" + FormatterManager.formatToLocaleDateTime(result.rows[i][0]) + "</td>";
                        html += "<td>" + result.rows[i][1] + "</td>";
                        html += "<td>" + result.rows[i][2] + "</td>";
                        html += "<td class='log_info' title='"+result.rows[i][3]+"'>" + result.rows[i][3] + "</td>";
                        if (result.rows[i][4] == "0") {
                            html += "<td class='fontcolor-success'>" + parent.formatExecutetatus(result.rows[i][4]) + "</td>";
                        } else {
                            html += "<td class='fontcolor-defeat'>" + parent.formatExecutetatus(result.rows[i][4]) + "</td>";
                        }
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='5'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='5'>暂无数据</td></tr>";
            }
            if (typeof (result.total) != "undefined") {
                parent.controller.pViewHandle.find(parent.controller.pTotalOperationLog).text(result.total);
            }
            parent.pViewHandle.find(parent.pTdLogList+">tbody").html(html);
            layer.close(loadIndex);

            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController(parent.pViewHandle.find(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectLogs();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='5'>暂无数据</td></tr>";
        this.pViewHandle.find(this.pTdLogList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - OperationLogController.selectLogs() - Unable to get logs: " + err.message);
    }
}

OperationLogController.prototype.formatExecutetatus = function (status) {
    try {
        switch (status) {
            case "1": return "失败";
            case "0": return "成功";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - OperationLogController.formatReadStatus() - Unable to format Executetatus: " + err.message);
    }
}

OperationLogController.prototype.formatFilter = function () {
    try {
        this.filter.ip = $.trim(this.pViewHandle.find(this.pTxtIP).val());
        this.filter.oper = $.trim(this.pViewHandle.find(this.pTxtExcuteCmd).val());
        this.filter.oper_result = this.pViewHandle.find(this.pDdlExecuteStatus).val();
        this.filter.user = $.trim(this.pViewHandle.find(this.pTxtUserName).val());
        this.filter.starttime = $.trim(this.pViewHandle.find(this.pTxtStartDateTime).val());
        this.filter.endtime = $.trim(this.pViewHandle.find(this.pTxtEndDateTime).val());
    }
    catch (err) {
        console.error("ERROR - OperationLogController.formatFilter() - Unable to get filter: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.log.OperationLogController", OperationLogController);