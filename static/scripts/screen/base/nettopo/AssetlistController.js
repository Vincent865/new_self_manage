/**
 * Created by 刘写辉 on 2018/11/12.
 */
function AssetlistController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.controller = controller;
    this.elementId = elementId;
    this.pSelectAll='#'+elementId+'_selectAll';
    this.pBtnAddDevice = "#" + this.elementId + "_btnAddDevice";
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
    this.pProtodlg='#'+this.elementId+'_dialog_proto_dialog01';
    this.pTxtDeviceName = "#" + this.elementId + "_txtDeviceName";
    this.pTxtIP = "#" + this.elementId + "_txtIP";
    this.pTxtMAC = "#" + this.elementId + "_txtMAC";
    this.pTxtVenderInfo = "#" + this.elementId + "_txtVenderInfo";
    this.pTxtDeviceType = "#" + this.elementId + "_txtDeviceType";
    this.pTxtIsTopo = "#" + this.elementId + "_txtIsTopo";
    this.pTxtAuth = "#" + this.elementId + "_txtAuthStatus";

    this.pTdAssetList = "#" + this.elementId + "_tdAssetList";
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
        oper: "",
        oper_result: "",
        user: "",
        starttime: "",
        endtime: ""
    };
}

AssetlistController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.TOPO_DEVICE_EDIT,
                Constants.TEMPLATES.TOPO_ASSET_ADD],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - ReportAuditController.init() - Unable to initialize all templates: " + err.message);
    }
}

AssetlistController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.TOPO_ASSETLIST), {
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

AssetlistController.prototype.initControls = function () {
    try {
        var parent = this;

        this.pViewHandle.find(this.pBtnFilter).on("click", function () {
            parent.pViewHandle.find(parent.pTxtIP).val("");
            parent.pViewHandle.find(parent.pTxtMAC).val("");
            parent.pViewHandle.find(parent.pTxtDeviceName).val("");
            parent.pViewHandle.find(parent.pTxtDeviceType).val("");
            parent.pViewHandle.find(parent.pTxtIsTopo).val("");
            parent.pViewHandle.find(parent.pTxtAuth).val("");
            parent.pViewHandle.find(parent.pTxtVenderInfo).val("");
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            parent.pViewHandle.find(parent.pDivFilter).toggle();
        });

        this.pViewHandle.find(this.pBtnRemove).on("click", function () {
            parent.delRuleList();
        });

        this.pViewHandle.find(this.pBtnAddDevice).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.addAsset();
        });
        this.pViewHandle.find(this.pBtnEditDeviceType).on("click", function () {
            parent.editDeviceType();
        });

        this.pViewHandle.find(this.pBtnSearch).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectAssets();
        });

        $(parent.pSelectAll).click(function(){
            parent.checkSwitch=!parent.checkSwitch;

            $(parent.pTdAssetList).find('input').filter('.selflag').map(function(i,d){
                if(!$(d).prop('disabled')){
                    return $(d);
                }
            }).each(function(i,d){
                $(d).prop('checked',parent.checkSwitch);
            })
        });
        this.pViewHandle.find(this.pBtnExportList).on("click", function () {
            parent.exportTopoAsset();
        });
        this.pViewHandle.find(this.pBtnImxportList).on("click", function () {
            $(parent.pBtnFile).val("");
            parent.importTopoAsset();
        });
        $(parent.pBtnFile).on("change",function(){
            var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
            var fileName = $.trim($(this).val());
            $("[name='loginuser']").val(AuthManager.getInstance().getUserName());
            if (fileName != "") {
                var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 3).toLowerCase();
                if (fieExtension != "csv") {
                    layer.alert("文件格式不对", { icon: 5 });
                }else{
                    var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].TOPO_ALL_IMPORT;
                    $("#importListForm").ajaxSubmit({
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
        this.pViewHandle.find(this.pBtnExportVendor).on("click", function () {
            parent.exportVendor();
        });
        this.pViewHandle.find(this.pBtnImxportVendor).on("click", function () {
            $(parent.pBtnVendorFile).val("");
            parent.importCategory();
        });
        $(parent.pBtnVendorFile).on("change",function(){
            var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
            var fileName = $.trim($(this).val()),size=$(this)[0].files[0].size/1024;
            $("[name='loginuser']").val(AuthManager.getInstance().getUserName());
            if (fileName != "") {
                var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 4).toLowerCase();
                if (fieExtension != "json") {
                    layer.alert("文件格式不对，请重新上传", { icon: 5 });
                }else if(size>1024){
                    layer.alert("文件大小超过1024kb，请重新上传", { icon: 5 });
                }else{
                    var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].TOPO_VENDOR_IMPORT;
                    $("#importVendorForm").ajaxSubmit({
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
        })
    }
    catch (err) {
        console.error("ERROR - OperationLogController.initControls() - Unable to initialize control: " + err.message);
    }
}

AssetlistController.prototype.load = function () {
    try {
        this.getDeviceType();
        this.selectAssets();
    }
    catch (err) {
        console.error("ERROR - OperationLogController.load() - Unable to load: " + err.message);
    }
}

AssetlistController.prototype.delRuleList=function(){
    var parent=this;
    parent.preDelete=[];
    $(parent.pTdAssetList).find('tbody input[type=checkbox]').filter('.selflag').each(function(i,d){
        if($(d).prop('checked')){
            parent.preDelete.push($(d).data('id'));
        }
    });
    if(parent.preDelete.length){
        var delIds=parent.preDelete.join(','),link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].OPER_ASSET_DEVICE;
        layer.confirm('确定要删除么？',{icon:7,title:'注意：'}, function(index) {
            layer.close(index);
            var promise = URLManager.getInstance().ajaxCallByURL(link,"DELETE",{ids:delIds});
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
        layer.alert('请勾选资产后再试！',{icon:2});
    }

};

AssetlistController.prototype.addAsset = function (edit) {
    try {
        var parent=this,dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.TOPO_ASSET_ADD), {
            elementId: parent.elementId + "_dialog"
        });
        var width = parent.pViewHandle.width() - 10 + "px";
        var link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].OPER_ASSET_DEVICE,promise;
        var height = $(window).height() - parent.pViewHandle.offset().top - $(window).height()/10 + "px";
        var tmplay = layer.open({
            type: 1,
            title: edit ? "编辑" : '新增',
            area: ["550px",edit?'560px':'520px'],
            //offset: ["82px", "200px"],
            shade: [0.5, '#393D49'],
            content: dialogTemplate,
            success: function (layero, index) {
                var btns = $(parent.pDetailCtrlBtns),
                    ipts=$(parent.pProtodlg).find('input.form-control'),
                    tips=$(parent.pProtodlg+'>span'),data=[],protoarr=[],itemProto,
                    vendersection=$(parent.pProtodlg+' li').eq(4),
                    autoflag=$(parent.pProtodlg+' li').eq(4).find('[name=autoflag]'),
                    authsection=$(parent.pProtodlg+' li').eq(8),
                    devtype=$(parent.pProtodlg+' select.form-control').eq(1),
                    authStatus=$(parent.pProtodlg+' select.form-control').eq(2);
                $(parent.pProtodlg+' li').eq(3).hide();
                for(var i=0;i<parent.devTypeList.length;i++){
                    devtype.append("<option value="+parent.devTypeList[i].id+">"+parent.devTypeList[i].name+"</option>")
                }
                if(edit){
                    ipts.eq(0).val(edit.name);
                    ipts.eq(1).val(edit.ip).prop("disabled",true);
                    ipts.eq(2).val(edit.mac).prop("disabled",true);
                    ipts.eq(1).css({backgroundColor:'#eee'});
                    ipts.eq(2).css({backgroundColor:'#eee'});
                    ipts.eq(3).val(edit.vender);
                    ipts.eq(4).val(edit.mode);
                    ipts.eq(5).val(edit.desc);
                    devtype.val(edit.type);
                    $("[name=autoflag][value='" + edit.autoflag + "']").prop("checked",true);
                    if(edit.autoflag==1){
                        $(parent.pProtodlg+' li').find('.isauto').prop('disabled',true);
                    }
                    authStatus.css({backgroundColor:edit.unknown?'#fff':'#eee'}).prop({disabled:edit.unknown?false:true}).val(edit.unknown);
                    itemProto=isNaN(edit.proto)?edit.proto.split(','):'';
                    $(itemProto).each(function(i,d){
                        $(parent.ptoList).each(function(ii,dd){
                            if(d==dd){
                                data.push(ii);
                            }
                        })
                    })
                }
                $(parent.ptoList).each(function(i,d){
                    var idx=null;
                    $(data).each(function(ii,dd){
                        if(i==dd){
                            idx=i;
                        }
                    });
                    if(idx){
                        protoarr.push({label:d,value: i,selected:true});
                    }else{
                        protoarr.push({label: d,value:i});
                    }
                });
                $(parent.pProtopt).multiselect({includeSelectAllOption: true,allSelectedText:'所有协议',selectAllText:"全选",buttonWidth:'240px',nonSelectedText:'未选择',maxHeight:'190'});
                $(parent.pProtopt).multiselect('dataprovider',protoarr);
                $(parent.pProtopt).multiselect('refresh');
                $(parent.pProtodlg+' li').find('[name=autoflag]').change(function(){
                    if($(this).val()==0){
                        $(parent.pProtodlg+' li').find('.isauto').prop('disabled',false);
                    }else{
                        $(parent.pProtodlg+' li').find('.isauto').prop('disabled',true);
                    }
                });
                ipts.eq(1).change(function(){
                    if((Validation.validateIP($(this).val())||Validation.validateIPV6($(this).val()))&&$(this).val()){
                        tips.hide();
                    }else{
                        tips.text('ip地址格式不正确').show();
                    }
                });
                ipts.eq(2).change(function(){
                    if(!Validation.validateMAC($(this).val())&&$(this).val()){
                        tips.text('MAC地址格式不正确').show();
                    }else{
                        tips.hide();
                    }
                });
                //!edit?$(vendersection).hide():'';
                !edit?$(authsection).hide():'';
                btns.eq(0).click(function(){
                    if($.trim(ipts.eq(0).val())&&/^(?=.*?[\u4e00-\u9fa5\w])[\u4e00-\u9fa5\w]+/.test($.trim(ipts.eq(0).val()))){
                        if(!(Validation.validateIP($(ipts).eq(1).val())||Validation.validateIPV6($(ipts).eq(1).val()))&&$(ipts).eq(1).val()){
                            tips.text('请确认IP地址填写正确再试').show();
                            return false;
                        }
                        if(!Validation.validateMAC($(ipts).eq(2).val())||!$(ipts).eq(2).val()){
                            tips.text('请确认MAC地址填写正确再试').show();
                            return false;
                        }
                        promise=URLManager.getInstance().ajaxCallByURL(link,edit?'PUT':'POST',{
                            id:edit?edit.id:'',
                            name:ipts.eq(0).val(),
                            ip:ipts.eq(1).val(),
                            mac:ipts.eq(2).val(),
                            //proto:$(parent.pProtopt).val().join(','),
                            vender:ipts.eq(3).val(),
                            type:Number(devtype.val()),
                            desc:ipts.eq(5).val(),
                            mode:ipts.eq(4).val(),
                            unknown:Number(authStatus.val()),
                            auto_flag:parseInt($('[name=autoflag]:checked').val())
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
                        tips.text('请确认设备名正确再试').show();
                    }
                });
                btns.eq(1).click(function () {
                    layer.close(tmplay);
                });
            }});
    }
    catch (err) {
        console.error("ERROR - OperationLogController.load() - Unable to load: " + err.message);
    }
}

AssetlistController.prototype.selectAssets = function () {
    var parent = this;
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_ASSET_LIST,
            jointLink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].IS_INTO_IPMAC_RULE;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST",this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='10'>暂无数据</td></tr>";
            parent.pViewHandle.find(parent.pTdAssetList+">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>"+"<input type='checkbox' class='chinput selflag "+ (result.rows[i][6]?"disipt' disabled ":"' ") + "data-idx='"+result.rows[i][1]+"' data-id=\""+result.rows[i][0]+"\" id=\""+result.rows[i][0]+"\" /><label for=\""+result.rows[i][0]+"\"></label></td>";
                        html += "<td title='" + result.rows[i][1] + "'>" + result.rows[i][1] + "</td>";
                        html += "<td title='" + result.rows[i][2] + "'>" + result.rows[i][2] + "</td>";
                        html += "<td title='" + result.rows[i][3] + "'>" + result.rows[i][3] + "</td>";
                        html += "<td title='" + (result.rows[i][7]?result.rows[i][7]:'') + "'>" + (result.rows[i][7]?result.rows[i][7]:'') + "</td>";
                        html += "<td title='"+result.rows[i][13]+"'>" + result.rows[i][13] + "</td>";
                        html += "<td>" + (result.rows[i][10]?result.rows[i][10]:'') + "</td>";
                        //html += "<td>" + result.rows[i][4] + "</td>";
                        html += "<td style='width:150px'>" + (result.rows[i][6]?'已加入':'未加入') + "</td>";
                        html += "<td style='width:15%'>" + (result.rows[i][9]?'非法接入':'正常接入') + "</td>";
                        html += "<td style='width:280px' >" +
                            "<button style='margin-right:5px;' class='btn btn-default btn-color-details btn-xs viewdetail' data-ip='"+  result.rows[i][2] +"' data-desc='"+ (result.rows[i][5]?result.rows[i][5]:'') +"' data-proto='"+ result.rows[i][4] +"' data-mac='"+ result.rows[i][3] +"' data-vender='"+ result.rows[i][7] +"' data-type='"+ result.rows[i][8]+"' data-typename='"+ result.rows[i][13] +"' data-auth='"+ result.rows[i][9] +"' data-mode='"+ result.rows[i][10] + "' data-name='"+result.rows[i][1]+"' data-id='" + result.rows[i][0] + "'><i class=\"fa fa-newspaper-o\"></i>查看详情</button>" +
                            "<button style='margin-right:5px;' class='btn btn-color-details btn-default btn-xs edititem' data-ip='"+  result.rows[i][2] +"' data-desc='"+ (result.rows[i][5]?result.rows[i][5]:'') +"' data-auth='"+ result.rows[i][9]+ "' data-mode='"+ result.rows[i][10] +"' data-proto='"+ result.rows[i][4] +"' data-mac='"+ result.rows[i][3] +"' data-vender='"+ result.rows[i][7] +"' data-type='"+ result.rows[i][8] + "' data-name='"+result.rows[i][1]+"' data-id='" + result.rows[i][0] + "' data-autoflag='"+ result.rows[i][11] +"'><i class=\"fa fa-edit\"></i>编辑</button>" +
                            "<button style='"+(result.rows[i][12]?"color:#888;border-color:#888;'":"'")+" class='btn btn-default btn-color-details btn-xs intorule' data-ip='"+  result.rows[i][2] +"' data-applied='"+ result.rows[i][12] +"' data-mac='"+ result.rows[i][3] +(result.rows[i][12]?"' disabled":"'")+"><i class='fa fa-upload'></i>加入IP/MAC</button></td>";
                        html += "</tr>";
                        //<button style='margin-right:5px;' data-id='" +  result.rows[i][0] + "' data-isput='" +  result.rows[i][6] + "' "+(result.rows[i][6]?"disabled":"")+" class=\"btn btn-default btn-xs btn-color-details puttopo\"><i class=\"fa fa-sitemap\"></i>"+(result.rows[i][6]?'已加入':'加入拓扑')+"</button>
                    }
                }
                else {
                    html += "<tr><td colspan='10'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='10'>暂无数据</td></tr>";
            }
            if (typeof (result.total) != "undefined") {
                parent.controller.pViewHandle.find(parent.controller.pTotalOperationLog).text(result.total);
            }
            parent.pViewHandle.find(parent.pTdAssetList+">tbody").html(html);
            layer.close(loadIndex);

            $(parent.pTdAssetList).find("button.edititem").on("click", function (event) {
                var params={};params.id = $(this).data("id");params.name=$(this).data('name');params.unknown=$(this).data('auth');params.mode=$(this).data('mode');params.proto=$(this).data('proto');params.type=$(this).data('type');params.ip=$(this).data('ip');params.mac=$(this).data('mac');params.vender=$(this).data('vender');params.desc=$(this).data('desc');
                params.autoflag = $(this).data("autoflag");
                parent.addAsset(params);
            });

            $(parent.pTdAssetList).find("button.intorule").on("click", function (event) {
                var params = {}; params.ip = $(this).data('ip'); params.applied = $(this).data('applied'); params.mac = $(this).data('mac');
                var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].IS_INTO_IPMAC_RULE;
                var loadIndex = layer.load(2);
                var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", params);
                promise.fail(function (jqXHR, textStatus, err) {
                    console.log(textStatus + " - " + err.message);
                    layer.alert('加入IPMAC规则失败',{icon:5});
                    layer.close(loadIndex);
                });
                promise.done(function (result) {
                    if (result.status) {                        
                        parent.selectAssets();
                        layer.alert('加入IPMAC规则成功',{icon:6});
                    }else{
                        layer.alert('加入IPMAC规则失败',{icon:5});
                    }
                });
            });

            $(parent.pTdAssetList).find("button.viewdetail").on("click", function (event) {
                var params={};params.value=$(this).data('name');params.device_info={desc:$(this).data('desc'),dev_type:$(this).data('type'),type_name:$(this).data('typename'),ip_addr:$(this).data('ip'),mac_addr:$(this).data('mac'),vender_info:$(this).data('vender'),unknown:$(this).data('auth'),mode:$(this).data('mode')};
                var topoview=new tdhx.base.topo.TopographController(parent.controller, parent.pViewHandle, parent.elementId).graphDetail(params);
                //topoview.graphDetail(params);
            });
            $(parent.pTdAssetList).find("button.puttopo").on("click", function (event) {
                var loadIdx1=layer.load(2,{shade:[0.4, '#fff']}),id=Number($(this).data('id')),
                subpromise=URLManager.getInstance().ajaxCallByURL(jointLink,'POST',{is_topo:1,id:id});
                subpromise.done(function (result) {
                    if (result.status > 0) {
                        layer.close(loadIdx1);
                        parent.selectAssets();
                        layer.alert(result.msg, {icon: 6});
                    }else{
                        layer.close(loadIdx1);
                        layer.alert(result.msg, {icon: 5});
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
        this.pViewHandle.find(this.pTdAssetList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - OperationLogController.selectAssets() - Unable to get assets: " + err.message);
    }
}

AssetlistController.prototype.exportTopoAsset = function () {
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].TOPO_ALL_EXPORT;
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
        console.error("ERROR - AssetlistController.exportTopoAsset() - Unable to export all exportTopoAsset: " + err.message);
    }
}

AssetlistController.prototype.importTopoAsset = function () {
    try {
        $(this.pBtnFile).click();
    }
    catch (err) {
        console.error("ERROR - AssetlistController.importTopoAsset() - Unable to import all importTopoAsset: " + err.message);
    }
};

AssetlistController.prototype.exportVendor = function () {
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].TOPO_VENDOR_EXPORT;
        window.open(link + "?loginuser=" + AuthManager.getInstance().getUserName());
    }
    catch (err) {
        console.error("ERROR - AssetlistController.exportVendor() - Unable to export all exportVendor: " + err.message);
    }
}
AssetlistController.prototype.importCategory = function () {
    try {
        $(this.pBtnVendorFile).click();
    }
    catch (err) {
        console.error("ERROR - AssetlistController.importCategory() - Unable to import all Category_Info: " + err.message);
    }
}

AssetlistController.prototype.formatExecutetatus = function (status) {
    try {
        switch (status) {
            case "1": return "失败";
            case "0": return "成功";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - OperationLogController.formatReadStatus() - Unable to format Executetatus: " + err.message);
    }
}

AssetlistController.prototype.num2type = function (num) {
    switch(num){
        case 0:return '未知';
        case 1:return 'PC';
        case 2:return '工程师站PC';
        case 3:return '操作员PC';
        case 4:return 'PLC';
        case 5:return 'RTU';
        case 6:return 'HMI';
        case 7:return '网络设备';
    }
}

AssetlistController.prototype.formatFilter = function () {
    try {
        this.filter.ip = $.trim(this.pViewHandle.find(this.pTxtIP).val());
        this.filter.mac = $.trim(this.pViewHandle.find(this.pTxtMAC).val());
        this.filter.name = this.pViewHandle.find(this.pTxtDeviceName).val();
        this.filter.type = $.trim(this.pViewHandle.find(this.pTxtDeviceType).val());
        this.filter.is_topo = $.trim(this.pViewHandle.find(this.pTxtIsTopo).val());
        this.filter.unknown = $.trim(this.pViewHandle.find(this.pTxtAuth).val());
        this.filter.vender = $.trim(this.pViewHandle.find(this.pTxtVenderInfo).val());
    }
    catch (err) {
        console.error("ERROR - OperationLogController.formatFilter() - Unable to get filter: " + err.message);
    }
}

AssetlistController.prototype.getDeviceType = function () {
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
            $(parent.pTxtDeviceType).empty();
            $(parent.pTxtDeviceType).append("<option value=''>全部</option>");
            for(var i=0;i<result.data.length;i++){
                $(parent.pTxtDeviceType).append("<option value="+result.data[i].id+">"+result.data[i].name+"</option>")
            }
        }else{
            layer.alert('获取设备类型失败',{icon:5});
        }
    });
}

AssetlistController.prototype.editDeviceType = function () {
    try {
        var parent=this,dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.TOPO_DEVICE_EDIT), {
            elementId: parent.elementId + "_dialog"
        });
        var loadIndex = layer.load(2);
        var width = parent.pViewHandle.width() - 10 + "px";
        var height = $(window).height() - parent.pViewHandle.offset().top - $(window).height()/10 + "px";
        var tmplay = layer.open({
            type: 1,
            title: "自定义设备类型",
            area: ["600px",'520px'],
            //offset: ["82px", "200px"],
            shade: [0.5, '#393D49'],
            content: dialogTemplate,
            success: function (layero, index) {
                parent.selectDeviceType();
                $(".btn-danger").click(function(){
                    layer.close(tmplay);
                });
                $(parent.pBtnAddType).click(function(){
                    var devType=$(parent.txtDevType).val();
                    if (devType.length>64) {
                        layer.alert("设备类型不能超过64字节", { icon: 5 });
                        return false;
                    }
                    if (!/^[\u4e00-\u9fa5a-zA-Z0-9()\-_]+$/.test(devType)) {
                        layer.alert("请输入正确有效的设备类型", { icon: 5 });
                        return false;
                    }
                    var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_TYPE;
                    var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {device_name: devType});
                    promise.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                        layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                        layer.close(loadIndex);
                    });
                    promise.done(function (result) {
                        if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                            switch (result.status) {
                                case 1:
                                    parent.selectDeviceType();
                                    layer.alert("添加设备类型成功", { icon: 6 });
                                    parent.getDeviceType();
                                    break;
                                default: layer.alert(result.msg, { icon: 5 }); break;
                            }
                        }
                        else {
                            layer.alert("添加设备类型失败", { icon: 5 });
                        }
                        layer.close(loadIndex);
                    });
                });
            }});
    }
    catch (err) {
        console.error("ERROR - OperationLogController.load() - Unable to load: " + err.message);
    }
}
AssetlistController.prototype.selectDeviceType = function () {
    var parent=this;
    var html = "";
    var loadIndex = layer.load(2);
    var link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_TYPE,promise;
    promise=URLManager.getInstance().ajaxCallByURL(link,'GET');
    promise.fail(function (jqXHR, textStatus, err) {
        console.log(textStatus + " - " + err.message);
        html += "<tr><td colspan='3'>暂无数据</td></tr>";
        $(parent.ptdDeviceList+">tbody").html(html);
        layer.close(loadIndex);
    });
    promise.done(function (result) {
        if (typeof (result) != "undefined" && typeof (result.data) != "undefined") {
            if (result.data.length > 0) {
                for (var i = 0; i < result.data.length; i++) {
                    html += "<tr>";
                    html += "<td>" + (i+1) + "</td>";
                    html += "<td class='td-w-300 hide_long' title='" + result.data[i].name + "'>" + result.data[i].name + "</td>";
                    html += "<td><button style='margin-right:5px;"+(result.data[i].pre_define==1?"display:none;":"")+"' class='btn btn-default btn-color-details btn-xs' data-id='" +result.data[i].id+ "'><i class='fa fa-trash-o'></i>删除</button></td>";
                    html += "</tr>";
                }
            }else {
                html += "<tr><td colspan='3'>暂无数据</td></tr>";
            }
        }else {
            html += "<tr><td colspan='3'>暂无数据</td></tr>";
        }
        $(parent.ptdDeviceList+">tbody").html(html);
        $(parent.ptdDeviceList+" .btn-default").click(function(){
            var promiseDel = URLManager.getInstance().ajaxCallByURL(link, "DELETE", {ids:$(this).data("id")});
            promiseDel.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                layer.alert('删除设备类型失败',{icon:5});
                layer.close(loadIndex);
            });
            promiseDel.done(function (result) {
                if (result.status) {
                    parent.selectDeviceType();
                    parent.getDeviceType();
                    layer.alert('删除设备类型成功',{icon:6});
                }else{
                    layer.alert(result.msg,{icon:5});
                }
            });
        })
        layer.close(loadIndex);
    });
}
ContentFactory.assignToPackage("tdhx.base.topo.AssetlistController", AssetlistController);