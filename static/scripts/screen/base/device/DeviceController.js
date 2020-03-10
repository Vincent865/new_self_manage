function DeviceController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pBasicHolder = "#" + this.elementId + "_basicHolder";
    this.pRemoteHolder = "#" + this.elementId + "_remoteHolder";
    this.pManageHolder = "#" + this.elementId + "_manageHolder";
    this.pProtocolHolder = "#" + this.elementId + "_protocolHolder";

    this.pTabBasic = "#" + this.elementId + "_tabBasic";
    this.pTabRemote = "#" + this.elementId + "_tabRemote";
    this.pTabManage = "#" + this.elementId + "_tabManage";
    this.pTabProtocol = "#" + this.elementId + "_tabProtocol";

    this.pBasicDeviceController = null;
    this.pRemoteDeviceController = null;
    this.pManageDeviceController = null;
    this.pProtocolDeviceController = null;

    this.currentTabId = "";
    this.currentTabHolder = null;
}

DeviceController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.DEVICE_BASIC,
                Constants.TEMPLATES.DEVICE_REMOTE,
                Constants.TEMPLATES.DEVICE_MANAGE,
                Constants.TEMPLATES.DEVICE_PROTOCOL],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - DeviceController.init() - Unable to initialize all templates: " + err.message);
    }
}

DeviceController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.DEVICE_LIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - DeviceController.initShell() - Unable to initialize: " + err.message);
    }
}

DeviceController.prototype.initControls = function () {
    try {
        var parent = this;

        //tab click event
        $(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.pTabBasic:
                    parent.currentTabHolder = $(parent.pBasicHolder);
                    if (parent.pBasicDeviceController == null) {
                        parent.pBasicDeviceController = new tdhx.base.device.BasicDeviceController(parent, parent.currentTabHolder, parent.elementId + "_basic");
                        parent.pBasicDeviceController.init();
                    }
                    break;
                case parent.pTabRemote:
                    parent.currentTabHolder = $(parent.pRemoteHolder);
                    if (parent.pRemoteDeviceController == null) {
                        parent.pRemoteDeviceController = new tdhx.base.device.RemoteDeviceController(parent, parent.currentTabHolder, parent.elementId + "_remote");
                        parent.pRemoteDeviceController.init();
                    }
                    break;
                case parent.pTabProtocol:
                    parent.currentTabHolder = $(parent.pProtocolHolder);
                    if (parent.pProtocolDeviceController == null) {
                        parent.pProtocolDeviceController = new tdhx.base.device.ProtocolDeviceController(parent, parent.currentTabHolder, parent.elementId + "_manage");
                        parent.pProtocolDeviceController.init();
                    }
                    break;
                case parent.pTabManage:
                    parent.currentTabHolder = $(parent.pManageHolder);
                    if (parent.pManageDeviceController == null) {
                        parent.pManageDeviceController = new tdhx.base.device.ManageDeviceController(parent, parent.currentTabHolder, parent.elementId + "_manage");
                        parent.pManageDeviceController.init();
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
        console.error("ERROR - DeviceController.initControls() - Unable to initialize control: " + err.message);
    }
}

DeviceController.prototype.load = function () {
    try {
        var authInfo=JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']);
        if(authInfo['authority']==mstat) {
            $(".row-cutbox>ul>li").eq(1).hide();
        }
    }
    catch (err) {
        console.error("ERROR - DeviceController.load() - Unable to load: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.device.DeviceController", DeviceController);