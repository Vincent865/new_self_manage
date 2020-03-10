function DiagnosisController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pDebugHolder = "#" + this.elementId + "_debugHolder";
    this.pPcapHolder = "#" + this.elementId + "_pcapHolder";

    this.pTabDebug = "#" + this.elementId + "_tabDebug";
    this.pTabPcap = "#" + this.elementId + "_tabPcap";
   
    this.pDebugDiagnosisController = null;
    this.pPcapDiagnosisController = null;

    this.currentTabId = "";
    this.currentTabHolder = null;
}

DiagnosisController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.DIAGNOSIS_DEBUG,
                Constants.TEMPLATES.DIAGNOSIS_PCAP],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - DiagnosisController.init() - Unable to initialize all templates: " + err.message);
    }
}

DiagnosisController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.DIAGNOSIS_LIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - DiagnosisController.initShell() - Unable to initialize: " + err.message);
    }
}

DiagnosisController.prototype.initControls = function () {
    try {
        var parent = this;

        //tab click event
        $(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.pTabDebug:
                    parent.currentTabHolder = $(parent.pDebugHolder);
                    if (parent.pDebugDiagnosisController == null) {
                        parent.pDebugDiagnosisController = new tdhx.base.diagnosis.DebugDiagnosisController(parent, parent.currentTabHolder, parent.elementId + "_manage");
                        parent.pDebugDiagnosisController.init();
                    }
                    break;
                case parent.pTabPcap:
                    parent.currentTabHolder = $(parent.pPcapHolder);
                    if (parent.pPcapDiagnosisController == null) {
                        parent.pPcapDiagnosisController = new tdhx.base.diagnosis.PcapDiagnosisController(parent, parent.currentTabHolder, parent.elementId + "_pcap");
                        parent.pPcapDiagnosisController.init();
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
        console.error("ERROR - DiagnosisController.initControls() - Unable to initialize control: " + err.message);
    }
}

DiagnosisController.prototype.load = function () {
    try {
    }
    catch (err) {
        console.error("ERROR - DiagnosisController.load() - Unable to load: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.diagnosis.DiagnosisController", DiagnosisController);