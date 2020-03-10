function CusProtoController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    // this.controller = controller;

    this.pSelectAll = '#' + elementId + '_selectAll';
    this.checkSwitch = false;

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnDel = "#" + this.elementId + "_btnDel";
    this.pBtnEnable = "#" + this.elementId + "_btnEnable";
    this.pBtnDisable = "#" + this.elementId + "_btnDisable";
    this.pBtnExportList = "#" + this.elementId + "_btnExportList";
    this.pBtnImxportList = "#" + this.elementId + "_btnImportList";
    this.pBtnFile = "#" + this.elementId + "_file";

    this.pTxtName = "#" + this.elementId + "_txtName";
    this.pTxtPort = "#" + this.elementId + "_txtPort";
    this.pDdlTyle = "#" + this.elementId + "_ddlType";
    this.pBtnAdd = "#" + this.elementId + "_btnAdd";
    this.pOpenform = "#" + this.elementId + "_dialog_detailForm";
    this.pOpenformBtns = "#" + this.elementId + "_dialog_detailCtrlBtns";
    this.devTypeList=[];

    this.pCusProtoRuleList = "#" + this.elementId + "_tdRuleList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotal = "#" + this.elementId + "_lblTotal";
    this.pager = null;
    this.filter = {
        page: 1
    };
}

CusProtoController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
            Constants.TEMPLATES.RULE_AUDITSTRATEGY_CUSPROTOCOL_OPEN],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - CusProtoController.init() - Unable to initialize: " + err.message);
    }
}
CusProtoController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_AUDITSTRATEGY_CUSPROTOCOL), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.init() - Unable to initialize: " + err.message);
    }
};
CusProtoController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pBtnRefresh).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.selectRules();
        });
        $(this.pBtnDel).on("click", function () {
            parent.deleteRule();
        });
        $(this.pBtnAdd).on("click", function () {
            parent.addRule();
        });

        $(this.pBtnDisable).on("click", function () {
            parent.disableRule();
        });

        $(this.pBtnEnable).on("click", function () {
            parent.enableRule();
        });
        $(parent.pSelectAll).click(function () {
            parent.checkSwitch = !parent.checkSwitch;
            $(parent.pCusProtoRuleList).find('input.chinput').prop('checked', parent.checkSwitch);
        });
        this.pViewHandle.find(this.pBtnExportList).on("click", function () {
            parent.exportCusList();
        });
        this.pViewHandle.find(this.pBtnImxportList).on("click", function () {
            parent.importdialog();
        });
    }
    catch (err) {
        console.error("ERROR - CusProtoController.initControls() - Unable to initialize control: " + err.message);
    }
}

CusProtoController.prototype.load = function () {
    try {
        this.selectRules();
        //this.getInitEventAction();
        this.getDeviceType();
    }
    catch (err) {
        console.error("ERROR - CusProtoController.load() - Unable to load: " + err.message);
    }
}

CusProtoController.prototype.multishow = function (o, s, n) {
    var labels = [];
    if (!o.length) {
        return '未选择';
    }
    if (o.length == s[0].length) {
        return '全选';
    }
    if (o.length > n) {
        o.each(function (i) {
            if (i <= n) {
                if ($(this).attr('label') !== undefined) {
                    labels.push($(this).attr('label'));
                }
                else {
                    labels.push($(this).html());
                }
            }
        });
        return labels.join(', ') + '...';
    }
    o.each(function () {
        if ($(this).attr('label') !== undefined) {
            labels.push($(this).attr('label'));
        }
        else {
            labels.push($(this).html());
        }
    });
    return labels.join(', ') + '';
};


CusProtoController.prototype.addRule = function (edit) {
    var loadIndex;
    try {
        var parent = this, dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_AUDITSTRATEGY_CUSPROTOCOL_OPEN), {
            elementId: parent.elementId + "_dialog"
        });
        var width = parent.pViewHandle.width() - 10 + "px";
        var height = $(window).height() - parent.pViewHandle.offset().top - $(window).height() / 10 + "px";
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_RULES_LIST, promise;//新增地址列表
        var tmplay = layer.open({
            type: 1,
            title: edit ? "编辑" : '新增',
            area: ["550px", '500px'],
            offset: '120px',
            shade: [0.5, '#393D49'],
            content: dialogTemplate,
            success: function (layero, index) {
                var openbtns = $(parent.pOpenformBtns + ' button'), ipts = $(parent.pOpenform + ' input'), selt = $(parent.pOpenform + ' select');
                selt.eq(3).multiselect({
                    includeSelectAllOption: true, selectAllText: '全选', maxHeight: 87, buttonText: (o, s) => {
                        return parent.multishow(o, s, 3);
                    }
                });
                promise = URLManager.getInstance().ajaxCallByURL(link, 'GET', { id: edit ? edit.id : '0' });
                promise.done(function (result) {
                    console.log(selt.eq(3))
                    if (result.status) {
                        $.each(result.data, (k, v) => {
                            selt.eq(3).append(Validation.formatString(`<option value=${k}>${v}</option>`));
                            console.log(k, v)
                        });
                        selt.eq(3).multiselect('rebuild');
                        selt.eq(2).empty();
                        selt.eq(2).append("<option value='0'>未知</option>");
                        for(var i=0;i<parent.devTypeList.length;i++){
                            selt.eq(2).append("<option value="+parent.devTypeList[i].id+">"+parent.devTypeList[i].name+"</option>")
                        }
                        selt.eq(1).empty();
                        selt.eq(1).append("<option value='0'>未知</option>");
                        for(var j=0;j<parent.devTypeList.length;j++){
                            selt.eq(1).append("<option value="+parent.devTypeList[j].id+">"+parent.devTypeList[j].name+"</option>")
                        }
                        if (edit) {
                            ipts.eq(0).val(edit.name);
                            ipts.eq(1).val(edit.port);
                            selt.eq(0).val(edit.type);
                            selt.eq(1).val(edit.client_type);
                            selt.eq(2).val(edit.server_type);
                            selt.eq(3).multiselect('select', String(edit.content).split(','));
                            if (edit.action) {
                                openbtns.eq(0).remove();
                                ipts.css({ borderColor: '#ccc', color: '#888' }).prop({ disabled: true });
                                selt.css({ borderColor: '#ccc', color: '#888' });
                                selt.prop({ disabled: true });
                                $('.multiselect-native-select').remove();
                                $('.showtpl').show();
                                if(edit.content){
                                    $(edit.content.split(',')).each(function(i,d){
                                        $('.showtpllist').append('<li title='+result.data[d]+'>'+result.data[d]+'</li>');
                                    });
                                }else{
                                    $('.showtpllist').append('<li>空</li>');
                                }
                            }
                        }
                    }
                });
                openbtns.eq(0).click(function () {
                    var name = $.trim(ipts.eq(0).val());
                    var port = $.trim(ipts.eq(1).val());
                    var type = $.trim(selt.eq(0).val());
                    var client_type = parseInt(selt.eq(1).val());
                    var server_type = parseInt(selt.eq(2).val());
                    if (name == "") {
                        layer.alert("协议名称不能为空", { icon: 5 });
                        return false;
                    }
                    if (name.length > 64) {
                        layer.alert("协议名称不能超过64个字符", { icon: 5 });
                        return false;
                    }
                    if (!/^[\u4e00-\u9fa50-9a-zA-Z-_]+$/.test(name)) {
                        layer.alert("协议名称由数字、字母、中文、字符(_,-)组成", { icon: 5 });
                        return false;
                    }
                    if (!Validation.validatePort(port)) {
                        layer.alert("请输入正确有效的端口", { icon: 5 });
                        return false;
                    }
                    var rules = [];
                    selt.eq(3).find('option:selected').each((i, d) => {
                        rules.push($(d).val());
                    });
                    loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
                    var linkconf = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].CUS_PROTO_LIST;
                    var promiseconf = URLManager.getInstance().ajaxCallByURL(linkconf, edit ? "PUT" : "POST", { id: edit ? edit.id : '', name: name, port: Number(port), type: type, content_id: rules.join(',') ,client_type:client_type , server_type :server_type});
                    promiseconf.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                        layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                        layer.close(loadIndex);
                    });
                    layer.close(tmplay);
                    promiseconf.done(function (result) {
                        if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                            switch (result.status) {
                                case 1:
                                    parent.pager = null;
                                    parent.filter.page = 1;
                                    layer.alert((edit ? '编辑' : '添加') + "规则成功", { icon: 6 });
                                    parent.selectRules();
                                    break;
                                /*case -1: layer.alert("当前规则已经存在，请不要重复添加", { icon: 5 }); break;
                                case 0: layer.alert("规则数量超出上限", { icon: 5 }); break;
                                case 2: layer.alert("白名单正在学习中...请稍后操作.", { icon: 5 }); break;*/
                                default: layer.alert(result.msg, { icon: 5 }); break;
                            }
                            layer.close(loadIndex);
                        }
                        else {
                            layer.alert((edit ? '编辑' : '添加') + "规则失败", { icon: 5 });
                        }
                    });
                });
                openbtns.eq(1).click(function () {
                    layer.close(tmplay);
                });
            }
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - CusProtoController.addRule() - Unable to export all events: " + err.message);
    }
}

CusProtoController.prototype.disableRule = function () {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        if ($(this.pLblTotal).html() == "0") {
            layer.alert("当前没有可以操作的规则", { icon: 5 });
            layer.close(loadIndex);
            return;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DEPLOY_CUS_PROTO;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "GET", { id: "0", action: "0" });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        $(parent.pCusProtoRuleList).find(".btn-on-box input[type='checkbox']").prop("checked", false);
                        layer.close(loadIndex);
                        break;
                    default: layer.alert(result.msg, { icon: 5 }); break;
                }
                parent.selectRules();
            }
            else {
                layer.alert("禁用所有规则失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - CusProtoController.disableRule() - Unable to export all events: " + err.message);
    }
}

CusProtoController.prototype.enableRule = function () {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        if ($(this.pLblTotal).html() == "0") {
            layer.alert("当前没有可以操作的规则", { icon: 5 });
            layer.close(loadIndex);
            return;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DEPLOY_CUS_PROTO;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { id: "0", action: "1" });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        $(parent.pCusProtoRuleList).find(".btn-on-box input[type='checkbox']").prop("checked", true);
                        break;
                    //case 2: layer.alert("白名单正在学习中...请稍后操作.", { icon: 5 }); break;
                    default: layer.alert(result.msg, { icon: 5 }); break;
                }
                parent.selectRules();
            }
            else {
                layer.alert("启用所有规则失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - CusProtoController.enableRule() - Unable to deploy rules: " + err.message);
    }
}

CusProtoController.prototype.deleteRule = function (id, $tr) {
    var parent = this;
    parent.preDelete = [];
    $(parent.pCusProtoRuleList).find('tbody input[type=checkbox].chinput').each(function (i, d) {
        if ($(d).prop('checked')) {
            parent.preDelete.push($(d).data('id'));
        }
    });
    if (id || parent.preDelete.length) {
        layer.confirm('确定删除该条数据么？', { icon: 7, title: '注意：' }, function (index) {
            layer.close(index);
            var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
            try {
                var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].CUS_PROTO_LIST;
                var promise = URLManager.getInstance().ajaxCallByURL(link, "DELETE", { id: id || parent.preDelete.join(",") });
                promise.fail(function (jqXHR, textStatus, err) {
                    console.log(textStatus + " - " + err.message);
                    layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                    layer.close(loadIndex);
                });
                promise.done(function (result) {
                    if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                        switch (result.status) {
                            case 1:
                                if (id) {
                                    $tr.remove();
                                    var cur = parseInt($(parent.pLblTotal).text()) - 1;
                                    $(parent.pLblTotal).text(cur);
                                } else {
                                    delete parent.pager;
                                    parent.filter.page = 1;
                                    parent.selectRules();
                                    if (parent.checkSwitch) {
                                        parent.checkSwitch = !parent.checkSwitch;
                                        $(parent.pCusProtoRuleList).find('input.chinput').prop('checked', parent.checkSwitch);
                                    }
                                }
                                layer.alert("删除规则成功", { icon: 6 });
                                break;
                            default:
                                layer.alert(result.msg, { icon: 5 });
                                break;
                        }
                    }
                    else {
                        layer.alert("删除规则失败", { icon: 5 });
                    }
                    layer.close(loadIndex);
                });
            }
            catch (err) {
                layer.close(loadIndex);
                console.error("ERROR - CusProtoController.exportLog() - Unable to delete this rule: " + err.message);
            }
        })
    } else {
        layer.alert("请选择要删除的规则再试！", { icon: 5 });
    }
}

CusProtoController.prototype.updateRule = function (id, status, obj, v) {
    var parent = this;
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DEPLOY_CUS_PROTO;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { id: id, action: status });
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
                    /*case 2:
                        layer.alert("白名单正在学习中,请稍后操作...", { icon: 5 });
                        obj.prop("checked", v);
                        break;*/
                    default:
                        layer.alert(result.msg, { icon: 5 });
                        obj.prop("checked", v);

                        break;
                }
                parent.selectRules();
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
        console.error("ERROR - CusProtoController.updateRule() - Unable to save this rule: " + err.message);
    }
}

CusProtoController.prototype.selectRules = function () {
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].CUS_PROTO_LIST;
        var promise = URLManager.getInstance().ajaxCall(link, this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='6'>暂无数据</td></tr>";
            $(parent.pCusProtoRuleList + ">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.data) != "undefined") {
                if (result.data.length > 0) {
                    for (var i = 0; i < result.data.length; i++) {
                        html += "<tr>";
                        html += "<td style='width:80px;'>" + "<input type='checkbox' class='chinput selflag' data-id='" + result.data[i]['protoId'] + "' id='d" + result.data[i]['protoId'] + "' /><label for='d" + result.data[i]['protoId'] + "'></label></td>";
                        html += "<td style='text-align:left;'>" + result.data[i]['protoName'] + "</td>";
                        html += "<td style='width:18%;'>" + result.data[i]['port'] + "</td>";
                        html += "<td style='width:18%;'>" + result.data[i]['protoType'] + "</td>";
                        html += "<td style='width:8%;'><span class='btn-on-box'>";
                        html += "<input type='checkbox' id='chk" + result.data[i]['protoId'] + "' class='btn-on' data-key='" + result.data[i]['protoId'] + "' " + (result.data[i]['action'] == 1 ? "checked" : "") + " /><label for='chk" + result.data[i]['protoId'] + "'></label>";
                        html += "</td>";
                        html += "<td style='width:10%;'><button style='margin-right:5px;' class='btn btn-default btn-xs btn-color-details' data-key='" + result.data[i]['protoId'] + "' data-name='" + result.data[i]['protoName'] + "' data-state='" + result.data[i]['action'] + "' data-content='" + result.data[i]['content_id'] + "' data-port='" + result.data[i]['port'] + "' data-type='" + result.data[i]['protoType'] + "' data-clienttype='"+ result.data[i]['client_type'] +"' data-servertype='"+ result.data[i]['server_type'] +"'><i class='fa "+(result.data[i]['action'] ? 'fa-eye' : 'fa-edit')+"'></i>" + (result.data[i]['action'] ? '查看' : '编辑') + "</button></td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='6'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='6'>暂无数据</td></tr>";
            }
            $(parent.pCusProtoRuleList + ">tbody").html(html);
            layer.close(loadIndex);

            $(parent.pCusProtoRuleList + ">tbody").find("button[class='btn btn-danger btn-xs']").on("click", function () {
                var id = $(this).attr("data-key");
                parent.deleteRule(id, $(this).parent().parent());
            });
            $(parent.pCusProtoRuleList + ">tbody").find("button[class='btn btn-default btn-xs btn-color-details']").on("click", function () {
                /* $(this).parents('tr').find('span.name').hide();
                $(this).parents('tr').find('.ipmark').show();
                $(this).next().show();
                $(this).hide(); */
                /* if ($(this).data('state')) {
                    layer.alert('启用状态下无法修改', { icon: 5 });
                    return;
                } */
                var params = { name: $(this).data('name'), id: $(this).data('key'), action: $(this).data('state'), type: $(this).data('type'), port: $(this).data('port'), content: String($(this).data('content')), client_type:$(this).data('clienttype'), server_type: $(this).data('servertype') };
                parent.addRule(params);

            });
            $(parent.pCusProtoRuleList + " .editform").on('click', '.cancel', function () {
                $(this).parents('tr').find('span.name').show();
                $(this).parents('tr').find('input.ipmark').map(
                    function (i, d) {
                        return $(d).val($(d).data('ov'));
                    }
                );
                $(this).parents('tr').find('.ipmark').hide();
                $(this).parents('tr').find('select.ipmark').val($(this).parents('tr').find('select.ipmark').data('ov'));
                $(this).parent().hide();
                $(this).parent().prev().show();
            });
            $(parent.pCusProtoRuleList + " .editform").on('click', '.confirm', function () {
                var id = $(this).attr("data-key");
                var name = $(this).parents('tr').find('.ipmark').eq(0).val();
                var port = $(this).attr("data-port");
                var type = $(this).attr("data-type");
                var subParent = this;
                if (name == "") {
                    layer.alert("协议名称不能为空", { icon: 5 });
                    return false;
                }
                if (name.length > 64) {
                    layer.alert("协议名称不能超过64个字符", { icon: 5 });
                    return false;
                }
                if (!/^[0-9a-zA-Z-_]+$/.test(name)) {
                    layer.alert("协议名称由数字、字母、字符(_,-)组成", { icon: 5 });
                    return false;
                }
                var loadIndex1 = layer.load(2), modpromise = URLManager.getInstance().ajaxCallByURL(link, "PUT", { id: id, name: name, port: port, type: type });
                modpromise.fail(function (jqXHR, textStatus, err) {
                    console.log(textStatus + " - " + err.message);
                    layer.close(loadIndex1);
                });
                modpromise.done(function (result) {
                    if (result.status) {
                        layer.close(loadIndex1);
                        layer.alert('修改成功！', { icon: 6 });
                    } else {
                        layer.close(loadIndex1);
                        layer.alert(result.msg, { icon: 5 });
                    }
                    parent.selectRules();
                });

            });
            $(parent.pCusProtoRuleList + ">tbody").find(".btn-on-box input[type='checkbox']").on("change", function () {
                var id = $(this).attr("data-key");
                var status = $(this).prop("checked") ? "1" : "0";
                parent.updateRule(id.toString(), status.toString(), $(this), !$(this).prop("checked"));
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
        html += "<tr><td colspan='6'>暂无数据</td></tr>";
        $(this.pCusProtoRuleList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - CusProtoController.selectRules() - Unable to get all events: " + err.message);
    }
}
CusProtoController.prototype.exportCusList = function () {
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL;
        window.open(link + "/cusProtoExport?loginuser=" + AuthManager.getInstance().getUserName());
    }
    catch (err) {
        console.error("ERROR - CusProtoController.exportCusList() - Unable to export all CusList: " + err.message);
    }
}
CusProtoController.prototype.importdialog = function () {
    try {
        var parent = this, importtype = "";
        var tmplay = layer.open({
            type: 1,
            title: "编辑",
            area: ["360px", '160px'],
            shade: [0.5, '#393D49'],
            content: `
            <div class="dialog-content" id="import_type">
            <label style="padding:10px 0">导入方式</label>
            <input type="radio" class="dxinput" name="imtype" id="imtype_all" value="1" checked><label for="imtype_all"></label><label>全局导入</label>
            <input type="radio" class="dxinput" name="imtype" id="imtype_more" value="2"><label for="imtype_more"></label><label>增量导入</label>
            <button class="btn btn-primary">选择文件</button>
            <button class="btn btn-danger">取消 </button>
            </div>
            `,
            success: function (layero, index) {
                $("#import_type .btn-danger").click(function () {
                    layer.close(tmplay);
                });
                $("#import_type .btn-primary").click(function () {
                    importtype = $("[name=imtype]:checked").val();
                    $(parent.pBtnFile).val("");
                    $(parent.pBtnFile).click();
                    $(parent.pBtnFile).off("change");
                    $(parent.pBtnFile).on("change", function () {
                        var loadIndex = layer.load(2, {shade: [0.4, '#fff']});
                        var fileName = $.trim($(this).val());
                        $("#loginuser").val(AuthManager.getInstance().getUserName());
                        if (fileName != "") {
                            var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 4).toLowerCase();
                            if (fieExtension != "json") {
                                layer.alert("文件格式不对", {icon: 5});
                            } else {
                                var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL;
                                $("#importListForm").ajaxSubmit({
                                    type: 'POST',
                                    url: link + "/cusProtoImport",
                                    data: {"import_type": importtype},
                                    success: function (result) {
                                        if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                                            if (result.status == 1) {
                                                layer.alert("导入成功", {icon: 6});
                                                parent.pager = null;
                                                parent.filter.page = 1;
                                                parent.selectRules();
                                            } else {
                                                layer.alert(result.msg, {icon: 5});
                                            }
                                        } else {
                                            layer.alert("导入失败", {icon: 5});
                                        }
                                        layer.close(tmplay);
                                    }
                                });
                            }
                        }
                        layer.close(loadIndex);
                    })
                });
            }
        });
    }
    catch (err) {
        console.error("ERROR - CusProtoController.importdialog() - Unable to import all importdialog: " + err.message);
    }
}
CusProtoController.prototype.getDeviceType = function () {
    var parent=this,devlink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_TYPE,devpromise;
    devpromise=URLManager.getInstance().ajaxCallByURL(devlink,'GET');
    devpromise.fail(function (jqXHR, textStatus, err) {
        console.log(textStatus + " - " + err.message);
        layer.alert('获取设备类型失败',{icon:5});
        layer.close(loadIndex);
    });
    devpromise.done(function (result) {
        if (result.data){
            parent.devTypeList=result.data;
        }else{
            layer.alert('获取设备类型失败',{icon:5});
        }
    });
}
ContentFactory.assignToPackage("tdhx.base.protoaudit.CusProtoController", CusProtoController);