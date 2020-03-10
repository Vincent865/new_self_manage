function SwitchallController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.controller = controller;
    this.elementId = elementId;
    this.pSelectAll='#'+elementId+'_selectAll';
    this.pBtnAddSwitch = "#" + this.elementId + "_btnAddSwitch";
    this.pBtnEditDeviceType = "#" + this.elementId + "_btnDeviceType";
    this.pBtnRemove = "#" + this.elementId + "_btnRemove";
    this.pBtnSearch = "#" + this.elementId + "_btnSearch";
    this.pBtnExportList = "#" + this.elementId + "_btnExportList";
    this.pBtnImxportList = "#" + this.elementId + "_btnImportList";
    this.pBtnFile = "#" + this.elementId + "_file";
    this.pBtnImxportVendor = "#" + this.elementId + "_btnImportVendor";
    this.pBtnVendorFile = "#" + this.elementId + "_Vendorfile";
    this.pBtnExportVendor = "#" + this.elementId + "_btnExportVendor";

    this.pBtnFilter = "#" + this.elementId + "_btnFilter";
    this.pDivFilter = "#" + this.elementId + "_divFilter";
    this.pDetailCtrlBtns='#'+this.elementId+'_dialog_detailCtrlBtns button';
    this.pProtopt='#'+this.elementId+'_dialog_protopt';
    this.pSwitchdlg='#'+this.elementId+'_dialog_switch_dialog';
    this.pTxtName = "#" + this.elementId + "_txtName";
    this.pTxtIP = "#" + this.elementId + "_txtIP";
    this.pTxtType = "#" + this.elementId + "_txtType";
    this.pTxtLocal = "#" + this.elementId + "_txtLocate";

    this.pTdSwitchList = "#tdSwitchLlist";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotalLog = "#" + this.elementId + "_lblTotalLog";
    this.protocolList = Constants.AUDIT_PROTOCOL_LIST[APPCONFIG.PRODUCT];
    //自定义设备类型弹窗
    this.ptdDeviceList='#'+this.elementId+'_dialog_tdDeviceList';
    this.pBtnAddType='#'+this.elementId+'_dialog_addDeviceType';
    this.txtDevType='#'+this.elementId+'_dialog_txtDeviceType';
    var tmpList=[];
    $(this.protocolList).each(function(i,d){
        tmpList.push(d.name);
    });
    this.ptoList=tmpList;
    this.pager = null;
    this.filter = {
        page: 1,
        ip: "",
        switch_name: "",
        type: "",
        locate: ""
    };
}

SwitchallController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.SWITCH_ADD
            ],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - ReportAuditController.init() - Unable to initialize all templates: " + err.message);
    }
}

SwitchallController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SWITCH_ALL), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - ReportAuditController.initShell() - Unable to initialize: " + err.message);
    }
}

SwitchallController.prototype.initControls = function () {
    try {
        var parent = this;

        this.pViewHandle.find(this.pBtnFilter).on("click", function () {
            parent.pViewHandle.find(parent.pTxtName).val("");
            parent.pViewHandle.find(parent.pTxtIP).val("");
            parent.pViewHandle.find(parent.pTxtType).val("");
            parent.pViewHandle.find(parent.pTxtLocal).val("");
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            parent.pViewHandle.find(parent.pDivFilter).toggle();
        });

        this.pViewHandle.find(this.pBtnRemove).on("click", function () {
            parent.delRuleList();
        });

        this.pViewHandle.find(this.pBtnAddSwitch).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.addAsset();
        });

        $(parent.pSelectAll).click(function(){
            parent.checkSwitch=!parent.checkSwitch;
            $(parent.pTdSwitchList).find('input').filter('.selflag').map(function(i,d){
                if(!$(d).prop('disabled')){
                    return $(d);
                }
            }).each(function(i,d){
                $(d).prop('checked',parent.checkSwitch);
            })
        });
        this.pViewHandle.find(this.pBtnExportList).on("click", function () {
            parent.exportSwitchList();
        });
        this.pViewHandle.find(this.pBtnImxportList).on("click", function () {
            $(parent.pBtnFile).val("");
            parent.importSwitchList();
        });
        $(parent.pBtnFile).on("change",function(){
            var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
            var fileName = $.trim($(this).val()),size=$(this)[0].files[0].size/1024/1024;
            $("[name='loginuser']").val(AuthManager.getInstance().getUserName());
            if (fileName != "") {
                var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 3).toLowerCase();
                if (fieExtension != "csv") {
                    layer.alert("文件格式不对，请重新上传", { icon: 5 });
                }else if(size>10){
                    layer.alert("文件大小超过1024mb，请重新上传", { icon: 5 });
                }else{
                    var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].SWITCH_IMPORT;
                    $("#importSwitchForm").ajaxSubmit({
                        type: 'POST',
                        url: link,
                        success: function (result) {
                            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                                if(result.status==1){
                                    layer.alert("导入成功", { icon: 6 });
                                    parent.pager = null;
                                    parent.filter.page = 1;
                                    parent.selectAssets();
                                }else{
                                    layer.alert(result.msg, { icon: 5 });
                                }
                            }
                            else {
                                layer.alert("导入失败", { icon: 5 });
                            }
                        }
                    });
                }
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - SwitchallController.initControls() - Unable to initialize control: " + err.message);
    }
}

SwitchallController.prototype.load = function () {
    try {
        this.selectAssets();
    }
    catch (err) {
        console.error("ERROR - SwitchallController.load() - Unable to load: " + err.message);
    }
}

SwitchallController.prototype.delRuleList=function(){
    var parent=this;
    parent.preDelete=[];
    $(parent.pTdSwitchList).find('tbody input[type=checkbox]').filter('.selflag').each(function(i,d){
        if($(d).prop('checked')){
            parent.preDelete.push($(d).data('id'));
        }
    });
    if(parent.preDelete.length){
        var delIds=parent.preDelete.join(','),link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_SWITCH_LIST;
        layer.confirm('确定要删除么？',{icon:7,title:'注意：'}, function(index) {
            layer.close(index);
            var promise = URLManager.getInstance().ajaxCallByURL(link,"DELETE",{id:delIds});
            var loadIdx=layer.load(2,{shade:[0.4, '#fff']});
            promise.fail(function (jqXHR, textStatus, err) {
                layer.alert(err.msg, { icon: 2 });
                console.log(textStatus + " - " + err.msg);
            });
            promise.done(function(res){
                if(res.status){
                    layer.alert(res.msg, { icon: 6 });
                    layer.close(loadIdx);
                    delete parent.pager;
                    parent.filter.page=1;
                    parent.selectAssets();
                }else{
                    layer.alert(res.msg, { icon: 5 });
                    layer.close(loadIdx);
                }
            });
        });
    }else{
        layer.alert('请选择要删除的资产再试！',{icon:2});
    }
};

SwitchallController.prototype.selectAssets = function () {
    var parent = this;
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_SWITCH_LIST,
            jointLink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].IS_INTO_IPMAC_RULE;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"GET",parent.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='6'>暂无数据</td></tr>";
            parent.pViewHandle.find(parent.pTdSwitchList+">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.data) != "undefined") {
                if (result.data.length > 0) {
                    for (var i = 0; i < result.data.length; i++) {
                        html += "<tr>";
                        html += "<td>"+"<input type='checkbox' class='chinput selflag' data-id='"+result.data[i].id+"' id='"+result.data[i].id+"'><label for='"+result.data[i].id+"'></label></td>";
                        html += "<td title='" + result.data[i].switch_name + "'>" + result.data[i].switch_name + "</td>";
                        html += "<td title='" + result.data[i].ip + "'>" + result.data[i].ip + "</td>";
                        html += "<td title='" + result.data[i].type + "'>" + result.data[i].type + "</td>";
                        html += "<td title='" + result.data[i].locate + "'>" + result.data[i].locate + "</td>";
                        html += "<td>" +
                            "<button style='margin-right:5px;' class='btn btn-default btn-color-details btn-xs viewdetail' data-name='"+  result.data[i].switch_name +"'><i class=\"fa fa-newspaper-o\"></i>查看详情</button>" +
                            "<button style='margin-right:5px;' class='btn btn-color-details btn-default btn-xs edititem' data-info='"+  JSON.stringify(result.data[i]) +"'></i>编辑</button>";
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
            if (typeof (result.total) != "undefined") {
                parent.controller.pViewHandle.find(parent.controller.pTotalOperationLog).text(result.total);
            }
            parent.pViewHandle.find(parent.pTdSwitchList+">tbody").html(html);
            layer.close(loadIndex);
            $(parent.pTdSwitchList).find("button.edititem").on("click", function (event) {
                parent.addAsset($(this).data("info"));
            });
            $(parent.pTdSwitchList).find("button.viewdetail").on("click", function (event) {
                var name=$(this).data("name");
                var dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SWITCH_ADD), {
                    elementId: parent.elementId + "_dialog"
                });
                var tmplay = layer.open({
                    type: 1,
                    title: "详情",
                    area: ["600px",'520px'],
                    shade: [0.5, '#393D49'],
                    content: dialogTemplate,
                    success: function (layero, index) {
                        $('.switch_dialog_edit').hide();
                        $('.switch_dialog_info').show();
                        parent.switchinfo(name);
                    }
                });

            });
            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController(parent.pViewHandle.find(parent.pPagerContent), parent.elementId, 10, result.num, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectAssets();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='5'>暂无数据</td></tr>";
        this.pViewHandle.find(this.pTdSwitchList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - SwitchallController.selectAssets() - Unable to get assets: " + err.message);
    }
}

SwitchallController.prototype.switchinfo = function (name) {
    try {
        var parent=this;
        var html = "";
        var link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_SWITCH_INFO_LIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST",{name:name});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='3'>暂无数据</td></tr>";
            $('.switch_dialog_info').find("tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>"+(i+1)+"</td>";
                        html += "<td>" + result.rows[i][0] + "</td>";
                        html += "<td>" + result.rows[i][1] + "</td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='3'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='3'>暂无数据</td></tr>";
            }
            $('.switch_dialog_info').find("tbody").html(html);
            $('.switch_dialog_info').find("button").on("click", function (event) {
                parent.switchinfo(name);
            });
        });
    }
    catch (err) {
        console.error("ERROR - SwitchallController.addAsset() - Unable to load: " + err.message);
    }
}

SwitchallController.prototype.addAsset = function (edit) {
    try {
        var parent=this,dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SWITCH_ADD), {
            elementId: parent.elementId + "_dialog"
        });
        var height = $(window).height() - parent.pViewHandle.offset().top - $(window).height()/10  - document.body.scrollTop + "px";
        var link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_SWITCH_LIST,promise;
        var tmplay = layer.open({
            type: 1,
            title: edit ? "编辑" : '新增',
            area: ["600px",height],
            //offset: ["82px", "200px"],
            shade: [0.5, '#393D49'],
            content: dialogTemplate,
            success: function (layero, index) {
                $('.switch_dialog_edit').show();
                $('.switch_dialog_info').hide();
                var btns = $(parent.pSwitchdlg).next('.button-box').find('.btn'),
                    commonIpts=$(parent.pSwitchdlg).find('.commonul input[type=text]'),
                    snmpIpts=$(parent.pSwitchdlg).find('.snmpul input[type=text]'),
                    snmpsel=$(parent.pSwitchdlg).find('.snmpul select'),
                    snmpchks=$(parent.pSwitchdlg).find('.snmpul [name=version]'),snmpchksNum=1,
                    sshIpts=$(parent.pSwitchdlg).find('.sshul input[type=text]'),
                    tips=$(parent.pSwitchdlg+' ul').next('span');
                $(parent.pSwitchdlg).find('.snmpul li.v3').hide();
                if(edit){
                    commonIpts.eq(0).val(edit.switch_name);
                    commonIpts.eq(1).val(edit.ip);
                    commonIpts.eq(2).val(edit.type);
                    commonIpts.eq(3).val(edit.locate);
                    $("[name=version][value='" + edit.snmp_version + "']").prop("checked",true);
                    snmpIpts.eq(0).val(edit.group_name);
                    snmpsel.eq(0).val(edit.security_level);
                    snmpIpts.eq(1).val(edit.security_name);
                    snmpsel.eq(1).val(edit.auth_mode);
                    snmpIpts.eq(2).val(edit.auth_pwd);
                    snmpsel.eq(2).val(edit.priv_mode);
                    snmpIpts.eq(3).val(edit.priv_pwd);
                    sshIpts.eq(0).val(edit.ssh_name);
                    sshIpts.eq(1).val(edit.ssh_pwd);
                    if(edit.snmp_version==3){
                        $(parent.pSwitchdlg).find('.snmpul li.v3').show();
                        $(parent.pSwitchdlg).find('.snmpul li.v1').hide();
                    }else{
                        $(parent.pSwitchdlg).find('.snmpul li.v3').hide();
                        $(parent.pSwitchdlg).find('.snmpul li.v1').show();
                    }
                    snmpchksNum=edit.snmp_version;
                    if(edit.security_level=='noAuthNoPriv'){
                        snmpsel.eq(1).prop('disabled',true);
                        snmpsel.eq(2).prop('disabled',true);
                    }else if(edit.security_level=='authNoPriv'){
                        snmpsel.eq(1).prop('disabled',false);
                        snmpsel.eq(2).prop('disabled',true);
                    }else{
                        snmpsel.eq(1).prop('disabled',false);
                        snmpsel.eq(2).prop('disabled',false);
                    }
                }
                snmpchks.click(function(){
                    if($(this).val()==3){
                        $(parent.pSwitchdlg).find('.snmpul li.v3').show();
                        $(parent.pSwitchdlg).find('.snmpul li.v1').hide();
                    }else{
                        $(parent.pSwitchdlg).find('.snmpul li.v3').hide();
                        $(parent.pSwitchdlg).find('.snmpul li.v1').show();
                    }
                    snmpchksNum=$(this).val();
                });
                snmpsel.eq(0).change(function(){
                    if($(this).val()=='noAuthNoPriv'){
                        snmpsel.eq(1).prop('disabled',true);
                        snmpsel.eq(2).prop('disabled',true);
                    }else if($(this).val()=='authNoPriv'){
                        snmpsel.eq(1).prop('disabled',false);
                        snmpsel.eq(2).prop('disabled',true);
                    }else{
                        snmpsel.eq(1).prop('disabled',false);
                        snmpsel.eq(2).prop('disabled',false);
                    }
                });

                commonIpts.eq(0).change(function(){
                    if(!/^\w{1,30}$/.test($(this).val())){
                        tips.eq(0).text('交换机名称请输入数字、字母、下划线，长度1-30位').show();
                    }else{
                        tips.eq(0).hide();
                    }
                });
                commonIpts.eq(1).change(function(){
                    if(Validation.validateIP($(this).val())||Validation.validateIPV6($(this).val())){
                        tips.eq(0).hide();
                    }else{
                        tips.eq(0).text('ip地址格式不正确').show();
                    }
                });
                snmpIpts.eq(0).change(function(){
                    if(!/^\w{1,32}$/.test($(this).val())){
                        tips.eq(1).text('团体名请输入数字、字母、下划线，长度1-32位').show();
                    }else{
                        tips.eq(1).hide();
                    }
                });
                snmpIpts.eq(1).change(function(){
                    if(!/^\w{1,32}$/.test($(this).val())){
                        tips.eq(1).text('安全用户名请输入数字、字母、下划线，长度1-32位').show();
                    }else{
                        tips.eq(1).hide();
                    }
                });
                snmpIpts.eq(2).change(function(){
                    if(!/^\w{1,64}$/.test($(this).val())){
                        tips.eq(1).text('认证密码请输入数字、字母、下划线，长度1-64位').show();
                    }else{
                        tips.eq(1).hide();
                    }
                });
                snmpIpts.eq(3).change(function(){
                    if(!/^\w{1,64}$/.test($(this).val())){
                        tips.eq(1).text('加密密码请输入数字、字母、下划线，长度1-64位').show();
                    }else{
                        tips.eq(1).hide();
                    }
                });
                btns.eq(0).click(function(){
                    tips.hide();
                    if($.trim(commonIpts.eq(0).val())&&/^\w{1,30}$/.test($.trim(commonIpts.eq(0).val()))){
                        if(!(Validation.validateIP(commonIpts.eq(1).val())||Validation.validateIPV6(commonIpts.eq(1).val()))){
                            tips.eq(0).text('请确认IP地址填写正确再试').show();
                            return false;
                        }
                        if(commonIpts.eq(3).val()==''){
                            tips.eq(0).text('位置不能为空').show();
                            return false;
                        }
                        var issnmp=false;
                        if(sshIpts.eq(0).val()==''&&sshIpts.eq(1).val()==''){
                            issnmp=true;  //ssh为空时 必须配置snmp;
                        }
                        if(snmpchks.find(':checked').val()!=3&&issnmp&&!/^\w{1,32}$/.test(snmpIpts.eq(0).val())){
                            tips.eq(1).text('团体名请输入数字、字母、下划线，长度1-32位').show();
                            return false;
                        }
                        if(snmpchksNum==3&&issnmp&&!/^\w{1,32}$/.test(snmpIpts.eq(1).val())){
                            tips.eq(1).text('安全用户名请输入数字、字母、下划线，长度1-32位').show();
                            return false;
                        }
                        if(snmpchksNum==3&&issnmp&&!/^\w{1,64}$/.test(snmpIpts.eq(2).val())){
                            tips.eq(1).text('认证密码请输入数字、字母、下划线，长度1-64位').show();
                            return false;
                        }
                        if(snmpchksNum==3&&issnmp&&!/^\w{1,64}$/.test(snmpIpts.eq(3).val())){
                            tips.eq(1).text('加密密码请输入数字、字母、下划线，长度1-64位').show();
                            return false;
                        }
                        if((sshIpts.eq(0).val()==''&&sshIpts.eq(1).val()!='') || (sshIpts.eq(0).val()!=''&&sshIpts.eq(1).val()=='')){
                            tips.eq(2).text('ssh配置必填项不能为空').show();
                            return false;
                        }
                        promise=URLManager.getInstance().ajaxCallByURL(link,edit?'PUT':'POST',{
                            id:edit?edit.id:'',
                            switch_name:commonIpts.eq(0).val(),
                            ip:commonIpts.eq(1).val(),
                            type:commonIpts.eq(2).val(),
                            locate:commonIpts.eq(3).val(),
                            snmp_version:parseInt(snmpchksNum),
                            group_name:snmpIpts.eq(0).val(),
                            security_level:snmpsel.eq(0).val(),
                            security_name:snmpIpts.eq(1).val(),
                            auth_mode:snmpsel.eq(1).val(),
                            auth_pwd:snmpIpts.eq(2).val(),
                            priv_mode:snmpsel.eq(2).val(),
                            priv_pwd:snmpIpts.eq(3).val(),
                            ssh_name:sshIpts.eq(0).val(),
                            ssh_pwd:sshIpts.eq(1).val()
                        });
                        var loadIdx=layer.load(2,{shade:[0.4, '#fff']});
                        promise.done(function(result) {
                            if (result.status > 0) {
                                layer.close(loadIdx);
                                layer.alert(result.msg, {icon: 6});
                                if(!edit){
                                    delete parent.pager;
                                    parent.filter.page=1;
                                }
                                layer.close(tmplay);
                                parent.selectAssets();
                            } else {
                                layer.alert( result.msg, {icon: 5});
                                layer.close(loadIdx);
                            }
                        });
                        promise.fail(function (jqXHR, textStatus, err) {
                            console.log(textStatus + '-' + err.msg);
                            layer.alert(err.msg, {icon: 5});
                            layer.close(loadIdx);
                        });
                    }else{
                        tips.eq(0).text('请确认设备名正确再试').show();
                    }
                });
                btns.eq(1).click(function () {
                    layer.close(tmplay);
                });
            }});
    }
    catch (err) {
        console.error("ERROR - SwitchallController.addAsset() - Unable to load: " + err.message);
    }
}

SwitchallController.prototype.exportSwitchList = function () {
    var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].SWITCH_EXPORT;
    window.open(link + "?action=1&loginuser=" + AuthManager.getInstance().getUserName());
}

SwitchallController.prototype.importSwitchList = function () {
    try {
        $(this.pBtnFile).click();
    }
    catch (err) {
        console.error("ERROR - SwitchallController.importTopoAsset() - Unable to import all importTopoAsset: " + err.message);
    }
};

SwitchallController.prototype.formatFilter = function () {
    try {
        this.filter.name = this.pViewHandle.find(this.pTxtName).val();
        this.filter.ip = $.trim(this.pViewHandle.find(this.pTxtIP).val());
        this.filter.type = $.trim(this.pViewHandle.find(this.pTxtType).val());
        this.filter.locate = $.trim(this.pViewHandle.find(this.pTxtLocal).val());
        
    }
    catch (err) {
        console.error("ERROR - SwitchallController.formatFilter() - Unable to get filter: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.topo.SwitchallController", SwitchallController);