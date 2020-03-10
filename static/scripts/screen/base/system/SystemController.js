function SystemController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pResetHolder = "#" + this.elementId + "_resetHolder";
    this.pUpgradeHolder = "#" + this.elementId + "_upgradeHolder";
    this.pBackupHolder = "#" + this.elementId + "_backupHolder";
    this.pManagersHolder = "#" + this.elementId + "_managersHolder";
    this.pIpTypeHolder = "#" + this.elementId + "_iptypeHolder";
    this.pLogCollectHolder = "#" + this.elementId + "_logCollectHolder";
    this.pSyslogHolder = "#" + this.elementId + "_syslogHolder";
    this.pSwitchHolder = "#" + this.elementId + "_switchHolder";
    this.pConfExportHolder = "#" + this.elementId + "_confexportHolder";

    this.pTabReset = "#" + this.elementId + "_tabReset";
    this.pTabUpgrade = "#" + this.elementId + "_tabUpgrade";
    this.pTabBackup = "#" + this.elementId + "_tabBackup";
    this.pTabManagers = "#" + this.elementId + "_tabManagers";
    this.pTabIptype = "#" + this.elementId + "_tabIptype";
    this.pTabLogCollect = "#" + this.elementId + "_tabLogCollect";
    this.pTabSyslog = "#" + this.elementId + "_tabSyslog";
    this.pTabSwitch = "#" + this.elementId + "_tabSwitch";
    this.pTabConfExport = "#" + this.elementId + "_tabConfexport";

    this.pResetSystemController = null;
    this.pUpgradeSystemController = null;
    this.pBackupSystemController = null;
    this.pManagersSystemController = null;
    this.pIptypeSystemController = null;
    this.pLogCollectSystemController = null;
    this.pSyslogController = null;
    this.pSwitchController = null;
    this.pConfExportController = null;

    this.currentTabId = "";
    this.currentTabHolder = null;
}

SystemController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.SYSTEM_RESET,
                Constants.TEMPLATES.SYSTEM_UPGRADE,
                Constants.TEMPLATES.SYSTEM_BACKUP,
                Constants.TEMPLATES.SYSTEM_IPTYPE,
                Constants.TEMPLATES.SYSTEM_LOGCOLLECT,
                Constants.TEMPLATES.SYSTEM_SYSLOG,
                Constants.TEMPLATES.SYSTEM_MANAGERS,
                Constants.TEMPLATES.SYSTEM_SWITCH,
                Constants.TEMPLATES.SYSTEM_CONFEXPORT],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - SystemController.init() - Unable to initialize all templates: " + err.message);
    }
}

SystemController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_LIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - SystemController.initShell() - Unable to initialize: " + err.message);
    }
}

SystemController.prototype.initControls = function () {
    try {
        var parent = this;

        //tab click event
        $(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.pTabReset:
                    parent.currentTabHolder = $(parent.pResetHolder);
                    if (parent.pResetSystemController == null) {
                        parent.pResetSystemController = new tdhx.base.system.ResetSystemController(parent, parent.currentTabHolder, parent.elementId + "_system");
                        parent.pResetSystemController.init();
                    }
                    parent.lastTab=parent.pTabReset;
                    break;
                case parent.pTabUpgrade:
                    parent.currentTabHolder = $(parent.pUpgradeHolder);
                    if (parent.pUpgradeSystemController == null) {
                        parent.pUpgradeSystemController = new tdhx.base.system.UpgradeSystemController(parent, parent.currentTabHolder, parent.elementId + "_upgrade");
                        parent.pUpgradeSystemController.init();
                    }
                    parent.lastTab=parent.pTabUpgrade;
                    break;
                case parent.pTabBackup:
                    parent.currentTabHolder = $(parent.pBackupHolder);
                    if (parent.pBackupSystemController == null) {
                        parent.pBackupSystemController = new tdhx.base.system.BackupSystemController(parent, parent.currentTabHolder, parent.elementId + "_manage");
                        parent.pBackupSystemController.init();
                    }
                    parent.lastTab=parent.pTabBackup;
                    break;
                case parent.pTabSyslog:
                    parent.currentTabHolder = $(parent.pSyslogHolder);
                    if (parent.pSyslogController == null) {
                        parent.pSyslogController = new tdhx.base.system.SyslogSystemController(parent, parent.currentTabHolder, parent.elementId + "_syslog");
                        parent.pSyslogController.init();
                    }
                    parent.lastTab=parent.pTabSyslog;
                    break;
                case parent.pTabManagers:
                    parent.currentTabHolder = $(parent.pManagersHolder);
                    if (parent.pManagersSystemController == null) {
                        parent.pManagersSystemController = new tdhx.base.system.ManagersSystemController(parent, parent.currentTabHolder, parent.elementId + "_managers");
                        parent.pManagersSystemController.init();
                    }
                    parent.lastTab=parent.pTabManagers;
                    break;
                case parent.pTabIptype:
                    parent.currentTabHolder = $(parent.pIpTypeHolder);
                    if (parent.pIptypeSystemController == null) {
                        parent.pIptypeSystemController = new tdhx.base.system.IptypeSystemController(parent, parent.currentTabHolder, parent.elementId + "_iptype");
                        parent.pIptypeSystemController.init();
                    }
                    parent.lastTab=parent.pTabIptype;
                    break;
                case parent.pTabLogCollect:
                    parent.currentTabHolder = $(parent.pLogCollectHolder);
                    if (parent.lastTab!=parent.pTabLogCollect) {
                        parent.pLogCollectSystemController = new tdhx.base.system.LogcollectSystemController(parent, parent.currentTabHolder, parent.elementId + "_logcollect");
                        parent.pLogCollectSystemController.init();
                    }
                    parent.lastTab=parent.pTabLogCollect;
                    break;
                case parent.pTabSwitch:
                    parent.currentTabHolder = $(parent.pSwitchHolder);
                    if (parent.pSwitchController == null) {
                        parent.pSwitchController = new tdhx.base.system.SwitchSystemController(parent, parent.currentTabHolder, parent.elementId + "_switch");
                        parent.pSwitchController.init();
                    }
                    break;
                case parent.pTabConfExport:
                    parent.currentTabHolder = $(parent.pConfExportHolder);
                    if (parent.lastTab != parent.pTabConfExport) {
                        parent.pConfExportController = new tdhx.base.system.ConfExportController(parent, parent.currentTabHolder, parent.elementId + "_confexport");
                        parent.pConfExportController.init();
                    }
                    parent.lastTab=parent.pTabConfExport;
                    break;
            }
            $(".row-cutbox>ul>li").removeClass("active");
            $(this).addClass("active");
            $(".row-cutcontent").css("display", "none");
            $(parent.currentTabHolder).css("display", "block");
        });
        $(".row-cutbox>ul>li").eq(0).click();
    }
    catch (err) {
        console.error("ERROR - SystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

SystemController.prototype.load = function () {
    try {
        //this.getLogInfo();
    }
    catch (err) {
        console.error("ERROR - SystemController.load() - Unable to load: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.SystemController", SystemController);
