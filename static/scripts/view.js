function View() {
    this.pInstance = null;
    this.type = null;
    this.pageName = null;
    this.content = "";
    this.controller = null;
    this.viewHandle = $("#viewContainer");
}

View.getInstance = function () {
    if (!this.pInstance) {
        this.pInstance = new View();
    }
    return this.pInstance;
};

View.prototype.clearAllTimer = function (timers) {
    $.each(timers, function (k) {
        clearInterval(timers[k]);
    });
};

View.prototype.init = function (type, pageName) {
    var parent = this;
    this.type = type;
    this.pageName = pageName;

    if (typeof (this.controller != null) != "undefined" && this.controller != null) {
        if (typeof (this.controller.disposeTipBox) == "function") {
            this.controller.disposeTipBox();
        }
        if (typeof (this.controller.clearTimer) == "function") {
            this.controller.clearTimer();
        }
        if (typeof (this.controller.totalFlowTimer) != "undefined" && typeof (this.controller.totalFlowTimer) != null) {
            clearInterval(this.controller.totalFlowTimer);
        }
        if (typeof (this.controller.studyTimer) != "undefined" && typeof (this.controller.studyTimer) != null) {
            clearInterval(this.controller.studyTimer);
        }
    }
    //����û�
    AuthManager.getInstance().isLoggedIn(function () {
        AuthManager.getInstance().checkUser();
    }, function () {
        AuthManager.getInstance().logOut();
    });
    //clearInterval(sysTimer);
    //getSysTime();
    switch (type) {
        case Constants.PageType.HOME:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES[APPCONFIG.PRODUCT].HOME_DASHBOARD
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.home.HomeController(parent.viewHandle, "home");
                parent.controller.init();
            });
            break;
        case Constants.PageType.USER:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.USER_EDIT
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.user.UserController(parent.viewHandle, "user");
                parent.controller.init();
            });
            break;
        case Constants.PageType.UKEY:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.UKEY_EDIT
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.user.UkeyController(parent.viewHandle, "ukey");
                parent.controller.init();
            });
            break;
        case Constants.PageType.LISENCE:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.LISENCE_RIGHT
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.system.LisenceSystemController(parent.viewHandle, "license");
                parent.controller.init();
            });
            break;
        case Constants.PageType.EVENT:
            TemplateManager.getInstance().requestTemplates([
            Constants.TEMPLATES.EVENT_LIST,
            Constants.TEMPLATES.EVENT_DIALOG,
            Constants.TEMPLATES.INVALID_DIALOG,
            Constants.TEMPLATES.EVENT_ASSETDIALOG,
            Constants.TEMPLATES.EVENT_FLOWDIALOG
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.event.EventController(parent.viewHandle, "event");
                parent.controller.init();
            });
            break;
        case Constants.PageType.MACFILTER:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.RULE_MAC_FILTER
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.rule.MacFilterRuleController(parent.viewHandle, "rulefilter");
                parent.controller.init();
            });
            break;
        case Constants.PageType.STREAM:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.STREAM_LIST
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.stream.StreamController(parent.viewHandle, "stream");
                parent.controller.init();
            });
            break;
        case Constants.PageType.LOG:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.LOG_LIST
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.log.LogController(parent.viewHandle, "log");
                parent.controller.init();
            });
            break;
        case Constants.PageType.COLLECTLOG:
            TemplateManager.getInstance().requestTemplates([
            Constants.TEMPLATES.COLLECT_LIST
            ], function () {
                parent.clearAllTimer(gloTimer);                 new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.collect.CollectLogController(parent.viewHandle, "collectlog");
                parent.controller.init();
            });
            break;
        case Constants.PageType.DEVICE:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.DEVICE_LIST,
                Constants.TEMPLATES.DEVICE_MODE
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.device.DeviceController(parent.viewHandle, "device");
                parent.controller.init();
            });
            break;
        case Constants.PageType.DEBUG:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.SYSTEM_DEBUG
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.system.SysDebugController(parent.viewHandle, "debug");
                parent.controller.init();
            });
            break;
        case Constants.PageType.SYSTEM:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.SYSTEM_LIST
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.system.SystemController(parent.viewHandle, "system");
                parent.controller.init();
            });
            break;
        case Constants.PageType.DIAGNOSIS:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.DIAGNOSIS_LIST
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.diagnosis.DiagnosisController(parent.viewHandle, "diagnosis");
                parent.controller.init();
            });
            break;
        case Constants.PageType.MAC:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.RULE_MAC
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.rule.MacRuleController(parent.viewHandle, "rule");
                parent.controller.init();
            });
            break;
        case Constants.PageType.WHITELIST:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.RULE_WHITELIST,
                Constants.TEMPLATES.RULE_WHITELIST_STUDY
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.rule.WhitelistController(parent.viewHandle, "whitelist");
                parent.controller.init();
            });
            break;
        case Constants.PageType.BLACKLIST:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.RULE_BLACKLIST
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.rule.BlacklistController(parent.viewHandle, "blacklist");
                parent.controller.init();
            });
            break;
        case Constants.PageType.ASLIST:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.RULE_AUDITSTRATEGY_LIST
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.auditstrategy.AsController(parent.viewHandle, "auditstrategy");
                parent.controller.init();
            });
            break;
        case Constants.PageType.NETTOPO:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.TOPO_TOPOLIST
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.topo.TopolistController(parent.viewHandle, "nettopo");
                parent.controller.init();
            });
            break;

        case Constants.PageType.SWITCH:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.SWITCH_LIST
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.topo.SwitchlistController(parent.viewHandle, "switch");
                parent.controller.init();
            });
            break;
        case Constants.PageType.PROTOCOL:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.AUDIT_PROTOCOL
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.audit.ProtocolAuditController(parent.viewHandle, "protocol");
                parent.controller.init();
            });
            break;
        case Constants.PageType.CUSTOMPROTO:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.RULE_AUDITSTRATEGY_CUSPROTOCOL
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.protoaudit.CusProtoController(parent.viewHandle, "cusproto");
                parent.controller.init();
            });
            break;
        case Constants.PageType.PROTOTPL_CONF:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.PROTOTPLCONF_LIST
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.protoaudit.prototplController(parent.viewHandle, "prototpl");
                parent.controller.init();
            });
            break;
        case Constants.PageType.BEHAVIOR:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.BEHAVIOR_LIST
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.behavior.BehaviorController(parent.viewHandle, "behavior");
                parent.controller.init();
            });
            break;
        case Constants.PageType.FLOW:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.AUDIT_FLOW
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.audit.FlowAuditController(parent.viewHandle, "flow");
                parent.controller.init();
            });
            break;
        case Constants.PageType.REPORTEVENT:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.REPORT_EVENT
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.report.ReportEventController(parent.viewHandle, "reportevent");
                parent.controller.init();
            });
            break;
        case Constants.PageType.REPORTLOG:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.REPORT_LOG
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.report.ReportLogController(parent.viewHandle, "reportlog");
                parent.controller.init();
            });
            break;
        case Constants.PageType.REPORTAUDIT:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.REPORT_AUDIT
            ], function () {
                parent.clearAllTimer(gloTimer); new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.report.ReportAuditController(parent.viewHandle, "reportaudit");
                parent.controller.init();
            });
            break;
        case Constants.PageType.REPORTASSET:
            TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.REPORT_ASSET
            ], function () {
                parent.clearAllTimer(gloTimer);                 new HeaderController($(".header")).getSystemTime();
                parent.controller = new tdhx.base.report.ReportAssetController(parent.viewHandle, "reportasset");
                parent.controller.init();
            });
            break;
        default:
            //handle error page
            this.viewHandle.html(ContentFactory.renderPageShell());
            break;
    }
}