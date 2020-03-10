function ConfExportController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRebootSuccess = true;
    this.isResetSuccess = true;

    this.pConfForm = "#" + this.elementId + "_ConfForm";
    this.pBtnConfExport = "#" + this.elementId + "_btnConfExport";
    this.pConfImportMedia = "#" + this.elementId + "_ConfImportMedia";
    this.pUptip= "#" + this.elementId + "_showtip";
    this.pBtnUpload="#" + this.elementId + "_btnUpload";
}

ConfExportController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_CONFEXPORT), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - ConfExportController.init() - Unable to initialize: " + err.message);
    }
}

ConfExportController.prototype.initControls = function () {
    try {
        var parent = this,link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPLOAD_CONFIG_FILE;
        $(this.pBtnUpload).on('click',function(){
            layer.confirm('　　配置导入将会清空目前的配置并重启当前设备，确定继续吗？',{icon:7,title:'注意：'}, function(index) {
                var fileName = $.trim($(parent.pConfImportMedia).val());
                parent.isRedirect = true;
                if (!fileName) {
                    layer.alert('请选择要上传的配置文件！', {icon: 5});
                    return false;
                } else if (fileName.substr(fileName.lastIndexOf('.') + 1, 3).toLowerCase() != 'sql') {
                    layer.alert('配置文件格式有误！', {icon: 5});
                    return false;
                }
                var layerIndex = layer.msg("正在导入配置文件...", {
                    time: 120000,
                    shade: [0.5, '#fff']
                }, function () {
                    parent.gotoPage();
                });
                $(parent.pConfForm).ajaxSubmit({
                    type: 'POST',
                    url: link,
                    success: function (res) {
                        if (!res.status) {
                            parent.isRedirect = false;
                            layer.close(layerIndex);
                            layer.alert(res.msg, {icon: 5});
                        }
                    }
                });
            });
            return false;
        });
        $(this.pBtnConfExport).on('click',function(){
            var subParent=this;
            $(this).after('<iframe style="display:none;" src="'+link+'?loginuser='+parent.loginUser+'&_='+new Date().getTime()+'"></iframe>');
            clearTimeout(this.getSqlfile);
            this.getSqlfile=setTimeout(function(){
                $(subParent).siblings('iframe').remove();
            },1000);
        });
        $(this.pConfImportMedia).on("change", function () {
            var fileName = $.trim($(this).val());
            if (fileName != "") {
                var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 3).toLowerCase();
                if (fieExtension == "sql") {
                    $(parent.pUptip).html(fileName);
                }
                else {
                    $(parent.pUptip).html("配置文件格式有误！");
                }
            }
            else {
                $(parent.pUptip).html("选择上传文件");
            }
        });
    }
    catch (err) {
        console.error("ERROR - ConfExportController.initControls() - Unable to initialize control: " + err.message);
    }
}

ConfExportController.prototype.load = function () {
    try {
        this.pViewHandle.find("#loginuser").val(AuthManager.getInstance().getUserName());
        this.loginUser=AuthManager.getInstance().getUserName();
    }
    catch (err) {
        console.error("ERROR - ConfExportController.load() - Unable to load: " + err.message);
    }
}

ConfExportController.prototype.gotoPage = function () {
    if (this.isRedirect == true) {
        window.location.replace(APPCONFIG[APPCONFIG.PRODUCT].LOGIN_URL);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.ConfExportController", ConfExportController);