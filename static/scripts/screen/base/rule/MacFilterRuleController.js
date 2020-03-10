function MacFilterRuleController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnEnable = "#" + this.elementId + "_btnEnable";
    this.pBtnDisable = "#" + this.elementId + "_btnDisable";

    this.pTxtIP = "#" + this.elementId + "_txtIP";
    this.pTxtMac = "#" + this.elementId + "_txtMac";
    this.pTxtDevice = "#" + this.elementId + "_txtDevice";
    this.pBtnAdd = "#" + this.elementId + "_btnAdd";

    this.pTdRuleList = "#" + this.elementId + "_tdRuleList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotal = "#" + this.elementId + "_pLblTotal";
    this.pBtnSearch='#' + this.elementId + "_btnSearch";
    this.pMacSearch = "#" + this.elementId + "_txtMacSearch";
    this.pager = null;
    this.filter = {
        page: 1
    };
}

MacFilterRuleController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_MAC_FILTER), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - MacFilterRuleController.init() - Unable to initialize: " + err.message);
    }
}

MacFilterRuleController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pBtnRefresh).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            $(parent.pMacSearch).val("");
            parent.selectRules();
        });
        $(this.pBtnAdd).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.addRule();
        });
        $(this.pBtnDisable).on("click", function () {
            parent.RuleALL(0);
        });

        $(this.pBtnEnable).on("click", function () {
            parent.RuleALL(1);
        });
        $(this.pBtnSearch).on("click", function () {
            var val=$(parent.pMacSearch).val(),s=/^[0-9a-zA-Z:]{0,17}$/;
            if(!s.test(val)){
                layer.alert("请输入合法字符", { icon: 5 });$(parent.pMacSearch).val("");
            }else{
                parent.pager = null;
                parent.filter.page = 1;
                parent.selectRules();
            }
        });
    }
    catch (err) {
        console.error("ERROR - MacFilterRuleController.initControls() - Unable to initialize control: " + err.message);
    }
}

MacFilterRuleController.prototype.load = function () {
    try {
        this.selectRules();
        //this.getInitEventAction();
    }
    catch (err) {
        console.error("ERROR - MacFilterRuleController.load() - Unable to load: " + err.message);
    }
}

MacFilterRuleController.prototype.addRule = function () {
    var loadIndex;
    try {
        var parent = this;
        var mac = $.trim($(this.pTxtMac).val());
        if (!Validation.validateMAC(mac)) {
            layer.alert("请输入正确有效的MAC地址", { icon: 5 });
            return false;
        }
        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].RULE_MACFILTER;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {mac: mac.toLowerCase()});
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
        console.error("ERROR - MacFilterRuleController.exportLog() - Unable to export all events: " + err.message);
    }
}

MacFilterRuleController.prototype.RuleALL = function (action) {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        if ($(this.pPagerContent).html() == "0") {
            layer.alert("当前没有可以操作的规则", { icon: 5 });
            layer.close(loadIndex);
            return;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].MACFILTER_ALL;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"PUT",{ action:action });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            switch(action){
                case 1:
                    if(result.status==1){
                        $(parent.pTdRuleList).find("input[type='checkbox']").prop("checked", true);
                        layer.close(loadIndex);
                    }else{
                        layer.close(loadIndex);
                        layer.alert(result.msg, { icon: 5 }); break;
                    }
                    break;
                case 0:
                    if(result.status==1){
                        $(parent.pTdRuleList).find("input[type='checkbox']").prop("checked", false);
                        layer.close(loadIndex);
                    }else{
                        layer.close(loadIndex);
                        layer.alert(result.msg, { icon: 5 }); break;
                    }
                    break;
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - MacFilterRuleController.exportLog() - Unable to export all events: " + err.message);
    }
}

MacFilterRuleController.prototype.deleteRule = function (id, $tr) {
    var parent = this;
    layer.confirm('确定删除该条数据么？',{icon:7,title:'注意：'}, function(index) {
        layer.close(index);
        var loadIndex = layer.load(2, {shade: [0.4, '#fff']});
        try {
            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].RULE_MACFILTER;
            var promise = URLManager.getInstance().ajaxCallByURL(link, "DELETE", {ids: id});
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                layer.alert("系统服务忙，请稍后重试！", {icon: 2});
                layer.close(loadIndex);
            });
            promise.done(function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 1:
                            $tr.remove();
                            var cur = parseInt($(parent.pLblTotal).text()) - 1;
                            $(parent.pLblTotal).text(cur);
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
            console.error("ERROR - MacFilterRuleController.exportLog() - Unable to delete this rule: " + err.message);
        }
    })
}

MacFilterRuleController.prototype.updateRule = function (id, status, obj, v) {
    var parent = this;
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].RULE_MACFILTER;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "PUT", { id: id, enable: status});
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
        console.error("ERROR - MacFilterRuleController.exportLog() - Unable to save this rule: " + err.message);
    }
}

MacFilterRuleController.prototype.selectRules = function () {
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var parent = this;
        this.filter.mac=$(this.pMacSearch).val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].RULE_MACFILTER;
        var promise = URLManager.getInstance().ajaxCall(link, this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='4'>暂无数据</td></tr>";
            $(parent.pTdRuleList+">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>" + ((parent.filter.page - 1) * 10 + 1 + i) + "</td>";
                        html += "<td>" + result.rows[i][1].toUpperCase() + "</td>";
                        html += "<td style='width:15%;'><span class='btn-on-box'>";
                        html += "<input type='checkbox' id='chk" + result.rows[i][0] + "' class='btn-on' data-key='" + result.rows[i][0] + "' " + (result.rows[i][2] == 1 ? "checked" : "") + " /><label for='chk" + result.rows[i][0] + "'></label>";
                        html += "</td>";
                        html += "<td style='width:15%;'><button class='btn btn-danger btn-xs' data-key='" + result.rows[i][0] + "'><i class='fa fa-trash-o'></i>删除</button>";
                        html += "</td></tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='4'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='4'>暂无数据</td></tr>";
            }
            $(parent.pTdRuleList + ">tbody").html(html);
            layer.close(loadIndex);

            $(parent.pTdRuleList + ">tbody").find("button[class='btn btn-danger btn-xs']").on("click", function () {
                var id = $(this).attr("data-key");
                parent.deleteRule(id, $(this).parent().parent());
            });

            $(parent.pTdRuleList + ">tbody").find("input[type='checkbox']").on("change", function () {
                var id = $(this).attr("data-key");
                var status = $(this).prop("checked") ? 1:0;
                parent.updateRule(parseInt(id), status, $(this), !$(this).prop("checked"));
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
        html += "<tr><td colspan='4'>暂无数据</td></tr>";
        $(this.pTdRuleList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - MacFilterRuleController.selectRules() - Unable to get all events: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.rule.MacFilterRuleController", MacFilterRuleController);