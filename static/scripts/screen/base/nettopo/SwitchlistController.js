function SwitchlistController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pSwitchallHolder = "#" + this.elementId + "_switchallHolder";
    this.pSwitchinfoHolder = "#" + this.elementId + "_switchinfoHolder";

    this.pSwitchall = "#" + this.elementId + "_switchall";
    this.pSwitchinfo = "#" + this.elementId + "_switchinfo";

    this.pSwitchallController = null;
    this.pSwitchinfoController = null;

    this.currentTabId = "";
    this.currentTabHolder = null;
}

SwitchlistController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.SWITCH_ALL,
                Constants.TEMPLATES.SWITCH_INFO],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - SystemController.init() - Unable to initialize all templates: " + err.message);
    }
}

SwitchlistController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SWITCH_LIST), {
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

SwitchlistController.prototype.initControls = function () {
    try {
        var parent = this;
        //tab click event
        $(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.pSwitchall:
                    parent.currentTabHolder = $(parent.pSwitchallHolder);
                    if (parent.pSwitchallController == null) {
                        parent.pSwitchallController = new tdhx.base.topo.SwitchallController(parent, parent.currentTabHolder, parent.elementId + "_switchall");
                        parent.pSwitchallController.init();
                    }
                    break;
                case parent.pSwitchinfo:
                    parent.currentTabHolder = $(parent.pSwitchinfoHolder);
                    if (parent.pSwitchinfoController == null) {
                        parent.pSwitchinfoController = new tdhx.base.topo.SwitchinfoController(parent, parent.currentTabHolder, parent.elementId + "_switchinfo");
                        parent.pSwitchinfoController.init();
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
        console.error("ERROR - SystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

SwitchlistController.prototype.load = function () {
    try {
        //this.getLogInfo();
    }
    catch (err) {
        console.error("ERROR - SystemController.load() - Unable to load: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.topo.SwitchlistController", SwitchlistController);