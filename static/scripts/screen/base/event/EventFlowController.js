function EventFlowController(viewHandle, elementId, id, table_id, deviceId, mac,ip,type,name,smacList,dmacList) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.tableId = table_id;
    this.deviceId = deviceId;
    this.deviceMac = mac;
    this.deviceIp = ip;
    this.eventType = type;
    this.recordId = id;
    this.dname = name;
    this.dmacList = dmacList;
    this.smacList = smacList;
    this.pBtnOne = "#" + this.elementId + "_btnEditOne";
    this.pBtnSaveOne = "#" + this.elementId + "_btnSaveOne";
    this.pBtnCancleOne = "#" + this.elementId + "_btnCancleOne";
    this.pBtnPlOne = "#" + this.elementId + "_btnPluseOne";
    this.pBtnRdOne = "#" + this.elementId + "_btnReduceOne";
    this.pSliderOne = "#" + this.elementId + "_sliderOne";
    this.pChartOne = this.elementId + "_divChartOne";
    this.pChartTwo = this.elementId + "_divChartTwo";
    this.pDivUpOne = "#" + this.elementId + "_divUpOne";
    this.pDivDownOne = "#" + this.elementId + "_divDownOne";
    this.pValueUpOne = "#" + this.elementId + "_valueUpOne";
    this.pValueDownOne = "#" + this.elementId + "_valueDownOne";
    this.plblDeviceName = "#" + this.elementId + "_lblDeviceName";
    this.plblDeviceName2 = "#" + this.elementId + "_lblDeviceName2";
    this.plblHigh = "#" + this.elementId + "_lblHigh";
    this.plblLow = "#" + this.elementId + "_lblLow";
    this.plblFlow = "#" + this.elementId + "_lblFlow";
    this.plblType = "#" + this.elementId + "_lblType";
    this.ChartOne = null;
    this.ChartTwo = null;
    this.timer = {
        FlowTimer1: null
    };

    this.pNextOne = "";
    this.deviceStatus = 0;
    this.pBtnDeleteOne = "#" + this.elementId + "_btnDeleteOne";
}

EventFlowController.prototype.init = function () {
    try {
        var parent = this;

        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.EVENT_FLOWDIALOG), {
            elementId: parent.elementId
        });
        this.pViewHandle.find(".layui-layer-content").html(tabTemplate);
        $(this.pBtnDeleteOne).on("click", function () {
            parent.deleteDeviceValue();
        });
        $(this.pValueUpOne).on("change", function () {
            $(parent.pValueUpOne).val(Validation.validateNum1($(parent.pValueUpOne).val()));
        });
        $(this.pValueDownOne).on("change", function () {
            $(parent.pValueDownOne).val(Validation.validateNum1($(parent.pValueDownOne).val()));
        });
        this.load();
    }
    catch (err) {
        console.error("ERROR - EventFlowController.initShell() - Unable to initialize: " + err.message);
    }
}

EventFlowController.prototype.load = function () {
    try {
        this.pPager = null;
        
        var deviceData = this.selectDeviceFlow1(this.recordId, this.tableId);
        //this.ChartOne = this.initFlowChart1(this.pChartOne, deviceData, deviceData.high_line, deviceData.low_line, deviceData.max_val, "流量快照", parseInt(this.eventType));
        this.initDevice1(this.deviceId, "设备实时流量图");
        $(this.plblDeviceName).text(this.deviceIp);
        $(this.plblDeviceName2).text(this.dname);
        $(this.plblHigh).text(deviceData.high_line);
        $(this.plblLow).text(deviceData.low_line);
        $(this.plblFlow).text(deviceData.alarm_y);
        $(this.plblType).text(parseInt(this.eventType) == 1? "流量告警" :"流量恢复");
        $('<hr><div class="pops-h1">交换机信息(交换机名#端口#位置)</div>'+this.smacList+'<br>'+this.dmacList).appendTo($(this.pViewHandle).find('.pops-content'));
    }
    catch (err) {
        console.error("ERROR - EventFlowController.load() - Unable to load: " + err.message);
    }
}

EventFlowController.prototype.selectDeviceFlow1 = function (id, tableid) {
    var html = "";
    try {
        var parent = this;
        var data = {
            high_line: 0,
            low_line: 0,
            max_val: 0,
            alarm_x: "",
            alarm_y:0,
            x: [],
            y: []
        };
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_DETAIL_FLOW_NEW;
        var dt = { recordid: id, tablenum: tableid }
        var promise = URLManager.getInstance().ajaxSyncCall(link, dt);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined") {
                data.high_line = result.high;
                data.low_line = result.low;
                data.max_val = result.max;
                data.alarm_x = result.alarm_time;
                data.alarm_y = result.alarm_val;
                for (var i = 0; i < result.bytes_list.length; i++) {
                    data.y.push(result.bytes_list[i]);
                }
                for (var i = 0; i < result.time_list.length; i++) {
                    data.x.push(result.time_list[i]);
                }
            }
        });
        return data;
    }
    catch (err) {
        console.error("ERROR - EventFlowController.selectFlow() - Unable to get all DeviceFlow: " + err.message);
        return data;
    }
}


EventFlowController.prototype.selectDeviceFlow2 = function (id) {
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
                parent.pNextOne = result.next_time;
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

EventFlowController.prototype.selectSingleTotalFlow = function (id, time) {
    var html = "";
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_PROTOCOL_FLOW_NEW;
        var data = { dev: id, time: time }
        var promise = URLManager.getInstance().ajaxSyncCall(link, data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.point) != "undefined" && typeof (result.timePoint) != "undefined"
                && result.timePoint != "undefined") {
                data.x = result.timePoint;
                data.y = result.point;
                parent.pNextOne = result.next_time;
            }
        });
        return data;
    }
    catch (err) {
        return data;
        console.error("ERROR - FlowAuditController.selectSingleTotalFlow() - Unable to get single point: " + err.message);
    }
}

EventFlowController.prototype.setDeviceRange = function (id, h, l) {
    var html = "";
    try {
        var parent = this;
        var data = { dev: id, high: h, low: l, mac: parent.deviceMac, flag: 1, ip: parent.deviceIp };
        if (parent.deviceStatus == 0) {
            data.flag = 2;
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
        console.error("ERROR - EventFlowController.setDeviceRange() - Unable to setDeviceRange: " + err.message);
    }
}

EventFlowController.prototype.initDevice1 = function (id, name) {
    try {
        var parent = this;
        var deviceData = parent.selectDeviceFlow2(id);
        parent.ChartTwo = this.initFlowChart2(parent.pChartTwo, deviceData, deviceData.high_line, deviceData.low_line, deviceData.max_val, name);
        if (deviceData.high_line == -1) {
            parent.deviceStatus = 0;
            $(parent.pBtnDeleteOne).hide();
        }
        else {
            parent.deviceStatus = 1;
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
                parent.ChartTwo = parent.initFlowChart2(parent.pChartTwo, deviceData, ui.values[1], ui.values[0], deviceData.max_val, name);
                $(parent.pValueUpOne).val(ui.values[1]);
                $(parent.pValueDownOne).val(ui.values[0]);
            }
        });

        $(this.pBtnOne).on("click", function () {
            $(parent.pBtnCancleOne).show();
            $(parent.pBtnPlOne).show();
            $(parent.pBtnRdOne).show();
            $(parent.pSliderOne).show();
            $(parent.pBtnSaveOne).show();
            $(parent.pDivUpOne).show();
            $(parent.pDivDownOne).show();
            $(parent.pBtnOne).hide();
            clearInterval(parent.timer.FlowTimer1);

        });
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
            parent.setIntervalOne(id);
            parent.setDeviceRange(id, $(parent.pValueUpOne).val(), $(parent.pValueDownOne).val());
            $(parent.pBtnDeleteOne).show();
            parent.ChartTwo = parent.initFlowChart2(parent.pChartTwo, deviceData, parseInt($(parent.pValueUpOne).val()), parseInt($(parent.pValueDownOne).val()), deviceData.max_val, name);
            $(parent.pSliderOne).slider("value", [$(parent.pValueDownOne).val(), $(parent.pValueUpOne).val()]);
        });

        $(this.pBtnPlOne).on("click", function () {
            $(parent.pSliderOne).slider("option", "max", $(parent.pSliderOne).slider("option", "max") * 2);
            if ($(parent.pSliderOne).slider("option", "max") > 102400000) {
                $(parent.pSliderOne).slider("option", "max", 102400000);
            }
        });
        $(this.pBtnRdOne).on("click", function () {
            if ($(parent.pSliderOne).slider("option", "max") >= parent.pMaxInterOne) {
                $(parent.pSliderOne).slider("option", "max", $(parent.pSliderOne).slider("option", "max") / 2);

            }
        });

        //得到设备流量图

        $(window).resize(function () {
            parent.ChartTwo.resize();
        });
        parent.setIntervalOne(id);

    }
    catch (err) {
        console.error("ERROR - EventFlowController.initDevice1() - Unable to initDevice1: " + err.message);
    }
}

EventFlowController.prototype.setIntervalOne = function (id) {
    try {
        var parent = this;
        clearInterval(parent.timer.FlowTimer1);
        parent.timer.FlowTimer1 = setInterval(function () {
            var data = parent.selectSingleTotalFlow(id, parent.pNextOne);
            var option = parent.ChartTwo.getOption();
            if (option.yAxis[0].max < Math.ceil(data.y)) {
                option.yAxis[0].max = Math.ceil(data.y + 100);
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
        console.error("ERROR - EventFlowController.setIntervalOne() - Unable to setIntervalOne: " + err.message);
    }
}

EventFlowController.prototype.initFlowChart2 = function (id, data, h, l, m, title) {
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
                max: m >= h ? m * 1.1 : h * 1.1,
                boundaryGap: false,
                axisLabel: {
                    formatter: function (v) {
                        if (v < 10) {
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

EventFlowController.prototype.initFlowChart1 = function (id, data, h, l, m, title,type) {
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
                max: m >= h ? m * 1.1 : h * 1.1,
                axisLabel: {
                    formatter: function (v) {
                        if (v < 10) {
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
                            { name: '高阈值', value: h, xAxis: -1, yAxis: h, itemStyle: { normal: { color: '#c50601' } } },
                            { xAxis: 10000000000, yAxis: h }
                         ],
                          [
                            { name: '低阈指', value: l, xAxis: -1, yAxis: l, itemStyle: { normal: { color: '#1ca826' } } },
                            { xAxis: 10000000000, yAxis: l }
                          ]
                    ]
                },
                markPoint: {
                    symbol: 'emptyCircle',
                    effect: {
                        show: true
                    },
                    data: [

                            { name: parseInt(type)==1?"告警点":"恢复点", value: data.alarm_y, xAxis: data.alarm_x, yAxis: data.alarm_y }
                    ]
                }

            }
        ]
    };
    pie.setOption(option);
    return pie;
}

EventFlowController.prototype.deleteDeviceValue = function () {
    try {
        var parent = this;
        var loadIndex = layer.load(2);
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DELETE_DEVICE_VALUE_NEW;
        var data = { dev: parent.deviceId }
        var promise = URLManager.getInstance().ajaxCall(link, data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.initDevice1(parent.deviceId, "设备实时流量图");
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
EventFlowController.prototype.clearTimer = function () {
    if (typeof (this.timer.FlowTimer1) != "undefined" && this.timer.FlowTimer1 != null) {
        clearInterval(this.timer.FlowTimer1);
    }
}

ContentFactory.assignToPackage("tdhx.base.event.EventFlowController", EventFlowController);