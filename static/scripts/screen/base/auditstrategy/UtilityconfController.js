function UtilityconfController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    // this.controller = controller;

    this.pSelectAll = '#' + elementId + '_selectAll';
    this.checkSwitch = false;

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnDel = "#" + this.elementId + "_btnDel";
    this.pBtnEnable = "#" + this.elementId + "_btnEnable";
    this.pBtnDisable = "#" + this.elementId + "_btnDisable";

    this.pTxtName = "#" + this.elementId + "_txtName";
    this.pTxtPort = "#" + this.elementId + "_txtPort";
    this.pDdlTyle = "#" + this.elementId + "_ddlType";
    this.pBtnAdd = "#" + this.elementId + "_btnAdd";
    this.pOpenform = "#" + this.elementId + "_dialog_detailForm";
    this.pOpentableBtns = "#" + this.elementId + "_dialog_tableBtns";
    this.pOpenformBtns = "#" + this.elementId + "_dialog_detailCtrlBtns";
    this.pOpenfntable = "#" + this.elementId + "_dialog_detailTable";

    this.pCusProtoRuleList = "#" + this.elementId + "_tdRuleList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotal = "#" + this.elementId + "_lblTotal";
    this.countVal=0;
    this.pager = null;
    this.filter = {
        page: 1
    };
}

UtilityconfController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
            Constants.TEMPLATES.UTILITYTPL_CONF_OPEN],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - UtilityconfController.init() - Unable to initialize: " + err.message);
    }
}
UtilityconfController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.UTILITYTPL_CONF), {
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
UtilityconfController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pBtnRefresh).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.selectUtiRules();
        });
        $(this.pBtnDel).on("click", function () {
            parent.deleteRule();
        });
        $(this.pBtnAdd).on("click", function () {
            if(parent.countVal<16){
                parent.addRule();
            }else{
                layer.alert('字段描述配置上限为16条',{icon:5});
            }
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
    }
    catch (err) {
        console.error("ERROR - UtilityconfController.initControls() - Unable to initialize control: " + err.message);
    }
}

UtilityconfController.prototype.load = function () {
    try {
        this.selectUtiRules();
        //this.getInitEventAction();
    }
    catch (err) {
        console.error("ERROR - UtilityconfController.load() - Unable to load: " + err.message);
    }
}

UtilityconfController.prototype.addRule = function (edit) {
    var loadIndex;
    try {
        var parent = this, dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.UTILITYTPL_CONF_OPEN), {
            elementId: parent.elementId + "_dialog"
        });
        var width = parent.pViewHandle.width() - 10 + "px";
        var height = $(window).height() - parent.pViewHandle.offset().top - $(window).height() / 10 + "px";
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_UTILITY_LIST, promise;//新增地址列表
        var tmplay = layer.open({
            type: 1,
            title: edit ? "编辑" : '新增',
            area: ["950px", '635px'],
            //offset: ["82px", "200px"],
            shade: [0.5, '#393D49'],
            content: dialogTemplate,
            success: function (layero, index) {
                var rules = [['', '']], dels = new Set([]), openbtns = $(parent.pOpenformBtns + ' button'), rulebtns = $(parent.pOpentableBtns + ' button'), ipts = $(parent.pOpenform + ' input'), table = $(parent.pOpenfntable + ' ul'), overDiv = $(parent.pOpenfntable + ' >div');
                parent.generate = function () {
                    var lis = ''; table.empty();
                    $(rules).each((i, d) => {
                        lis += Validation.formatString(`<li>
                            <input type='checkbox' class='idx chinput' data-idx="${i}" id='chkt_"${i}"'/><label for='chkt_"${i}"'></label>
                            <span>
                                <label>字段值：</label><input type="text" maxlength="128" value="${d[0]}" class="fieldval" data-idx="${i}_0" placeholder="16进制编码并不可重复" /><e style="color:red;">*</e>
                            </span>
                            <span>
                                <label>字段描述：</label><input type="text" maxlength="64" value="${d[1]}" class="fieldesc" data-idx="${i}_1" placeholder="" value="" /><e style="color:red;">*</e>
                            </span>
                        </li>`);
                    });
                    table.append(lis);
                }
                if(edit){
                    ipts.eq(0).val(edit.name);
                    ipts.eq(1).val(edit.desc);
                    rules=[];
                    edit.content.forEach(d=>{
                        var tmp=[];
                        tmp.push(d.audit_value),tmp.push(d.value_desc);
                        rules.push(tmp);
                    });
                    parent.generate();
                    if(edit.used){
                        ipts.css({ borderColor: '#ccc', color: '#888' }).prop({disabled:true});
                        table.find('input').css({ borderColor: '#ccc', color: '#888' }).prop({disabled:true});
                        rulebtns.css({ borderColor: '#ccc' }).prop({disabled:true});
                        openbtns.eq(0).remove();
                    }
                }else{
                    parent.generate();
                }
                parent.checkComplete = (size) => {
                    if (rules.length >= size) {
                        layer.alert('规则数量上限为'+size+'条', { icon: 5 });
                        return false;
                    }
                    var swi = false;
                    $(rules).each((i, d) => {
                        $(d).each((ii, dd) => {
                            if (dd==='') {
                                swi = true;
                                return false;
                            }
                        });
                        if (swi) {
                            return false;
                        }
                    });
                    if (swi) {
                        layer.alert('请完整填写必填项再试！', { icon: 5 });
                        return false;
                    }
                    return true;
                }
                rulebtns.eq(0).click(function () {
                    if(!parent.checkComplete(32)){
                        return false;
                    }
                    var tmparr = ['', ''];
                    rules.push(tmparr);
                    parent.generate();
                    var th = table.height(), oh = overDiv.height();
                    if (th > oh)
                        overDiv.scrollTop(th - oh);
                });
                rulebtns.eq(1).click(function () {
                    $(Array.from(dels)).each((i, d) => {
                        delete rules[d];
                    });
                    dels = new Set([]);
                    var tmp = [];
                    $(rules).each((i, d) => { if (d !== undefined) tmp.push(d) });
                    rules = tmp;
                    parent.generate();
                });
                parent.checkVal = function (_this, limit, type) {
                    var val = $(_this).val(), idx = $(_this).data('idx').split('_').map(Number),isRepeat;
                    if (type && (val === '' || val.length > limit || !/^[0-9a-fA-F]+$/.test(val) || val.length % 2)) {
                        $(_this).val(rules[idx[0]][idx[1]]);
                        layer.alert('请输入正确有效长度不超过' + limit + '的16进制偶数位字段值码', { icon: 5 });
                        return false;
                    }
                    $(rules).each(function(i,d){
                        if(val==d[0]){
                            isRepeat=true;
                            return false;
                        }
                    });
                    if(type&&isRepeat){
                        layer.alert('字段值不允许重复', { icon: 5 });
                        $(_this).val(rules[idx[0]][idx[1]]);
                        return false;
                    }
                    if (!type && val.length > limit) {
                        $(_this).val(rules[idx[0]][idx[1]]);
                        layer.alert('请输入正确有效长度为' + limit + '的描述', { icon: 5 });
                        return false;
                    }
                    rules[idx[0]][idx[1]] = val.toLowerCase();
                }
                $(parent.pOpenfntable + ' ul').on('change', '.chinput', function () {
                    var idx = $(this).data('idx');
                    if (dels.has(idx)) {
                        dels.delete(idx);
                        $(this).prop({ checked: false });
                    } else {
                        if (dels.size == rules.length - 1) {
                            layer.alert('至少保留一条规则', { icon: 5 });
                            $(this).prop({ checked: false });
                            return;
                        }
                        dels.add(idx);
                        $(this).prop({ checked: true });
                    }
                });
                $(parent.pOpenfntable + ' ul').on('change', '.fieldval', function () { var _this = this; parent.checkVal(_this, 128, 1) });
                $(parent.pOpenfntable + ' ul').on('change', '.fieldesc', function () { var _this = this; parent.checkVal(_this, 64) });
                openbtns.eq(0).click(function () {
                    var name = $.trim(ipts.eq(0).val());
                    var desc = $.trim(ipts.eq(1).val());
                    if (name == "") {
                        layer.alert("规则名称不能为空", { icon: 5 });
                        return false;
                    }
                    if (name.length > 128) {
                        layer.alert("规则名称不能超过128个字符", { icon: 5 });
                        return false;
                    }
                    if (!/^[\u4e00-\u9fa50-9a-zA-Z-_]+$/.test(name)) {
                        layer.alert("规则名称由中文、数字、字母、字符(_,-)组成", { icon: 5 });
                        return false;
                    }
                    if (desc.length > 128) {
                        layer.alert("描述长度不可大于128字节", { icon: 5 });
                        return false;
                    }
                    if (!parent.checkComplete(33)) {
                        return false;
                    }
                    loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
                    promise = URLManager.getInstance().ajaxCallByURL(link, edit ? "PUT" : "POST", { value_map_id: edit ? edit.id : '', value_map_name: name, value_map_desc: desc, value_list: rules.map(d => {return { audit_value: d[0], value_desc: d[1] };}) });
                    promise.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                        layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                        layer.close(loadIndex);
                    });
                    promise.done(function (result) {
                        layer.close(tmplay);
                        if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                            switch (result.status) {
                                case 1:
                                    delete parent.pager;
                                    parent.filter.page = 1;
                                    parent.selectUtiRules();
                                    layer.alert((edit?'编辑':'添加')+"规则成功", { icon: 6 });
                                    break;
                                /*case -1: layer.alert("当前规则已经存在，请不要重复添加", { icon: 5 }); break;
                                case 0: layer.alert("规则数量超出上限", { icon: 5 }); break;
                                case 2: layer.alert("白名单正在学习中...请稍后操作.", { icon: 5 }); break;*/
                                default: layer.alert(result.msg, { icon: 5 }); break;
                            }
                            layer.close(loadIndex);
                        }
                        else {
                            layer.alert((edit?'编辑':'添加')+"规则失败", { icon: 5 });
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
        console.error("ERROR - UtilityconfController.addRule() - Unable to export all events: " + err.message);
    }
}

UtilityconfController.prototype.deleteRule = function (id, $tr) {
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
                var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_UTILITY_LIST;
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
                                    parent.selectUtiRules();
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
                console.error("ERROR - UtilityconfController.exportLog() - Unable to delete this rule: " + err.message);
            }
        })
    } else {
        layer.alert("请选择要删除的规则再试！", { icon: 5 });
    }
}

UtilityconfController.prototype.selectUtiRules = function () {
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_UTILITY_LIST;
        var promise = URLManager.getInstance().ajaxCall(link, this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='6'>暂无数据</td></tr>";
            $(parent.pCusProtoRuleList + ">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.data) != "undefined") {
                parent.countVal=result.total;
                if (result.data.length > 0) {
                    for (var i = 0; i < result.data.length; i++) {
                        html += "<tr>";
                        html += "<td style='width:80px;'>" + "<input type='checkbox' class='chinput selflag' data-id='" + result.data[i]['value_map_id'] + "' id='u" + result.data[i]['value_map_id'] + "' /><label for='u" + result.data[i]['value_map_id'] + "'></label></td>";
                        html += "<td style='text-align:left;width:18%;'>" + result.data[i]['value_map_name'] + "</td>";
                        html += "<td style=''>" + (result.data[i]['value_map_desc']?result.data[i]['value_map_desc']:'') + "</td>";
                        html += "<td style='width:18%;'>" + (result.data[i]['is_used'] ? '是' : '否') + "</td>";
                        html += "<td style='width:10%;'><button style='margin-right:5px;' class='btn btn-default btn-xs btn-color-details' data-key='" + result.data[i]['value_map_id'] + "' data-name='" + result.data[i]['value_map_name'] + "' data-used='" + result.data[i]['is_used'] + "' data-desc='" + result.data[i]['value_map_desc'] + "' data-content='" + JSON.stringify(result.data[i]['value_list']) + "'><i class='fa "+(result.data[i]['is_used'] ?"fa-eye":"fa-edit")+"'></i>"+(result.data[i]['is_used'] ?"查看":"编辑")+"</button></td>";
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
                var params={id:$(this).data('key'),name:$(this).data('name'),used:$(this).data('used'),desc:$(this).data('desc'),content:$(this).data('content')};
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
                    layer.alert("规则名称不能为空", { icon: 5 });
                    return false;
                }
                if (name.length > 64) {
                    layer.alert("规则名称不能超过64个字符", { icon: 5 });
                    return false;
                }
                if (!/^[\u4e00-\u9fa50-9a-zA-Z-_]+$/.test(name)) {
                    layer.alert("规则名称由中文、数字、字母、字符(_,-)组成", { icon: 5 });
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
                    parent.selectUtiRules();
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
                    parent.selectUtiRules();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='6'>暂无数据</td></tr>";
        $(this.pCusProtoRuleList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - UtilityconfController.selectUtiRules() - Unable to get all events: " + err.message);
    }
}
ContentFactory.assignToPackage("tdhx.base.protoaudit.UtilityconfController", UtilityconfController);