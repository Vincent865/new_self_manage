function LogController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pTotalOperationLog = "#" + this.elementId + "_totalOperationLog";
    this.pTotalSystemLog = "#" + this.elementId + "_totalSystemLog";
    this.pOperatioLogHolder = "#" + this.elementId + "_operationLogHolder";
    this.pSystemLogHolder = "#" + this.elementId + "_systemLogHolder";
    this.pSystemLogController = null;
    this.pOperationLogController = null;
    this.currentTabId="";
    this.currentTabHolder = null;
}

LogController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.LOG_SYSTEM,
                Constants.TEMPLATES.LOG_OPERATION],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - LogController.init() - Unable to initialize all templates: " + err.message);
    }
}

LogController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.LOG_LIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - LogController.initShell() - Unable to initialize: " + err.message);
    }
}

LogController.prototype.initControls = function () {
    try {
        var parent = this;

        //tab click event
        parent.pViewHandle.find(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.pTotalSystemLog:
                    parent.currentTabHolder = $(parent.pSystemLogHolder);
                    if (parent.pSystemLogController == null) {
                        parent.pSystemLogController = new tdhx.base.log.SystemLogController(parent, parent.currentTabHolder, parent.elementId + "_system");
                        parent.pSystemLogController.init();
                    }
                    break;
                case parent.pTotalOperationLog:
                    parent.currentTabHolder = $(parent.pOperatioLogHolder);
                    if (parent.pOperationLogController == null) {
                        parent.pOperationLogController = new tdhx.base.log.OperationLogController(parent, parent.currentTabHolder, parent.elementId + "_operation");
                        parent.pOperationLogController.init();
                    }
                    break;
            }
            parent.pViewHandle.find(".row-cutbox>ul>li").removeClass("active");
            parent.pViewHandle.find(this).addClass("active");
            parent.pViewHandle.find(".row-cutcontent").css("display", "none");
            parent.pViewHandle.find(parent.currentTabHolder).css("display", "block");
        });
        parent.pViewHandle.find(".row-cutbox>ul>li").eq(0).click();
    }
    catch (err) {
        console.error("ERROR - LogController.initControls() - Unable to initialize control: " + err.message);
    }
}

LogController.prototype.load = function () {
    try {
        this.getLogCount();
    }
    catch (err) {
        console.error("ERROR - LogController.load() - Unable to load: " + err.message);
    }
}

LogController.prototype.getLogCount = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_LOG_INFO;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined") {
                parent.pViewHandle.find(parent.pTotalOperationLog).html(result.operlog_num);
                parent.pViewHandle.find(parent.pTotalSystemLog).html(result.syslog_num);
            }
        });
    }
    catch (err) {
        console.error("ERROR - LoginLogController.getLogCount() - Unable to load: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.log.LogController", LogController);