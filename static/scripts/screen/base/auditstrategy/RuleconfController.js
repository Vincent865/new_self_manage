function RuleconfController(controller, viewHandle, elementId) {
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
    this.pOpentable = "#" + this.elementId + "_dialog_detailTable";
    this.pOpenform = "#" + this.elementId + "_dialog_detailForm";
    this.pOpenform1 = "#" + this.elementId + "_dialog_detailForm1";
    this.pOpenform2 = "#" + this.elementId + "_dialog_detailForm2";
    this.pOpenform3 = "#" + this.elementId + "_dialog_detailForm3";
    this.pOpenformBtns = "#" + this.elementId + "_dialog_detailCtrlBtns";
    this.pOpenaddBtns = "#" + this.elementId + "_dialog_detailFormBtns";

    this.pCusProtoRuleList = "#" + this.elementId + "_tdRuleList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotal = "#" + this.elementId + "_lblTotal";
    this.pager = null;
    this.filter = {
        page: 1
    };
}

RuleconfController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
            Constants.TEMPLATES.RULETPL_CONF_OPEN],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - RuleconfController.init() - Unable to initialize: " + err.message);
    }
}
RuleconfController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULETPL_CONF), {
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
RuleconfController.prototype.initControls = function () {
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
    }
    catch (err) {
        console.error("ERROR - RuleconfController.initControls() - Unable to initialize control: " + err.message);
    }
}

RuleconfController.prototype.load = function () {
    try {
        this.selectRules();
        //this.getInitEventAction();
    }
    catch (err) {
        console.error("ERROR - RuleconfController.load() - Unable to load: " + err.message);
    }
}

RuleconfController.prototype.addRule = function (edit) {
    var loadIndex;
    try {
        var parent = this, dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULETPL_CONF_OPEN), {
            elementId: parent.elementId + "_dialog"
        });
        var width = parent.pViewHandle.width() - 10 + "px";
        var height = $(window).height() - parent.pViewHandle.offset().top - $(window).height() / 10 + "px";
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_UTILITY_TPL, promise;//新增地址列表
        var tmplay = layer.open({
            type: 1,
            title: edit ? "编辑" : '新增',
            area: ["980px", '660px'],
            //offset: ["82px", "200px"],
            shade: [0.5, '#393D49'],
            content: dialogTemplate,
            success: function (layero, index) {
                var openbtns = $(parent.pOpenformBtns + ' button'), openaddbtns = $(parent.pOpenaddBtns + ' button'), ipts = $(parent.pOpenform + ' input'), iptss=[], selt = $(parent.pOpenform + ' select'), dels = new Set([]);iptss[0] = $(parent.pOpenform1 + ' input'),iptss[1] = $(parent.pOpenform2 + ' input'),iptss[2] = $(parent.pOpenform3 + ' input');
                var rules = [['', '', '', '', 0]], table = $(parent.pOpentable + ' ul'), u_list = [], selts = parent.pOpentable + ' ul select';
                promise = URLManager.getInstance().ajaxCall(link);
                promise.done(function (result) {
                    if (result.status) {
                        u_list = result.data;
                        if (edit) {
                            ipts.eq(0).val(edit.name).attr({title:edit.name});
                            ipts.eq(1).val(edit.desc).attr({title:edit.desc});
                            iptss.map((d,i)=>{d.eq(0).val(edit['charCode'+i]).attr({title:edit['charCode'+i]})});
                            iptss.map((d,i)=>{
                                if(edit['charCode'+i]!==''){
                                    iptss[i].eq(1).prop({disabled:false}).css({backgroundColor:'white'});
                                    iptss[i].eq(2).prop({disabled:false}).css({backgroundColor:'white'});
                                    $('.warningtip'+i).show();
                                }else{
                                    iptss[i].eq(1).prop({disabled:true}).css({backgroundColor:'#eee'});
                                    iptss[i].eq(2).prop({disabled:true}).css({backgroundColor:'#eee'});
                                    $('.warningtip'+i).hide();
                                }
                                iptss[i].eq(2).val(edit['depth'+i]===1500?'':edit['depth'+i]);
                                iptss[i].eq(1).val(edit['charCode'+i]?edit['soffset'+i]:edit['soffset'+i]===0?'':edit['soffset'+i]);
                            });
                            rules = [];
                            edit.content.forEach(d => {
                                var tmp = [];
                                tmp.push(d.offset), tmp.push(d.bit_offset), tmp.push(d.length), tmp.push(d.audit_name), tmp.push(d.value_map_id);
                                rules.push(tmp);
                            });
                            parent.generate();
                            if(edit.used){
                                ipts.css({ borderColor: '#ccc', color: '#888' }).prop({disabled:true});
                                iptss.map((d)=>{d.css({ borderColor: '#ccc', color: '#888' }).prop({disabled:true})});
                                openaddbtns.css({ borderColor: '#ccc'}).prop({disabled:true});
                                openbtns.eq(0).remove();
                                table.find('input').css({ borderColor: '#ccc', color: '#888' }).prop({ disabled: true });
                                table.find('select').css({ borderColor: '#ccc', color: '#888' }).prop({ disabled: true });
                            }
                        }else{
                            parent.generate();
                        }
                    }
                });
                $(iptss).each(function(i,d){
                    $(d).eq(0).blur(function () {
                        if(i){
                            if($(iptss[i-1]).eq(0).val()===''){
                                layer.alert('特征码请逐行填写！', { icon: 5 });
                                $(this).val('');$(d).eq(1).val('').prop({disabled:true}).css({backgroundColor:'#eee'});
                                $(d).eq(2).val('').prop({disabled:true}).css({backgroundColor:'#eee'});
                                return false;
                            }
                        }
                        var val = $.trim($(this).val()).toLowerCase();
                        if(val){
                            $(d).eq(1).prop({disabled:false}).css({backgroundColor:'white'});
                            $(d).eq(2).prop({disabled:false}).css({backgroundColor:'white'});
                            $('.warningtip'+i).show();
                        }else{
                            $(d).eq(1).val(''),$(d).eq(2).val('');
                            $(d).eq(1).prop({disabled:true}).css({backgroundColor:'#eee'});
                            $(d).eq(2).prop({disabled:true}).css({backgroundColor:'#eee'});
                            $('.warningtip'+i).hide();
                        }
                        $(this).val(val);
                    });
                });
                parent.checkComplete = () => {
                    var swi = false;
                    $(rules).each((i, d) => {
                        $(d).each((ii, dd) => {
                            if (ii !== 4 && ii!==1 && dd==='') {
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
                openaddbtns.eq(0).click(() => {
                    if (rules.length == 5) {
                        layer.alert('规则数量上限为5条', { icon: 5 });
                        return;
                    }
                    if (!parent.checkComplete()) return;
                    var tmparr = ['','', '', '', 0];
                    rules.push(tmparr);
                    parent.generate();
                });
                parent.generate = function () {
                    table.empty();
                    var lis = '';
                    $(rules).each((i, d) => {
                        lis += Validation.formatString(`<li>
                            <input type='checkbox' class='idx chinput' data-idx="${i}" id='chk_"${i}"'/><label for='chk_"${i}"'></label>
                            <span><label>字节偏移：</label><input type="text" class="ruleoffset" maxlength="1500" data-idx="${i}_0" value="${d[0]}"><e style="color:red;">*</e></span>
                            <span><label>位偏移：</label><input type="text" class="spaceoffset" maxlength="1500" data-idx="${i}_1" value="${d[1]}"></span>
                            <span><label>字段长度：</label><input type="text" class="rulelength" data-idx="${i}_2" minlength="1" maxlength="256" value="${d[2]}"><e style="color:red;">*</e></span>
                            <span><label>字段名：</label><input type="text" class="rulefield" data-idx="${i}_3" maxlength="64" value="${d[3]}" style="width: 95px;"><e style="color:red;">*</e></span>
                            <span><label>内容描述：</label>
                                <select class="content" data-idx="${i}_4">
                                    <option value="0">空</option>
                                </select>
                            </span>
                            </li>`);
                    });
                    table.append(lis);
                    var selects = $(selts);
                    $.each(u_list, function (k, v) {
                        $('<option>').val(k).text(v).appendTo(selects);
                    });
                    $(selects).each((i, d) => { $(d).val(rules[i][4]) });
                }
                //     }
                // });
                openaddbtns.eq(1).click(() => {
                    $(Array.from(dels)).each((i, d) => {
                        delete rules[d];
                    });
                    dels = new Set([]);
                    var tmp = [];
                    $(rules).each((i, d) => { if (d !== undefined) tmp.push(d) });
                    rules = tmp;
                    parent.generate();
                });
                parent.checkVal = function (_this, num,min,isnone) {
                    var val = $(_this).val(), idx = $(_this).data('idx').split('_').map(Number);
                    if (typeof (num) === 'number') {
                        if ((isnone?0:($(_this).val() === '')) || isNaN(val) || Number(val) < (min?min:0) || Number(val) > num) {
                            $(_this).val(isnone?'':rules[idx[0]][idx[1]]);
                            layer.alert('该值必须为大于等于'+min+'小于' + num + '的整数', { icon: 5 });
                            return false;
                        }
                    } else {
                        if ($(_this).val() === '') {
                            $(_this).val(rules[idx[0]][idx[1]]);
                            layer.alert('该值不能为空', { icon: 5 });
                            return false;
                        }
                    }
                    rules[idx[0]][idx[1]] = val;
                }
                $(parent.pOpentable + ' ul').on('change', '.chinput', function () {
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
                $(parent.pOpentable + ' ul').on('change', '.ruleoffset', function () { var _this = this; parent.checkVal(_this, 1500,0) });
                $(parent.pOpentable + ' ul').on('change', '.spaceoffset', function () { var _this = this; var pn=$(this).parent(),preval=pn.next().children('input').val();if(!isNaN(preval)&&Number(preval)>16){$(this).val('');layer.alert('字段长度大于16，该值必须为空',{icon:5});}else{parent.checkVal(_this,7,0,true)} });
                $(parent.pOpentable + ' ul').on('change', '.rulelength', function () { var _this = this; var pn=$(this).parent(),preval=pn.prev().children('input').val();parent.checkVal(_this, preval?16:256,1,true) });
                $(parent.pOpentable + ' ul').on('change', '.rulefield', function () { var _this = this; parent.checkVal(_this, '64') });
                $(parent.pOpentable + ' ul').on('change', '.content', function () { var val = $(this).val(), idx = $(this).data('idx').split('_').map(Number); rules[idx[0]][idx[1]] = val; });
                openbtns.eq(0).click(function () {
                    var name = $.trim(ipts.eq(0).val()),perm=false, desc = $.trim(ipts.eq(1).val()),feacodeset=[];
                    $(iptss).each((i,d)=>{
                        feacodeset[i]={};
                        feacodeset[i]['feacode']=iptss[i].eq(0).val();
                        feacodeset[i]['soffset']=iptss[i].eq(1).val()!==''?Number(iptss[i].eq(1).val()):'';
                        feacodeset[i]['matdepth']=iptss[i].eq(2).val()!==''?Number(iptss[i].eq(2).val()):''
                        if(i&&!(i%2)){
                            if($(d).eq(0).val()!=='') {
                                if ($(iptss[i - 1]).eq(0).val() === '' || $(iptss[i - 2]).eq(0).val() === '') {
                                    perm = true;
                                    layer.alert('特征码请逐行填写！', {icon: 5});
                                    return false;
                                }
                            }
                        }else if(i&&(i%2)){
                            if($(d).eq(0).val()!=='') {
                                if ($(iptss[i - 1]).eq(0).val() === '') {
                                    perm = true;
                                    layer.alert('特征码请逐行填写！', {icon: 5});
                                    return false;
                                }
                            }
                        }
                    });
                    if (name == "" || name.length > 128) {
                        layer.alert("规则名称不能为空且不能超过128个字符", { icon: 5 });
                        return false;
                    }
                    if (!/^[\u4e00-\u9fa50-9a-zA-Z-_]+$/.test(name)) {
                        layer.alert("规则名称由中文、数字、字母、字符(_,-)组成", { icon: 5 });
                        return false;
                    }
                    $(feacodeset).each((i,d)=>{
                        if (feacodeset[i]['feacode'] !== '' && (!/^[0-9a-fA-F]+$/.test(feacodeset[i]['feacode']) || feacodeset[i]['feacode'].length % 2)) {
                            layer.alert("请输入长度不超过128的16进制偶数位特征码", { icon: 5 });perm=true;
                            return false;
                        }
                        if (feacodeset[i]['feacode']) {
                            if (feacodeset[i]['soffset']===''||isNaN(feacodeset[i]['soffset']) || (Number(feacodeset[i]['soffset']) > 1500 || Number(feacodeset[i]['soffset']) < 0)) {
                                layer.alert("请输入长度为0-1500的整数起始偏移", { icon: 5 });perm=true;
                                return false;
                            }
                            if (feacodeset[i]['matdepth']===""||isNaN(feacodeset[i]['matdepth']) || (Number(feacodeset[i]['matdepth']) > 1500 || Number(feacodeset[i]['matdepth']) < 0)) {
                                layer.alert("请输入长度为0-1500的整数匹配深度", { icon: 5 });perm=true;
                                return false;
                            }
                            if (Number(feacodeset[i]['matdepth'])*2 < feacodeset[i]['feacode'].length) {
                                layer.alert("匹配深度必须大于等于特征码长度", { icon: 5 });perm=true;
                                return false;
                            }
                            if(i){
                                if(Number(feacodeset[i]['soffset'])<=(feacodeset[i-1]['feacode'].length/2+feacodeset[i-1]['soffset'])){
                                    layer.alert("下一行起始偏移长度必须大于上一行特征码长度+起始偏移长度", { icon: 5 });perm=true;
                                    return false;
                                }
                            }
                        }
                    });
                    if(perm) return;
                    if (!parent.checkComplete()) return;
                    loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
                    var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_RULES_TPL;
                    var promise = URLManager.getInstance().ajaxCallByURL(link, edit ? "PUT" : "POST", {
                        content_id: edit?edit.id:'',
                        content_name: name,
                        content_desc: desc,
                        verify_code: feacodeset[0]['feacode'],
                        start_offset: feacodeset[0]['soffset'],
                        depth: feacodeset[0]['matdepth'],
                        verify_code2: feacodeset[1]['feacode'],
                        start_offset2: feacodeset[1]['soffset'],
                        depth2: feacodeset[1]['matdepth'],
                        verify_code3: feacodeset[2]['feacode'],
                        start_offset3: feacodeset[2]['soffset'],
                        depth3: feacodeset[2]['matdepth'],
                        audit_sets: rules.map(d => { return { offset: d[0], bit_offset:d[1],length: d[2], audit_name: d[3], value_map_id: d[4] }; })
                    });
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
                                    parent.pager = null;
                                    parent.filter.page = 1;
                                    parent.selectRules();
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
        console.error("ERROR - RuleconfController.addRule() - Unable to export all events: " + err.message);
    }
}

RuleconfController.prototype.validate416Range = function (input) {
    if (/^[0-9a-fA-F]+$/.test(input) && parseInt(input, 16) > 2000) {
        input = input.toLowerCase();
        return parseInt(input.split('x')[1], 16);
    }
    return false;
};

RuleconfController.prototype.deleteRule = function (id, $tr) {
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
                var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_RULES_TPL;
                var promise = URLManager.getInstance().ajaxCallByURL(link, "DELETE", { content_id: id || parent.preDelete.join(",") });
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
                console.error("ERROR - RuleconfController.exportLog() - Unable to delete this rule: " + err.message);
            }
        })
    } else {
        layer.alert("请选择要删除的规则再试！", { icon: 5 });
    }
}

RuleconfController.prototype.selectRules = function () {
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_RULES_TPL;
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
                        html += "<td style='width:80px;'>" + "<input type='checkbox' class='chinput selflag' data-id='" + result.data[i]['content_id'] + "' id='d" + result.data[i]['content_id'] + "' /><label for='d" + result.data[i]['content_id'] + "'></label></td>";
                        html += "<td style='text-align:left;width:18%;'>" + result.data[i]['content_name'] + "</td>";
                        html += "<td>" + (result.data[i]['content_desc'] ? result.data[i]['content_desc'] : '') + "</td>";
                        html += "<td style='width:18%;'>" + (result.data[i]['is_used'] ? '是' : '否') + "</td>";
                        html += "<td style='width:10%;'><button style='margin-right:5px;' class='btn btn-default btn-xs btn-color-details' data-key='" + result.data[i]['content_id'] + "' data-name='" + result.data[i]['content_name'] + "' data-desc='" + result.data[i]['content_desc']+ "' data-used='" + result.data[i]['is_used'] + "' data-charCode0='" + (result.data[i]['verify_code']!==undefined?result.data[i]['verify_code']:'') + "' data-depth0='" + (result.data[i]['depth']!==undefined?result.data[i]['depth']:'') + "' data-soffset0='" + (result.data[i]['start_offset']!==undefined?result.data[i]['start_offset']:'') + "' data-charCode1='" +(result.data[i]['verify_code2']!==undefined?result.data[i]['verify_code2']:'') + "' data-depth1='" + (result.data[i]['depth2']!==undefined?result.data[i]['depth2']:'') + "' data-soffset1='" + (result.data[i]['start_offset2']!==undefined?result.data[i]['start_offset2']:'') + "' data-charCode2='" + (result.data[i]['verify_code3']!==undefined?result.data[i]['verify_code3']:'') + "' data-depth2='" + (result.data[i]['depth3']!==undefined?result.data[i]['depth3']:'') + "' data-soffset2='" + (result.data[i]['start_offset3']!==undefined?result.data[i]['start_offset3']:'') + "' data-content='" + JSON.stringify(result.data[i]['audit_sets']) + "'><i class='fa "+(result.data[i]['is_used'] ?"fa-eye":"fa-edit")+"'></i>"+(result.data[i]['is_used'] ?"查看":"编辑")+"</button></td>";
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
                var params = { id: $(this).data('key'), name: $(this).data('name'), desc: $(this).data('desc'), used: $(this).data('used'),
                    charCode0: $(this).data('charcode0'), soffset0: $(this).data('soffset0'), depth0: $(this).data('depth0'),
                    charCode1: $(this).data('charcode1'), soffset1: $(this).data('soffset1'), depth1: $(this).data('depth1'),
                    charCode2: $(this).data('charcode2'), soffset2: $(this).data('soffset2'), depth2: $(this).data('depth2'),
                    content: $(this).data('content') };
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
                if (name.length > 128) {
                    layer.alert("规则名称不能超过128个字符", { icon: 5 });
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
        console.error("ERROR - RuleconfController.selectRules() - Unable to get all events: " + err.message);
    }
}
ContentFactory.assignToPackage("tdhx.base.protoaudit.RuleconfController", RuleconfController);