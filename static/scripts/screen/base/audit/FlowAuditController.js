function FlowAuditController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;


    this.pBtnOne = "#" + this.elementId + "_btnEditOne";
    this.pBtnTwo = "#" + this.elementId + "_btnEditTwo";
    this.pBtnThree = "#" + this.elementId + "_btnEditThree";
    this.pBtnFour = "#" + this.elementId + "_btnEditFour";

    this.pBtnSaveOne = "#" + this.elementId + "_btnSaveOne";
    this.pBtnSaveTwo = "#" + this.elementId + "_btnSaveTwo";
    this.pBtnSaveThree = "#" + this.elementId + "_btnSaveThree";
    this.pBtnSaveFour = "#" + this.elementId + "_btnSaveFour";

    this.pBtnCancleOne = "#" + this.elementId + "_btnCancleOne";
    this.pBtnCancleTwo = "#" + this.elementId + "_btnCancleTwo";
    this.pBtnCancleThree = "#" + this.elementId + "_btnCancleThree";
    this.pBtnCancleFour = "#" + this.elementId + "_btnCancleFour";

    this.pBtnDeleteOne = "#" + this.elementId + "_btnDeleteOne";
    this.pBtnDeleteTwo = "#" + this.elementId + "_btnDeleteTwo";
    this.pBtnDeleteThree = "#" + this.elementId + "_btnDeleteThree";
    this.pBtnDeleteFour = "#" + this.elementId + "_btnDeleteFour";

    this.pBtnPlOne = "#" + this.elementId + "_btnPluseOne";
    this.pBtnPlTwo = "#" + this.elementId + "_btnPluseTwo";
    this.pBtnPlThree = "#" + this.elementId + "_btnPluseThree";
    this.pBtnPlFour = "#" + this.elementId + "_btnPluseFour";

    this.pBtnRdOne = "#" + this.elementId + "_btnReduceOne";
    this.pBtnRdTwo = "#" + this.elementId + "_btnReduceTwo";
    this.pBtnRdThree = "#" + this.elementId + "_btnReduceThree";
    this.pBtnRdFour = "#" + this.elementId + "_btnReduceFour";

    this.pSliderOne = "#" + this.elementId + "_sliderOne";
    this.pSliderTwo = "#" + this.elementId + "_sliderTwo";
    this.pSliderThree = "#" + this.elementId + "_sliderThree";
    this.pSliderFour = "#" + this.elementId + "_sliderFour";

    this.pChartOne = this.elementId + "_divChartOne";
    this.pChartTwo = this.elementId + "_divChartTwo";
    this.pChartThree = this.elementId + "_divChartThree";
    this.pChartFour = this.elementId + "_divChartFour";

    this.pTdFlowList = "#" + this.elementId + "_tdFlowList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotalFlow = "#" + this.elementId + "_lblTotalFlow";
    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnFilter = "#" + this.elementId + "_btnFilter";
    this.pDivFilter = "#" + this.elementId + "_divFilter";
    this.pBtnSearch = "#" + this.elementId + "_btnSearch";

    this.pDivUpOne = "#" + this.elementId + "_divUpOne";
    this.pDivDownOne = "#" + this.elementId + "_divDownOne";
    this.pDivUpTwo = "#" + this.elementId + "_divUpTwo";
    this.pDivDownTwo = "#" + this.elementId + "_divDownTwo";
    this.pDivUpThree = "#" + this.elementId + "_divUpThree";
    this.pDivDownThree = "#" + this.elementId + "_divDownThree";
    this.pDivUpFour = "#" + this.elementId + "_divUpFour";
    this.pDivDownFour = "#" + this.elementId + "_divDownFour";

    this.pValueUpOne = "#" + this.elementId + "_valueUpOne";
    this.pValueDownOne = "#" + this.elementId + "_valueDownOne";
    this.pValueUpTwo = "#" + this.elementId + "_valueUpTwo";
    this.pValueDownTwo = "#" + this.elementId + "_valueDownTwo";
    this.pValueUpThree = "#" + this.elementId + "_valueUpThree";
    this.pValueDownThree = "#" + this.elementId + "_valueDownThree";
    this.pValueUpFour = "#" + this.elementId + "_valueUpFour";
    this.pValueDownFour = "#" + this.elementId + "_valueDownFour";

    this.pTxtDevName = "#" + this.elementId + "_txtDevName";
    this.pTxtDevIp = "#" + this.elementId + "_txtDevIp";
    this.pTxtDevMac = "#" + this.elementId + "_txtDevMac";

    this.pPager = null;
    this.pDetailController = null;

    this.lineChart = null;
    this.ChartOne = null;
    this.ChartTwo = null;
    this.ChartThree = null;
    this.ChartFour = null;
    this.timer = {
        FlowTimer1: null,
        FlowTimer2: null,
        FlowTimer3: null,
        FlowTimer4: null
    };
    this.pNextOne = "";
    this.pNextTwo = "";
    this.pNextThree = "";
    this.pNextFour = "";

    this.pMaxInterOne = 100;

    this.deviceArry = [];
    this.deviceNameArry = [];
    this.deviceMac = [];
    this.deviceIp = [];
    this.deviceStatus = [1, 1, 1, 1];

    this.filter = {
        page: 1,
        devName:"",
        devIp:"",
        devMac:""
    };
}

FlowAuditController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
            Constants.TEMPLATES.AUDIT_FLOW_DETAIL],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.init() - Unable to initialize: " + err.message);
    }
}

FlowAuditController.prototype.initShell = function () {
    try {
        var parent = this;

        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.AUDIT_FLOW), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.initShell() - Unable to initialize: " + err.message);
    }
}

FlowAuditController.prototype.initControls = function () {
    try {
        var parent = this;
        //刷新
        $(this.pBtnRefresh).on("click", function () {
            var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
            parent.pPager = null;
            parent.clearTimer();
            parent.selectFlow(1);
            parent.buildDeviceChart();
            layer.close(loadIndex);
        });
        this.pViewHandle.find(this.pBtnFilter).on("click", function () {
            parent.pViewHandle.find(parent.pTxtDevName).val("");
            parent.pViewHandle.find(parent.pTxtDevIp).val("");
            parent.pViewHandle.find(parent.pTxtDevMac).val("");
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            parent.pViewHandle.find(parent.pDivFilter).toggle();
        });
        this.pViewHandle.find(this.pBtnSearch).on("click", function () {
            var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
            parent.pPager = null;
            parent.clearTimer();
            parent.selectFlow(1);
            parent.buildDeviceChart();
            layer.close(loadIndex);
        });
        $(this.pBtnDeleteOne).on("click", function () {
            parent.deleteDeviceValue(0);
            $(parent.pBtnPlOne).hide();
            $(parent.pBtnRdOne).hide();
            $(parent.pSliderOne).hide();
        });
        $(this.pBtnDeleteTwo).on("click", function () {
            parent.deleteDeviceValue(1);
            $(parent.pBtnPlTwo).hide();
            $(parent.pBtnRdTwo).hide();
            $(parent.pSliderTwo).hide();
        });
        $(this.pBtnDeleteThree).on("click", function () {
            parent.deleteDeviceValue(2);
            $(parent.pBtnPlThree).hide();
            $(parent.pBtnRdThree).hide();
            $(parent.pSliderThree).hide();
        });
        $(this.pBtnDeleteFour).on("click", function () {
            parent.deleteDeviceValue(3);
            $(parent.pBtnPlFour).hide();
            $(parent.pBtnRdFour).hide();
            $(parent.pSliderFour).hide();
        });
        $(this.pValueUpOne).on("change", function () {
                $(parent.pValueUpOne).val(Validation.validateNum1($(parent.pValueUpOne).val()));
        });
        $(this.pValueDownOne).on("change", function () {
            $(parent.pValueDownOne).val(Validation.validateNum1($(parent.pValueDownOne).val()));
        });
        $(this.pValueUpTwo).on("change", function () {
            $(parent.pValueUpTwo).val(Validation.validateNum1($(parent.pValueUpTwo).val()));
        });
        $(this.pValueDownTwo).on("change", function () {
            $(parent.pValueDownTwo).val(Validation.validateNum1($(parent.pValueDownTwo).val()));
        });
        $(this.pValueUpThree).on("change", function () {
            $(parent.pValueUpThree).val(Validation.validateNum1($(parent.pValueUpThree).val()));
        });
        $(this.pValueDownThree).on("change", function () {
            $(parent.pValueDownThree).val(Validation.validateNum1($(parent.pValueDownThree).val()));
        });
        $(this.pValueUpFour).on("change", function () {
            $(parent.pValueUpFour).val(Validation.validateNum1($(parent.pValueUpFour).val()));
        });
        $(this.pValueDownFour).on("change", function () {
            $(parent.pValueDownFour).val(Validation.validateNum1($(parent.pValueDownFour).val()));
        });
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.initControls() - Unable to initialize control: " + err.message);
    }
}

FlowAuditController.prototype.load = function () {
    try {
        this.pPager = null;
        this.selectFlow(1);
        this.buildDeviceChart();
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.load() - Unable to load: " + err.message);
    }
}

FlowAuditController.prototype.selectFlow = function (pageIndex) {
    var html = "<thead>";
    html += '<tr>';
    html += '<th>设备名称</th>';
    html += '<th style="width:7%;">IP地址</th>';
    html += '<th style="width:10%;">MAC地址</th>';
    html += '<th style="width:13.5%;">平均输入速率(1小时)</th>';
    html += '<th style="width:13.5%;"">平均输出速率(1小时)</th>';
    html += '<th style="width:11%;"">平均流量百分比</th>';
    //html += '<th style="width:10%;"">更新时间</th>';
    html += '<th style="width:8%;">内容</th>';
    html += '</thead>';
    try {
        var parent = this;
        parent.deviceArry = [];
        parent.deviceNameArry = [];
        parent.deviceMac = [];
        parent.deviceIp = [];
        var loadIndex = layer.load(2);
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_FLOW_LIST;
        this.filter.page = pageIndex;
        this.filter.devName = $.trim(this.pViewHandle.find(this.pTxtDevName).val());
        this.filter.devIp = $.trim(this.pViewHandle.find(this.pTxtDevIp).val());
        this.filter.devMac = $.trim(this.pViewHandle.find(this.pTxtDevMac).val());

        var promise = URLManager.getInstance().ajaxCallByURL(link, "get", this.filter, false);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='7'>暂无数据</th></tr>";
            $(parent.pTdFlowList).html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    //parent.total=result.total;
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tbody><tr>";
                        html += "<td title='" + result.rows[i][5] + "'>" + FormatterManager.stripText(result.rows[i][5], 18) + "</td>";
                        html += "<td style='width:7%;text-align:center;'>" + result.rows[i][0] + "</td>";
                        html += "<td style='width:10%;text-align:center;'>" + result.rows[i][1].toUpperCase() + "</td>";
                        html += "<td style='width:13.5%;text-align:center;'>" + (result.rows[i][2]).toFixed(2) + " Kbps</td>";
                        html += "<td style='width:13.5%;text-align:center;'>" + (result.rows[i][3]).toFixed(2) + " Kbps</td>";
                        html += "<td style='width:11%;text-align:center;'>" + (result.rows[i][6] * 100).toFixed(2) + "%</td>";
                        //html += "<td style='width:10%;'>" + result.rows[i][4] + "</td>";
                        html += "<td style='color:#1ca826;width:8%;'><button class='btn btn-default btn-xs btn-color-details' data-key='" + result.rows[i][7] + "' data-name='"+result.rows[i][5]+"'><i class='fa fa-file-text-o'></i>详情</button></td>";
                        html += "</tr></tbody>";
                        parent.deviceArry.push(result.rows[i][7]);
                        parent.deviceNameArry.push(result.rows[i][5]);
                        parent.deviceMac.push(result.rows[i][1]);
                        parent.deviceIp.push(result.rows[i][0]);
                    }
                    //parent.total?$(parent.pLblTotal).text(parent.total):$(parent.pLblTotal).text(0);
                }
                else {
                    html += "<tbody><tr><td colspan='7'>暂无数据</td></tr><tbody>";
                }
            }
            else {
                html += "<tbody><tr><td colspan='7'>暂无数据</td></tr><tbody>";
            }
            if (typeof (result.total) != "undefined") {
                $(parent.pLblTotalFlow).text(result.total);
            }

            $(parent.pTdFlowList).html(html);
            layer.close(loadIndex);

            $(parent.pTdFlowList).find("button[class='btn btn-default btn-xs btn-color-details']").on("click", function () {
                var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
                var mac = $(this).attr("data-key");
                var ip = $(this).attr("ip");
                var devname = $(this).attr("data-name");
                var dialogHandler = $("<div />");
                var width = parent.pViewHandle.width() - 10 + "px";
                var height = $(window).height() - 100 + "px";
                var openDialog = layer.open({
                    type: 1,
                    title: "设备流量信息（"+devname+"）",
                    area: [width, height],
                    offset: ["82px", "200px"],
                    shade: [0.5, '#393D49'],
                    content: dialogHandler.html(),
                    success: function (layero, index) {
                        parent.pDetailController = new tdhx.base.audit.FlowDetailAuditController(layero, parent.elementId + "_dialog", mac, parent);
                        parent.pDetailController.init();
                        layer.close(loadIndex);
                        $(window).on("resize", function () {
                            var pwidth = parent.pViewHandle.width() - 10 + "px";
                            var pheight = $(window).height() -100 + "px";
                            layero.width(pwidth);
                            layero.height(pheight);
                        })
                    }
                });
            });

            if (parent.pPager == null) {
                parent.pPager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 4, result.total, function (pageIndex, filters) {
                    parent.selectFlow(pageIndex);
                    parent.buildDeviceChart();
                    parent.clearTimer();
                });
                parent.pPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tbody><tr><td colspan='7'>暂无数据</td></tr><tbody>";
        $(this.pTdFlowList).html(html);
        console.error("ERROR - FlowAuditController.selectFlow() - Unable to get all events: " + err.message);
    }
}
//构建Chart
FlowAuditController.prototype.buildDeviceChart = function () {
    try {
        var parent = this;
        $("#" + parent.elementId + "_divFlow1").hide();
        $("#" + parent.elementId + "_divFlow2").hide();
        $("#" + parent.elementId + "_divFlow3").hide();
        $("#" + parent.elementId + "_divFlow4").hide();
        if (parent.deviceArry.length > 0) {
            for (var i = 0; i < parent.deviceArry.length; i++) {
                switch (i) {
                    case 0:
                        $("#" + parent.elementId + "_divFlow1").show();
                        parent.initDevice1(parent.deviceArry[i], parent.deviceNameArry[i]);
                        break;
                    case 1:
                        $("#" + parent.elementId + "_divFlow2").show();
                        parent.initDevice2(parent.deviceArry[i], parent.deviceNameArry[i]);
                        break;
                    case 2:
                        $("#" + parent.elementId + "_divFlow3").show();
                        parent.initDevice3(parent.deviceArry[i], parent.deviceNameArry[i]);
                        break;
                    case 3:
                        $("#" + parent.elementId + "_divFlow4").show();
                        parent.initDevice4(parent.deviceArry[i], parent.deviceNameArry[i]);
                        break;
                }
            }
        }
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.buildDeviceChart() - Unable to buildDeviceChart: " + err.message);
    }
}

FlowAuditController.prototype.selectDeviceFlow = function (id, status) {
    var html = "";
    try {
        var parent = this;
        var data = {
            high_line: 0,
            low_line: 0,
            max_val: 0,
            x: [],
            y: []
        };
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_FLOW_NEW;
        var dt = { dev: id }
        var promise = URLManager.getInstance().ajaxSyncCall(link, dt);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined") {
                data.high_line = result.high_line;
                data.low_line = result.low_line;
                data.max_val = result.max_val;
                switch (status) {
                    case 1:
                        parent.pNextOne = result.next_time;
                        break;
                    case 2:
                        parent.pNextTwo = result.next_time;
                        break;
                    case 3:
                        parent.pNextThree = result.next_time;
                        break;
                    case 4:
                        parent.pNextFour = result.next_time;
                        break;
                }

                for (var i = 0; i < result.points.length; i++) {
                    data.y.push(result.points[i]);
                }
                for (var i = 0; i < result.timePoints.length; i++) {
                    data.x.push(result.timePoints[i]);
                }
            }
        });
        return data;
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.selectFlow() - Unable to get all events: " + err.message);
        return data;
    }
}

FlowAuditController.prototype.selectSingleTotalFlow = function (id, time, status) {
    var html = "";
    try {
        var parent = this;
        var data = { x: '', y: 0 };
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_PROTOCOL_FLOW_NEW;
        var data = { dev: parent.deviceArry[status-1], time: time }
        var promise = URLManager.getInstance().ajaxSyncCall(link, data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.point) != "undefined" && typeof (result.timePoint) != "undefined"
                && result.timePoint != "undefined") {
                data.x = result.timePoint;
                data.y = result.point;
                switch (status) {
                    case 1:
                        parent.pNextOne = result.next_time;
                        break;
                    case 2:
                        parent.pNextTwo = result.next_time;
                        break;
                    case 3:
                        parent.pNextThree = result.next_time;
                        break;
                    case 4:
                        parent.pNextFour = result.next_time;
                        break;
                }
            }
        });
        return data;
    }
    catch (err) {
        return data;
        console.error("ERROR - FlowAuditController.selectSingleTotalFlow() - Unable to get single point: " + err.message);
    }
}
//设置阈值
FlowAuditController.prototype.setDeviceRange = function (id, h, l,index) {
    var html = "";
    try {
        var parent = this;
        var data = { dev: id, high: h, low: l, mac: parent.deviceMac[index - 1], flag: 1, ip: parent.deviceIp[index - 1] };
        if (parent.deviceStatus[index - 1] == 0) {
            data.flag = 2;
            parent.deviceStatus[index - 1] = 1;
        }
        else {
            data.flag = 1;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].SET_DEVICE_RANGE_NEW;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("阈值设置失败", { icon: 5 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && result.status == 0) {
                layer.alert("阈值设置失败", { icon: 5 });
            }
        });

        return data;
    }
    catch (err) {
        return data;
        console.error("ERROR - FlowAuditController.setDeviceRange() - Unable to setDeviceRange: " + err.message);
    }
}

//设备流量图
FlowAuditController.prototype.initFlowChart = function (id, data, h, l, m, title) {
    var parent = this;
    var pie = echarts.init(document.getElementById(id));
    var option = {
        title: {
            x: 'center',
            y: 'top',
            text: title,
            subtext: '单位：Kbps',
            textStyle:
                {
                    fontSize: 14,
                    fontWeight: 'bolder',
                    fontFamily: '微软雅黑',
                    color: '#666'
                }
        },
        calculable: false,
        tooltip: {
            trigger: 'axis',
            formatter: '{b}: {c}Kbps'
        },
        grid: { height: '120' },
        xAxis: [
            {
                type: 'category',
                axisLine: {
                    show: true,
                    lineStyle: {
                        color: '#ccc',
                        width: 1,
                        type: 'solid'
                    }
                },
                boundaryGap: false,
                data: data.x
            }
        ],
        yAxis: [
            {
                type: 'value',
                min: 0,
                max: m >= h ? m*1.1 : h*1.1,
                boundaryGap: false,
                axisLabel: {
                    formatter: function (v) {
                        if (v < 10)
                        {
                            return v.toFixed(1);
                        }
                        else {
                            return Math.ceil(v);
                        }
                        
                    }
                },
                axisLine: {
                    show: true,
                    lineStyle: {
                        color: '#ccc',
                        width: 1,
                        type: 'solid'
                    }
                }
            }
        ],
        series: [
            {
                type: 'line',
                symbol: 'none',
                itemStyle: {
                    normal: {
                        areaStyle: {
                            type: 'default',
                            color: '#6dc7be'
                        },
                        lineStyle: {
                            color: '#6dc7be'
                        }
                    }
                },
                data: data.y,
                markLine: {

                    data: [
                         [
                            { name: '高阈值', value: h == -1 ? 0 : h, xAxis: -1, yAxis: h, itemStyle: { normal: { color: '#c50601' } } },
                            { xAxis: 10000000000, yAxis: h }
                         ],
                          [
                            { name: '低阈值', value: l == -1 ? 0 : l, xAxis: -1, yAxis: l, itemStyle: { normal: { color: '#1ca826' } } },
                            { xAxis: 10000000000, yAxis: l }
                          ]
                    ]
                }
            }
        ]
    };
    pie.setOption(option);
    return pie;
}
//设备初始化1
FlowAuditController.prototype.initDevice1 = function (id, name) {
    try {
        var parent = this;
        var deviceData = parent.selectDeviceFlow(id, 1);
        parent.ChartOne = this.initFlowChart(parent.pChartOne, deviceData, deviceData.high_line, deviceData.low_line, deviceData.max_val, name);
        if (deviceData.high_line == -1) {
            parent.deviceStatus[0] = 0;
            $(parent.pBtnDeleteOne).hide();
        }
        else {
            parent.deviceStatus[0] = 1;
            $(parent.pBtnDeleteOne).show();
        }
        $(parent.pValueUpOne).val(deviceData.high_line == -1 ? 0 : deviceData.high_line);
        $(parent.pValueDownOne).val(deviceData.low_line == -1 ? 0 : deviceData.low_line);
        $(this.pSliderOne).slider({
            orientation: "vertical",
            range: true,
            values: [deviceData.low_line, deviceData.high_line],
            max: deviceData.high_line >= deviceData.max_val ? deviceData.high_line + 100 : deviceData.max_val + 100,
            slide: function (event, ui) {
                parent.ChartOne = parent.initFlowChart(parent.pChartOne, deviceData, ui.values[1], ui.values[0], deviceData.max_val, name);
                $(parent.pValueUpOne).val(ui.values[1]);
                $(parent.pValueDownOne).val(ui.values[0]);
            }
        });
        $(this.pBtnOne).unbind("click");
        $(this.pBtnOne).on("click", function () {
            $(parent.pBtnCancleOne).show();
            $(parent.pBtnPlOne).show();
            $(parent.pBtnRdOne).show();
            $(parent.pSliderOne).show();
            $(parent.pBtnSaveOne).show();
            $(parent.pDivUpOne).show();
            $(parent.pDivDownOne).show();
            $(parent.pBtnOne).hide();
            //clearInterval(parent.timer.FlowTimer1);
        });
        $(this.pBtnCancleOne).unbind("click");
        $(this.pBtnCancleOne).on("click", function () {
            $(parent.pBtnCancleOne).hide();
            $(parent.pBtnPlOne).hide();
            $(parent.pBtnRdOne).hide();
            $(parent.pSliderOne).hide();
            $(parent.pBtnSaveOne).hide();
            $(parent.pDivUpOne).hide();
            $(parent.pDivDownOne).hide();
            $(parent.pBtnOne).show();
            parent.initDevice1(id, name);
        });
        $(this.pBtnSaveOne).unbind("click");
        $(this.pBtnSaveOne).on("click", function () {
            if (parseInt($(parent.pValueUpOne).val()) < parseInt($(parent.pValueDownOne).val())) {
                layer.alert("高阈值不能小于低阈值,请重新设置", { icon: 5 });
                return false;
            }
            $(parent.pBtnCancleOne).hide();
            $(parent.pBtnPlOne).hide();
            $(parent.pBtnRdOne).hide();
            $(parent.pSliderOne).hide();
            $(parent.pBtnSaveOne).hide();
            $(parent.pDivUpOne).hide();
            $(parent.pDivDownOne).hide();
            $(parent.pBtnOne).show();
            
            //parent.setIntervalOne(id);
            parent.setDeviceRange(id, $(parent.pValueUpOne).val(), $(parent.pValueDownOne).val(), 1);
            $(parent.pBtnDeleteOne).show();
            parent.ChartOne = parent.initFlowChart(parent.pChartOne, deviceData, parseInt($(parent.pValueUpOne).val()), parseInt($(parent.pValueDownOne).val()), deviceData.max_val, name);
            $(parent.pSliderOne).slider("value", [$(parent.pValueDownOne).val(), $(parent.pValueUpOne).val()]);
            
        });
        $(this.pBtnPlOne).unbind("click");
        $(this.pBtnPlOne).on("click", function () {
            $(parent.pSliderOne).slider("option", "max", $(parent.pSliderOne).slider("option", "max") * 2);
            if ($(parent.pSliderOne).slider("option", "max") > 102400000)
            {
                $(parent.pSliderOne).slider("option", "max", 102400000);
            }
        });
        $(this.pBtnRdOne).unbind("click");
        $(this.pBtnRdOne).on("click", function () {
            if ($(parent.pSliderOne).slider("option", "max") >= parent.pMaxInterOne) {
                $(parent.pSliderOne).slider("option", "max", $(parent.pSliderOne).slider("option", "max") / 2);

            }
        });
        //得到设备流量图
        $(window).resize(function () {
            parent.ChartOne.resize();
        });
        parent.setIntervalOne(id);
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.initDevice1() - Unable to initDevice1: " + err.message);
    }
}
//设备初始化2
FlowAuditController.prototype.initDevice2 = function (id, name) {
    try {
        var parent = this;
        var deviceData = parent.selectDeviceFlow(id, 2);
        parent.ChartTwo = this.initFlowChart(parent.pChartTwo, deviceData, deviceData.high_line, deviceData.low_line, deviceData.max_val, name);
        if (deviceData.high_line == -1) {
            parent.deviceStatus[1] = 0;
            $(parent.pBtnDeleteTwo).hide();
        }
        else {
            parent.deviceStatus[1] = 1;
            $(parent.pBtnDeleteTwo).show();
        }
        $(parent.pValueUpTwo).val(deviceData.high_line == -1 ? 0 : deviceData.high_line);
        $(parent.pValueDownTwo).val(deviceData.low_line == -1 ? 0 : deviceData.low_line);
        $(this.pSliderTwo).slider({
            orientation: "vertical",
            range: true,
            values: [deviceData.low_line, deviceData.high_line],
            max: deviceData.high_line >= deviceData.max_val ? deviceData.high_line + 100 : deviceData.max_val + 100,
            slide: function (event, ui) {
                parent.ChartTwo = parent.initFlowChart(parent.pChartTwo, deviceData, ui.values[1], ui.values[0], deviceData.max_val, name);
                $(parent.pValueUpTwo).val(ui.values[1]);
                $(parent.pValueDownTwo).val(ui.values[0]);
            }
        });
        $(this.pBtnTwo).unbind("click");
        $(this.pBtnTwo).on("click", function () {
            $(parent.pBtnCancleTwo).show();
            $(parent.pBtnPlTwo).show();
            $(parent.pBtnRdTwo).show();
            $(parent.pSliderTwo).show();
            $(parent.pBtnSaveTwo).show();
            $(parent.pDivUpTwo).show();
            $(parent.pDivDownTwo).show();
            $(parent.pBtnTwo).hide();
            //clearInterval(parent.timer.FlowTimer2);

        });
        $(this.pBtnCancleTwo).unbind("click");
        $(this.pBtnCancleTwo).on("click", function () {
            $(parent.pBtnCancleTwo).hide();
            $(parent.pBtnPlTwo).hide();
            $(parent.pBtnRdTwo).hide();
            $(parent.pSliderTwo).hide();
            $(parent.pBtnSaveTwo).hide();
            $(parent.pDivUpTwo).hide();
            $(parent.pDivDownTwo).hide();
            $(parent.pBtnTwo).show();
            parent.initDevice2(id, name);
        });
        $(this.pBtnSaveTwo).unbind("click");
        $(this.pBtnSaveTwo).on("click", function () {
            if (parseInt($(parent.pValueUpTwo).val()) < parseInt($(parent.pValueDownTwo).val())) {
                layer.alert("高阈值不能小于低阈值,请重新设置", { icon: 5 });
                return false;
            }
            $(parent.pBtnCancleTwo).hide();
            $(parent.pBtnPlTwo).hide();
            $(parent.pBtnRdTwo).hide();
            $(parent.pSliderTwo).hide();
            $(parent.pBtnSaveTwo).hide();
            $(parent.pDivUpTwo).hide();
            $(parent.pDivDownTwo).hide();
            $(parent.pBtnTwo).show();
            //parent.setIntervalTwo(id);
            parent.setDeviceRange(id, $(parent.pValueUpTwo).val(), $(parent.pValueDownTwo).val(), 2);
            $(parent.pBtnDeleteTwo).show();
            parent.ChartTwo = parent.initFlowChart(parent.pChartTwo, deviceData, parseInt($(parent.pValueUpTwo).val()), parseInt($(parent.pValueDownTwo).val()), deviceData.max_val, name);
            $(parent.pSliderTwo).slider("value", [$(parent.pValueDownTwo).val(), $(parent.pValueUpTwo).val()]);

        });
        $(this.pBtnPlTwo).unbind("click");
        $(this.pBtnPlTwo).on("click", function () {
            $(parent.pSliderTwo).slider("option", "max", $(parent.pSliderTwo).slider("option", "max") * 2);
            if ($(parent.pSliderTwo).slider("option", "max") > 102400000) {
                $(parent.pSliderTwo).slider("option", "max", 102400000);
            }
        });
        $(this.pBtnRdTwo).unbind("click");
        $(this.pBtnRdTwo).on("click", function () {
            if ($(parent.pSliderTwo).slider("option", "max") >= parent.pMaxInterOne) {
                $(parent.pSliderTwo).slider("option", "max", $(parent.pSliderTwo).slider("option", "max") / 2);

            }
        });

        //得到设备流量图

        $(window).resize(function () {
            parent.ChartTwo.resize();
        });
        parent.setIntervalTwo(id);

    }
    catch (err) {
        console.error("ERROR - FlowAuditController.initDevice2() - Unable to initDevice2: " + err.message);
    }
}
//设备初始化3
FlowAuditController.prototype.initDevice3 = function (id, name) {
    try {
        var parent = this;
        var deviceData = parent.selectDeviceFlow(id, 3);
        parent.ChartThree = this.initFlowChart(parent.pChartThree, deviceData, deviceData.high_line, deviceData.low_line, deviceData.max_val, name);
        if (deviceData.high_line == -1) {
            parent.deviceStatus[2] = 0;
            $(parent.pBtnDeleteThree).hide();
        }
        else {
            parent.deviceStatus[2] = 1;
            $(parent.pBtnDeleteThree).show();
        }
        $(parent.pValueUpThree).val(deviceData.high_line == -1 ? 0 : deviceData.high_line);
        $(parent.pValueDownThree).val(deviceData.low_line == -1 ? 0 : deviceData.low_line);
        $(this.pSliderThree).slider({
            orientation: "vertical",
            range: true,
            values: [deviceData.low_line, deviceData.high_line],
            max: deviceData.high_line >= deviceData.max_val ? deviceData.high_line + 100 : deviceData.max_val + 100,
            slide: function (event, ui) {
                parent.ChartThree = parent.initFlowChart(parent.pChartThree, deviceData, ui.values[1], ui.values[0], deviceData.max_val, name);
                $(parent.pValueUpThree).val(ui.values[1]);
                $(parent.pValueDownThree).val(ui.values[0]);
            }
        });
        $(this.pBtnThree).unbind("click");
        $(this.pBtnThree).on("click", function () {
            $(parent.pBtnCancleThree).show();
            $(parent.pBtnPlThree).show();
            $(parent.pBtnRdThree).show();
            $(parent.pSliderThree).show();
            $(parent.pBtnSaveThree).show();
            $(parent.pDivUpThree).show();
            $(parent.pDivDownThree).show();
            $(parent.pBtnThree).hide();
            //clearInterval(parent.timer.FlowTimer3);

        });
        $(this.pBtnCancleThree).unbind("click");
        $(this.pBtnCancleThree).on("click", function () {
            $(parent.pBtnCancleThree).hide();
            $(parent.pBtnPlThree).hide();
            $(parent.pBtnRdThree).hide();
            $(parent.pSliderThree).hide();
            $(parent.pBtnSaveThree).hide();
            $(parent.pDivUpThree).hide();
            $(parent.pDivDownThree).hide();
            $(parent.pBtnThree).show();
            parent.initDevice3(id, name);
        });
        $(this.pBtnSaveThree).unbind("click");
        $(this.pBtnSaveThree).on("click", function () {
            if (parseInt($(parent.pValueUpThree).val()) < parseInt($(parent.pValueDownThree).val())) {
                layer.alert("高阈值不能小于低阈值,请重新设置", { icon: 5 });
                return false;
            }
            $(parent.pBtnCancleThree).hide();
            $(parent.pBtnPlThree).hide();
            $(parent.pBtnRdThree).hide();
            $(parent.pSliderThree).hide();
            $(parent.pBtnSaveThree).hide();
            $(parent.pDivUpThree).hide();
            $(parent.pDivDownThree).hide();
            $(parent.pBtnThree).show();
            //parent.setIntervalThree(id);
            parent.setDeviceRange(id, $(parent.pValueUpThree).val(), $(parent.pValueDownThree).val(), 3);
            $(parent.pBtnDeleteThree).show();
            parent.ChartThree = parent.initFlowChart(parent.pChartThree, deviceData, parseInt($(parent.pValueUpThree).val()), parseInt($(parent.pValueDownThree).val()), deviceData.max_val, name);
            $(parent.pSliderThree).slider("value", [$(parent.pValueDownThree).val(), $(parent.pValueUpThree).val()]);
        });
        $(this.pBtnPlThree).unbind("click");
        $(this.pBtnPlThree).on("click", function () {
            $(parent.pSliderThree).slider("option", "max", $(parent.pSliderThree).slider("option", "max") * 2);
            if ($(parent.pSliderThree).slider("option", "max") > 102400000) {
                $(parent.pSliderThree).slider("option", "max", 102400000);
            }
        });
        $(this.pBtnRdThree).unbind("click");
        $(this.pBtnRdThree).on("click", function () {
            if ($(parent.pSliderThree).slider("option", "max") >= parent.pMaxInterOne) {
                $(parent.pSliderThree).slider("option", "max", $(parent.pSliderThree).slider("option", "max") / 2);

            }
        });

        //得到设备流量图

        $(window).resize(function () {
            parent.ChartThree.resize();
        });
        parent.setIntervalThree(id);

    }
    catch (err) {
        console.error("ERROR - FlowAuditController.initDevice3() - Unable to initDevice3: " + err.message);
    }

}
//设备初始化4
FlowAuditController.prototype.initDevice4 = function (id, name) {
    try {
        var parent = this;
        var deviceData = parent.selectDeviceFlow(id, 4);
        parent.ChartFour = this.initFlowChart(parent.pChartFour, deviceData, deviceData.high_line, deviceData.low_line, deviceData.max_val, name);
        if (deviceData.high_line == -1) {
            parent.deviceStatus[3] = 0;
            $(parent.pBtnDeleteFour).hide();
        }
        else {
            parent.deviceStatus[3] = 1;
            $(parent.pBtnDeleteFour).show();
        }
        $(parent.pValueUpFour).val(deviceData.high_line == -1 ? 0 : deviceData.high_line);
        $(parent.pValueDownFour).val(deviceData.low_line == -1 ? 0 : deviceData.low_line);
        $(this.pSliderFour).slider({
            orientation: "vertical",
            range: true,
            values: [deviceData.low_line, deviceData.high_line],
            max: deviceData.high_line >= deviceData.max_val ? deviceData.high_line + 100 : deviceData.max_val + 100,
            slide: function (event, ui) {
                parent.ChartFour = parent.initFlowChart(parent.pChartFour, deviceData, ui.values[1], ui.values[0], deviceData.max_val, name);
                $(parent.pValueUpFour).val(ui.values[1]);
                $(parent.pValueDownFour).val(ui.values[0]);
            }
        });
        $(this.pBtnFour).unbind("click");
        $(this.pBtnFour).on("click", function () {
            $(parent.pBtnCancleFour).show();
            $(parent.pBtnPlFour).show();
            $(parent.pBtnRdFour).show();
            $(parent.pSliderFour).show();
            $(parent.pBtnSaveFour).show();
            $(parent.pDivUpFour).show();
            $(parent.pDivDownFour).show();
            $(parent.pBtnFour).hide();
            //clearInterval(parent.timer.FlowTimer3);

        });
        $(this.pBtnCancleFour).unbind("click");
        $(this.pBtnCancleFour).on("click", function () {
            $(parent.pBtnCancleFour).hide();
            $(parent.pBtnPlFour).hide();
            $(parent.pBtnRdFour).hide();
            $(parent.pSliderFour).hide();
            $(parent.pBtnSaveFour).hide();
            $(parent.pDivUpFour).hide();
            $(parent.pDivDownFour).hide();
            $(parent.pBtnFour).show();
            parent.initDevice4(id, name);
        });
        $(this.pBtnSaveFour).unbind("click");
        $(this.pBtnSaveFour).on("click", function () {
            if (parseInt($(parent.pValueUpFour).val()) < parseInt($(parent.pValueDownFour).val())) {
                layer.alert("高阈值不能小于低阈值,请重新设置", { icon: 5 });
                return false;
            }
            $(parent.pBtnCancleFour).hide();
            $(parent.pBtnPlFour).hide();
            $(parent.pBtnRdFour).hide();
            $(parent.pSliderFour).hide();
            $(parent.pBtnSaveFour).hide();
            $(parent.pDivUpFour).hide();
            $(parent.pDivDownFour).hide();
            $(parent.pBtnFour).show();
            //parent.setIntervalFour(id);
            parent.setDeviceRange(id, $(parent.pValueUpFour).val(), $(parent.pValueDownFour).val(), 4);
            $(parent.pBtnDeleteFour).show();
            parent.ChartFour = parent.initFlowChart(parent.pChartFour, deviceData, parseInt($(parent.pValueUpFour).val()), parseInt($(parent.pValueDownFour).val()), deviceData.max_val, name);
            $(parent.pSliderFour).slider("value", [$(parent.pValueDownFour).val(), $(parent.pValueUpFour).val()]);
        });
        $(this.pBtnPlFour).unbind("click");
        $(this.pBtnPlFour).on("click", function () {
            $(parent.pSliderFour).slider("option", "max", $(parent.pSliderFour).slider("option", "max") * 2);
            if ($(parent.pSliderFour).slider("option", "max") > 102400000) {
                $(parent.pSliderFour).slider("option", "max", 102400000);
            }
        });
        $(this.pBtnRdFour).unbind("click");
        $(this.pBtnRdFour).on("click", function () {
            if ($(parent.pSliderFour).slider("option", "max") >= parent.pMaxInterOne) {
                $(parent.pSliderFour).slider("option", "max", $(parent.pSliderFour).slider("option", "max") / 2);

            }
        });

        //得到设备流量图

        $(window).resize(function () {
            parent.ChartFour.resize();
        });
        parent.setIntervalFour(id);

    }
    catch (err) {
        console.error("ERROR - FlowAuditController.initDevice4() - Unable to initDevice4: " + err.message);
    }
}

FlowAuditController.prototype.setIntervalOne = function (id) {
    try {
        var parent = this;
        //clearInterval(parent.timer.FlowTimer1);
        parent.timer.FlowTimer1 = setInterval(function () {
            var data = parent.selectSingleTotalFlow(id, parent.pNextOne, 1);
            var option = parent.ChartOne.getOption();
            if (option.yAxis[0].max < Math.ceil(data.y)) {
                option.yAxis[0].max = Math.ceil(data.y*1.1);
                parent.ChartOne.setOption(option);
            }
            parent.ChartOne.addData([
                [
                    0,
                    data.y,
                    false,
                    false,
                    data.x
                ]
            ]);
        }, 20000);
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.setIntervalOne() - Unable to setIntervalOne: " + err.message);
    }
}

FlowAuditController.prototype.setIntervalTwo = function (id) {
    try {
        var parent = this;
        //clearInterval(parent.timer.FlowTimer2);
        parent.timer.FlowTimer2 = setInterval(function () {
            var data = parent.selectSingleTotalFlow(id, parent.pNextTwo, 2);
            var option = parent.ChartTwo.getOption();
            if (option.yAxis[0].max < Math.ceil(data.y)) {
                option.yAxis[0].max = Math.ceil(data.y*1.1);
                parent.ChartTwo.setOption(option);
            }
            parent.ChartTwo.addData([
                [
                    0,
                    data.y,
                    false,
                    false,
                    data.x
                ]
            ]);
        }, 20000);
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.setIntervalTwo() - Unable to setIntervalTwo: " + err.message);
    }
}

FlowAuditController.prototype.setIntervalThree = function (id) {
    try {
        var parent = this;
        //clearInterval(parent.timer.FlowTimer3);
        parent.timer.FlowTimer3 = setInterval(function () {
            var data = parent.selectSingleTotalFlow(id, parent.pNextThree, 3);
            var option = parent.ChartThree.getOption();
            if (option.yAxis[0].max < Math.ceil(data.y)) {
                option.yAxis[0].max = Math.ceil(data.y*1.1);
                parent.ChartThree.setOption(option);
            }
            parent.ChartThree.addData([
                [
                    0,
                    data.y,
                    false,
                    false,
                    data.x
                ]
            ]);
        }, 20000);
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.setIntervalThree() - Unable to setIntervalThree: " + err.message);
    }
}

FlowAuditController.prototype.setIntervalFour = function (id) {
    try {
        var parent = this;
        clearInterval(gloTimer.FlowTimer4);
        gloTimer.FlowTimer4 = setInterval(function () {
            var data = parent.selectSingleTotalFlow(id, parent.pNextFour, 4);
            var option = parent.ChartFour.getOption();
            if (option.yAxis[0].max < Math.ceil(data.y)) {
                option.yAxis[0].max = Math.ceil(data.y*1.1);
                parent.ChartFour.setOption(option);
            }
            parent.ChartFour.addData([
                [
                    0,
                    data.y,
                    false,
                    false,
                    data.x
                ]
            ]);
        }, 20000);
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.setIntervalFour() - Unable to setIntervalFour: " + err.message);
    }
}
//删除阈值
FlowAuditController.prototype.deleteDeviceValue = function (index) {
    try {
        var parent = this;
        var loadIndex = layer.load(2);
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DELETE_DEVICE_VALUE_NEW;
        var data = { dev: parent.deviceArry[index] }
        var promise = URLManager.getInstance().ajaxCall(link,data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        switch (index)
                        {
                            case 0:
                                parent.initDevice1(parent.deviceArry[0], parent.deviceNameArry[0]);
                                $(parent.pBtnCancleOne).hide();
                                $(parent.pBtnSaveOne).hide();
                                $(parent.pBtnOne).show();
                                $(parent.pDivUpOne).hide();
                                $(parent.pDivDownOne).hide();
                                parent.deviceStatus[0] = 0;
                                break;
                            case 1:
                                parent.initDevice2(parent.deviceArry[1], parent.deviceNameArry[1]);
                                $(parent.pBtnCancleTwo).hide();
                                $(parent.pBtnSaveTwo).hide();
                                $(parent.pBtnTwo).show();
                                $(parent.pDivUpTwo).hide();
                                $(parent.pDivDownTwo).hide();
                                parent.deviceStatus[1] = 0;
                                break;
                            case 2:
                                parent.initDevice3(parent.deviceArry[2], parent.deviceNameArry[2]);
                                $(parent.pBtnCancleThree).hide();
                                $(parent.pBtnSaveThree).hide();
                                $(parent.pBtnThree).show();
                                $(parent.pDivUpThree).hide();
                                $(parent.pDivDownThree).hide();
                                parent.deviceStatus[2] = 0;
                                break;
                            case 3:
                                parent.initDevice4(parent.deviceArry[3], parent.deviceNameArry[3]);
                                $(parent.pBtnCancleFour).hide();
                                $(parent.pBtnSaveFour).hide();
                                $(parent.pBtnFour).show();
                                $(parent.pDivUpFour).hide();
                                $(parent.pDivDownFour).hide();
                                parent.deviceStatus[3] = 0;
                                break;
                        }
                        
                        break;
                    default: layer.alert("删除阈值失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("删除阈值失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
        
    }
    catch (err) {
        console.error("ERROR - FlowAuditController.setIntervalFour() - Unable to setIntervalFour: " + err.message);
    }
}

FlowAuditController.prototype.clearTimer = function () {
    if (typeof (this.timer.FlowTimer1) != "undefined" && this.timer.FlowTimer1 != null) {
        clearInterval(this.timer.FlowTimer1);
    }
    if (typeof (this.timer.FlowTimer2) != "undefined" && this.timer.FlowTimer2 != null) {
        clearInterval(this.timer.FlowTimer2);
    }
    if (typeof (this.timer.FlowTimer3) != "undefined" && this.timer.FlowTimer3 != null) {
        clearInterval(this.timer.FlowTimer3);
    }
    if (typeof (gloTimer.FlowTimer4) != "undefined" && gloTimer.FlowTimer4 != null) {
        clearInterval(gloTimer.FlowTimer4);
    }
}



ContentFactory.assignToPackage("tdhx.base.audit.FlowAuditController", FlowAuditController);
