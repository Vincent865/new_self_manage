function MenuController(viewHandle) {
    this.pViewHandle = viewHandle;
}

MenuController.prototype.init = function () {
    try {
        var parent = this;
        var authInfo=JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']);
        if(!authInfo['redirect']){//密码未到期，不需要修改时
            switch(authInfo['authority']){
                case mstat:
                    var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_MENU_ADMIN), {
                        elementId: parent.elementId
                    });
                    break;
                case astat:
                    var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_MENU_AUDIT), {
                        elementId: parent.elementId
                    });
                    break;
                case ostat:
                    var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_MENU_OPERA), {
                        elementId: parent.elementId
                    });
                    break;
            }
        }else{
            var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_MENU_ADMIN), {
                elementId: parent.elementId
            });
        }
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
        var authInfo=JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']);
        if(authInfo['redirect']){
            $(".not-show").hide();
        }
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
            $('.nav').height($(window).height()-72);
        });
        this.pViewHandle.find(".second-nav .second-nav-list>li").on("click", function () {
            $(".second-nav-list>li").removeClass("on");
            $(this).addClass("on");
        });
        $(window).resize(function(){
            $('.nav').height($(window).height()-72);
        });
    }
    catch (err) {
        console.error("ERROR - MenuController.initControls() - Unable to initialize control: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.index.MenuController", MenuController);