function HomeController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pInterfaceFlow = this.elementId + '_divInterface';
    this.pDeviceFlow = this.elementId + '_divDevice';
    this.pProtocolFlow = this.elementId + '_divProtocol';
    this.pCPUState = this.elementId + '_cpuState';
    this.pMemoryState = this.elementId + '_memoryState';
    this.pDiskState = this.elementId + '_diskState';

    this.pRuleNum = "#" + this.elementId + '_ruleNum';
    this.pBlackNum = "#" + this.elementId + '_blackNum';
    this.pHistoryEventNum = "#" + this.elementId + '_historyEventNum';
    this.pIpmacNum = "#" + this.elementId + '_ipmacNum';
    this.pNoReadNum = "#" + this.elementId + '_noReadNum';
    this.pTodayEventNum = "#" + this.elementId + '_todayEventNum';
    this.pWhiteNum = "#" + this.elementId + '_whiteNum';

    this.pBP0Light = "#" + this.elementId + '_bp0Light';
    this.pBP1Light = "#" + this.elementId + '_bp1Light';
    this.pExtPort = "#" + this.elementId + '_extPort';
    this.pMgmtPort = "#" + this.elementId + '_mgmtPort';
    this.pP0Port = "#" + this.elementId + '_p0Port';
    this.pP1Port = "#" + this.elementId + '_p1Port';
    this.pP2Port = "#" + this.elementId + '_p2Port';
    this.pP3Port = "#" + this.elementId + '_p3Port';
    this.pP4Port = "#" + this.elementId + '_p4Port';
    this.pP5Port = "#" + this.elementId + '_p5Port';

    this.pDdlTime1 = "#" + this.elementId + "_ddlTime1";
    this.pDdlTime2 = "#" + this.elementId + "_ddlTime2";
    this.pDdlTime3 = "#" + this.elementId + "_ddlTime3";

    this.pPortInformation = "#" + this.elementId + '_portInformation';

    this.color = ['#3994d3', '#f98665', '#fac767', '#28daca', '#9569f9', '#e36585'];

    this.layerTip = {
        tip0: null,
        tip1: null,
        tip2: null,
        tip3: null,
        tip4: null,
        tip5: null,
        tip6: null
    };
    this.interfaceChart = null;
    this.deviceChart = null;
    this.protocolChart = null;
    this.timer = {
        chartTimer: null
    };
}

HomeController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES[APPCONFIG.PRODUCT].HOME_DASHBOARD), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - HomeController.init() - Unable to initialize: " + err.message);
    }
}

HomeController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pDdlTime1).on("change", function () {
            parent.interfaceChart = parent.initLineChart(parent.pInterfaceFlow, '总流量', parent.selectTotalFlow());
        });
        $(this.pDdlTime2).on("change", function () {
            var deviceFlow = parent.selectDeviceFlow();
            if (typeof (deviceFlow.item) == "undefined" || deviceFlow.item.length == 0) {
                parent.deviceChart = parent.initPieNoDataChart(parent.pDeviceFlow, '设备流量排名');
            }
            else {
                parent.deviceChart = parent.initPieChart(parent.pDeviceFlow, '设备流量排名', deviceFlow);
            }
        });
        $(this.pDdlTime3).on("change", function () {
            var protocolFlow = parent.selectProtocolFlow();
            if (typeof (protocolFlow.item) == "undefined" || protocolFlow.item.length == 0) {
                parent.protocolChart = parent.initPieNoDataChart(parent.pProtocolFlow, '协议流量排名');
            }
            else {
                parent.protocolChart = parent.initPieChart(parent.pProtocolFlow, '协议流量排名', protocolFlow);
            }
        });
        $(window).resize(function () {
            parent.deviceChart.resize();
            parent.protocolChart.resize();
            parent.interfaceChart.resize();
        });
    }
    catch (err) {
        console.error("ERROR - HomeController.initControls() - Unable to initialize control: " + err.message);
    }
}

HomeController.prototype.load = function () {
    try {
        var parent = this;
        var CPUChrt = parent.initGaugeChart(this.pCPUState, 'CPU利用率', 1, 0);
        var memoryChart = parent.initGaugeChart(this.pMemoryState, '内存利用率', 2, 0);
        var diskChart = parent.initGaugeChart(this.pDiskState, '磁盘利用率', 3, 0);
        var totalFlow = this.selectTotalFlow();
        parent.interfaceChart = this.initLineChart(this.pInterfaceFlow, '总流量', totalFlow);
        var deviceFlow = this.selectDeviceFlow();
        if (typeof (deviceFlow.item) == "undefined" || deviceFlow.item.length == 0) {
            parent.deviceChart = this.initPieNoDataChart(this.pDeviceFlow, '设备流量排名');
        }
        else {
            parent.deviceChart = this.initPieChart(this.pDeviceFlow, '设备流量排名', deviceFlow);
        }

        var protocolFlow = this.selectProtocolFlow();
        if (typeof (protocolFlow.item) == "undefined" || protocolFlow.item.length == 0) {
            parent.protocolChart = this.initPieNoDataChart(this.pProtocolFlow, '协议流量排名');
        }
        else {
            parent.protocolChart = this.initPieChart(this.pProtocolFlow, '协议流量排名', protocolFlow);
        }

        this.selectBaseData(CPUChrt, memoryChart, diskChart);

        clearInterval(this.timer.chartTimer);
        this.timer.chartTimer = setInterval(function () {
            parent.selectBaseData(CPUChrt, memoryChart, diskChart);

            var data = parent.selectSingleTotalFlow();
            var option = parent.interfaceChart.getOption();
            if (option.yAxis[0].max < Math.ceil(data.y)) {
                option.yAxis[0].max = Math.ceil(data.y);
                parent.interfaceChart.setOption(option);
            }
            parent.interfaceChart.addData([
                [
                    0,
                    data.y,
                    false,
                    false,
                    data.x
                ]
            ]);
        }, 20000);
        $(window).resize(function () {
            CPUChrt.resize();
            memoryChart.resize();
            diskChart.resize();
            parent.deviceChart.resize();
            parent.protocolChart.resize();
            parent.interfaceChart.resize();
        });
    }
    catch (err) {
        console.error("ERROR - HomeController.load() - Unable to load: " + err.message);
    }
}

HomeController.prototype.selectBaseData = function (CPUChrt, memoryChart, diskChart) {
    var parent = this;
    try {
        var promise = URLManager.getInstance().ajaxCall(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_HOME_BASE);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            return null;
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined") {
                parent.pViewHandle.find(parent.pRuleNum).text(result.sys_info.rulesNum);
                parent.pViewHandle.find(parent.pRuleNum).unbind("click");
                parent.pViewHandle.find(parent.pRuleNum).on("click", function () {
                    $(".nav-list .nav-title").removeClass("active");
                    $(".nav-list .nav-title").eq(3).addClass("active");
                    $(".second-nav-list>li").removeClass("on");
                    $(".nav-list .nav-title").eq(3).next(".second-nav").slideDown(300, function () {
                        $(".nav-list .nav-title").eq(3).next().find(".second-nav-list>li").eq(0).addClass("on").click();
                    });
                });
                parent.pViewHandle.find(parent.pBlackNum).text(result.sys_info.blackNum);
                parent.pViewHandle.find(parent.pBlackNum).unbind("click");
                parent.pViewHandle.find(parent.pBlackNum).on("click", function () {
                    $(".nav-list .nav-title").removeClass("active");
                    $(".nav-list .nav-title").eq(3).addClass("active");
                    $(".second-nav-list>li").removeClass("on");
                    $(".nav-list .nav-title").eq(3).next(".second-nav").slideDown(300, function () {
                        $(".nav-list .nav-title").eq(3).next().find(".second-nav-list>li").eq(1).addClass("on").click();
                    });
                });
                parent.pViewHandle.find(parent.pIpmacNum).text(result.sys_info.ipmacNum);
                parent.pViewHandle.find(parent.pIpmacNum).unbind("click");
                parent.pViewHandle.find(parent.pIpmacNum).on("click", function () {
                    $(".nav-list .nav-title").removeClass("active");
                    $(".nav-list .nav-title").eq(3).addClass("active");
                    $(".second-nav-list>li").removeClass("on");
                    $(".nav-list .nav-title").eq(3).next(".second-nav").slideDown(300, function () {
                        $(".nav-list .nav-title").eq(3).next().find(".second-nav-list>li").eq(2).addClass("on").click();
                    });
                });
                parent.pViewHandle.find(parent.pWhiteNum).text(result.sys_info.whiteNum);
                parent.pViewHandle.find(parent.pWhiteNum).unbind("click");
                parent.pViewHandle.find(parent.pWhiteNum).on("click", function () {
                    $(".nav-list .nav-title").removeClass("active");
                    $(".nav-list .nav-title").eq(3).addClass("active");
                    $(".second-nav-list>li").removeClass("on");
                    $(".nav-list .nav-title").eq(3).next(".second-nav").slideDown(300, function () {
                        $(".nav-list .nav-title").eq(3).next().find(".second-nav-list>li").eq(0).addClass("on").click();
                    });
                });

                parent.pViewHandle.find(parent.pNoReadNum).text(result.sys_info.noReadNum);
                parent.pViewHandle.find(parent.pNoReadNum).unbind("click");
                parent.pViewHandle.find(parent.pNoReadNum).on("click", function () {
                    $(".nav-list .nav-title").eq(1).click();
                });
                parent.pViewHandle.find(parent.pTodayEventNum).text(result.sys_info.todayEventNum);
                parent.pViewHandle.find(parent.pTodayEventNum).unbind("click");
                parent.pViewHandle.find(parent.pTodayEventNum).on("click", function () {
                    $(".nav-list .nav-title").eq(1).click();
                });
                parent.pViewHandle.find(parent.pHistoryEventNum).text(result.sys_info.historyEventNum);
                parent.pViewHandle.find(parent.pHistoryEventNum).unbind("click");
                parent.pViewHandle.find(parent.pHistoryEventNum).on("click", function () {
                    $(".nav-list .nav-title").eq(1).click();
                });

                //EXT,MGMT
                if (result.sys_info.extLinkState) {
                    $(parent.pExtPort).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_YES);
                }
                else {
                    $(parent.pExtPort).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_NO)
                }
                if (typeof (result.sys_info.extInfo) != "undefined" && result.sys_info.extInfo != "") {
                    $(parent.pExtPort).attr("alt", result.sys_info.extInfo);
                    $(parent.pExtPort).hover(function () {
                        var data = $(this).attr("alt").split(';');
                        var tipBox = parent.initTipBox("EXT", data[1], data[2], data[3]);
                        parent.layerTip.tip0 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }

                if (result.sys_info.agl0LinkState) {
                    $(parent.pMgmtPort).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_YES);
                }
                else {
                    $(parent.pMgmtPort).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_NO)
                }

                if (typeof (result.sys_info.agl0Info) != "undefined" && result.sys_info.agl0Info != "") {
                    $(parent.pMgmtPort).attr("alt", result.sys_info.agl0Info);
                    $(parent.pMgmtPort).hover(function () {
                        var data = $(this).attr("alt").split(';');
                        var tipBox = parent.initTipBox("MGMT", data[1], data[2], data[3]);
                        parent.layerTip.tip1 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }

                //p0,p1
                if (result.sys_info.p0LinkState) {
                    $(parent.pP0Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_YES);
                }
                else {
                    $(parent.pP0Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_NO);
                }
                if (typeof (result.sys_info.p0Info) != "undefined" && result.sys_info.p0Info != "") {
                    $(parent.pP0Port).attr("alt", result.sys_info.p0Info);
                    $(parent.pP0Port).hover(function () {
                        var data = $(this).attr("alt").split(';');
                        var tipBox = parent.initTipBox("P0", data[1], data[2], data[3]);
                        parent.layerTip.tip2 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }

                if (result.sys_info.p1LinkState) {
                    $(parent.pP1Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_YES);
                }
                else {
                    $(parent.pP1Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_NO)
                }
                if (typeof (result.sys_info.p1Info) != "undefined" && result.sys_info.p1Info != "") {
                    $(parent.pP1Port).attr("alt", result.sys_info.p1Info);
                    $(parent.pP1Port).hover(function () {
                        var data = $(this).attr("alt").split(';');
                        var tipBox = parent.initTipBox("P1", data[1], data[2], data[3]);
                        parent.layerTip.tip3 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }

                var CPUOption = CPUChrt.getOption();
                CPUOption.series[0].data[0].value = result.sys_info.cpuState;
                $("#" + parent.pCPUState).attr("data-value", result.sys_info.cpuState);
                CPUChrt.setOption(CPUOption, true);

                var memoryOption = memoryChart.getOption();
                memoryOption.series[0].data[0].value = result.sys_info.memoryState;
                memoryOption.series[0].data[0].name = result.sys_info.memorySize+"GB";
                $("#" + parent.pMemoryState).attr("data-value", result.sys_info.memoryState);
                $("#" + parent.pMemoryState).attr("data-name", result.sys_info.memorySize);
                memoryChart.setOption(memoryOption, true);

                var diskOption = diskChart.getOption();
                diskOption.series[0].data[0].value = result.sys_info.diskState;
                diskOption.series[0].data[0].name = result.sys_info.diskSize + "GB";
                $("#" + parent.pDiskState).attr("data-value", result.sys_info.diskState);
                $("#" + parent.pDiskState).attr("data-name", result.sys_info.diskSize);
                diskChart.setOption(diskOption, true);
            }
        });

    }
    catch (err) {
        console.error("ERROR - HomeController.getBaseData() - Unable to load: " + err.message);
    }
}

HomeController.prototype.selectTotalFlow = function () {
    var html = "";
    try {
        var parent = this;
        var data = {
            x: [],
            y: []
        };
        var timeFlag = $(this.pDdlTime1 + " option:selected").val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_TOTAL_FLOW;
        var promise = URLManager.getInstance().ajaxSyncCall(link, { port: timeFlag });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined") {
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
        console.error("ERROR - HomeController.selectFlow() - Unable to get all points: " + err.message);
        return data;
    }
}

HomeController.prototype.selectSingleTotalFlow = function () {
    var html = "";
    try {
        var parent = this;
        var data = { x: '', y: 0 };
        var timeFlag = $(this.pDdlTime1 + " option:selected").val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_TOTAL_FLOW_POINT;
        var promise = URLManager.getInstance().ajaxSyncCall(link, { timeDelta: timeFlag });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.point) != "undefined" && typeof (result.timePoint) != "undefined"
                && result.timePoint != "undefined") {
                data.x = result.timePoint;
                data.y = result.point;
            }
        });

        return data;
    }
    catch (err) {
        return data;
        console.error("ERROR - HomeController.selectSingleTotalFlow() - Unable to get single point: " + err.message);
    }
}

HomeController.prototype.selectDeviceFlow = function () {
    var html = "";
    try {
        var parent = this;
        var data = {
            name: [],
            item: []
        };
        var timeFlag = $(this.pDdlTime2 + " option:selected").val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_TOTAL_FLOW;
        var promise = URLManager.getInstance().ajaxSyncCall(link, { timeDelta: timeFlag });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                for (var i = 0; i < result.rows.length; i++) {
                    if (result.rows[i][1] != 0) {
                        var color = parent.color[i];
                        if (result.rows[i][0].toLowerCase() == "others") {
                            color = parent.color[5];
                            result.rows[i][0] = "其他";
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
        console.error("ERROR - HomeController.selectDeviceFlow() - Unable to get device flow data: " + err.message);
        return data;
    }
}

HomeController.prototype.selectProtocolFlow = function () {
    var html = "";
    try {
        var parent = this;
        var data = {
            name: [],
            item: []
        };
        var timeFlag = $(this.pDdlTime3 + " option:selected").val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PROTOCOL_TOTAL_FLOW;
        var promise = URLManager.getInstance().ajaxSyncCall(link, { timeDelta: timeFlag });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                for (var i = 0; i < result.rows.length; i++) {
                    if (result.rows[i][1] != 0) {
                        var color = parent.color[i];
                        if (result.rows[i][0].toLowerCase() == "others") {
                            color = parent.color[5];
                            result.rows[i][0] = "其他";
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
        console.error("ERROR - HomeController.selectProtocolFlow() - Unable to get protocol flow data: " + err.message);
        return data;
    }
}

HomeController.prototype.initGaugeChart = function (id, title, type, initValue) {
    var gauge = echarts.init(document.getElementById(id));
    var axisLineCPUColor = [[0.3, '#e1f1fe'], [0.7, '#c2def3'], [1, '#85c5f3']];
    var axisLineMemoryColor = [[0.3, '#e0e5fd'], [0.7, '#c2c9fa'], [1, '#8592f3']];
    var axisLineDiskColor = [[0.3, '#e6d1f5'], [0.7, '#cfa9f1'], [1, '#b277e8']];
    var axisLineColor;
    var detailTextColor;
    var pointerColor;
    switch (type) {
        case 1: axisLineColor = axisLineCPUColor; detailTextColor = '#85c5f3'; pointerColor = '#85c5f3'; break;
        case 2: axisLineColor = axisLineMemoryColor; detailTextColor = '#8592f3'; pointerColor = '#8592f3'; break;
        default: axisLineColor = axisLineDiskColor; detailTextColor = '#b277e8'; pointerColor = '#b277e8'; break;
    }
    var option = {
        tooltip: {
            formatter: "{a}: {c}%"
        },
        series: [
            {
                name: title,
                type: 'gauge',
                center: ['50%', '65%'],    // 默认全局居中
                radius: [0, '120%'],
                startAngle: 180,
                endAngle: 0,
                min: 0,                     // 最小值
                max: 100,                   // 最大值
                precision: 0,               // 小数精度，默认为0，无小数点
                splitNumber: 10,             // 分割段数，默认为5
                axisLine: {            // 坐标轴线
                    show: true,        // 默认显示，属性show控制显示与否
                    lineStyle: {       // 属性lineStyle控制线条样式
                        color: axisLineColor,
                        width: 30
                    }
                },
                axisTick: {            // 坐标轴小标记
                    show: true,        // 属性show控制显示与否，默认不显示
                    splitNumber: 2,    // 每份split细分多少段
                    length: 5,         // 属性length控制线长
                    lineStyle: {       // 属性lineStyle控制线条样式
                        color: '#eee',
                        width: 1,
                        type: 'solid'
                    }
                },
                axisLabel: {           // 坐标轴文本标签，详见axis.axisLabel
                    show: true,
                    formatter: function (v) {
                        switch (v) {
                            case 0: return 0 + '%';
                            case 50: return 50 + '%';
                            case 100: return 100 + '%';
                            default: return '';
                        }
                    },
                    textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                        color: '#333'
                    }
                },
                splitLine: {           // 分隔线
                    show: true,        // 默认显示，属性show控制显示与否
                    length: 30,         // 属性length控制线长
                    lineStyle: {       // 属性lineStyle（详见lineStyle）控制线条样式
                        color: '#eee',
                        width: 2,
                        type: 'solid'
                    }
                },
                pointer: {
                    length: '80%',
                    width: 3,
                    color: pointerColor
                },
                title: {
                    show: true,
                    offsetCenter: ['0%', -30],       // x, y，单位px
                    textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                        color: axisLineColor[2][1],
                        fontSize: 16
                    }
                },
                detail: {
                    show: true,
                    backgroundColor: 'rgba(0,0,0,0)',
                    borderWidth: 0,
                    borderColor: '#ccc',
                    width: 100,
                    height: 40,
                    offsetCenter: ['0%', 15],       // x, y，单位px
                    formatter: function (v) {
                        return title + '\n' + v + '%';
                    },
                    textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                        color: detailTextColor,
                        fontFamily: '微软雅黑',
                        fontWeight:600,
                        fontSize: 16
                    }
                },
                data: [{ value: initValue, name: '' }]
            }
        ]
    };

    gauge.setOption(option);

    return gauge;
}

HomeController.prototype.initBarChart = function (id, title, data) {
    var bar = echarts.init(document.getElementById(id));
    var option = {
        title: {
            x: 'left',
            y: 'top',
            text: title,
            textStyle:
                {
                    fontSize: 14,
                    fontWeight: 'bolder',
                    fontFamily: '微软雅黑',
                    color: '#666'
                },
            subtextStyle:
                {
                    fontSize: 12,
                    fontWeight: 'bolder',
                    fontFamily: '微软雅黑',
                    color: '#bbb'
                }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function (a) {
                return a[0][1] + ": " + (a[0][2] * 100) + "%";
            }
        },
        legend: {
            orient: 'vertical',
            x: 'left',
            y: 'bottom',
            data: data.y
        },
        calculable: false,
        xAxis: [
            {
                type: 'value',
                max: 1,
                min: 0,
                boundaryGap: false,
                axisLabel: {
                    formatter: function (v) { return v * 100 + "%"; }
                },
                axisLine: {
                    show: true,
                    lineStyle: {
                        color: '#eee',
                        width: 1,
                        type: 'solid'
                    }
                }
            }
        ],
        yAxis: [
            {
                type: 'category',
                data: data.x,
                axisLabel: {
                    formatter: function (v) { return v; }
                },
                axisLine: {
                    show: true,
                    lineStyle: {
                        color: '#ccc',
                        width: 1,
                        type: 'solid'
                    }
                },
                splitLine: {
                    show: true
                }
            }
        ],
        series: [
            {
                type: 'bar',
                data: data.y,
                itemStyle: {
                    normal: {
                        color: function (a) {
                            switch (a.dataIndex) {
                                case 0: return "#3a94d3";
                                case 1: return "#fa8567";
                                case 2: return "#fac567";
                                case 3: return "#28d8ca";
                                default: return "#9667fa";
                            }
                        },
                        label: {
                            show: true,
                            textStyle: {
                                fontSize: 12,
                                color: '#333'
                            },
                            formatter: function (a) {
                                return (a.value * 100) + "%";
                            }
                        }
                    }
                },
                barWidth: 12
            }
        ]
    };

    bar.setOption(option);

    return bar;
}

HomeController.prototype.initLineChart = function (id, title, data) {
    var line = echarts.init(document.getElementById(id));
    var option = {
        title: {
            text: title,
            subtext: '单位：Kbps',
            textStyle:
                {
                    fontSize: 14,
                    fontWeight: 'bolder',
                    fontFamily: '微软雅黑',
                    color: '#666'
                },
            subtextStyle:
                {
                    fontSize: 12,
                    fontWeight: 'bolder',
                    fontFamily: '微软雅黑',
                    color: '#bbb'
                }
        },
        calculable: false,
        tooltip: {
            trigger: 'axis',
            formatter: '{b}: {c}Kbps'
        },
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
                axisLabel:{
                    //X轴刻度配置
                    interval:29
                },
                boundaryGap: false,
                data: data.x
            }
        ],
        yAxis: [
            {
                type: 'value',
                min: 0,
                max: data.y.length == 0 ? 1 : Math.ceil(Math.max.apply(null, data.y)) + 1,
                boundaryGap: false,
                axisLabel: {
                    formatter: function (v) {
                        if (v == 0) {
                            return v;
                        }
                        return v.toFixed(1);
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
                data: data.y
            }
        ]
    };

    line.setOption(option);

    return line;
}

HomeController.prototype.initPieChart = function (id, title, data) {
    var parent = this;
    var pie = echarts.init(document.getElementById(id));
    var option = {
        title: {
            x: 'left',
            y: 'top',
            text: title,
            textStyle: {
                fontSize: 14,
                fontWeight: 'bolder',
                fontFamily: '微软雅黑',
                color: '#666'
            },
            subtextStyle: {
                fontSize: 12,
                fontWeight: 'bolder',
                fontFamily: '微软雅黑',
                color: '#bbb'
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: "{d}%"
        },
        legend: {
            orient: 'vertical',
            x: 'left',
            y:50,
            data: data.name
        },
        calculable: true,
        series: [
            {
                name: 'pie',
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['60%', '50%'],
                data: data.item
            }
        ]
    };

    pie.setOption(option);

    return pie;
}

HomeController.prototype.initPieNoDataChart = function (id,title) {
    var parent = this;
    var labelBottom = {
        normal: {
            label: {
                show: true,
                position: 'center',
                formatter: '{b}',
                textStyle: {
                    baseline: 'center',
                    fontSize: 20,
                    fontWeight: 'bolder',
                    color: '#333333',
                    fontFamily: '微软雅黑',

                }
            },
            labelLine: {
                show: false
            }
        }
    };
    var pie = echarts.init(document.getElementById(id));
    var option = {
        title: {
            text: title,
            subtext: '暂无数据',
            x: 'left',
            y: 'top',
            textStyle: {
                color: '#333333',
                fontFamily: '微软雅黑',
                fontSize: 14
            },
            subtextStyle: {
                fontSize: 12,
                fontFamily: '微软雅黑',
                color: '#333333'
            }
        },
        tooltip: {
            show: false
        },
        color: ['#eeeeee'],
        calculable: true,
        series: [
            {
                name: 'pie',
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['50%', '50%'],
                data: [
                        { value: 335, name: '0%', itemStyle: labelBottom }
                ]
            }
        ]
    };

    pie.setOption(option);

    return pie;
}

HomeController.prototype.createPieStruct = function (name, value, color) {
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

HomeController.prototype.initTipBox = function (title, mac, ip, subip) {
    var tipBox = '';
    tipBox += ' <ul>';
    tipBox += '<li>接口名称：<span>' + title + '</span></li>';
    tipBox += '<li>硬件地址：<span>' + ip + '</span></li>';
    tipBox += '<li>接口地址：<span>' + mac + '</span></li>';
    tipBox += '<li>子网掩码：<span>' + subip + '</span></li>';
    tipBox += '</ul>';

    return tipBox;
}

HomeController.prototype.disposeTipBox = function () {
    layer.closeAll("tips");
}

HomeController.prototype.clearTimer = function () {
    if (typeof (this.timer.chartTimer) != "undefined" && this.timer.chartTimer != null) {
        clearInterval(this.timer.chartTimer);
    }
}

HomeController.prototype.formatStatus = function (v, perent) {
    try {
        switch (v) {
            case 0:
                return "离线";
            case 1:
                return "正常";
            case 2:
                return "重建" + perent + "%";
            case 3:
                return "降级";
            case 4:
                return "同步" + perent + "%";
            case 5:
                return "不支持RAID";
            default:
                return "错误";
        }
    }
    catch (err) {
        console.error("ERROR - HomeController.formatStatus() - Unable to format raid status: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.home.HomeController", HomeController);