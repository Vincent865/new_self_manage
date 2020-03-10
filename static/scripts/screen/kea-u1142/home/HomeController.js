function HomeController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pSysClientIP =  "#" + this.elementId + '_sysClientIP';
    this.pSysClientIP6 =  "#" + this.elementId + '_sysClientIP6';
	this.pSysProduct =  "#" + this.elementId + '_sysProduct';
	this.pSysSerialNum = "#" +  this.elementId + '_sysSerialNum';
	this.pSysSoftware = "#" +  this.elementId + '_sysSoftware';
	this.pSysRunTime =  "#" + this.elementId + '_sysRunTime';
	
	this.pIndexBlackNum = "#" +  this.elementId + '_indexBlackNum';
	this.pIndexTodayEventNum = "#" +  this.elementId + '_indexTodayEventNum';
	this.pIndexHistoryEventNum = "#" +  this.elementId + '_indexHistoryEventNum';
	this.pIndex_indexAssetNum = "#" +  this.elementId + '_indexAssetNum';
    this.pBtnDevice = "#" +this.elementId + '_btnDevice';
    this.pBtnProto = "#" +this.elementId + '_btnProto';

    this.pInterfaceFlow = this.elementId + '_divInterface';
    this.pDeviceFlow = this.elementId + '_divDevice';
	this.pProtocolFlow = this.elementId + '_divProtocol';
    this.pSessionNum = this.elementId + '_divSessionNum';
    this.pEvent = this.elementId + '_divEvent';
    this.pLiverate = this.elementId + '_divLiverate';
    this.pSessionCpu = "#" +  this.elementId + '_cpu';
    this.pSessionMem = "#" +  this.elementId + '_memory';
    this.pSessionDisk = "#" +  this.elementId + '_disk';

   /* this.pCPUState = this.elementId + '_cpuState';
    this.pMemoryState = this.elementId + '_memoryState';*/
	
	this.pRuleNum = "#" + this.elementId + '_ruleNum';
    this.pBlackNum = "#" + this.elementId + '_blackNum';
    this.pHistoryEventNum = "#" + this.elementId + '_historyEventNum';
    this.pIpmacNum = "#" + this.elementId + '_ipmacNum';
    this.pNoReadNum = "#" + this.elementId + '_noReadNum';
    this.pTodayEventNum = "#" + this.elementId + '_todayEventNum';
    this.pWhiteNum = "#" + this.elementId + '_whiteNum';

    this.pExtPort = "#" + this.elementId + '_extPort';
    this.pMgmtPort = "#" + this.elementId + '_mgmtPort';
    this.pP1Port = "#" + this.elementId + '_p1Port';
    this.pP2Port = "#" + this.elementId + '_p2Port';
    this.pP3Port = "#" + this.elementId + '_p3Port';
    this.pP4Port = "#" + this.elementId + '_p4Port';
    this.pP5Port = "#" + this.elementId + '_p5Port';
    this.pP6Port = "#" + this.elementId + '_p6Port';

    this.pPortInformation = "#" + this.elementId + '_portInformation';

    this.color = ['#3994d3', '#f98665', '#fac767', '#28daca', '#9569f9', '#e36585','#a8ed85'];

    this.layerTip = {
        tip1: null,
        tip2: null,
        tip3: null,
        tip4: null,
        tip5: null,
        tip6: null
    };

    this.pDdlTime1 = "#" + this.elementId + "_ddlTime1";
    this.pDdlTime2 = "#" + this.elementId + "_ddlTime2";

    this.interfaceChart = null;
    this.deviceChart = null;
	this.protocolChart = null;
	this.sessionNumChart = null;

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
        /*$(this.pDdlTime1).on("change", function () {
            parent.interfaceChart = parent.initLineChart(parent.pInterfaceFlow, '总流量', parent.selectTotalFlow());
        });*/
        /*$(this.pDdlTime2).on("change", function () {
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
        });*/
        this.deviceFlowChartPack=function(){
            var deviceFlow = parent.selectDeviceFlow();
            if($(parent.pBtnDevice).val()==1){
                if (typeof (deviceFlow.item) == "undefined" || deviceFlow.item.length == 0) {
                    parent.devicePieChart = parent.initPieNoDataChart(parent.pDeviceFlow, '设备流量排名');
                }
                else {
                    parent.devicePieChart = parent.initPieChart(parent.pDeviceFlow, '设备流量排名', deviceFlow);
                }
            }else if($(parent.pBtnDevice).val()==2){
                if (typeof (deviceFlow.item) == "undefined" || deviceFlow.item.length == 0) {
                    parent.deviceBarChart = parent.initNoDataBarChart(parent.pDeviceFlow, '设备流量排名');
                }
                else {
                    parent.deviceBarChart = parent.initBarChart(parent.pDeviceFlow, '设备流量排名', deviceFlow);
                }
            }
        };
        this.protoFlowChartPack=function(){
            var protoFlow = parent.selectProtocolFlow();
            if($(parent.pBtnProto).val()==1){
                if (typeof (protoFlow.item) == "undefined" || protoFlow.item.length == 0) {
                    parent.protocolPieChart = parent.initPieNoDataChart(parent.pProtocolFlow, '协议流量排名');
                }
                else {
                    parent.protocolPieChart = parent.initPieChart(parent.pProtocolFlow, '协议流量排名', protoFlow);
                }
            }else if($(parent.pBtnProto).val()==2){
                if (typeof (protoFlow.item) == "undefined" || protoFlow.item.length == 0) {
                    parent.protocolBarChart = parent.initNoDataBarChart(parent.pProtocolFlow, '协议流量排名');
                }
                else {
                    parent.protocolBarChart = parent.initBarChart(parent.pProtocolFlow, '协议流量排名', protoFlow);
                }
            }
        };

        parent.deviceFlowChartPack(),
            parent.protoFlowChartPack(),
            $(this.pBtnProto).on('change',parent.protoFlowChartPack),
        $(this.pBtnDevice).on('change',parent.deviceFlowChartPack);
        $(window).resize(function () {
            if($(parent.pBtnProto).val()==1){
                parent.protocolPieChart.resize();
            }else{
                parent.protocolBarChart.resize();
            }
            if($(parent.pBtnDevice).val()==1){
                parent.devicePieChart.resize();
            }else{
                parent.deviceBarChart.resize();
            }
            /*parent.deviceChart.resize();
		    parent.protocolChart.resize();*/
            //parent.interfaceChart.resize();
        });
    }
    catch (err) {
        console.error("ERROR - HomeController.initControls() - Unable to initialize control: " + err.message);
    }
}

HomeController.prototype.load = function () {
    try {
		this.getSystemInfo();
		this.getIndexBlackNum();
        var parent = this;
        /*var CPUChrt = parent.initGaugeChart(this.pCPUState, 'CPU利用率', 1, 0);
        var memoryChart = parent.initGaugeChart(this.pMemoryState, '内存利用率', 2, 0);*/
        var totalFlow = this.selectTotalFlow();
		var interfaceChart = this.initLineChart(this.pInterfaceFlow, '总流量', totalFlow);
		var sessionNum = this.selectSessionNum();
        var sessionNumChart = this.initSessionLineChart(this.pSessionNum, '并发连接数', sessionNum);
        var event = this.selectEventPie()
        if(event.name.length){
            var eventPie = this.initPieChart(this.pEvent, '安全事件分布', event);
        }else{
            var eventPie = this.initPieNoDataChart(this.pEvent, '安全事件分布');
        }
        /*var deviceFlow = this.selectDeviceFlow();
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
        }*/
		
        /*this.selectBaseData(CPUChrt, memoryChart);*/
		this.selectBaseData();


        clearInterval(gloTimer.chartTimer);
        gloTimer.chartTimer = setInterval(function () {
			/*parent.selectFlowDate(interfaceChart);*/
            parent.selectBaseData();

            this.pSessionMem = this.elementId + '_memory';
            this.pSessionDisk = this.elementId + '_disk';

            var data = parent.selectSingleTotalFlow();
            var option = interfaceChart.getOption();
            if (option.yAxis[0].max < Math.ceil(data.y)) {
                option.yAxis[0].max = Math.ceil(data.y);
                interfaceChart.setOption(option);
            }
            interfaceChart.addData([
                [
                    0,
                    data.y,
                    false,
                    false,
                    data.x
                ]
            ]);
			
        }, 20000);
		gloTimer.chartTimer = setInterval(function () {
			/*parent.selectFlowDate(interfaceChart);*/
           
			var sessiondata = parent.selectoneSessionNum();
            var sessionoption = sessionNumChart.getOption();
            if (sessionoption.yAxis[0].max < Math.ceil(sessiondata.y)) {
                sessionoption.yAxis[0].max = Math.ceil(sessiondata.y);
                sessionNumChart.setOption(sessionoption);
            }
            sessionNumChart.addData([
                [
                    0,
                    sessiondata.y,
                    false,
                    false,
                    sessiondata.x
                ]
            ]);
        }, 5000);
        $(window).resize(function () {
            /*CPUChrt.resize();
            memoryChart.resize();*/
            /*deviceChart.resize();
			protocolChart.resize();*/
            interfaceChart.resize();
			sessionNumChart.resize();
        });
    }
    catch (err) {
        console.error("ERROR - HomeController.load() - Unable to load: " + err.message);
    }
}

HomeController.prototype.getIndexBlackNum = function (){
	try{
		var parent = this;
		var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_HOME_BASE;
		var promise = URLManager.getInstance().ajaxCall(link);
		promise.fail(function (jqXHR, textStatus, err) {
			console.log(textStatus + " - " + err.message);
			layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
		});
		promise.done(function (result) {
			if (typeof (result) != "undefined" && typeof (result.dpiInfo) != null) {
				parent.pViewHandle.find(parent.pIndexBlackNum).html(result.sys_info.blackNum);
				parent.pViewHandle.find(parent.pIndexTodayEventNum).html(result.sys_info.todayEventNum);
				parent.pViewHandle.find(parent.pIndexHistoryEventNum).html(result.sys_info.historyEventNum);
				parent.pViewHandle.find(parent.pIndex_indexAssetNum).html(result.sys_info.top_num);
                var data={name:['在线率','离线率'],item:[parent.createPieStruct('在线率',Math.round(result.sys_info.live_per)),
                    parent.createPieStruct('离线率',Math.round(result.sys_info.unlive_per))]};
                var eventPie = parent.initPieChart(parent.pLiverate, '资产在线率',data,true);
			}
			else {
				layer.alert("获取失败", { icon: 5 });
			}
		});
	} 
	catch (err) {
        console.error("ERROR - HomeController.getIndexBlackNum() - Unable to get device inforamtion: " + err.message);
    }	
}

HomeController.prototype.getSystemInfo = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_INFO;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.dpiInfo) != null) {
                parent.pViewHandle.find(parent.pSysClientIP).html(result.dpiInfo.ip);
                parent.pViewHandle.find(parent.pSysClientIP6).html(result.dpiInfo.ip6).attr("title",result.dpiInfo.ip6);
                parent.pViewHandle.find(parent.pSysProduct).html(result.dpiInfo.product);
                parent.pViewHandle.find(parent.pSysSerialNum).html(result.dpiInfo.SN);
                parent.pViewHandle.find(parent.pSysSoftware).html(result.dpiInfo.version);
				//parent.pViewHandle.find(parent.pSysRunTime).html(result.dpiInfo.runtime);
                if(result.dpiInfo.ip6==""){
                    $(".ip6").hide()
                }else{
                    $(".ip6").show()
                }
                var day,hour,minute,second;
                clearInterval(gloTimer.homeTimer);
                var curTime=result.dpiInfo.runtime,durationTime;
                gloTimer.homeTimer=setInterval(function(){
                    parent.countTime(curTime);
                },1000);
                parent.countTime=function(times){
                    curTime+=1;
                    day=Math.floor(times/86400),
                    hour=Math.floor((times%86400)/3600),
                    minute=Math.floor((times%86400)%3600/60),
                    second=((times%86400)%3600)%60;
                    durationTime=day+'天'+hour+'小时'+minute+'分钟'+second+'秒';
                    parent.pViewHandle.find(parent.pSysRunTime).html(durationTime);
                };
                parent.countTime(curTime);
            }
            else {
                layer.alert("获取失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - HomeController.getSystemInfo() - Unable to get device inforamtion: " + err.message);
    }
}

HomeController.prototype.initGaugeChart = function (id, title, type, initValue) {
    var gauge = echarts.init(document.getElementById(id));
    var axisLineCPUColor = [[0.3, '#e1f1fe'], [0.7, '#c2def3'], [1, '#85c5f3']];
    var axisLineMemoryColor = [[0.3, '#e0e5fd'], [0.7, '#c2c9fa'], [1, '#8592f3']];
    var axisLineColor;
    var detailTextColor;
    var pointerColor;
    switch (type) {
        case 1: axisLineColor = axisLineCPUColor; detailTextColor = '#85c5f3'; pointerColor = '#85c5f3'; break;
        default : axisLineColor = axisLineMemoryColor; detailTextColor = '#8592f3'; pointerColor = '#8592f3'; break;
    }
    var option = {
        tooltip: {
            formatter: "{a}: {c}%"
        },
        series: [
            {
                name: title,
                type: 'gauge',
                center: ['50%', '55%'],    // 默认全局居中
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
                data: [{ value: initValue, name: 'kaka' }]
            }
        ]
    };

    gauge.setOption(option);

    return gauge;
}

HomeController.prototype.selectProtocolFlow = function () {
    var html = "";
    try {
        var parent = this;
        var data = {
            name: [],
            item: []
        };
        var timeFlag = 1;//$(this.pDdlTime3 + " option:selected").val();
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
                    fontFamily: '微软雅黑'
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
            x: 18,
            y: 15,
            textStyle: {
                color: '#248aa2',
                fontFamily: '微软雅黑',
                fontSize: 18
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
        series: [
            {
                name: 'pie',
                type: 'pie',
                radius: ['30%', '53%'],
                center: ['50%', '60%'],
                data: [
                        { value: 1, name: '0%', itemStyle: labelBottom }
                ]
            }
        ]
    };
    pie.setOption(option);
    return pie;
}

HomeController.prototype.initPieChart = function (id, title, data,noselt) {
    var parent = this;
    var pie = echarts.init(document.getElementById(id));
    var option = {
        title: {
            x: 18,
            y: 15,
            text: title,
            textStyle: {
                fontSize: 18,
                fontWeight: 'bolder',
                fontFamily: '微软雅黑',
                color: '#248aa2'
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
            formatter: "{b}：{d}%"
        },
        color:noselt?[parent.color[1],parent.color[0]]:parent.color,
        legend: {
            orient: 'horizontal',
            x: 30,
            y: 50,
            selectedMode:!noselt,
            data: data.name
        },
        calculable: false,
        series: [
            {
                name: 'pie',
                type: 'pie',
                radius: noselt?'53%':['30%', '53%'],
                center: ['50%', '60%'],
                data: data.item,
                itemStyle : {
                    normal : {
                        label : {
                            show : noselt?true:false,
                            formatter: "{b}：{c} ({d}%)"
                        },
                        labelLine : {
                            show : noselt?true:false
                        }
                    },
                    emphasis : {
                        label : {
                            show : false,
                            position : 'center',
                            textStyle : {
                                fontSize : '30',
                                fontWeight : 'bold'
                            }
                        }
                    }
                }
            }
        ]
    };
    pie.setOption(option);
    return pie;
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

HomeController.prototype.selectSessionNum = function () {
    var html = "";
    try {
        var parent = this;
        var data = {
            x: [],
            y: []
        };
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_SESSION_ALL_NUM;
        var promise = URLManager.getInstance().ajaxSyncCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined") {
                for (var i = 0; i < result.rows.length; i++) {
                    data.y.unshift(result.rows[i][1]);
					
                }
                for (var i = 0; i < result.rows.length; i++) {
                    data.x.unshift(result.rows[i][0]);
                }
            }
        });
        return data;
    }
    catch (err) {
        console.error("ERROR - HomeController.selectSessionNum() - Unable to get all points: " + err.message);
        return data;
    }
}

HomeController.prototype.selectEventPie = function () {
    var html = "";
    try {
        var parent = this;
        var data = {
            name: [],
            item: []
        };
        var timeFlag = 1;//$(this.pDdlTime2 + " option:selected").val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_EVENT_PERCENT;
        var promise = URLManager.getInstance().ajaxSyncCall(link, { timeDelta: timeFlag });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                for (var i = 0; i < result.rows.length; i++) {
                    var color = parent.color[i];
                    if (result.rows[i][1] != 0) {
                        switch(result.rows[i][0]){
                            case 1:
                                result.rows[i][0]='白名单';break;
                            case 2:
                                result.rows[i][0]='黑名单';break;
                            case 3:
                                result.rows[i][0]='IP/MAC';break;
                            case 4:
                                result.rows[i][0]='流量告警';break;
                            case 5:
                                result.rows[i][0]='MAC过滤';break;
                            case 6:
                                result.rows[i][0]='资产告警';break;
                            case 7:
                                result.rows[i][0]='不合规报文告警';break;
                        }
                        var item = parent.createPieStruct(result.rows[i][0], result.rows[i][1], color);
                        data.name.push(result.rows[i][0]);
                        data.item.push(item);
                    }
                }
                /*if(!data.name.length){
                    var item = parent.createPieStruct('暂无数据', 1, '#eeeeee');
                    data.name.push('暂无数据');
                    data.item.push(item);
                }*/
            }/*else{
                result.rows[i][0]='';
                var item = parent.createPieStruct('暂无数据', 0, '#eeeeee');
                data.name.push('暂无数据');
                data.item.push(item);
            }*/
        });
        return data;
    }
    catch (err) {
        console.error("ERROR - HomeController.selectEventPie() - Unable to get device flow data: " + err.message);
        return data;
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
        var timeFlag = 1;//$(this.pDdlTime2 + " option:selected").val();
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

HomeController.prototype.selectBaseData = function (CPUChrt, memoryChart) {
    var parent = this;
    //debugger;
    try {
        var promise = URLManager.getInstance().ajaxCall(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_HOME_BASE);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            return null;
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined") {
                parent.sysInfo={
                    cpu:result.sys_info.cpuState,
                    mem:result.sys_info.memoryState,
                    disk:result.sys_info.diskState
                };
                $(parent.pSessionCpu).children().eq(0).find('span').text(parent.sysInfo.cpu);
                $(parent.pSessionCpu).children().eq(1).find('progress').val(parent.sysInfo.cpu);
                $(parent.pSessionMem).children().eq(0).find('span').text(parent.sysInfo.mem);
                $(parent.pSessionMem).children().eq(1).find('progress').val(parent.sysInfo.mem);
                $(parent.pSessionDisk).children().eq(0).find('span').text(parent.sysInfo.disk);
                $(parent.pSessionDisk).children().eq(1).find('progress').val(parent.sysInfo.disk);

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
                        var tipBox = parent.initTipBox("EXT", data[1], data[2], data[3], (data[4]||""), (data[5]||""));
                        parent.layerTip.tip0 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000'],
                            area:['auto']
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
                        var tipBox = parent.initTipBox("MGMT", data[1], data[2], data[3], (data[4]||""), (data[5]||""));
                        parent.layerTip.tip1 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000'],
                            area:['auto']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }
                //判断是否为新硬件，显示几个接口
                if(result.sys_info.hw_type=="1"){
                    $(".socket-content .jackbox").width('300');
                    $(".type_1").show();
                }else{
                    $(".socket-content .jackbox").width('205');
                    $(".type_1").hide();
                }

                //p0,p1,p2,p3,p4,p5
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
                        var tipBox = parent.initTipBox("ETH1", data[1], data[2], data[3], (data[4]||""), (data[5]||""));
                        parent.layerTip.tip3 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000'],
                            area:['auto']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }

                if (result.sys_info.p2LinkState) {
                    $(parent.pP2Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_YES);
                }
                else {
                    $(parent.pP2Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_NO)
                }
                if (typeof (result.sys_info.p2Info) != "undefined" && result.sys_info.p2Info != "") {
                    $(parent.pP2Port).attr("alt", result.sys_info.p2Info);
                    $(parent.pP2Port).hover(function () {
                        var data = $(this).attr("alt").split(';');
                        var tipBox = parent.initTipBox("ETH2", data[1], data[2], data[3],(data[4]||""), (data[5]||""));
                        parent.layerTip.tip3 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000'],
                            area:['auto']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }
                if (result.sys_info.p3LinkState) {
                    $(parent.pP3Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_YES);
                }
                else {
                    $(parent.pP3Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_NO)
                }
                if (typeof (result.sys_info.p3Info) != "undefined" && result.sys_info.p3Info != "") {
                    $(parent.pP3Port).attr("alt", result.sys_info.p3Info);
                    $(parent.pP3Port).hover(function () {
                        var data = $(this).attr("alt").split(';');
                        var tipBox = parent.initTipBox("ETH3", data[1], data[2], data[3], (data[4]||""), (data[5]||""),parseInt(result.sys_info.hw_type)?0:1);
                        parent.layerTip.tip4 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000'],
                            area:['auto']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }
                if (result.sys_info.p4LinkState){
                    $(parent.pP4Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_YES);
                }
                else {
                    $(parent.pP4Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_NO)
                }
                if (typeof (result.sys_info.p4Info) != "undefined" && result.sys_info.p4Info != "") {
                    $(parent.pP4Port).attr("alt", result.sys_info.p4Info);
                    $(parent.pP4Port).hover(function () {
                        var data = $(this).attr("alt").split(';');
                        var tipBox = parent.initTipBox("ETH4", data[1], data[2], data[3], (data[4]||""), (data[5]||""));
                        parent.layerTip.tip5 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000'],
                            area:['auto']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }
                if (result.sys_info.p5LinkState) {
                    $(parent.pP5Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_YES);
                }
                else {
                    $(parent.pP5Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_NO)
                }
                if (typeof (result.sys_info.p5Info) != "undefined" && result.sys_info.p5Info != "") {
                    $(parent.pP5Port).attr("alt", result.sys_info.p5Info);
                    $(parent.pP5Port).hover(function () {
                        var data = $(this).attr("alt").split(';');
                        var tipBox = parent.initTipBox("ETH5", data[1], data[2], data[3], (data[4]||""), (data[5]||""),parseInt(result.sys_info.hw_type)?1:0);
                        parent.layerTip.tip6 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000'],
                            area:['auto']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }
                if (result.sys_info.p6LinkState) {
                    $(parent.pP6Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_YES);
                }
                else {
                    $(parent.pP6Port).attr("src", Constants.PORT_IMAGETYPE[APPCONFIG.PRODUCT].PORT_NO)
                }
                if (typeof (result.sys_info.p6Info) != "undefined" && result.sys_info.p6Info != "") {
                    $(parent.pP6Port).attr("alt", result.sys_info.p6Info);
                    $(parent.pP6Port).hover(function () {
                        var data = $(this).attr("alt").split(';');
                        var tipBox = parent.initTipBox("P6", data[1], data[2], data[3], (data[4]||""), (data[5]||""));
                        parent.layerTip.tip6 = layer.tips(tipBox, this, {
                            time: 100000,
                            tips: [2, '#eee', '#ff0000'],
                            area:['auto']
                        });
                        $(".layui-layer-content").css("color", "#222");
                    }, function () {
                        parent.disposeTipBox();
                    });
                }
				
               /* var CPUOption = CPUChrt.getOption();
                CPUOption.series[0].data[0].value = result.sys_info.cpuState;
                $("#"+parent.pCPUState).attr("data-value", result.sys_info.cpuState);
                CPUChrt.setOption(CPUOption, true);

                var memoryOption = memoryChart.getOption();
                memoryOption.series[0].data[0].value = result.sys_info.memoryState;
                memoryOption.series[0].data[0].name = result.sys_info.memorySize+"GB";
                $("#" + parent.pMemoryState).attr("data-value", result.sys_info.memoryState);
                $("#" + parent.pMemoryState).attr("data-name", result.sys_info.memorySize);
                memoryChart.setOption(memoryOption, true);*/

            }
        });

    }
    catch (err) {
        console.error("ERROR - HomeController.selectBaseData() - Unable to load: " + err.message);
    }
}

HomeController.prototype.selectSingleTotalFlow = function () {
    var html = "";
    try {
        var parent = this;
        var data = { x: '', y: 0 };
        
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_TOTAL_FLOW_POINT;
        var promise = URLManager.getInstance().ajaxSyncCall(link);
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

HomeController.prototype.selectoneSessionNum = function () {
    var html = "";
    try {
        var parent = this;
        var data = { x: '', y: 0 };
        var timeFlag = $(this.pDdlTime1 + " option:selected").val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_SESSION_ONE_NUM;
        var promise = URLManager.getInstance().ajaxSyncCall(link, { timeDelta: timeFlag });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
				for (var i = 0; i < result.rows.length; i++) {
                    data.x = result.rows[0];
                }
                for (var i = 0; i < result.rows.length; i++) {
                    data.y = result.rows[1];
                }
            }
        });
		
        return data;
    }
    catch (err) {
        return data;
        console.error("ERROR - HomeController.selectSingleTotalFlow() - Unable to get single point: " + err.message);
    }
}

HomeController.prototype.initBarChart = function (id, title, data) {
    var parent=this;
    var dataName=[],dataVal=[];
    $(data['item']).each(function(i,d){
        dataName.push(d['name']);
        dataVal.push(d['value']);
    });
    var bar = echarts.init(document.getElementById(id));
    var option = {
        title: {
            x: 18,
            y: 15,
            text: title,
            textStyle:
                {
                    fontSize: 18,
                    fontWeight: 'bolder',
                    fontFamily: '微软雅黑',
                    color: '#248aa2'
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
                return a[0][1] + ": " + Math.round(a[0][2] * 10000)/100 + "%";
            }
        },/*
        legend: {
            orient: 'horizontal',
            x: 30,
            y: 50,
            data: dataName
        },*/
        calculable: false,
        yAxis: [
            {
                type: 'value',
                max: 1,
                min: 0,
                boundaryGap: false,
                axisLabel: {
                    formatter: function (v) { return Math.round(v * 10000)/100 + "%"; }
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
        grid: {
            y: 80,
            x:70,
            x2:70
        },
        xAxis: [
            {
                type: 'category',
                data: dataName,
                axisLabel: {
                    formatter: function (v) {
                        if($('#'+parent.pDeviceFlow).innerWidth()<=767&&$('#'+parent.pDeviceFlow).innerWidth()>570){
                            return v.length>10? v.substr(0,6)+'...':v;
                        }else if($('#'+parent.pDeviceFlow).innerWidth()<=570){
                            return v.substr(0,2)+'...';
                        }
                        return v.length>10? v.substr(0,8)+'...':v;
                    }
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
        color: ["#3a94d3","#fa8567","#fac567","#28d8ca","#9667fa"],
        series: [
            {
                type: 'bar',
                //name:dataName[0],
                data: dataVal,
                itemStyle: {
                    normal: {
                        color: function(params) {
                            // build a color map as your need.
                            var colorList = [
                                "#3a94d3","#fa8567","#fac567","#28d8ca","#9667fa",'#E87C25','#27727B',
                                '#FE8463','#9BCA63','#FAD860'
                            ];
                            return colorList[params.dataIndex]
                        },
                        label: {
                            show: true,
                            textStyle: {
                                fontSize: 12
                            },
                            formatter: function (a) {
                                return Math.round(a.value * 10000)/100 + "%";
                            }
                        }
                    }
                },
                barWidth: 30
            }
        ]

    };

    bar.setOption(option);
    return bar;
}


HomeController.prototype.initNoDataBarChart = function (id, title) {
    var bar = echarts.init(document.getElementById(id));
    var option = {
        title: {
            x: 18,
            y: 15,
            text: title,
            subtext: '暂无数据',
            textStyle:
            {
                fontSize: 18,
                fontWeight: 'bolder',
                fontFamily: '微软雅黑',
                color: '#248aa2'
            },
            subtextStyle:
            {
                fontSize: 12,
                /*fontWeight: 'bolder',*/
                fontFamily: '微软雅黑',
                color: '#333'
            }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function (a) {
                return a[0][1] + ": " + (a[0][2] * 100) + "%";
            }
        },
        calculable: false,
        yAxis: [
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
        grid: {
            y: 80
        },
        xAxis: [
            {
                type: 'category',
                data: ['暂无数据'],
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
        color: ["#ccc"],
        series: [
            {
                type: 'bar',
                name:'暂无数据',
                data: [0],
                itemStyle: {
                    normal: {
                        label: {
                            show: true,
                            textStyle: {
                                fontSize: 12/*,
                                 color: '#333'*/
                            },
                            formatter: function (a) {
                                return (a.value * 100) + "%";
                            }
                        }
                    }
                },
                barWidth: 30
            }
        ]

    };

    bar.setOption(option);
    return bar;
}


HomeController.prototype.initLineChart = function (id, title,data) {
   var line = echarts.init(document.getElementById(id));
    var option = {
        title: {
            x: 18,
            y: 15,
            text: title,
            textStyle:
                {
                    fontSize: 18,
                    fontWeight: 'bolder',
                    fontFamily: '微软雅黑',
                    color: '#248aa2'
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
            formatter: '{b} -- {c}Kbps'
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
                axisLabel: {
                    //X轴刻度配置
                    interval: 29
                },
                boundaryGap: false,
                data: data.x
            }
        ],
        yAxis: [
            {
                type: 'value',/*
                min: 0,
                max: data.y.length == 0 ? 1 : Math.ceil(Math.max.apply(null, data.y)) + 1,
                boundaryGap: false,*/
                axisLabel: {
                    formatter: function (v) {
                        if (v == 0) {
                            return v+' kbps';
                        }
                        return v+' kbps';
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

HomeController.prototype.initSessionLineChart = function (id, title,data) {
   var line = echarts.init(document.getElementById(id));
    var option = {
        title: {
            x: 18,
            y: 15,
            text: title,
            textStyle:
                {
                    fontSize: 18,
                    fontWeight: 'bolder',
                    fontFamily: '微软雅黑',
                    color: '#248aa2'
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
            formatter: '{b} -- {c}条'
        },
        xAxis: [
            {
                type: 'category',
                data: data.x
            }
        ],
        yAxis: [
            {
                type: 'value',/*
                min: 0,
                max: data.y.length == 0 ? 5 : (Math.round(Math.max.apply(null, data.y)/5)+1) *5,*/
                /*splitNumber:5,
                boundaryGap: false,
                scale:false,*/
                axisLabel: {
                    formatter: function (v) {
                        if (v == 0) {
                            return v;
                        }
                        return v;
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

HomeController.prototype.createPieStruct = function (name, value, color) {
    var item = {
        name: name,
        value: value/*,
        itemStyle: {
            normal: {
                color: color,
                label: {
                    show: line ? true : false,
                    //formatter: '{d}%',
                    textStyle: {
                        fontSize: 14,
                        fontFamily: "微软雅黑"
                    },
                    position: 'outer'
                },
                labelLine: {
                    show: line ? true : false
                }
            }
        }*/
    };
    if(color){
        item.itemStyle={
            normal: {
                color: color
            }
        }
    }
    return item;
}

HomeController.prototype.initTipBox = function (title, mac, ip, subip,ip6,Subnet_prefix,devtype) {
    var tipBox = '';
    tipBox += '<ul>';
    tipBox += '<li>接口名称：<span>' + title + '</span></li>';
    tipBox += '<li>硬件地址：<span>' + ip + '</span></li>';
    if(title=="MGMT"||devtype){
        tipBox += '<li>接口ipv4地址：<span>' + mac + '</span></li>';
        tipBox += '<li>ipv4子网掩码 ：<span>' + subip + '</span></li>';
    }
    if(title=="MGMT"&&ip6!=""){
        tipBox += '<li>接口ipv6地址：<span>' + ip6 + '</span></li>';
        tipBox += '<li>ipv6前缀：<span>' + Subnet_prefix + '</span></li>';
    }
    tipBox += '</ul>';
    tipBox += '';
    return tipBox;
}

HomeController.prototype.disposeTipBox = function () {
    layer.closeAll("tips");
}


// HomeController.prototype.clearTimer = function () {
//     if (typeof (gloTimer.chartTimer) != "undefined" && gloTimer.chartTimer != null) {
//         clearInterval(gloTimer.chartTimer);
//     }
// }

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