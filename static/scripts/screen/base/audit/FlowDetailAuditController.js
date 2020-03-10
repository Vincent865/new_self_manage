function FlowDetailAuditController(viewHandle, elementId, mac,controller) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.controller = controller;
    this.mac = mac;
    this.pDdlTime2 = "#" + this.elementId + "_ddlTime2";
    this.pDivPieChart = this.elementId + "_divPieChart";
    this.pDivLineChart = this.elementId + "_divLineChart";
    this.pCusDivLineChart = this.elementId + "_cusDivLineChart";

    this.pTdFlowList = "#" + this.elementId + "_tdFlowList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotalFlow = "#" + this.elementId + "_lblTotalFlow";

    this.pTabHisFlow= "#" + this.elementId + "_tabHisFlow";
    this.pTabRealFlow= "#" + this.elementId + "_tabRealFlow";
    this.pHisHolder= "#" + this.elementId + "_hisHolder";
    this.pRealHolder= "#" + this.elementId + "_realHolder";

    this.currentTabId = "";
    this.pPager = null;
    this.pieChart = null;
    this.protocolFlowTimer = null;
    this.color = ['#3994d3', '#f98665', '#fac767', '#28daca', '#9569f9', '#e36585'];

    this.LineChart=null;
    this.FlowTimer=null;
}

FlowDetailAuditController.prototype.init = function () {
    try {
        var parent = this;

        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.AUDIT_FLOW_DETAIL), {
            elementId: parent.elementId
        });
        this.pViewHandle.find(".layui-layer-content").html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - FlowDetailAuditController.initShell() - Unable to initialize: " + err.message);
    }
}

FlowDetailAuditController.prototype.initControls = function () {
    try {
        var parent = this;
        //$(".flow-content").parent().css("background-color", "#E3E3E8")
        $(".row-cutbox>ul>li").on("click", function () {
            parent.currentTabId = "#" + $(this).attr("data-id");
            switch (parent.currentTabId) {
                case parent.pTabHisFlow:
                    $(parent.pHisHolder).show();
                    $(parent.pRealHolder).hide();
                    clearInterval(gloTimer.FlowTimer);
                    break;
                case parent.pTabRealFlow:
                    $(parent.pHisHolder).hide();
                    $(parent.pRealHolder).show();
                    clearInterval(gloTimer.FlowTimer);
                    parent.selectRealFlow();
                    parent.selectCusRealFlow();
                    break;
            }
            $(".row-cutbox>ul>li").removeClass("active");
            $(this).addClass("active");
        });

        $(this.pDdlTime2).on("change", function () {
            parent.pieChart = parent.initPieChart(parent.pDivPieChart, parent.selectDeviceProtocolPerc());
        });
        this.pieChart = this.initPieChart(this.pDivPieChart, parent.selectDeviceProtocolPerc());
        $(window).resize(function () {
            parent.pieChart.resize();
        });
    }
    catch (err) {
        console.error("ERROR - FlowDetailAuditController.initControls() - Unable to initialize control: " + err.message);
    }
}

FlowDetailAuditController.prototype.load = function () {
    try {
        this.pPager = null;
        this.selectDeviceProtocol(1);
    }
    catch (err) {
        console.error("ERROR - FlowDetailAuditController.load() - Unable to load: " + err.message);
    }
}

FlowDetailAuditController.prototype.selectDeviceProtocol = function (pageIndex) {
    var html = "";
    html += '<thead>';
    html += '<tr><th>协议名</th><th style="width:40%;">平均流量百分比(一周)</th><th style="width:20%;">更新时间</th></tr>';
    html += '</thead>';
    try {
        var parent = this;
        var loadIndex = layer.load(2);
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_FLOW_LIST;
        var data = {page:pageIndex,deviceId:parent.mac};
        var promise = URLManager.getInstance().ajaxCall(link, data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='3'>暂无数据</td></tr>";
            $(parent.pTdFlowList).html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tbody><tr>";
                        html += "<td style='text-align:center;padding-left:5px;'>" + result.rows[i][0] + "</td>";
                        html += "<td style='width:40%;text-align:center;'>" + (result.rows[i][1] * 100).toFixed(2) + "%</td>";
                        html += "<td style='width:20%;'>" + result.rows[i][2] + "</td>";
                        html += "</tr></tbody>";
                    }
                }
                else {
                    html += "<tr><td colspan='3'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='3'>暂无数据</td></tr>";
            }
            if (typeof (result.total) != "undefined") {
                $(parent.pLblTotalFlow).text(result.total);
            }

            $(parent.pTdFlowList).html(html);
            layer.close(loadIndex);

            if (parent.pPager == null) {
                parent.pPager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex, filters) {
                    parent.selectDeviceProtocol(pageIndex);
                });
                parent.pPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='3'>暂无数据</td></tr>";
        $(this.pTdFlowList).html(html);
        console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
    }
}
FlowDetailAuditController.prototype.selectRealFlow = function (pageIndex) {
    try {
        var parent = this;
        var data = {
            name: [],
            item: [],
            time: []
        };
        var order_list=[];
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PROTOCOL_INFO_FLOW;
        var promise = URLManager.getInstance().ajaxSyncCall(link,{deviceId:parent.mac});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.time) != "undefined") {
                data.time=result.time;
                var show_num=0;
                for (var i = 0; i < result.data.length; i++) {
                    var pro=result.data[i][0][0];
                    order_list.push(pro);
                    var name= pro=='tradition_pro'?'通用网络协议':pro=='unknown'?'未知':pro;
                    data.name.push(name);
                    var item ={name:name,data:result.data[i][1],type:'line'};
                    data.item.push(item);
                    if(result.data[i][2]!=0) show_num++;
                }
            }
            parent.LineChart=parent.initLineChart(parent.pDivLineChart,data,show_num);
            parent.flowcharts(result.nexttime,order_list);
        });
    }
    catch (err) {
        console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
    }
};
FlowDetailAuditController.prototype.selectCusRealFlow = function (pageIndex) {
    try {
        var parent = this;
        parent.dict={};
        var data = {
            name: [],
            item: [],
            time: []
        };
        var order_list=[];
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PROTOCOL_CUS_INFO_FLOW;
        var promise = URLManager.getInstance().ajaxSyncCall(link,{deviceId:parent.mac});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.time) != "undefined") {
                data.time=result.time;
                var show_num=0;
                for (var i = 0; i < result.data.length; i++) {
                    var pro=result.data[i][0][0];
                    parent.dict[pro]=result.data[i][3];
                    order_list.push(result.data[i][3]);
                    var name= pro=='tradition_pro'?'通用网络协议':pro=='unknown'?'未知':pro;
                    data.name.push(name);
                    var item ={name:name,data:result.data[i][1],type:'line'};
                    data.item.push(item);
                    if(result.data[i][2]!=0) show_num++;
                }
            }
            parent.cusLineChart=parent.initLineChart(parent.pCusDivLineChart,data,show_num);
            parent.cusflowcharts(result.nexttime,order_list);
        });
    }
    catch (err) {
        console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
    }
};

FlowDetailAuditController.prototype.initLineChart = function (id, data,show_num) {
    var parent = this;
    var charts=document.getElementById(id);
    var line = echarts.init(charts);
    var selectedList={};
    for(var i=show_num;i<=data.name.length;i++){
        var name=data.name[i];
        selectedList[name]=false;
    }
    var option = {
        tooltip: {
            trigger: 'axis',
            confine:true,
            enterable:true,
            textStyle:{
                fontSize:13
            }
        },
        legend: {
            data:data.name,
            selected:selectedList
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: [{
            type: 'category',
            boundaryGap: false,
            data: data.time
        }],
        yAxis: [
            {
                type : 'value',
                name: '速率（Kbps）'
            }
        ],
        series:data.item
    };
    line.setOption(option);
    return line;
}

FlowDetailAuditController.prototype.flowcharts = function (nexttime,proto_order) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PROTOCOL_INFO_RRFRESH;
        var nexttimeL=nexttime;
        gloTimer.FlowTimer = setInterval(function () {
            var promise = URLManager.getInstance().ajaxSyncCall(link,{deviceId:parent.mac,nexttime:nexttimeL,proto_order:proto_order});
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
            });
            promise.done(function (result) {
                if(result.refersh==0){
                    nexttimeL=result.nexttime;
                    //var addData=[],n=,item=[];
                    for(var i=1;i<=result.time.length;i++){  //按时间点循环
                        var addData=[];
                        for(var j=0;j<result.data.length;j++){
                            addData.push([
                                j,
                                result.data[j][1][i-1],
                                false,
                                false
                            ]);
                        }
                        addData[0][4]=result.time[i-1];
                        parent.LineChart.addData(addData);
                    }
                }else{
                    clearInterval(gloTimer.FlowTimer);
                    parent.selectRealFlow();
                    return;
                }
            });
        }, 20000);
    }
    catch (err) {
        console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
    }
};

FlowDetailAuditController.prototype.cusflowcharts = function (nexttime,proto_order) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_CUS_PROTOCOL_INFO_RRFRESH;
        var nexttimeL=nexttime;
        gloTimer.cusFlowTimer = setInterval(function () {
            var promise = URLManager.getInstance().ajaxSyncCall(link,{deviceId:parent.mac,nexttime:nexttimeL,proto_order:proto_order});
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
            });
            promise.done(function (result) {
                if(result.refersh==0){
                    nexttimeL=result.nexttime;
                    //var addData=[],n=,item=[];
                    for(var i=1;i<=result.time.length;i++){  //按时间点循环
                        var addData=[];
                        for(var j=0;j<result.data.length;j++){
                            addData.push([
                                j,
                                result.data[j][1][i-1],
                                false,
                                false
                            ]);
                        }
                        addData[0][4]=result.time[i-1];
                        parent.cusLineChart.addData(addData);
                    }
                }else{
                    clearInterval(gloTimer.cusFlowTimer);
                    parent.selectCusRealFlow();
                    return;
                }
            });
        }, 20000);
    }
    catch (err) {
        console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
    }
};

FlowDetailAuditController.prototype.selectDeviceProtocolPerc = function () {
    var html = "";
    try {
        var parent = this;
        var data = {
            name: [],
            item: []
        };
        var timeFlag = $(this.pDdlTime2 + " option:selected").val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_PROTOCOL_FLOW;
        var dt = { timeDelta: timeFlag ,mac:parent.mac};
        var promise = URLManager.getInstance().ajaxSyncCall(link,dt);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                for (var i = 0; i < result.rows.length; i++) {
                    if (result.rows[i][1] != 0) {
                        var color = parent.color[i];
                        if (result.rows[i][0].toLowerCase() == "其他") {
                            color = parent.color[5];
                        }
                        var item = parent.createPieStruct(result.rows[i][0], result.rows[i][1], color);
                        data.name.push(result.rows[i][0]);
                        data.item.push(item);
                    }
                }
            }
        });
        return data;
    }
    catch (err) {
        console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
        return data;
    }
}

FlowDetailAuditController.prototype.initPieChart = function (id, data) {
    var parent = this;
    var pie = echarts.init(document.getElementById(id));
    var option = {
        tooltip: {
            trigger: 'item',
            formatter: "{d}%"
        },
        legend: {
            orient: 'vertical',
            x: 'right',
            data: data.name
        },
        calculable: true,
        series: [
            {
                name: 'pie',
                type: 'pie',
                radius: ['50%', '80%'],
                center: ['40%', '50%'],
                data: data.item
            }
        ]
    };

    pie.setOption(option);

    return pie;
}

FlowDetailAuditController.prototype.createPieStruct = function (name, value, color) {
    return {
        name: name,
        value: value,
        itemStyle: {
            normal:
                {
                    color: color,
                    label: {
                        show: false,
                        formatter: '{d}%',
                        textStyle: {
                            fontSize: 14,
                            fontFamily: "微软雅黑"
                        },
                        position: 'inner'
                    },
                    labelLine: {
                        show: false
                    }
                }
        }
    }
}

ContentFactory.assignToPackage("tdhx.base.audit.FlowDetailAuditController", FlowDetailAuditController);