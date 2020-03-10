/**
 * Created by 刘写辉 on 2018/11/12.
 */
function TopolistController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pTopographHolder = "#" + this.elementId + "_topographHolder";
    this.pAssetlistHolder = "#" + this.elementId + "_assetlistHolder";
    this.pFingerprintHolder = "#" + this.elementId + "_fingerprintHolder";

    this.pTopograph = "#" + this.elementId + "_topograph";
    this.pAssetlist = "#" + this.elementId + "_assetlist";
    this.pFingerprint = "#" + this.elementId + "_fingerprint";

    this.pTopographController = null;
    this.pAssetlistController = null;
    this.pFingerprintController = null;

    this.currentTabId = "";
    this.currentTabHolder = null;
}

TopolistController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.TOPO_TOPOGRAPH,
                Constants.TEMPLATES.TOPO_ASSETLIST],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - SystemController.init() - Unable to initialize all templates: " + err.message);
    }
}

TopolistController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.TOPO_TOPOLIST), {
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

TopolistController.prototype.initControls = function () {
    try {
        var parent = this;

        //tab click event
        $(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.pTopograph:
                    parent.currentTabHolder = $(parent.pTopographHolder);
                    if(parent.lastTab!==parent.pTopograph){
                        parent.pTopographController = new tdhx.base.topo.TopographController(parent, parent.currentTabHolder, parent.elementId + "_graph");
                        parent.pTopographController.init();
                    }
                    /*if (parent.pTopographController == null) {

                    }*/
                    parent.lastTab=parent.pTopograph;
                    break;
                case parent.pAssetlist:
                    parent.currentTabHolder = $(parent.pAssetlistHolder);
                    if(parent.lastTab!==parent.pAssetlist){
                        parent.pAssetlistController = new tdhx.base.topo.AssetlistController(parent, parent.currentTabHolder, parent.elementId + "_asset");
                        parent.pAssetlistController.init();
                    }
                    parent.lastTab=parent.pAssetlist;
                    break;
                case parent.pFingerprint:
                    parent.currentTabHolder = $(parent.pFingerprintHolder);
                    if(parent.lastTab!==parent.pFingerprint){
                        parent.pFingerprintController = new tdhx.base.topo.FingerprintController(parent, parent.currentTabHolder, parent.elementId + "_fingerprint");
                        parent.pFingerprintController.init();
                    }
                    parent.lastTab=parent.pFingerprint;
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

TopolistController.prototype.load = function () {
    try {
        //this.getLogInfo();
    }
    catch (err) {
        console.error("ERROR - SystemController.load() - Unable to load: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.topo.TopolistController", TopolistController);