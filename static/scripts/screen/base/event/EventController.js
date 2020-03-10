﻿function EventController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pTodayEvent = "#" + this.elementId + "_todayEvent";
    this.pNoReadEvent = "#" + this.elementId + "_noReadyEvent";
    this.pHighPeriod = "#" + this.elementId + "_highPeriod";
    this.pLblEventCount = "#" + this.elementId + "_lblEventCount";

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnSetRead = "#" + this.elementId + "_btnSetRead";
    this.pBtnClear = "#" + this.elementId + "_btnClear";
    this.pBtnExport = "#" + this.elementId + "_btnExport";
    this.pBtnFilter = "#" + this.elementId + "_btnFilter";
    this.pBtnSearch = "#" + this.elementId + "_btnSearch";
    this.pBtnExport = "#" + this.elementId + "_btnExport";
    this.pDivFilter = "#" + this.elementId + "_divFilter";

    this.pTxtKeywords = "#" + this.elementId + "_txtKeywords";
    this.pTxtSourceIP = "#" + this.elementId + "_txtSourceIP";
    this.pTxtDestinationIP = "#" + this.elementId + "_txtDestinationIP";
    this.pTxtSourceName = "#" + this.elementId + "_txtSourceName";
    this.pTxtDestinationName = "#" + this.elementId + "_txtDestinationName";
    this.pTxtProtocol = "#" + this.elementId + "_txtProtocol";
    this.pTxtStartDateTime = "#" + this.elementId + "_txtStartDateTime";
    this.pTxtEndDateTime = "#" + this.elementId + "_txtEndDateTime";

    this.pTdEventList = "#" + this.elementId + "_tdEventList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";

    this.pLblEventLevel = "#" + this.elementId + "_dialog_lblEventLevel";
    this.pLblRiskLevel = "#" + this.elementId + "_dialog_lblRiskLevel";
    this.pLblEventType = "#" + this.elementId + "_dialog_lblEventType";
    this.pLblEventName = "#" + this.elementId + "_dialog_lblEventName";
    this.pLblEventAddr = "#" + this.elementId + "_dialog_lblEventAddr";
    this.pLblEventDate = "#" + this.elementId + "_dialog_lblEventDate";
    this.pLblEventTime = "#" + this.elementId + "_dialog_lblEventTime";
    this.pLblApplicationProtocol = "#" + this.elementId + "_dialog_lblApplicationProtocol";
    this.pLblNetworkProtocol = "#" + this.elementId + "_dialog_lblNetworkProtocol";
    this.pLblEventRemark = "#" + this.elementId + "_dialog_lblEventRemark";
    this.pLblProtocolContent = "#" + this.elementId + "_dialog_lblProtocolContent";
    this.pLblRuleContent = "#" + this.elementId + "_dialog_lblRuleContent";
    this.pLblEventContent = "#" + this.elementId + "_dialog_lblEventContent";
    this.pLblEventSize = "#" + this.elementId + "_dialog_lblEventSize";
    this.pLblEventDescription = "#" + this.elementId + "_dialog_lblEventDescription";
    this.pdEventSource = "#" + this.elementId + "_dialog_lblEventSource";
    this.pDdlEventSource = "#" + this.elementId + "_ddlEventSource";
    this.pDdlRiskLevel = "#" + this.elementId + "_ddlRiskLevel";

    this.pLblBugName = "#" + this.elementId + "_dialog_lblBugName";
    this.pLblBugNo = "#" + this.elementId + "_dialog_lblBugNo";
    this.pLblBugType = "#" + this.elementId + "_dialog_lblBugType";
    this.pLblBugSource = "#" + this.elementId + "_dialog_lblBugSource";
    this.pLblBugTime = "#" + this.elementId + "_dialog_lblBugTime";
    this.pLblBugLevel = "#" + this.elementId + "_dialog_lblBugLevel";
    this.pLblBugDevice = "#" + this.elementId + "_dialog_lblBugDevice";
    this.pLblBugRuleSource = "#" + this.elementId + "_dialog_lblBugRuleSource";
    this.pLblBugEventHandle = "#" + this.elementId + "_dialog_lblBugEventHandle";
    this.pLblCompactCompany = "#" + this.elementId + "_dialog_lblCompactCompany";
    this.pLblAttackCondition = "#" + this.elementId + "_dialog_lblAttackCondition";
    this.pLblRuleDes = "#" + this.elementId + "_dialog_lblRuleDes";
    this.pLblFeatureName = "#" + this.elementId + "_dialog_lblFeatureName";
    this.pLblFeaturePriority = "#" + this.elementId + "_dialog_lblFeaturePriority";
    this.pLblFeatureRisk = "#" + this.elementId + "_dialog_lblFeatureRisk";
    this.pLblFeatureNo = "#" + this.elementId + "_dialog_lblFeatureNo";

    this.pager = null;
    this.filter = {
        page:1,
        action:"",
        sourceIp:"",
        status:"",
        destinationIp:"",
        appLayerProtocol:"",
        starttime:"",
        endtime:"",
        signatureName: "",
        sourceName: "",
        destinationName:"",
        riskLevel:""
    };

    this.pModeTip = "#" + this.elementId + "_modetip";
    this.timer = {
        tipTimer:null
    };

    this.protocolList = Constants.EVENT_PROTOCOL_LIST[APPCONFIG.PRODUCT];
}

EventController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.EVENT_LIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.load();
        this.initControls();
    }
    catch (err) {
        console.error("ERROR - EventController.initShell() - Unable to initialize: " + err.message);
    }
}

EventController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pTxtProtocol).empty();
        $(this.pTxtProtocol).append("<option value=''>所有协议</option>");
        $.each(this.protocolList, function () {
            $(parent.pTxtProtocol).append("<option value='" + this.key + "'>" + this.name + "</option>");
        });

        this.pViewHandle.find(this.pBtnRefresh).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectEvents();
            $(parent.pModeTip).hide();
        });

        this.pViewHandle.find(this.pBtnSetRead).on("click", function () {
            parent.flagEvent();
        });

        this.pViewHandle.find(this.pBtnClear).on("click", function () {
            parent.clearEvent();
        });

        this.pViewHandle.find(this.pBtnExport).on("click", function () {
            parent.exportEvent();
        });

        this.pViewHandle.find(this.pBtnFilter).on("click", function () {
            parent.pViewHandle.find(parent.pTxtSourceName).val("");
            parent.pViewHandle.find(parent.pTxtDestinationName).val("");
            parent.pViewHandle.find(parent.pTxtSourceIP).val("");
            parent.pViewHandle.find(parent.pTxtDestinationIP).val("");
            parent.pViewHandle.find(parent.pTxtProtocol).val("");
            parent.pViewHandle.find(parent.pTxtStartDateTime).val("");
            parent.pViewHandle.find(parent.pTxtEndDateTime).val("");
            parent.pViewHandle.find(parent.pDdlEventSource).val(0);
            parent.pViewHandle.find(parent.pDdlRiskLevel).val("");
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            parent.pViewHandle.find(parent.pDivFilter).toggle();
        });

        this.pViewHandle.find(this.pBtnSearch).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectEvents();
        });

        this.pViewHandle.find(".number").on("click", function () {
            var data_id = "#" + $(this).attr("data-id");
            switch (data_id) {
                case parent.pTodayEvent:
                    parent.filter.page = 1;
                    parent.formatFilter("datetime");
                    parent.pager = null;
                    parent.selectEvents();
                    break;
                case parent.pNoReadEvent:
                    parent.filter.page = 1;
                    parent.formatFilter("isready");
                    parent.pager = null;
                    parent.selectEvents();
                    break;
            }
        });
    }
    catch (err) {
        console.error("ERROR - EventController.initControls() - Unable to initialize control: " + err.message);
    }
}

EventController.prototype.load = function () {
    try {
        var parent = this;
        this.setEventNum();
        this.selectEvents();
        //获取安全事件状态
        parent.getTipStatus();
    }
    catch (err) {
        console.error("ERROR - EventController.load() - Unable to load: " + err.message);
    }
}

EventController.prototype.getTipStatus = function () {
    try {
        var parent = this;
        var ws=io.connect(location.protocol+'//'+location.host+':443');
        ws.on('data_refresh',function(data){
            console.log(data.msg_type);
            $(parent.pModeTip).show();
        });
    }
    catch (err) {
        console.error("ERROR - EventController.getTipStatus() - Unable to load: " + err.message);
    }
}

EventController.prototype.setEventNum = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_EVENT_INFO;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined") {
                parent.pViewHandle.find(parent.pTodayEvent).html(result.safeeventinfo.todaySafeEvent);
                parent.pViewHandle.find(parent.pNoReadEvent).html(result.safeeventinfo.noReadSafeEvent);
                parent.pViewHandle.find(parent.pHighPeriod).html(result.safeeventinfo.highestPeriod);
                var historyEvent = result.safeeventinfo.allSafeEvent - result.safeeventinfo.todaySafeEvent;
                if (historyEvent < 0) {
                    historyEvent = 0;
                }
                parent.pViewHandle.find(parent.pLblEventCount).html(historyEvent);
            }
        });
    }
    catch (err) {
        console.error("ERROR - EventController.getEventInfo() - Unable to load: " + err.message);
    }
}

EventController.prototype.flagEvent = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].FLAG_SAFE_EVENT_LIST;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        // var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {loginuser: AuthManager.getInstance().getUserName()});
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert("设置已读成功", { icon: 6 });
                        parent.setEventNum();
                        //parent.selectEvents();
                        $(parent.pTdEventList + ">tbody").find("td").each(function (i) {
                            if($(this)[0].innerText=="未读")
                            {
                                $(this)[0].innerText = "已读";
                            }
                        });
                        break;
                    default: layer.alert("设置已读失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("设置已读失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - EventController.flagEvent() - Unable to set all events to read status: " + err.message);
    }
}

EventController.prototype.clearEvent = function () {
    var parent = this;
    try {
        layer.confirm('确定清空所有事件么？',{icon:7,title:'注意：'}, function(index) {
            layer.close(index);
            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DELETE_SAFE_EVENT_LIST;
            var loadIndex = layer.load(2, {shade: [0.4, '#fff']});
            var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {});

            /*var promise = function runAsync() {
                var def = $.Deferred();
                //做一些异步操作
                setTimeout(function () {
                    console.log('执行完成');
                    def.resolve({status: 1});
                }, 2000);
                return def;
            };*/
            /*runAsync().then(function(data){
             console.log(data)
             });    */

            promise.fail(function (jqXHR, textStatus, err) {
             console.log(textStatus + " - " + err.message);
             layer.close(loadIndex);
             layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
             });
            promise.done(function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 1:
                            layer.alert("清除所有事件成功", {icon: 6});
                            parent.filter.page = 1;
                            parent.pager = null;
                            parent.setEventNum();
                            parent.selectEvents();
                            break;
                        default:
                            layer.alert("清除所有事件失败", {icon: 5});
                            break;
                    }
                }
                else {
                    layer.alert("清除所有事件失败", {icon: 5});
                }
                layer.close(loadIndex);
            });
        })
    }
    catch (err) {
        console.error("ERROR - EventController.clearEvent() - Unable to clear all events: " + err.message);
    }
}

EventController.prototype.exportEvent = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].EXPORT_SAFE_EVENT;
        window.open(link + "?loginuser=" + AuthManager.getInstance().getUserName());
        //var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        //var promise = URLManager.getInstance().ajaxCall(link);
        //promise.fail(function (jqXHR, textStatus, err) {
        //    console.log(textStatus + " - " + err.message);
        //    layer.close(loadIndex);
        //    layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        //});
        //promise.done(function (result) {
        //    if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
        //        switch (result.status) {
        //            case 1:
        //                window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].SAFE_EVENT_FILEPATH + result.filename);
        //                break;
        //            default: layer.alert("导出失败", { icon: 5 }); break;
        //        }
        //    }
        //    else {
        //        layer.alert("导出失败", { icon: 5 });
        //    }
        //    layer.close(loadIndex);
        //});
    }
    catch (err) {
        console.error("ERROR - EventController.exportEvent() - Unable to export all events: " + err.message);
    }
}

EventController.prototype.selectEvents = function () {
    var html = "";
    try {
        var parent = this;
        var loadIndex = layer.load(2);
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].SEARCH_SAFE_EVENT;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='11'>暂无数据</td></tr>";
            $(parent.pTdEventList + ">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    $('#evtcout').text(result.num);
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        //sourceIp,destinationIp,appLayerProtocol,timestamp,action,status,incidentId
                        var protocolItem = $.grep(parent.protocolList, function (item) { return item.key == result.rows[i][2] });
                        html += "<td>" + FormatterManager.formatToLocaleDateTime(result.rows[i][3]) + "</td>";
                        html += "<td>" + result.rows[i][13] + "</td>";
                        html += "<td>" + result.rows[i][14] + "</td>";
                        html += "<td>" + result.rows[i][0] + "</td>";
                        html += "<td>" + result.rows[i][1] + "</td>";
                        html += "<td>" + ((protocolItem.length==0)?result.rows[i][2]:protocolItem[0].name) + "</td>";
                        html += "<td>" + parent.formatEventType(result.rows[i][4]) + "</td>";
                        html += "<td>" + parent.formatEventSource(result.rows[i][8]) + "</td>";
                        html += "<td>" + parent.formatRiskLevel(result.rows[i][15]) + "</td>";
                        html += "<td>" + parent.formatReadStatus(result.rows[i][5]) + "</td>";
                        html += "<td><button class='btn btn-default btn-xs btn-color-details' table-num='" + result.rows[i][7] + "' data-key='" + result.rows[i][6] + "' status=" + result.rows[i][8] + " deviceId=" + result.rows[i][9] + " mac=" + result.rows[i][10] + " ip=" + result.rows[i][0] + " type=" + result.rows[i][4] + " sid=" + result.rows[i][12] + " dname = " + result.rows[i][13] + " daddr = " + result.rows[i][1] + "><i class='fa fa-file-text-o'></i>详情</button></td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='11'>暂无数据</td></tr>";
                    $('#evtcout').text(0)
                }
            }
            else {
                html += "<tr><td colspan='11'>暂无数据</td></tr>";
                $('#evtcout').text(0)
            }
            $(parent.pTdEventList + ">tbody").html(html);
            layer.close(loadIndex);
            $(parent.pTdEventList + ">tbody").find("button").on("click", function (event) {
                var id = $(this).attr("data-key");
                var table_id = $(this).attr("table-num");
                var deviceId = $(this).attr("deviceId");
                var mac = $(this).attr("mac");
                var ip = $(this).attr("ip");
                var type = $(this).attr("status");
                var eventType = $(this).attr("type");
                var sid = $(this).attr("sid");
                var dname = $(this).attr("dname");
                var daddr = $(this).attr("daddr");
                var $tr = $(this).parent().prev();
                var dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(type=='6'?Constants.TEMPLATES.EVENT_ASSETDIALOG:type=='7'?Constants.TEMPLATES.INVALID_DIALOG:Constants.TEMPLATES.EVENT_DIALOG), {
                    elementId: parent.elementId + "_dialog"
                });
                if (type == "4")
                    dialogTemplate = "<div />";
                var width = parent.pViewHandle.width() - 10 + "px";
                var height = $(window).height() - parent.pViewHandle.offset().top - document.body.scrollTop - 10 + "px";
                var switchlink = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_SWITCH_MAC_INFO,switchsmac,switchdmac;
                //获取交换机信息
                var smacList='',dmacList='';
                switchsmac = URLManager.getInstance().ajaxCallByURL(switchlink,"POST", {mac:ip});
                switchsmac.done(function (smaclist) {
                    smacList += "<b>源设备所在交换机信息：</b><span>";
                    for (var i = 0; i < smaclist.rows.length; i++) {
                        smacList += smaclist.rows[i][0] + " # ";
                        smacList += smaclist.rows[i][2] + " # ";
                        smacList += smaclist.rows[i][1];
                        smacList += ";";
                    }
                    if(smaclist.num==0) smacList += "无";
                    smacList += "</span>";
                    switchsmac = URLManager.getInstance().ajaxCallByURL(switchlink,"POST", {mac:daddr});
                    switchsmac.done(function (dmaclist) {
                        dmacList += "<b>目的设备所在交换机信息：</b><span>";
                        for (var i = 0; i < dmaclist.rows.length; i++) {
                            dmacList += dmaclist.rows[i][0] + " # ";
                            dmacList += dmaclist.rows[i][2] + " # ";
                            dmacList += dmaclist.rows[i][1];
                            dmacList += ";";
                        }
                        if(dmaclist.num==0) dmacList += "无";
                        dmacList += "</span>";
                        layer.open({
                            type: 1,
                            title: "事件信息",
                            area: [width, height],
                            offset: ["82px", "200px"],
                            shade: [0.5, '#393D49'],
                            content: dialogTemplate,
                            success: function (layero, index) {
                                if(type == "4") {
                                    parent.pDetailController = new tdhx.base.event.EventFlowController(layero, parent.elementId + "_dialog", id, table_id, deviceId, mac, ip, eventType,dname,smacList,dmacList);
                                    parent.pDetailController.init();
                                }else if(type=='6'){
                                    parent.getAssetEventDetails(layero, id, table_id, $tr,dname,smacList,dmacList);
                                }else if(type=='7'){
                                    parent.getInvalidDetails(layero, id, table_id, $tr,dname,smacList,dmacList);
                                }else{
                                    parent.getEventDetails(layero, id, table_id, $tr,smacList,dmacList);
                                    if(type == 2){
                                        parent.getBlacklistDetails(layero, sid);
                                        $("#divBlackDetail").height("0");
                                        $("#divBlackDetail").show();
                                    }else{
                                        $("#divBlackDetail").hide();
                                    }
                                }
                                $(window).on("resize", function () {
                                    var pwidth = parent.pViewHandle.width() - 10 + "px";
                                    var pheight = $(window).height() - parent.pViewHandle.offset().top - 10 + "px";
                                    layero.width(pwidth);
                                    layero.height(pheight);
                                })
                            },
                            end: function () {
                                if (type == "4") {
                                    if (parent.pDetailController != null && typeof (parent.pDetailController.timer) != "undefined" && parent.pDetailController.timer != null) {
                                        parent.pDetailController.clearTimer();
                                    }
                                    parent.flagSingleEvent(id, $tr, table_id);
                                }
                            }
                        });
                    });

                });


            });


            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectEvents();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='11'>暂无数据</td></tr>";
        $(parent.pTdEventList + ">tbody").html(html);
        $('#evtcout').text(0);
        console.error("ERROR - EventController.selectEvents() - Unable to get all events: " + err.message);
    }
}

EventController.prototype.getInvalidDetails=function(viewHandler, id, table_id, $tr,smacList,dmacList){
    try {
        var parent = this;
        /*var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.INVALID_DIALOG), {
         elementId: parent.elementId + "_dialog"
         });
         var tmpViewHandle = $("<div />").html(tabTemplate);*/
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_INVALID_EVENT;
        var promise = URLManager.getInstance().ajaxCall(link,{recordid:id,tablenum:table_id});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (result.status) {
                var times=result.values[1].split(' ');
                parent.flagSingleEvent(id, $tr, table_id);
                $(viewHandler).find(parent.pLblEventLevel).text(result.values[0] == 0 ? "通过" : (result.values[0] == 1 ? "警告" : (result.values[0] == 3 ? "通知" :"阻断")));
                $(viewHandler).find(parent.pLblEventType).text("不合规报文告警");
                $(viewHandler).find(parent.pLblEventDate).text(times[0]);
                $(viewHandler).find(parent.pLblEventTime).text(times[1]);
                $(viewHandler).find(parent.pLblEventDescription).text(result.values[2]);
                $('<hr><div class="pops-h1">交换机信息(交换机名#端口#位置)</div>'+smacList+'<br>'+dmacList).appendTo($(viewHandler).find('.pops-content'));
            }
        });
    }
    catch (err) {
        console.error("ERROR - EventController.getInvalidDetails() - Unable to get safe event information: " + err.message);
    }
}

EventController.prototype.getEventDetails = function (viewHandler, id, table_id, $tr,smacList,dmacList) {
    try {
        var parent = this;
        /*var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.EVENT_DIALOG), {
            elementId: parent.elementId + "_dialog"
        });
        var tmpViewHandle = $("<div />").html(tabTemplate);
        console.log(tabTemplate);*/
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_SAFE_EVENT;
        var promise = URLManager.getInstance().ajaxCall(link,{recordid:id,tablenum:table_id});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.values) != "undefined") {
                parent.flagSingleEvent(id, $tr, table_id);
                $(viewHandler).find(parent.pLblEventLevel).text(result.values[0] == 0 ? "通过" : (result.values[0] == 1 ? "警告" : (result.values[0] == 3 ? "通知" :"阻断")));
                $(viewHandler).find(parent.pLblRiskLevel).text(parent.formatRiskLevel(result.values[1]));
                $(viewHandler).find(parent.pLblEventType).text("安全事件");
                $(viewHandler).find(parent.pLblEventDate).text(FormatterManager.formatDate(result.values[2]));
                $(viewHandler).find(parent.pLblEventTime).text(FormatterManager.formatToLongTime(result.values[2]));
                $(viewHandler).find(parent.pLblApplicationProtocol).text(result.values[3]);
                var protocolItem = $.grep(parent.protocolList, function (item) { return item.key == result.values[4] });
                $(viewHandler).find(parent.pLblNetworkProtocol).text((protocolItem.length==0)?result.values[4]:protocolItem[0].name);
                $(viewHandler).find(parent.pLblEventRemark).text(result.values[6]);
                $(viewHandler).find(parent.pLblProtocolContent).text(result.values[5]);
                $(viewHandler).find(parent.pLblRuleContent).text(result.values[7]);
                $(viewHandler).find(parent.pLblEventSize).text(result.values[8]);
                $(viewHandler).find(parent.pLblEventDescription).text(result.values[9]);
                $(viewHandler).find(parent.pLblEventContent).text(result.packstr);
                $('<hr><div class="pops-h1">交换机信息(交换机名#端口#位置)</div>'+smacList+'<br>'+dmacList).appendTo($(viewHandler).find('.pops-content'));
            }
        });
    }
    catch (err) {
        console.error("ERROR - EventController.getEventDetails() - Unable to get safe event information: " + err.message);
    }
}

EventController.prototype.getAssetEventDetails = function (viewHandler, id, table_id, $tr,dname,smacList,dmacList) {
    try {
        var parent = this;
        /*var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.EVENT_ASSETDIALOG), {
            elementId: parent.elementId + "_dialog"
        });
        var tmpViewHandle = $("<div />").html(tabTemplate);*/
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_ASSET_EVENT;
        var promise = URLManager.getInstance().ajaxCall(link,{recordid:id,tablenum:table_id});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.rows) != "undefined") {
                parent.flagSingleEvent(id, $tr, table_id);
                result.values=result.rows[0];
                $(viewHandler).find(parent.pLblEventLevel).text(result.values[4] == 0 ? "通过" : (result.values[4] == 1 ? "警告" : (result.values[4] == 3 ? "通知" :"阻断")));
                $(viewHandler).find(parent.pLblEventType).text("资产告警");
                $(viewHandler).find(parent.pLblEventDate).text(FormatterManager.formatDate(FormatterManager.formatDateTime(Number(result.values[0])*1000,'yyyy-MM-dd HH:mm:ss')));
                $(viewHandler).find(parent.pLblEventTime).text(FormatterManager.formatToLongTime(FormatterManager.formatDateTime(Number(result.values[0])*1000,'yyyy-MM-dd HH:mm:ss')));
                $(viewHandler).find(parent.pLblEventName).text(dname);
                $(viewHandler).find(parent.pLblEventAddr).text(result.values[2]);
                $(viewHandler).find(parent.pLblEventDescription).text(result.values[3]);
                $('<hr><div class="pops-h1">交换机信息(交换机名#端口#位置)</div>'+smacList+'<br>'+dmacList).appendTo($(viewHandler).find('.pops-content'));
            }
        });
    }
    catch (err) {
        console.error("ERROR - EventController.getAssetEventDetails() - Unable to get safe event information: " + err.message);
    }
}

EventController.prototype.getBlacklistDetails = function (viewHandler, id) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_BLACKLIST;
        var promise = URLManager.getInstance().ajaxCall(link, { recordid: id });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.rows) != "undefined" && result.rows.length > 0) {
                $(viewHandler).find(parent.pLblBugName).text(result.rows[0][0]);
                $(viewHandler).find(parent.pLblBugNo).text(result.rows[0][5]);
                $(viewHandler).find(parent.pLblBugType).text(result.rows[0][1]);
                $(viewHandler).find(parent.pLblBugSource).text("iSightPartners");
                $(viewHandler).find(parent.pLblBugTime).text(result.rows[0][2]);
                $(viewHandler).find(parent.pLblBugLevel).text(parent.formatDangerLevel(result.rows[0][3]));
                $(viewHandler).find(parent.pLblBugDevice).text("Genesis");
                $(viewHandler).find(parent.pLblBugRuleSource).text("漏洞库");
                $(viewHandler).find(parent.pLblBugEventHandle).text(parent.formatEventType(result.rows[0][4]));
                $(viewHandler).find(parent.pLblCompactCompany).text("Iconics");
                $(viewHandler).find(parent.pLblAttackCondition).text(result.rows[0][6]);
                $(viewHandler).find(parent.pLblRuleDes).html(result.rows[0][8]);
                $(viewHandler).find(parent.pLblFeatureName).text(result.rows[0][9]);
                $(viewHandler).find(parent.pLblFeaturePriority).text("1");
                $(viewHandler).find(parent.pLblFeatureRisk).text(parent.formatRiskLevel(result.rows[0][10]));
                $(viewHandler).find(parent.pLblFeatureNo).text(result.rows[0][11]);
            }
        });
    }
    catch (err) {
        console.error("ERROR - BlacklistController.EventController() - Unable to get safe event information: " + err.message);
    }
}

EventController.prototype.flagSingleEvent = function (id, obj, tableNum) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].FLAG_SAFE_EVENT;
        var promise = URLManager.getInstance().ajaxCall(link,{recordindex:id,tablenum:tableNum});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.setEventNum();
                        obj.html("已读");
                        break;
                    default: layer.alert("设置已读失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("设置已读失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - EventController.flagEvent() - Unable to set event to read status: " + err.message);
    }
}

EventController.prototype.formatReadStatus = function (status) {
    try {
        switch (status) {
            case 1: return "已读";
            case 0: return "<span style='color:#ff0000'>未读</span>";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - EventController.formatReadStatus() - Unable to format ReadStaus: " + err.message);
    }
}

EventController.prototype.formatEventSource = function (status) {
    try {
        switch (status) {
            case 1: return "白名单";
            case 2: return "黑名单";
            case 3: return "IP/MAC";
            case 4: return "流量告警";
            case 5: return "MAC过滤";
            case 7: return "不合规报文告警";
            case 6: return "资产告警";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - EventController.formatReadStatus() - Unable to format ReadStaus: " + err.message);
    }
}

EventController.prototype.formatEventType = function (status) {
    try {
        switch (status) {
            case 1: return "警告";
            case 0: return "通过";
            case 2: return "阻断";
            case 3: return "通知";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - EventController.formatEventType() - Unable to format event type: " + err.message);
    }
}

EventController.prototype.formatRiskLevel = function (v) {
    try {
        switch (v) {
            case 0: return "低";
            case 1: return "中";
            case 2: return "高";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - EventController.formatRiskLevel() - Unable to format RiskLevel: " + err.message);
    }
}

EventController.prototype.formatDangerLevel = function (status) {
    try {
        switch (status) {
            case 0:
                return "低";
            case 1:
                return "中";
            case 2:
                return "高";
            default:
                return "";
        }
    }
    catch (err) {
        console.error("ERROR - EventController.formatDangerLevel() - Unable to get danger level via id: " + err.message);
    }
}

EventController.prototype.formatFilter = function (flag) {
    try {
        this.filter.action = "";
        this.filter.status = "";
        this.filter.sourceIp= $.trim(this.pViewHandle.find(this.pTxtSourceIP).val());
        this.filter.destinationIp = $.trim(this.pViewHandle.find(this.pTxtDestinationIP).val());
        this.filter.sourceName = $.trim(this.pViewHandle.find(this.pTxtSourceName).val());
        this.filter.destinationName = $.trim(this.pViewHandle.find(this.pTxtDestinationName).val());
        this.filter.appLayerProtocol = $.trim(this.pViewHandle.find(this.pTxtProtocol).val());
        this.filter.signatureName = this.pViewHandle.find(this.pDdlEventSource).val();
        this.filter.riskLevel = this.pViewHandle.find(this.pDdlRiskLevel).val();
        if (flag == "isready") {
            this.filter.sourceIp = "";
            this.filter.destinationIp = "";
            this.filter.appLayerProtocol = "";
            this.filter.status = "0";
            this.filter.signatureName = "";
            this.filter.starttime = "";
            this.filter.endtime = "";
        } else if (flag == "datetime") {
            this.filter.sourceIp = "";
            this.filter.destinationIp = "";
            this.filter.appLayerProtocol = "";
            this.filter.signatureName = "";
            var sysDateTime = $("#spanSystemTime").text().replace(/-/g, '/');
            var datetime = new Date();
            if (typeof (sysDateTime) != "undefined" && sysDateTime != "") {
                datetime = new Date(sysDateTime);
            }
            var years = datetime.getFullYear();
            var months = datetime.getMonth() + 1;
            var days = datetime.getDate();
            if (months < 10) {
                months = "0" + months;
            }
            if (days < 10) {
                days = "0" + days;
            }
            this.filter.starttime = years + "-" + months + "-" + days + " 00:00:00";
            this.filter.endtime = years + "-" + months + "-" + days + " 23:59:59";
        }
        else {
            this.filter.starttime=$.trim(this.pViewHandle.find(this.pTxtStartDateTime).val());
            this.filter.endtime=$.trim(this.pViewHandle.find(this.pTxtEndDateTime).val());
        }
    }
    catch (err) {
        console.error("ERROR - EventController.formatFilter() - Unable to get filter for searching: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.event.EventController", EventController);