function SysDebugController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pPcapHolder = "#" + this.elementId + "_pcapHolder";
    this.pDebugHolder = "#" + this.elementId + "_debugHolder";

    this.pTabPcap = "#" + this.elementId + "_tabPcap";
    this.pTabDebug = "#" + this.elementId + "_tabDebugInfo";

    this.pPcapController = null;
    this.pDebugController = null;

    this.currentTabId = "";
    this.currentTabHolder = null;
}

SysDebugController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.SYSTEM_PCAP,
                Constants.TEMPLATES.SYSTEM_DEBUG_INFO],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - SysDebugController.init() - Unable to initialize all templates: " + err.message);
    }
}

SysDebugController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_DEBUG), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - SysDebugController.initShell() - Unable to initialize: " + err.message);
    }
}

SysDebugController.prototype.initControls = function () {
    try {
        var parent = this;
        //tab click event
        $(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.pTabPcap:
                    parent.currentTabHolder = $(parent.pPcapHolder);
                    if (parent.pPcapController == null) {
                        parent.pPcapController = new tdhx.base.system.PcapController(parent, parent.currentTabHolder, parent.elementId + "_pcap");
                        parent.pPcapController.init();
                    }
                    break;
                case parent.pTabDebug:
                    parent.currentTabHolder = $(parent.pDebugHolder);
                    if (parent.pDebugController == null) {
                        parent.pDebugController = new tdhx.base.system.DebugInfoController(parent, parent.currentTabHolder, parent.elementId + "_debugInfo");
                        parent.pDebugController.init();
                    }
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
        console.error("ERROR - SysDebugController.initControls() - Unable to initialize control: " + err.message);
    }
}

SysDebugController.prototype.load = function () {
    try {
        //this.getLogInfo();
    }
    catch (err) {
        console.error("ERROR - SysDebugController.load() - Unable to load: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.SysDebugController", SysDebugController);
