function StreamController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pRecoverStreamHolder = "#" + this.elementId + "_recoverStreamHolder";
    this.pTotalRecoverStream = "#" + this.elementId + "_totalRecoverStream";

    this.pRecoverStreamController = null;
    this.currentTabId="";
    this.currentTabHolder = null;
}

StreamController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.STREAM_RECOVER,
                Constants.TEMPLATES.STREAM_RECOVER_DIALOG,
                Constants.TEMPLATES.STREAM_DOWNLOAD_DIALOG],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - StreamController.init() - Unable to initialize all templates: " + err.message);
    }
}

StreamController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.STREAM_LIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.load();
        this.initControls();
    }
    catch (err) {
        console.error("ERROR - StreamController.initShell() - Unable to initialize: " + err.message);
    }
}

StreamController.prototype.initControls = function () {
    try {
        var parent = this;
        //tab click event
        $(".tabtitle>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.pTotalRecoverStream:
                    parent.currentTabHolder = $(parent.pRecoverStreamHolder);
                    if (parent.pRecoverStreamController == null) {
                        parent.pRecoverStreamController = new tdhx.base.stream.RecoverStreamController(parent, parent.currentTabHolder, parent.elementId + "_recover");
                        parent.pRecoverStreamController.init();
                    }
                    break;
            }
            $(".tabtitle>ul>li").removeClass("hit");
            $(this).addClass("hit");
            $(".tabmiantxt").css("display", "none");
            $(parent.currentTabHolder).css("display", "block");
        });
        $(".tabtitle>ul>li").eq(0).click();
    }
    catch (err) {
        console.error("ERROR - StreamController.initControls() - Unable to initialize control: " + err.message);
    }
}

StreamController.prototype.load = function () {
    try {
    }
    catch (err) {
        console.error("ERROR - StreamController.load() - Unable to load: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.stream.StreamController", StreamController);