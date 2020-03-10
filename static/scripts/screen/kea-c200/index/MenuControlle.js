function MenuController(viewHandle) {
    this.pViewHandle = viewHandle;
}

MenuController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_MENU), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - MenuController.init() - Unable to initialize: " + err.message);
    }
}

MenuController.prototype.load = function () {
    try {
        var parent = this;
    }
    catch (err) {
        console.error("ERROR - MenuController.load() - Unable to load: " + err.message);
    }
}

MenuController.prototype.initControls = function () {
    try {
        var parent = this;
        this.pViewHandle.find(".nav-list li .nav-title").click(function () {
            $(".nav-list li .nav-title").removeClass("active");
            $(".second-nav-list>li").removeClass("on");
            $(this).addClass("active");
            $(this).next(".second-nav").slideToggle(300, function () { });
        });
        this.pViewHandle.find(".second-nav .second-nav-list>li").on("click", function () {
            $(".second-nav-list>li").removeClass("on");
            $(this).addClass("on");
        });
    }
    catch (err) {
        console.error("ERROR - MenuController.initControls() - Unable to initialize control: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.index.MenuController", MenuController);