function FingerprintController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pSelectAll = '#' + elementId + '_selectAll';
    this.checkSwitch = false;

    this.pBtnAddFinger = "#" + this.elementId + "_btnAddFinger";
    this.pBtnRemove = "#" + this.elementId + "_btnRemove";

    this.pDetailForm = "#" + this.elementId + "_detailForm";
    this.pTxtPort = "#" + this.elementId + "_txtPort";
    this.pDdlTyle = "#" + this.elementId + "_ddlType";
    this.pBtnAdd = "#" + this.elementId + "_btnAdd";

    this.pOpenform = "#" + this.elementId + "_dialog_detailForm";

    this.pMacTable = "#" + this.elementId + "_dialog_macTable";
    this.pMacFormBtns = "#" + this.elementId + "_dialog_macFormBtns";
    this.pProtoTable = "#" + this.elementId + "_dialog_protoTable";
    this.pProtoFormBtns = "#" + this.elementId + "_dialog_protoFormBtns";
    this.pOpenformBtns = "#" + this.elementId + "_dialog_detailCtrlBtns";
    this.devTypeList=[];

    this.pFingerList = "#" + this.elementId + "_tdFingerList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotal = "#" + this.elementId + "_lblTotal";
    this.pager = null;
    this.filter = {
        page: 1
    };
    this.protocolList = Constants.AUDIT_PROTOCOL_LIST[APPCONFIG.PRODUCT];
}

FingerprintController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.TOPO_FINGER_DIALOG,
                Constants.TEMPLATES.TOPO_FINGER],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - FingerprintController.init() - Unable to initialize: " + err.message);
    }
}

FingerprintController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.TOPO_FINGER), {
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

FingerprintController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pBtnRemove).on("click", function () {
            parent.deleteRule();
        });

        $(this.pBtnAddFinger).on("click", function () {
            parent.addRule();
        });

        $(parent.pSelectAll).click(function () {
            parent.checkSwitch = !parent.checkSwitch;
            $(parent.pFingerList).find('input.chinput').prop('checked', parent.checkSwitch);
        });
    }
    catch (err) {
        console.error("ERROR - FingerprintController.initControls() - Unable to initialize control: " + err.message);
    }
}

FingerprintController.prototype.load = function () {
    try {
        this.selectRules();
    }
    catch (err) {
        console.error("ERROR - FingerprintController.load() - Unable to load: " + err.message);
    }
}

FingerprintController.prototype.deleteRule = function () {
    var parent = this;
    parent.preDelete = [];
    $(parent.pFingerList).find('tbody input[type=checkbox].chinput').each(function (i, d) {
        if ($(d).prop('checked')) {
            parent.preDelete.push($(d).data('id'));
        }
    });
    if (parent.preDelete.length) {
        layer.confirm('确定删除该条数据么？', { icon: 7, title: '注意：' }, function (index) {
            layer.close(index);
            var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
            try {
                var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].TOPO_FINGER_PRINT;
                var promise = URLManager.getInstance().ajaxCallByURL(link, "DELETE", { content_id:  parent.preDelete.join(",") });
                promise.fail(function (jqXHR, textStatus, err) {
                    console.log(textStatus + " - " + err.message);
                    layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                    layer.close(loadIndex);
                });
                promise.done(function (result) {
                    if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                        switch (result.status) {
                            case 1:
                                parent.selectRules();
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
                console.error("ERROR - FingerprintController.exportLog() - Unable to delete this rule: " + err.message);
            }
        })
    } else {
        layer.alert("请选择要删除的规则再试！", { icon: 5 });
    }
}

FingerprintController.prototype.selectRules = function () {
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].TOPO_FINGER_PRINT;
        var devlink = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_TYPE, devpromise;//获取设备型号
        var promise = URLManager.getInstance().ajaxCall(link, this.filter);
        //获取设备类型
        devpromise = URLManager.getInstance().ajaxCallByURL(devlink, 'GET');
        devpromise.done(function (res) {
            console.log(res.data)
            parent.devTypeList=res.data;
            var devlist=['未知'];
            $(res.data).each(function(i,d){
                devlist.push(d.name);
            });
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                html += "<tr><td colspan='4'>暂无数据</td></tr>";
                $(parent.pFingerList + ">tbody").html(html);
                layer.close(loadIndex);
            });
            promise.done(function (result) {
                if (typeof (result) != "undefined" && typeof (result.data) != "undefined") {
                    if (result.data.length > 0) {
                        for (var i = 0; i < result.data.length; i++) {
                            html += "<tr>";
                            html += "<td style='width:80px;'>" + "<input type='checkbox' class='chinput selflag' data-id='" + result.data[i]['content_id'] + "' id='d" + result.data[i]['content_id'] + "' /><label for='d" + result.data[i]['content_id'] + "'></label></td>";
                            html += "<td>" + result.data[i]['update_time'] + "</td>";
                            html += "<td style='width:18%;'>" + result.data[i]['rule_name'] + "</td>";
                            html += "<td style='width:18%;'>" + result.data[i]['vendor'] + "</td>";
                            html += "<td style='width:18%;'>" + devlist[result.data[i]['dev_type']] + "</td>";
                            html += "<td style='width:18%;'>" + result.data[i]['dev_model'] + "</td>";
                            html += "<td style='width:10%;'><button style='margin-right:5px;' class='btn btn-default btn-xs btn-color-details' data-key='" + result.data[i]['content_id'] + "' data-name='" + result.data[i]['rule_name'] + "' data-vendor='" + result.data[i]['vendor'] + "' data-type='" + result.data[i]['dev_type'] + "' data-model='" + result.data[i]['dev_model'] + "' data-protoset='"+ JSON.stringify(result.data[i]['proto_port_set']) +"' data-macsets='"+ JSON.stringify(result.data[i]['mac_sets']) +"'><i class='fa fa-edit'></i>编辑</button></td>";
                            html += "</tr>";
                        }
                    }
                    else {
                        html += "<tr><td colspan='4'>暂无数据</td></tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='4'>暂无数据</td></tr>";
                }
                $(parent.pFingerList + ">tbody").html(html);
                layer.close(loadIndex);

                $(parent.pFingerList + ">tbody").find("button[class='btn btn-default btn-xs btn-color-details']").on("click", function () {
                    var params = { content_id: $(this).data('key'), rule_name: $(this).data('name'), vendor: $(this).data('vendor'), dev_type: $(this).data('type'), dev_model: $(this).data('model'), proto_port_set: $(this).data('protoset') , mac_sets: $(this).data('macsets')};
                    parent.addRule(params);
                });

                if (parent.pager == null) {
                    parent.pager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                        parent.filter.page = pageIndex;
                        parent.selectRules();
                    });
                    parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
                }
            });
        });
    }
    catch (err) {
        html += "<tr><td colspan='4'>暂无数据</td></tr>";
        $(this.pFingerList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - FingerprintController.selectRules() - Unable to get all events: " + err.message);
    }
}
FingerprintController.prototype.addRule = function (edit) {
    var loadIndex;
    try {
        var parent = this, dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.TOPO_FINGER_DIALOG), {
            elementId: parent.elementId + "_dialog"
        });
        var width = parent.pViewHandle.width() - 10 + "px";
        var height = $(window).height() - parent.pViewHandle.offset().top - $(window).height() / 10 + "px";
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].TOPO_CUSPROTO_LIST, promise;//获取自定义协议
        var tmplay = layer.open({
            type: 1,
            title: edit ? "编辑" : '新增',
            area: ["950px", '590px'],
            //offset: ["82px", "200px"],
            shade: [0.5, '#393D49'],
            content: dialogTemplate,
            success: function (layero, index) {
                var sel = $(parent.pOpenform).find("select"), ipts = $(parent.pOpenform).find("input");
                var openbtns = $(parent.pOpenformBtns + ' button');
                var macbtns = $(parent.pMacFormBtns + ' button'),protobtns = $(parent.pProtoFormBtns + ' button');
                var macrules = [['', '', '', '','','']], mactable = $(parent.pMacTable + ' ul'),macdels = new Set([]);
                var prorules = [['', '', 0]], protable = $(parent.pProtoTable + ' ul'),selfproto_list=[],prodels = new Set([]), selts = parent.pProtoTable + ' ul select';
                //获取设备类型
                sel.empty();
                sel.append("<option value='0'>未知</option>");
                for (var i = 0; i < parent.devTypeList.length; i++) {
                    sel.append("<option value=" + parent.devTypeList[i].id + ">" + parent.devTypeList[i].name + "</option>")
                }
                //获取自定义协议
                promise = URLManager.getInstance().ajaxCall(link);
                promise.done(function (result) {
                    if (result.status) {
                        selfproto_list = result.data;
                        if (edit) {
                            ipts.eq(0).val(edit.rule_name).attr({title:edit.rule_name});
                            ipts.eq(1).val(edit.vendor).attr({title:edit.vendor});
                            sel.val(edit.dev_type);
                            ipts.eq(2).val(edit.dev_model).attr({title:edit.dev_model});
                            macrules = [];
                            prorules = [];
                            edit.mac_sets.forEach(d => {
                                macrules.push(d.mac.toUpperCase().split(':'));
                            });
                            edit.proto_port_set.forEach(d => {
                                var pros = [];
                                pros.push(d.proto_name), pros.push(d.proto_port), pros.push(d.cli_server_type);
                                prorules.push(pros);
                            });
                        }
                        parent.addMac();
                        parent.addProto();
                    }
                    openbtns.eq(0).click(function () {
                        var name = $.trim(ipts.eq(0).val());
                        if (name == "") {
                            layer.alert("指纹名称不能为空", { icon: 5 });
                            return false;
                        }
                        var i='';
                        ipts.each(function(){
                            var val=$(this).val();
                            if(val!=''&&(!/^[\u4e00-\u9fa50-9a-zA-Z-_]+$/.test(val)||val.length > 128)) {
                                i=$(this).prev('label').html().replace(':','');
                                return false;
                            }
                        })
                        if(i!='') {
                            layer.alert(i+"由中文、数字、字母、字符(_,-)组成，且不能超过128个字符", { icon: 5 });
                            return false;
                        }

                        if (!parent.checkMacComplete()) return;
                        if (!parent.checkProComplete()) return;
                        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
                        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].TOPO_FINGER_PRINT;
                        var promise = URLManager.getInstance().ajaxCallByURL(link, edit ? "PUT" : "POST", {
                            content_id: edit?edit.content_id:'', rule_name: name, vendor: $.trim(ipts.eq(1).val()), dev_type: sel.val(), dev_model: $.trim(ipts.eq(2).val()),
                            mac_sets: macrules.map(d => { return { mac: d.join(':') }; }),
                            proto_port_set: prorules.map(d => { return { proto_name: d[0], proto_port: d[1], cli_server_type: d[2].toString() }; })
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
                })
                //MAC新增删除
                macbtns.eq(0).click(() => {
                    if (macrules.length == 5) {
                        layer.alert('MAC数量上限为5条', { icon: 5 });
                        return;
                    }
                    if (!parent.checkMacComplete()) return;
                    var tmparr = ['', '', '','', '', ''];
                    macrules.push(tmparr);
                    parent.addMac();
                });
                parent.checkMacComplete = () => {
                    var swi = false,msg='';
                    $(macrules).each((i, d) => {
                        $(d).each((ii, dd) => {
                            if (ii <= 2 && dd==='') {
                                swi = true;
                                msg='MAC地址前三个字节必填';
                                return false;
                            }
                            if( ( ii==4 && dd!='' && d[3]=='') || ( ii==5 && dd!='' && (d[4]==''||d[3]=='') ) ){
                                swi = true;
                                msg='MAC地址字节必须连续';
                                return false;
                            }
                        });
                        if (swi) {
                            return false;
                        }
                    });
                    if (swi) {
                        layer.alert(msg, { icon: 5 });
                        return false;
                    }
                    return true;
                }
                macbtns.eq(1).click(() => {
                    $(Array.from(macdels)).each((i, d) => {
                        delete macrules[d];
                    });
                    macdels = new Set([]);
                    var tmp = [];
                    $(macrules).each((i, d) => { if (d !== undefined) tmp.push(d) });
                    macrules = tmp;
                    parent.addMac();
                });
                $(parent.pMacTable + ' ul').on('change', '.chinput', function () {
                    var idx = $(this).data('idx');
                    if (macdels.has(idx)) {
                        macdels.delete(idx);
                        $(this).prop({ checked: false });
                    } else {
                        if (macdels.size == macrules.length - 1) {
                            layer.alert('至少保留一条MAC规则', { icon: 5 });
                            $(this).prop({ checked: false });
                            return;
                        }
                        macdels.add(idx);
                        $(this).prop({ checked: true });
                    }
                });
                parent.addMac = function () {
                    mactable.empty();
                    var lis = '';
                    $(macrules).each((i, d) => {
                        lis += Validation.formatString(`<li>
                            <input type='checkbox' class='idx chinput' data-idx="${i}" id='chk_mac_${i}'/><label for='chk_mac_${i}'></label>
                            <label>MAC地址:</label>
                            <input type="text" maxlength="2" data-idx="${i}_0" value="${d[0]}" class="aaa">:
                            <input type="text" maxlength="2" data-idx="${i}_1" value="${d[1]}">:
                            <input type="text" maxlength="2" data-idx="${i}_2" value="${d[2]}">:
                            <input type="text" maxlength="2" data-idx="${i}_3" value="${d[3]}">:
                            <input type="text" maxlength="2" data-idx="${i}_4" value="${d[4]}">:
                            <input type="text" maxlength="2" data-idx="${i}_5" value="${d[5]}">
                            <span style="color:red">*</span>
                        </li>`);
                    });
                    mactable.append(lis);
                }
                //协议端口新增删除
                protobtns.eq(0).click(() => {
                    if (prorules.length == 5) {
                        layer.alert('协议端口数量上限为5条', { icon: 5 });
                        return;
                    }
                    if (!parent.checkProComplete()) return;
                    var tmparr = ['', '', 0];
                    prorules.push(tmparr);
                    parent.addProto();
                });
                parent.checkProComplete = () => {
                    var swi = false;
                    $(prorules).each((i, d) => {
                        if(d[0]==''&&d[1]==''){
                            swi = true;
                            return false;
                        }
                        if (swi) {
                            return false;
                        }
                    });
                    if (swi) {
                        layer.alert('协议和端口不能同时为空', { icon: 5 });
                        return false;
                    }
                    return true;
                }
                protobtns.eq(1).click(() => {
                    $(Array.from(prodels)).each((i, d) => {
                        delete prorules[d];
                    });
                    prodels = new Set([]);
                    var tmp = [];
                    $(prorules).each((i, d) => { if (d !== undefined) tmp.push(d) });
                    prorules = tmp;
                    parent.addProto();
                });
                $(parent.pProtoTable + ' ul').on('change', 'li>.chinput', function () {
                    var idx = $(this).data('idx');
                    if (prodels.has(idx)) {
                        prodels.delete(idx);
                        $(this).prop({ checked: false });
                    } else {
                        prodels.add(idx);
                        $(this).prop({ checked: true });
                    }
                });
                parent.addProto = function () {
                    protable.empty();
                    var lis = '';
                    $(prorules).each((i, d) => {
                        lis += Validation.formatString(`<li>
                            <input type='checkbox' class='idx chinput' data-idx="${i}" id='chk_type_${i}'/><label for='chk_type_${i}'></label>
                            <label>协议:</label><select data-idx="${i}_0" value="${d[0]}"></select>
                            <label>端口:</label><input type="text" placeholder="范围1-65535" data-idx="${i}_1" value="${d[1]}" `+(d[2]=="1"?'disabled':'')+`>
                            <label>资产属性:</label>
                            <div>
                                <input type="checkbox" class="idx chinput" data-idx="${i}_2" value="1" id="chk_type_${i}_1" `+(d[2]!="2"?'checked':'')+`><label for="chk_type_${i}_1"></label>
                                客户端
                                <input type="checkbox" class="idx chinput" data-idx="${i}_3" value="2" id="chk_type_${i}_2" `+(d[2]!="1"?'checked':'')+`><label for="chk_type_${i}_2"></label>
                                服务端
                                <span style="color:red">*</span>
                            </div>
                        </li>`);
                    });
                    protable.append(lis);
                    var selects = $(selts);
                    var htmlpro = "<option value=''>--请选择--</option><optgroup label='自定义协议'>";
                    $.each(selfproto_list, function (i,d) {
                        htmlpro += "<option value='" + d + "'>" + d + "</option>";
                    });
                    htmlpro += "</optgroup><optgroup label='预定义协议'>";
                    $.each(parent.protocolList, function () {
                        htmlpro += "<option value='" + this.key + "'>" + this.name + "</option>";
                    });
                    htmlpro += "</optgroup>";
                    selects.append(htmlpro);
                    $(selects).each((i, d) => { $(d).val(prorules[i][0]) });
                    //mac地址输入时，自动后移
                    $(parent.pMacTable + ' ul').on('keyup','input[type=text]',function () {
                        var val = $(this).val();
                        if (val !== ''&&!/^[a-fA-F\d]{2}$/.test(val)) {
                            $(this).val(val.replace(/[^\w]/g, ''));
                        }
                        if(val.length == 2){
                            $(this).next('input').focus();
                        }
                    });
                };
                //输入mac地址,校验
                $(parent.pMacTable + ' ul').on('change', '[type=text]',function () {
                    var val = $(this).val(), idx = $(this).data('idx').split('_').map(Number);
                    if ($(this).val() !== ''&&!/^[a-fA-F\d]{2}$/.test(val)) {
                        $(this).val(macrules[idx[0]][idx[1]]);
                        layer.alert('请输入正确MAC字节格式', { icon: 5 });
                        return false;
                    }else{
                        if (idx[1]<3&&$(this).val() === '') {
                            $(this).val(macrules[idx[0]][idx[1]]);
                            layer.alert('该值不能为空', { icon: 5 });
                            return false;
                        }
                    }
                    macrules[idx[0]][idx[1]] = val;
                });
                //资产属性
                $(parent.pProtoTable + ' ul').on('change', 'li>div>.chinput', function (){
                    var chks=$(this).parent().find('.chinput');
                    if(!chks.eq(0).is(':checked')&&!chks.eq(1).is(':checked')){
                        layer.alert('资产属性不能为空', { icon: 5 });
                        $(this).prop({ checked: true });
                        return false;
                    }
                    var idx = $(this).data('idx').split('_').map(Number);
                    if(chks.eq(0).is(':checked')&&!chks.eq(1).is(':checked')){
                        prorules[idx[0]][2] = 1;
                        prorules[idx[0]][1] = '';
                        $(this).parent().parent().find('input[type=text]').val('').prop('disabled',true)
                    }else if(!chks.eq(0).is(':checked')&&chks.eq(1).is(':checked')){
                        prorules[idx[0]][2] = 2;
                        $(parent.pProtoTable + ' input[type=text]').prop('disabled',false)
                    }else{
                        prorules[idx[0]][2] = 0;
                        $(parent.pProtoTable + ' input[type=text]').prop('disabled',false)
                    }
                });
                //端口
                $(parent.pProtoTable + ' ul').on('change', 'input[type=text]', function (){
                    if(!Validation.validatePort($(this).val())){
                        layer.alert('请输入正确端口，范围：1-65535', { icon: 5 });
                        $(this).val('');
                        return false;
                    }
                    var idx = $(this).data('idx').split('_').map(Number);
                    prorules[idx[0]][idx[1]] = $(this).val();
                });
                //协议
                $(parent.pProtoTable + ' ul').on('change', 'select', function (){
                    var idx = $(this).data('idx').split('_').map(Number);
                    prorules[idx[0]][idx[1]] = $(this).val();
                });
            }
        })
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - FingerprintController.addRule() - Unable to export all events: " + err.message);
    }
};
ContentFactory.assignToPackage("tdhx.base.topo.FingerprintController", FingerprintController);