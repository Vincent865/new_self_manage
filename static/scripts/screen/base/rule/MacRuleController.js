function MacRuleController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnEnable = "#" + this.elementId + "_btnEnable";
    this.pBtnDisable = "#" + this.elementId + "_btnDisable";

    this.pIPTYPE = "[name=iptype]";
    this.pTxtIP = "#" + this.elementId + "_txtIP";
    this.pTxtIP6 = "#" + this.elementId + "_txtIP6";
    this.pTxtMac = "#" + this.elementId + "_txtMac";
    this.pTxtDevice = "#" + this.elementId + "_txtDevice";
    this.pTxtDevName = "#" + this.elementId + "_txtDevName";
    this.pTxtDevIp = "#" + this.elementId + "_txtDevIp";
    this.pTxtDevMac = "#" + this.elementId + "_txtDevMac";

    this.pTdRuleList = "#" + this.elementId + "_tdRuleList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotal = "#" + this.elementId + "_lblTotal";

    this.pBtnFilter="#" + this.elementId + "_btnFilter";
    this.pAdvOpt='#' + this.elementId + "_divFilter_ser";
    this.pBtnSearch='#' + this.elementId + "_btnSearch";
    this.pBtnAddShow="#" + this.elementId + "_btnAddShow";
    this.pAdvOptAdd='#' + this.elementId + "_divFilter_add";
    this.pBtnAdd = "#" + this.elementId + "_btnAdd";
    this.pBtnExport = "#" + this.elementId + "_btnExport";
    this.pBtnImxport = "#" + this.elementId + "_btnImport";
    this.pBtnFile = "#" + this.elementId + "_file";
    this.pBtnDelAll = "#" + this.elementId + "_btnDelAll";

    this.pEditDetail='#'+elementId+'_dialog'+'_editDetail';
    this.pIPTYPEDialog = "[name=iptypedialog]";
    this.pager = null;
    this.filter = {
        page: 1,
        name:'',
        ip:'',
        mac:''
    };
}
MacRuleController.prototype.init=function(){
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.RULE_MAC_DIALOG],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - MacRuleController.init() - Unable to initialize all templates: " + err.message);
    }
};
MacRuleController.prototype.initShell=function(){
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_MAC), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - MacRuleController.initShell() - Unable to initialize: " + err.message);
    }
};
MacRuleController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pBtnRefresh).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.selectRules();
        });
        $(this.pBtnSearch).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.selectRules();
        });
        $(this.pBtnAdd).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.addRule();
        });
        $(this.pBtnFilter).bind({click:function(){
            parent.pViewHandle.find(parent.pTxtDevName).val("");
            parent.pViewHandle.find(parent.pTxtDevIp).val("");
            parent.pViewHandle.find(parent.pTxtDevMac).val("");
            $(parent.pAdvOpt).toggle();
            $(parent.pAdvOptAdd).hide();
        }});
        $(this.pBtnAddShow).bind({click:function(){
            parent.pViewHandle.find(parent.pIPTYPE).eq(0).prop("checked", true);
            $(".v4").show();
            $(".v6").hide();
            $("input.v6").val('');
            parent.pViewHandle.find(parent.pTxtDevice).val("");
            parent.pViewHandle.find(parent.pTxtIP).val("");
            parent.pViewHandle.find(parent.pTxtIP6).val("");
            parent.pViewHandle.find(parent.pTxtMac).val("");
            $(parent.pAdvOptAdd).toggle();
            $(parent.pAdvOpt).hide();
        }});
        $(this.pBtnDisable).on("click", function () {
            parent.disableRule();
        });
        $(this.pBtnEnable).on("click", function () {
            parent.enableRule();
        });
        $(this.pIPTYPE).on("change", function () {
            if(this.value==4){
                $(".v4").show();
                $(".v6").hide();
                $("input.v6").val('');
            }else{
                $(".v6").show();
                $(".v4").hide();
                $("input.v4").val('');
            }
        });
        this.pViewHandle.find(this.pBtnExport).on("click", function () {
            parent.exportDesc();
        });
        this.pViewHandle.find(this.pBtnImxport).on("click", function () {
            $(parent.pBtnFile).val("");
            parent.importDesc();
        });
        $(parent.pBtnFile).on("change",function(){
            var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
            var fileName = $.trim($(this).val());
            $("#loginuser").val(AuthManager.getInstance().getUserName());
            if (fileName != "") {
                var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 3).toLowerCase();
                if (fieExtension != "csv") {
                    layer.alert("文件格式不对", { icon: 5 });
                }else{
                    var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].MAC_ALL_IMPORT;
                    $("#importProtoForm").ajaxSubmit({
                        type: 'POST',
                        url: link,
                        success: function (result) {
                            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                                if(result.status==1){
                                    layer.alert("导入成功", { icon: 6 });
                                    parent.pager = null;
                                    parent.filter.page = 1;
                                    parent.selectRules();
                                }else{
                                    layer.alert("导入失败", { icon: 5 });
                                }
                            }
                            else {
                                layer.alert("导入失败", { icon: 5 });
                            }
                            $(parent.pFileUpload).val("");
                        }
                    });
                }
            }
            layer.close(loadIndex);
        })
        $(parent.pBtnDelAll).on('click',function(){
            parent.deleteRule('all','all')
        })
    }
    catch (err) {
        console.error("ERROR - MacRuleController.initControls() - Unable to initialize control: " + err.message);
    }
}

MacRuleController.prototype.load = function () {
    try {
        this.selectRules();
        //this.getInitEventAction();
    }
    catch (err) {
        console.error("ERROR - MacRuleController.load() - Unable to load: " + err.message);
    }
}

MacRuleController.prototype.addRule = function () {
    var loadIndex;
    try {
        var parent = this;
        var device = $.trim($(this.pTxtDevice).val());
        var ip = $.trim($(this.pTxtIP).val());
        var ip6 = $.trim($(this.pTxtIP6).val());
        var mac = $.trim($(this.pTxtMac).val());
        var iptype = $(this.pIPTYPE+":checked").val();
        var intf = "2";//接口
        /*if (device == "") {
            layer.alert("规则名称不能为空", { icon: 5 });
            return false;
        }
        if (device.length > 16) {
            layer.alert("规则名称不能超过16个字符", { icon: 5 });
            return false;
        }*/
        if(iptype==4){
            if (!Validation.validateIP(ip)) {
                layer.alert("请输入正确有效的IPV4地址", { icon: 5 });
                return false;
            }
        }else{
            if (!Validation.validateIPV6(ip6)) {
                layer.alert("请输入正确有效的IPV6地址", { icon: 5 });
                return false;
            }
        }
        if (!Validation.validateMAC(mac)) {
            layer.alert("请输入正确有效的MAC地址", { icon: 5 });
            return false;
        }
        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].ADD_RULE_MAC;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { name: device, ip: (ip||ip6), mac: mac.toLowerCase(), intf: intf,iptype:iptype});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        setTimeout(function () { parent.selectRules(); }, 2000);
                        layer.alert("添加规则成功", { icon: 6 });
                        break;
                    default: layer.alert(result.msg, { icon: 5 }); break;
                }
            }
            else {
                layer.alert("添加规则失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - MacRuleController.exportLog() - Unable to export all events: " + err.message);
    }
}

MacRuleController.prototype.disableRule = function () {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        if ($(this.pLblTotal).html() == "0") {
            layer.alert("当前没有可以操作的规则", { icon: 5 });
            layer.close(loadIndex);
            return;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DISABLE_RULE_MAC;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST");
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        $(parent.pTdRuleList).find("input[type='checkbox']").prop("checked", false);
                        layer.close(loadIndex);
                        break;
                    default: layer.alert(result.msg, { icon: 5 }); break;
                }
            }
            else {
                layer.alert("禁用所有规则失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - MacRuleController.exportLog() - Unable to export all events: " + err.message);
    }
}

MacRuleController.prototype.enableRule = function () {
    try {
        var parent = this;
        if ($(this.pLblTotal).html() == "0") {
            layer.alert("当前没有可以操作的规则", { icon: 5 });
            layer.close(loadIndex);
            return;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].ENABLE_RULE_MAC;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST");
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        $(parent.pTdRuleList).find("input[type='checkbox']").prop("checked", true);
                        break;
                    default: layer.alert(result.msg, { icon: 5 }); break;
                }
            }
            else {
                layer.alert("启用所有规则失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - MacRuleController.exportLog() - Unable to deploy rules: " + err.message);
    }
}

MacRuleController.prototype.deleteRule = function (id, $tr) {
    var parent = this;
    layer.confirm('确定删除'+(id=='all'?'全部':'该条')+'数据么？',{icon:7,title:'注意：'}, function(index) {
        layer.close(index);
        var loadIndex = layer.load(2, {shade: [0.4, '#fff']});
        try {
            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DELETE_RULE_MAC;
            var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {id: id});
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                layer.alert("系统服务忙，请稍后重试！", {icon: 2});
                layer.close(loadIndex);
            });
            promise.done(function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 1:
                            if($tr=='all'){
                                parent.pager = null;
                                parent.filter.page = 1;
                                parent.selectRules();
                            }else{
                                $tr.remove();
                                var cur = parseInt($(parent.pLblTotal).text()) - 1;
                                $(parent.pLblTotal).text(cur);
                            }
                            layer.alert("删除规则成功", {icon: 6});
                            break;
                        default:
                            layer.alert(result.msg, {icon: 5});
                            break;
                    }
                }
                else {
                    layer.alert("删除规则失败", {icon: 5});
                }
                layer.close(loadIndex);
            });
        }
        catch (err) {
            layer.close(loadIndex);
            console.error("ERROR - MacRuleController.exportLog() - Unable to delete this rule: " + err.message);
        }
    })
}

MacRuleController.prototype.updateRule = function (id, status, obj, v) {
    var parent = this;
    try {
        var action = "1";//$("input[name='macEvent']:checked").val();1--告警   2--阻断
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_RULE_MAC;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { id: id, status: status, action: action });
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            obj.prop("checked", v);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1: break;
                    default:
                        layer.alert(result.msg, { icon: 5 });
                        obj.prop("checked", v);
                        break;
                }
            }
            else {
                obj.prop("checked", v);
                layer.alert("修改失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        obj.prop("checked", v);
        layer.close(loadIndex);
        console.error("ERROR - MacRuleController.exportLog() - Unable to save this rule: " + err.message);
    }
}

MacRuleController.prototype.selectRules = function () {
    var html = "";
    /*var loadIndex = layer.load(2);*/
    try {
        var parent = this;
        this.filter.name = $.trim(this.pViewHandle.find(this.pTxtDevName).val());
        this.filter.ip = $.trim(this.pViewHandle.find(this.pTxtDevIp).val());
        this.filter.mac = $.trim(this.pViewHandle.find(this.pTxtDevMac).val());
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_RULE_MAC_LIST;
        var promise = URLManager.getInstance().ajaxCall(link, this.filter);
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='5'>暂无数据</td></tr>";
            $(parent.pTdRuleList+">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>" + ((parent.filter.page - 1) * 10 + 1 + i) + "</td>";
                        //html += "<td style='text-align:left;'>" + result.rows[i][5] + "</td>";
                        html += "<td style='min-width:200px;'>" + result.rows[i][2] + "</td>";
                        html += "<td style='min-width:200px'>" + result.rows[i][3].toUpperCase() + "</td>";
                        html += "<td style='width:8%;'><span class='btn-on-box'>";
                        html += "<input type='checkbox' id='chk" + result.rows[i][0] + "' class='btn-on' data-key='" + result.rows[i][0] + "' " + (result.rows[i][4] == 1 ? "checked" : "") + " /><label for='chk" + result.rows[i][0] + "'></label>";
                        html += "</td>";
                        html += "<td style='width:12%;'><button class='btn btn-default btn-xs btn-color-details' data-key='"+result.rows[i][0]+"' data-name='"+result.rows[i][5]+"' data-ip='"+result.rows[i][2]+"' data-mac='"+result.rows[i][3]+"' data-iptype='"+result.rows[i][8]+"'><i class='fa fa-edit'></i>编辑</button>";
                        html += "<button style='margin-left:5px;' class='btn btn-danger btn-xs' data-key='" + result.rows[i][0] + "'><i class='fa fa-trash-o'></i>删除</button></td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='5'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='5'>暂无数据</td></tr>";
            }
            $(parent.pTdRuleList + ">tbody").html(html);
            layer.close(loadIndex);

            $(parent.pTdRuleList + ">tbody").find("button[class='btn btn-danger btn-xs']").on("click", function () {
                var id = $(this).attr("data-key");
                parent.deleteRule(id, $(this).parent().parent());
            });
            $(parent.pTdRuleList + ">tbody").find("button[class='btn btn-default btn-xs btn-color-details']").on("click", function () {
                var id=$(this).attr("data-key"),
                    name=$(this).attr("data-name"),
                    ip=$(this).attr("data-ip"),
                    mac=$(this).attr("data-mac"),
                    iptype=$(this).attr("data-iptype");
                parent.editRule(id,name,ip,mac,iptype);
            });
            $(parent.pTdRuleList + ">tbody").find("input[type='checkbox']").on("change", function () {
                var id = $(this).attr("data-key");
                var status = $(this).prop("checked") ? "1" : "0";
                parent.updateRule(id, status, $(this), !$(this).prop("checked"));
            });

            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectRules();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='5'>暂无数据</td></tr>";
        $(this.pTdRuleList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - MacRuleController.selectRules() - Unable to get all events: " + err.message);
    }
}
MacRuleController.prototype.editRule=function(id,name,ip,mac,iptype){
    var parent=this,link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].ADD_RULE_MAC,promise;
    var dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_MAC_DIALOG), {
        elementId: parent.elementId + "_dialog"
    });
    var width = 500 + "px";
    var height = 350 + "px";
    var tmplay=layer.open({
        type: 1,
        title:"编辑",
        area: [width, height],
        //offset: ["82px", "200px"],
        shade: [0.5, '#393D49'],
        content: dialogTemplate,
        success: function (layero, index) {
            var detailVals=$(parent.pEditDetail).find('input.input-feedback'),btns=$(parent.pEditDetail).find('button');
            if(iptype==4){
                $(parent.pIPTYPEDialog).eq(0).prop("checked", true);
                $(".dialog-content .v4").show();$(".dialog-content .v6").hide();
                detailVals.eq(0).val(ip);
            }else{
                $(".dialog-content .v6").show();$(".dialog-content .v4").hide();
                detailVals.eq(1).val(ip);
                $(parent.pIPTYPEDialog).eq(1).prop("checked", true);
            }
            $(parent.pIPTYPEDialog).on("change", function () {
                $(parent.pEditDetail).find('span').eq(2).text('');
                if(this.value==4){
                    $(".dialog-content .v4").show();$(".dialog-content .v6").hide();
                }else{
                    $(".dialog-content .v6").show();$(".dialog-content .v4").hide();
                }
            });
            //detailVals.eq(0).val(name);
            detailVals.eq(2).val(mac);
            btns.eq(0).click(function(){
                var iptypeD=$(parent.pIPTYPEDialog+":checked").val();

                    if((iptypeD==6&&Validation.validateIPV6($.trim(detailVals.eq(1).val())))||(iptypeD==4&&Validation.validateIP($.trim(detailVals.eq(0).val())))){
                        if(Validation.validateMAC($.trim(detailVals.eq(2).val()))){
                            if(iptypeD==4){
                                var ipTo=$.trim(detailVals.eq(0).val());
                            }else{
                                ipTo=$.trim(detailVals.eq(1).val());
                            }
                            promise=URLManager.getInstance().ajaxCallByURL(link,'PUT',{id:id,name:"",ip:ipTo,iptype:iptypeD,mac:$.trim(detailVals.eq(2).val())});
                            var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
                            promise.fail(function(jqXHR, textStatus, err){
                                console.log(textStatus+'-'+err);
                                layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                                layer.close(tmplay);
                                layer.close(loadIndex);
                            });
                            promise.done(function(result){
                                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                                    switch (result.status) {
                                        case 1:
                                            layer.alert("修改规则成功", { icon: 6 });
                                            break;
                                        default: layer.alert(result.msg, { icon: 5 }); break;
                                    }
                                    parent.selectRules();
                                    layer.close(tmplay);
                                    layer.close(loadIndex);
                                }
                            });
                        }else{
                            $(parent.pEditDetail).find('span').eq(2).text('mac地址不符合规范').show();
                            detailVals.eq(2).val("")
                        }
                    }else{
                        $(parent.pEditDetail).find('span').eq(2).text('ipv'+iptypeD+'地址不符合规范').show();
                        detailVals.eq((iptypeD==4?0:1)).val("")
                    }

            });
            btns.eq(1).click(function(){
                layer.close(tmplay);
            });
            $(window).on("resize", function () {
                var pwidth = parent.pViewHandle.width() - 10;
                var pheight = $(window).height() - parent.pViewHandle.offset().top - 10;
                tmplay.width(pwidth);
                tmplay.height(pheight);
            })
        }
    });
};
MacRuleController.prototype.exportDesc = function () {
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].MAC_ALL_EXPORT;
        var promise = URLManager.getInstance().ajaxCall(link,{action:0});
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        window.open(link + "?action=1&loginuser=" + AuthManager.getInstance().getUserName());
                        break;
                    default:
                        layer.alert(result.msg, { icon: 5 }); break;
                }
            }
            else {
                layer.alert("导出数据失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - MacRuleController.exportDesc() - Unable to export all desc: " + err.message);
    }
}
MacRuleController.prototype.importDesc = function () {
    try {
        $(this.pBtnFile).click();
    }
    catch (err) {
        console.error("ERROR - MacRuleController.importDesc() - Unable to import all desc: " + err.message);
    }
}
ContentFactory.assignToPackage("tdhx.base.rule.MacRuleController", MacRuleController);