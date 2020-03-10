function AsController( viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pProtocolHolder = "#" + this.elementId + "_protocolHolder";
    this.pDataCHolder = "#" + this.elementId + "_DataCHolder";

    this.pTabProtocol = "#" + this.elementId + "_tabProtocol";
    this.pTabDataC = "#" + this.elementId + "_tabDataC";

    this.pProtocolDeviceController = null;
    this.pCusProtoController = null;
    this.pDataCController = null;
   
    this.currentTabId = "";
    this.currentTabHolder = null;
}

AsController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                //Constants.TEMPLATES.DEVICE_MANAGE,
				Constants.TEMPLATES.RULE_AUDITSTRATEGY_DATAC,
                Constants.TEMPLATES.RULE_AUDITSTRATEGY_PROTOCOL],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - AsController.init() - Unable to initialize all templates: " + err.message);
    }
}

AsController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_AUDITSTRATEGY_LIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - AsController.initShell() - Unable to initialize: " + err.message);
    }
}

AsController.prototype.initControls = function () {
    try {
        var parent = this;
        //tab click event
        $(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
			
            switch (parent.currentTabId) {
                case parent.pTabDataC:
                    parent.currentTabHolder = $(parent.pDataCHolder);
                    if (parent.pDataCController == null) {
                        parent.pDataCController = new tdhx.base.auditstrategy.DataCController(parent, parent.currentTabHolder, parent.elementId + "_manage");
                        parent.pDataCController.init();
                    }
                    break;
                case parent.pTabProtocol:
                    parent.currentTabHolder = $(parent.pProtocolHolder);
                    if (parent.pProtocolDeviceController == null) {
                        parent.pProtocolDeviceController = new tdhx.base.auditstrategy.ProtocolController(parent, parent.currentTabHolder, parent.elementId + "_manage");
                        parent.pProtocolDeviceController.init();
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
        console.error("ERROR - AsController.initControls() - Unable to initialize control: " + err.message);
    }
}

AsController.prototype.load = function () {
    try {
    }
    catch (err) {
        console.error("ERROR - AsController.load() - Unable to load: " + err.message);
    }
}




ContentFactory.assignToPackage("tdhx.base.auditstrategy.AsController", AsController);
