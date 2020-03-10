function DataCController( controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.controller = controller;
   
    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnEnable = "#" + this.elementId + "_btnEnable";
    this.pBtnDisable = "#" + this.elementId + "_btnDisable";

    this.pIPTYPE = "[name=iptype]";
    this.pTxtSRCIP = "#" + this.elementId + "_txtSrcip";
    this.pTxtSRCIP6 = "#" + this.elementId + "_txtSrcip6";
    this.pTxtDSTIP = "#" + this.elementId + "_txtDstip";
    this.pTxtDSTIP6 = "#" + this.elementId + "_txtDstip6";
    this.pTxtSRCMac = "#" + this.elementId + "_txtSrcMac";
	this.pTxtDSTMac = "#" + this.elementId + "_txtDstMac";
    this.pTxtDSTPort = "#" + this.elementId + "_txtDstport";
	this.pTxtProto = "#" + this.elementId + "_txtProto";
    this.pBtnAdd = "#" + this.elementId + "_btnAdd";

    this.pDatacList = "#" + this.elementId + "_tdDatacList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotal = "#" + this.elementId + "_lblTotal";
    this.pager = null;
    this.filter = {
        page: 1
    };
    this.iptype=4;

}

DataCController.prototype.init = function () {
    try {
        var parent = this;

        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_AUDITSTRATEGY_DATAC), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
      this.initControls();
      this.load();
    }
    catch (err) {
        console.error("ERROR - UserController.init() - Unable to initialize: " + err.message);
    }
}

DataCController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pBtnRefresh).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.selectDatac();
        });
        $(this.pBtnAdd).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.addDatac();
        });

        $(this.pBtnDisable).on("click", function () {
            parent.disableDatac();
        });

        $(this.pBtnEnable).on("click", function () {
           parent.enableDatac();
        });
        $(this.pIPTYPE).on("change", function () {
            parent.iptype=this.value;
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
    }
    catch (err) {
        console.error("ERROR - DataCController.initControls() - Unable to initialize control: " + err.message);
    }
}

DataCController.prototype.load = function () {
    try {
		
          this.selectDatac();
        //this.getInitEventAction();
    }
    catch (err) {
        console.error("ERROR - DataCController.load() - Unable to load: " + err.message);
    }
}

DataCController.prototype.addDatac = function () {
    var loadIndex;
    try {
        var parent = this;
        var srcip = $.trim($(this.pTxtSRCIP).val());
        var srcip6 = $.trim($(this.pTxtSRCIP6).val());
        var dstip = $.trim($(this.pTxtDSTIP).val());
        var dstip6 = $.trim($(this.pTxtDSTIP6).val());
        var srcmac = $.trim($(this.pTxtSRCMac).val());
		var dstmac = $.trim($(this.pTxtDSTMac).val());
		var dstport = $.trim($(this.pTxtDSTPort).val());
        var proto = $.trim($(this.pTxtProto).val());
        var intf = "2";//接口
		if (srcip&&!Validation.validateIP(srcip)) {
            layer.alert("请输入正确有效的源IP地址", { icon: 5 });
            return false;
        }else if (dstip&&!Validation.validateIP(dstip)) {
            layer.alert("请输入正确有效的目的IP地址", { icon: 5 });
            return false;
        }else if (srcmac&&!Validation.validateMAC(srcmac)) {
            layer.alert("请输入正确有效的源MAC地址", { icon: 5 });
            return false;
        }else if (dstmac&&!Validation.validateMAC(dstmac)) {
            layer.alert("请输入正确有效的目的MAC地址", { icon: 5 });
            return false;
        }else if (dstport&&!Validation.validatePort(dstport)) {
            layer.alert("请输入正确有效的目的端口", { icon: 5 });
            return false;
        }
        if (!Validation.validateIP(srcip)&&!Validation.validateIP(dstip)&&!Validation.validateMAC(srcmac)&&!Validation.validateMAC(dstmac)&&!Validation.validatePort(dstport)&&!Number(proto)&&!srcip6&&!dstip6) {
            layer.alert("请至少输入有效的其中任意一项字段", { icon: 5 });
            return false;
        }
        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].MW_AUDITSTRATEGY_ADD;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { srcip: (srcip||srcip6), dstip: (dstip||dstip6), srcmac: srcmac.toLowerCase(), dstmac: dstmac.toLowerCase(),port: dstport,proto: proto,iptype:this.iptype});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        setTimeout(function () { parent.selectDatac(); }, 2000);
                        layer.confirm("添加规则成功", {icon:6,btn:['确定']},function(){
                            layer.closeAll();
                            $(parent.pTxtSRCIP).val(''),$(parent.pTxtDSTIP).val(''),$(parent.pTxtSRCMac).val(''),
                            $(parent.pTxtDSTMac).val(''),$(parent.pTxtDSTPort).val(''),$(parent.pTxtProto).val(0);
                        });
                        break;
                    //case -1: layer.alert("当前规则已经存在，请不要重复添加", { icon: 5 }); break;
                    case 0: layer.alert(result.msg, { icon: 5 }); break;
                    //case 2: layer.alert("白名单正在学习中...请稍后操作.", { icon: 5 }); break;
                    default: layer.alert("添加规则失败", { icon: 5 }); break;
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
        console.error("ERROR - DataCController.exportLog() - Unable to export all events: " + err.message);
    }
}


DataCController.prototype.selectDatac = function () {
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].MW_AUDITSTRATEGY_SEARCH;
        var promise = URLManager.getInstance().ajaxCall(link, this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='9'>暂无数据</td></tr>";
            $(parent.pDatacList+">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>" + ((parent.filter.page - 1) * 10 + 1 + i) + "</td>";
                        html += "<td>" + result.rows[i][1] + "</td>";
                        html += "<td>" + result.rows[i][2] + "</td>";
						html += "<td>" + result.rows[i][3] + "</td>";
						html += "<td>" + result.rows[i][4] + "</td>";
						html += "<td>" + result.rows[i][5] + "</td>";
						if(result.rows[i][6]=="0"){
							html += "<td>" + "全部" + "</td>";
						}
						if(result.rows[i][6]=="1"){
							html += "<td>" + "TCP" + "</td>";
						}
						if(result.rows[i][6]=="2"){
							html += "<td>" + "UDP" + "</td>";
						}
                        html += "<td><span class='btn-on-box'>";
                        html += "<input type='checkbox' id='chk" + result.rows[i][0] + "' class='btn-on' data-key='" + result.rows[i][0] + "' " + (result.rows[i][7] == 1 ? "checked" : "") + " /><label for='chk" + result.rows[i][0] + "'></label>";
                        html += "</td>";
                        html += "<td><button class='btn btn-danger btn-xs' data-key='" + result.rows[i][0] + "'><i class='fa fa-trash-o'></i>删除</button></td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='9'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='9'>暂无数据</td></tr>";
            }
            $(parent.pDatacList + ">tbody").html(html);
            layer.close(loadIndex);

            $(parent.pDatacList + ">tbody").find("button[class='btn btn-danger btn-xs']").on("click", function () {
                var id = $(this).attr("data-key");
                parent.deleteDatac(id, $(this).parent().parent());
            });

            $(parent.pDatacList + ">tbody").find("input[type='checkbox']").on("change", function () {
                var id = $(this).attr("data-key");
                var status = $(this).prop("checked") ? "1" : "0";
                parent.updateDatac(id, status, $(this), !$(this).prop("checked"),0);
            });

            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectDatac();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='9'>暂无数据</td></tr>";;
        $(this.pTdRuleList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - DataCController.selectDatac() - Unable to get all events: " + err.message);
    }
}

DataCController.prototype.deleteDatac = function (id, $tr) {
    var parent = this;
    layer.confirm('确定删除该条数据么？',{icon:7,title:'注意：'}, function(index) {
        layer.close(index);
        var loadIndex = layer.load(2, {shade: [0.4, '#fff']});
        try {
            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].MW_AUDITSTRATEGY_DEL;
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
                            $tr.remove();
                            var cur = parseInt($(parent.pLblTotal).text()) - 1;
                            $(parent.pLblTotal).text(cur);
                            layer.alert("删除规则成功", {icon: 6});
                            break;
                        default:
                            layer.alert("删除规则失败", {icon: 5});
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
            console.error("ERROR - DataCController.exportLog() - Unable to delete this rule: " + err.message);
        }
    })
}

DataCController.prototype.updateDatac = function (id, status, obj, v,isall) {
    var parent = this;
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var action = "1";//$("input[name='macEvent']:checked").val();1--告警   2--阻断
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].MW_AUDITSTRATEGY_DEPLOY;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { id: id, status: status,isall:isall});
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
                    case 2:
                        layer.alert("白名单正在学习中,请稍后操作...", { icon: 5 });
                        obj.prop("checked", v);
                        break;
                    default:
                        layer.alert("修改失败", { icon: 5 });
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

DataCController.prototype.enableDatac = function () {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        if ($(this.pLblTotal).html() == "0") {
            layer.alert("当前没有可以操作的规则", { icon: 5 });
            layer.close(loadIndex);
            return;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].MW_AUDITSTRATEGY_DEPLOY;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
       var promise = URLManager.getInstance().ajaxCallByURL(link,"POST", { id: "0", status: "1",isall:"1"});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        $(parent.pDatacList).find("input[type='checkbox']").prop("checked", true);
                        break;
                    case 2: layer.alert("白名单正在学习中...请稍后操作.", { icon: 5 }); break;
                    default: layer.alert("启用所有规则失败", { icon: 5 }); break;
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
        console.error("ERROR - DataCController.exportLog() - Unable to deploy rules: " + err.message);
    }
}

DataCController.prototype.disableDatac = function () {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        if ($(this.pLblTotal).html() == "0") {
            layer.alert("当前没有可以操作的规则", { icon: 5 });
            layer.close(loadIndex);
            return;
        }
		var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].MW_AUDITSTRATEGY_DEPLOY;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST", { id: "0", status: "0",isall:"1"});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        $(parent.pDatacList).find("input[type='checkbox']").prop("checked", false);
                        layer.close(loadIndex);
                        break;
                    default: layer.alert("禁用所有规则失败", { icon: 5 }); break;
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
        console.error("ERROR - DataCController.exportLog() - Unable to export all events: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.auditstrategy.DataCController", DataCController);
