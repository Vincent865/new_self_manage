/**
 * Created by inchling on 2017/11/6.
 */
function LogcollectSystemController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;
    this.isTestSuccess = false;
    //this.isResetSuccess = true;
    this.pEthIP="#" + this.elementId +'_txtEthIP';
    this.pSubnet="#" + this.elementId +'_txtSubnet';
    this.pServerport="#" + this.elementId +'_txtServerPort';
    this.pProtectport="#" + this.elementId +'_txtProtectPort';
    this.pCollectConf="#" + this.elementId +'_txtCollectConf';
    this.pRouteConf="#" + this.elementId +'_txtRouteConf';
    this.pTabSelt="#" + this.elementId +'_tabSelt';
    this.pBtnEthConf="#" + this.elementId +'_btnEthConf';
//
    this.pTxtIPtype = "#" + this.elementId + "_txtIPtype";
    this.pTxtIPMask = "#" + this.elementId + "_txtIPMask";
    this.pTxtNextGateway = "#" + this.elementId + "_txtNextGateway";
    this.pBtnAdd = "#" + this.elementId + "_btnAdd";
    this.pDelBtn = "#" + this.elementId + '_delBtn';


    this.pSelectAll='#'+elementId+'_selectAll';
    this.pRuleList = "#" + this.elementId + "_RuleList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotal = "#" + this.elementId + "_lblTotal";
    this.pTxtPage = "#" + this.elementId + "_txtPageNO";
    this.pager = null;
    this.filter = {
        page: 1
    };
}

LogcollectSystemController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_LOGCOLLECT), {
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
}

LogcollectSystemController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pTabSelt).change(function(e){
            if(Number($(e.target).val())){
                $(parent.pCollectConf).hide();
                $(parent.pRouteConf).show();
            }else{
                $(parent.pCollectConf).show();
                $(parent.pRouteConf).hide();
            }
        });
        $(this.pBtnEthConf).click(function(){
            parent.logEthConf(1)
        });
//
        $(this.pBtnAdd).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.addRule();
        });
        $(parent.pSelectAll).click(function(){
            parent.checkSwitch=!parent.checkSwitch;
            $(parent.pRuleList).find('input').prop('checked',parent.checkSwitch);
        });
        $(parent.pDelBtn).on("click", function () {
            parent.delRuleList();
        });
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

LogcollectSystemController.prototype.logEthConf = function (edit) {
    try {
        var parent = this;
        var ip = $.trim($(this.pEthIP).val());
        var subnet = $.trim($(this.pSubnet).val());
        var serverport = $.trim($(this.pServerport).val());
        var protectport = $.trim($(this.pProtectport).val());
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].COLLECT_LOG;
        if(edit){
            if((ip&&!subnet)||(!ip&&subnet)){
                layer.alert("IP地址与子网掩码必须同时存在", { icon: 5 });
                return false;
            }
            if ((ip&&!Validation.validateIP(ip)) || (subnet&&!Validation.validateSubnet(subnet)) || !Validation.validatePort(serverport)|| !Validation.validatePort(protectport)) {
                layer.alert("请输入有效的IP、子网掩码和端口", { icon: 5 });
                return false;
            }
        }
        var promise = URLManager.getInstance().ajaxCallByURL(link,edit?'POST':'GET',edit?{
            ip:ip,
            mask:subnet,
            serverdev_dcport:Number(serverport),
            protectdev_dcport:Number(protectport)
        }:'');
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != null && result.status == "1") {
                if(edit){
                    layer.alert("日志采集配置成功", { icon: 6 });
                }else{
                    $(parent.pEthIP).val(result.ip),$(parent.pSubnet).val(result.mask),$(parent.pServerport).val(result.serverdev_dcport),$(parent.pProtectport).val(result.protectdev_dcport);
                }
            }
            else {
                if(edit){
                    layer.alert("日志采集配置失败", { icon: 5 });
                }else{
                    layer.alert("日志采集配置失败", { icon: 5 });
                }
            }
        });
    }
    catch (err) {
        console.error("ERROR - BasicDeviceController.updateDeviceIP() - Unable to update ip setting: " + err.message);
    }
}

LogcollectSystemController.prototype.load = function (info) {
    try {
        this.logEthConf();
        this.selectRules();
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.load() - Unable to load: " + err.message);
    }
}

LogcollectSystemController.prototype.addRule = function () {
    var loadIndex;
    try {
        var parent = this;
        var type=$(this.pTxtIPtype).val();
        var ipmask = $.trim($(this.pTxtIPMask).val());
        var nextgw = $.trim($(this.pTxtNextGateway).val());

        if (ipmask == "") {
            layer.alert("目的IP/掩码不能为空", { icon: 5 });
            return false;
        }
        if (nextgw == "") {
            layer.alert("下一跳不能为空", { icon: 5 });
            return false;
        }
        // if(type=='4'){
            if (!Validation.validateMaskIP(ipmask)) {
                layer.alert("请输入正确有效的IPV4目的IP/掩码", { icon: 5 });
                return false;
            }
            if (!Validation.validateIP(nextgw)) {
                layer.alert("请输入正确有效的IPV4下一跳地址", { icon: 5 });
                return false;
            }
        /*}else if(type=='6'){
            if (!Validation.validateIpv6Addr(ipmask,true)) {
                layer.alert("请输入正确有效的IPV6目的IP/掩码", { icon: 5 });
                return false;
            }
            if (!Validation.validateIPV6(nextgw)) {
                layer.alert("请输入正确有效的IPV6下一跳地址", { icon: 5 });
                return false;
            }
        }*/
        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_ROUTE_LIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { d_ip_mask: ipmask, next_gateway: nextgw,iptype:Number(type) });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        delete parent.pager;
                        parent.filter.page=1;
                        setTimeout(function () { parent.selectRules(); }, 2000);
                        layer.alert("添加路由成功", { icon: 6 });
                        $(parent.pTxtIPMask).val(''),$(parent.pTxtNextGateway).val('');
                        break;
                    case 0: layer.alert(result.msg, { icon: 5 }); break;
                    default: layer.alert(result.msg, { icon: 5 }); break;
                }
            }
            else {
                layer.alert(result.msg, { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - RouteSettingController.exportLog() - Unable to export all events: " + err.message);
    }
};

LogcollectSystemController.prototype.delRuleList=function(){
    var parent=this;
    parent.preDelete=[];
    $(parent.pRuleList).find('tbody input[type=checkbox]').each(function(i,d){
        if($(d).prop('checked')){
            parent.preDelete.push($(d).data('id'));
        }
    });
    var delIds=parent.preDelete,link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_ROUTE_LIST;
    if(parent.preDelete.length<=0){
        layer.alert('请选择需要删除的规则！',{icon:2});
        return;
    }else{
        layer.confirm('确定要删除么？',{icon:7,title:'注意：'}, function(index) {
            layer.close(index);
            var promise = URLManager.getInstance().ajaxCallByURL(link,"DELETE",{"id_list":delIds});
            promise.fail(function (jqXHR, textStatus, err) {
                layer.alert(err.msg, { icon: 2 });
                console.log(textStatus + " - " + err.msg);
            });
            promise.done(function(res){
                if(res.status){
                    delete parent.pager;
                    parent.filter.page=1;
                    parent.selectRules();
                    layer.alert(res.msg, { icon: 6 });
                    /*parent.total=$(parent.pLblTotal).text() - parent.preDelete.length;
                     $(parent.pLblTotal).text(parent.total);*/
                    if(parent.checkSwitch ){
                        parent.checkSwitch=!parent.checkSwitch;
                        $(parent.pAddgroupList).find('input').prop('checked',parent.checkSwitch);
                    }
                }else{
                    layer.alert(res.msg, { icon: 5 });
                }
            });
        })
    }

};

LogcollectSystemController.prototype.selectRules = function () {
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_ROUTE_LIST;
        var promise = URLManager.getInstance().ajaxCall(link, this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='5'>暂无数据</td></tr>";
            $(parent.pRuleList+">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.data) != "undefined") {
                if (result.data.length > 0) {
                    for (var i = 0; i < result.data.length; i++) {
                        html += "<tr>";
                        html += "<td>"+"<input type='checkbox' class='chinput' data-id=\""+result.data[i].id+"\" id=\""+result.data[i].id+"\" /><label for=\""+result.data[i].id+"\"></label>";
                        html += "<td><span>" + result.data[i].d_ip_mask + "</span><input type='text' style='display:none;' data-id='"+result.data[i].d_ip_mask+"' value='"+result.data[i].d_ip_mask+"'>" + "</td>";
                        html += "<td><span>" + result.data[i].next_gateway + "</span><input type='text' style='display:none;' data-id='"+result.data[i].next_gateway+"' value='"+result.data[i].next_gateway+"'>" + "</td>";
                        html += "<td>" + (result.data[i].is_activate==true?"有效":"无效") + "</td>";
                        html += "<td>";
                        html += "<button class='btn btn-default btn-xs btn-color-details' data-key='" + result.data[i].id + "'><i class='fa fa-edit'></i>编辑</button>";
                        html += "<button class='btn btn-primary btn-xs btn-primary-s' style='display:none;' data-id='" + result.data[i].id + "'data-mask='" + result.data[i].d_ip_mask+ "'data-ip_type='" + result.data[i].ip_type + "'data-next='" + result.data[i].next_gateway + "'>确认</button>";
                        html += " ";
                        html += "<button class='btn btn-danger btn-xs btn-danger-s' style='display:none;' data-key='" + result.data[i].id + "'>取消</button>";
                        html += "</td>";
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
            $(parent.pRuleList + ">tbody").html(html);
            layer.close(loadIndex);

            parent.total=result.total;
            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectRules();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }

            //编辑
            $(parent.pRuleList).find(".btn-color-details").on("click", function (event){
                $(this).hide().nextAll().show();
                $(this).parent().parent().find("span").hide();
                $(this).parent().parent().find("input[type=text]").show();
            });
            //取消
            $(parent.pRuleList).find(".btn-danger-s").on("click", function (event){
                $(this).parent().find(".btn-color-details").show().nextAll().hide();
                $(this).parent().parent().find("span").show();
                $(this).parent().parent().find("input[type=text]").map(
                    function(i,d){
                        return $(d).val($(d).data('id')).hide();
                    }
                );
            });
            //确认
            $(parent.pRuleList).find(".btn-primary-s").on("click", function (event){
                var id=$(this).data("id"),type=$(this).data('ip_type');
                parent.editRoute(id,type,this);
            });

        });
    }
    catch (err) {
        html += "<tr><td colspan='5'>暂无数据</td></tr>";
        $(this.pRuleList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - RouteSettingController.selectRules() - Unable to get all events: " + err.message);
    }
}

LogcollectSystemController.prototype.editRoute=function(id,type,t){
    try {
        var parent = this;
        var ipmask = $(t).parent().parent().find('input[type=text]').first().val();
        var nextgw = $(t).parent().parent().find('input[type=text]').last().val();
        if (ipmask == "") {
            layer.alert("目的IP/掩码不能为空", { icon: 5 });
            return false;
        }
        if (nextgw == "") {
            layer.alert("下一跳不能为空", { icon: 5 });
            return false;
        }
        /*if(type=='4'){
            if (!Validation.validateMaskIP(ipmask)) {
                layer.alert("请输入正确有效的目的IP/掩码", { icon: 5 });
                return false;
            }
            if (!Validation.validateIP(nextgw)) {
                layer.alert("请输入正确有效的下一跳地址", { icon: 5 });
                return false;
            }
        }else if(type=='6'){
            if (!Validation.validateIpv6Addr(ipmask,true)) {
                layer.alert("请输入正确有效的IPV6目的IP/掩码", { icon: 5 });
                return false;
            }
            if (!Validation.validateIPV6(nextgw)) {
                layer.alert("请输入正确有效的IPV6下一跳地址", { icon: 5 });
                return false;
            }
        }*/
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_ROUTE_LIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "PUT", { id:id, d_ip_mask: ipmask, next_gateway: nextgw,iptype:type });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if(result.status){
                layer.close(loadIndex);layer.alert(result.msg,{icon:6});parent.selectRules();
            }else{
                layer.close(loadIndex);layer.alert(result.msg,{icon:5});parent.selectRules();
            }
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - RouteSettingController.exportLog() - Unable to export all events: " + err.message);
    }
};

ContentFactory.assignToPackage("tdhx.base.system.LogcollectSystemController", LogcollectSystemController);
