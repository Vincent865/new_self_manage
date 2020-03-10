function prototplController( viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pCusProtoHolder = "#" + this.elementId + "_cusProtoHolder";
    this.pRuletplHolder = "#" + this.elementId + "_ruletplHolder";
    this.pUtilityHolder = "#" + this.elementId + "_utilityHolder";

    this.pTabCusProto = "#" + this.elementId + "_tabCusProto";
    this.pTabRuletpl = "#" + this.elementId + "_tabRuletpl";
    this.pTabUtility = "#" + this.elementId + "_tabUtility";

    this.pCusProtoController = null;
    this.pRuleconfController = null;
    this.pUtilityconfController = null;
   
    this.currentTabId = "";
    this.currentTabHolder = null;
}

prototplController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                //Constants.TEMPLATES.DEVICE_MANAGE,
                Constants.TEMPLATES.RULE_AUDITSTRATEGY_CUSPROTOCOL,
				Constants.TEMPLATES.RULETPL_CONF,
                Constants.TEMPLATES.UTILITYTPL_CONF],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - prototplController.init() - Unable to initialize all templates: " + err.message);
    }
}

prototplController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.PROTOTPLCONF_LIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - prototplController.initShell() - Unable to initialize: " + err.message);
    }
}

prototplController.prototype.initControls = function () {
    try {
        var parent = this;
        //tab click event
        $(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
			
            switch (parent.currentTabId) {
                case parent.pTabCusProto:
                    parent.currentTabHolder = $(parent.pCusProtoHolder);
                    if (parent.lastTab != parent.pTabCusProto) {
                        parent.pCusProtoController = new tdhx.base.protoaudit.CusProtoController(parent, parent.currentTabHolder, parent.elementId + "_cusproto");
                        parent.pCusProtoController.init();
                    }
                    parent.lastTab=parent.pTabCusProto;
                    break;
                case parent.pTabRuletpl:
                    parent.currentTabHolder = $(parent.pRuletplHolder);
                    if (parent.lastTab != parent.pTabRuletpl) {
                        parent.pRuleconfController = new tdhx.base.protoaudit.RuleconfController(parent, parent.currentTabHolder, parent.elementId + "_ruletpl");
                        parent.pRuleconfController.init();
                    }
                    parent.lastTab=parent.pTabRuletpl;
                    break;
                case parent.pTabUtility:
                    parent.currentTabHolder = $(parent.pUtilityHolder);
                    if (parent.lastTab != parent.pTabUtility) {
                        parent.pUtilityconfController = new tdhx.base.protoaudit.UtilityconfController(parent, parent.currentTabHolder, parent.elementId + "_utitpl");
                        parent.pUtilityconfController.init();
                    }
                    parent.lastTab=parent.pTabUtility;
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
        console.error("ERROR - prototplController.initControls() - Unable to initialize control: " + err.message);
    }
}

prototplController.prototype.load = function () {
    try {
    }
    catch (err) {
        console.error("ERROR - prototplController.load() - Unable to load: " + err.message);
    }
}


ContentFactory.assignToPackage("tdhx.base.protoaudit.prototplController", prototplController);