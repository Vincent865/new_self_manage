function WhitelistController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.studyHolder = "#"+this.elementId+"_studyHolder";
    this.defineHolder = "#" + this.elementId + "_defineHolder";
    this.pBtnExport = "#" + this.elementId + "_btnExport";

    this.pStudyWhitelistController = null;
    this.pDefineWhitelistController = null;
    this.currentTabId = "";
    this.currentTabHolder = null;
    this.studyTimer = null;
}

WhitelistController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.RULE_WHITELIST_STUDY],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - WhitelistController.init() - Unable to initialize all templates: " + err.message);
    }
}

WhitelistController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_WHITELIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls
        this.initControls();
    }
    catch (err) {
        console.error("ERROR - WhitelistController.initShell() - Unable to initialize: " + err.message);
    }
}

WhitelistController.prototype.initControls = function () {
    try {
        var parent = this;
        //tab click event
        parent.pViewHandle.find(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.studyHolder:
                    parent.currentTabHolder = $(parent.studyHolder);
                    if (parent.pStudyWhitelistController == null) {
                        parent.pStudyWhitelistController = new tdhx.base.rule.StudyController(parent, parent.currentTabHolder, parent.elementId + "_study");
                        parent.pStudyWhitelistController.init();
                    }
                    break;
                case parent.defineHolder:
                    parent.currentTabHolder = $(parent.defineHolder);
                    if (parent.pDefineWhitelistController == null) {
                        parent.pDefineWhitelistController = new tdhx.base.rule.DefineController(parent, parent.currentTabHolder, parent.elementId + "_define");
                        parent.pDefineWhitelistController.init();
                    }
                    break;
            }
            parent.pViewHandle.find(".tabtitle>ul>li").removeClass("active");
            $(this).addClass("active");
            parent.pViewHandle.find(".row-cutcontent").css("display", "none");
            parent.pViewHandle.find(parent.currentTabHolder).css("display", "block");
        });
        parent.pViewHandle.find(".row-cutbox>ul>li").eq(0).click();

    }
    catch (err) {
        console.error("ERROR - WhitelistController.initControls() - Unable to initialize control: " + err.message);
    }
}

WhitelistController.prototype.load = function () {
    try {
    }
    catch (err) {
        console.error("ERROR - WhitelistController.load() - Unable to load: " + err.message);
    }
}

WhitelistController.prototype.exportWhitelist = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].EXPORT_WHITELIST;
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
                        window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].EXPORT_WHITELIST_FILEPATH + result.filename);
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
        console.error("ERROR - WhitelistController.exportWhitelist() - Unable to export whitelist: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.rule.WhitelistController", WhitelistController);