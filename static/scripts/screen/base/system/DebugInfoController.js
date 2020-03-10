function DebugInfoController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pBtnDebugInfo= "#" + this.elementId + "_btnDebugInfo";
}

DebugInfoController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_DEBUG_INFO), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - DebugInfoController.init() - Unable to initialize: " + err.message);
    }
}

DebugInfoController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pBtnDebugInfo).on("click", function () {
            layer.open({
                type:1,
                title:'确认收集调试信息并下载吗？',
                closeBtn:false,
                area:'300px',
                shade:0.5,
                btn:['确认','取消'],
                btnAlign:'c',
                yes:function(res){
                    layer.closeAll();
                    parent.debugInfo();
                }
            });
        });
    }
    catch (err) {
        console.error("ERROR - DebugInfoController.initControls() - Unable to initialize control: " + err.message);
    }
}

DebugInfoController.prototype.load = function () {
    try {
    }
    catch (err) {
        console.error("ERROR - DebugInfoController.load() - Unable to load: " + err.message);
    }
}

DebugInfoController.prototype.debugInfo = function () {
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].DEBUG_INFO_COLLECT;
        open(link + "?loginuser=" + AuthManager.getInstance().getUserName(),'_self')
    }
    catch (err) {
        this.isRebootSuccess = false;
        console.error("ERROR - DebugInfoController.debugInfo() - Unable to cellect the debugInfo: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.DebugInfoController", DebugInfoController);