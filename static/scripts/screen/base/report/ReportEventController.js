function ReportEventController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pBtnSetting = "#" + this.elementId + "_btnSetting";
	this.pBtnGenerate = "#" + this.elementId + "_btnGenerate";
    this.pTdEventlistList = "#" + this.elementId + "_tdEventlistList";
    this.pDdlDurtion = "#" + this.elementId + "_ddlDurtion";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pBtnDetailDownload = "#btnDetailDownload";
    this.pBtnReportDownload = "#btnReportDownload";
    this.pBtnDelete = "#" + this.elementId + "_btnDelete";
    
	this.pTxtStrateTime = "#" + this.elementId + "_txtStartTime";
	this.pTxtEndTime = "#" + this.elementId + "_txtEndTime";
    this.pTxtSourceName = "#" + this.elementId + "_txtSourceName";
    this.pTxtDestinationName = "#" + this.elementId + "_txtDestinationName";
	this.pTxtSrcAddr = "#" + this.elementId + "_txtSrcAddr";
	this.pTxtDstAddr = "#" + this.elementId + "_txtDstAddr";
	this.pDdlProtocol = "#" + this.elementId + "_ddlProtocol";
    this.pDdlEventSource = "#" + this.elementId + "_ddlEventSource";
    this.pDdlRiskLevel = "#" + this.elementId + "_ddlRiskLevel";

    this.pBtnFilter="#" + this.elementId + '_event_btnFilter';
    this.pAdvOpt='#' + this.elementId + "_advOpt";
	
    this.pDownloadFile = "";

    this.interfaceChart = null;
    this.pEventlistPager = null;
	
	this.protocolList = Constants.AUDIT_PROTOCOL_LIST[APPCONFIG.PRODUCT];
}

ReportEventController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.REPORT_EVENT_DIALOG],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - ReportEventController.init() - Unable to initialize all templates: " + err.message);
    }
}

ReportEventController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.REPORT_EVENT), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - ReportEventController.initShell() - Unable to initialize: " + err.message);
    }
}

ReportEventController.prototype.initControls = function () {
    try {
        var parent = this;
		$(this.pDdlProtocol).empty();
        $(this.pDdlProtocol).append("<option value=''>所有协议</option>");
        $.each(this.protocolList, function () {
            $(parent.pDdlProtocol).append("<option value='" + this.key + "'>" + this.name + "</option>");
        });
        $(this.pBtnSetting).on("click", function () {
            parent.setReportEventModel($(parent.pDdlDurtion).val());
        });
        $(this.pBtnGenerate).on("click", function () {
            parent.setReportAlarmModel();
        });
        $(this.pBtnFilter).bind({click:function(){
            parent.pViewHandle.find(parent.pTxtSrcAddr).val("");
            parent.pViewHandle.find(parent.pTxtDstAddr).val("");
            parent.pViewHandle.find(parent.pDdlProtocol).val("");
            parent.pViewHandle.find(parent.pTxtStrateTime).val("");
            parent.pViewHandle.find(parent.pTxtEndTime).val("");
            parent.pViewHandle.find(parent.pDdlRiskLevel).val("");
            parent.pViewHandle.find(parent.pDdlEventSource).val('');
            parent.pViewHandle.find(parent.pTxtDestinationName).val("");
            parent.pViewHandle.find(parent.pTxtSourceName).val("");
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            $(parent.pAdvOpt).toggle();
        }});
        $(this.pBtnDelete).on("click", function () {
            parent.preDelete=[];
            $(parent.pTdEventlistList).find('tbody input[type=checkbox]').filter('.selflag').each(function(i,d){
                if($(d).prop('checked')){
                    parent.preDelete.push($(d).data('id'));
                }
            });
            var delIds=parent.preDelete;
            if(parent.preDelete.length<=0){
                layer.alert('请选择需要删除的规则！',{icon:2});
                return;
            }
            layer.confirm('确定要删除么？',{icon:7,title:'注意：'}, function(index) {
                layer.close(index);
                parent.delReportList(delIds);
            })
        });
    }
    catch (err) {
        console.error("ERROR - ReportEventController.initControls() - Unable to initialize control: " + err.message);
    }
}

/*ReportEventController.prototype.exportEvent = function (file) {
    try {
        window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].SET_REPORT_DOWNLOADDETAIL + file);
    }
    catch (err) {
        console.error("ERROR - SystemReportEventController.exportEvent() - Unable to export all events: " + err.message);
    }
}*/

ReportEventController.prototype.load = function () {
    try {
        this.getReportEventModel();
        this.selectEventlists(1);
    }
    catch (err) {
        console.error("ERROR - ReportEventController.load() - Unable to load: " + err.message);
    }
}

ReportEventController.prototype.getReportEventModel = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_REPORT_EVENTMODEL;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.status) != "undefined" && typeof (result.freq) != "undefined") {
                switch (result.status) {
                    case 1:
                        $(parent.pDdlDurtion).val(result.freq);
                        break;
                }
            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportEventController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

ReportEventController.prototype.setReportEventModel = function (freq) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].SET_REPORT_EVENTMODEL;
        var data = { freq: freq };
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert("操作成功", { icon: 6 });
                        break;
                    case 0:
                        layer.alert("操作失败", { icon: 5 });
                        break;
                }
            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportEventController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

ReportEventController.prototype.setReportAlarmModel = function (freq) {
    try {
        var parent = this;
        var layerLoad=layer.load(2, {content:'报告正在生成中...',shade: [0.4, '#fff'],success: function(layero) {
            layero.css('padding-left', '30px');
            layero.find('.layui-layer-content').css({
                'padding-left': '40px',
                'width': '170px',
                lineHeight:'32px',
                fontWeight:'bold'
            });
        }});
		var starttime = $.trim($(this.pTxtStrateTime).val());
        var endtime  = $.trim($(this.pTxtEndTime).val());
        var srcaddr = $.trim($(this.pTxtSrcAddr).val());
		var dstaddr = $.trim($(this.pTxtDstAddr).val());
		var proto = $.trim($(this.pDdlProtocol).val());
        var signatureName= $.trim($(this.pDdlEventSource).val());
        var sourceName= $.trim($(this.pTxtSourceName).val());
        var destinationName= $.trim($(this.pTxtDestinationName).val());
        var riskLevel= $.trim($(this.pDdlRiskLevel).val());
        if(starttime==""){
            layer.alert("请选择开始时间", { icon: 5 });
            layer.close(layerLoad);
            return false;
        }
        if(endtime==""){
            layer.alert("请选择结束时间", { icon: 5 });
            layer.close(layerLoad);
            return false;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].REPORT_ALARM_MANUAL;
        var data = {
            starttime: starttime,
            endtime:endtime,
            srcaddr:srcaddr,
            dstaddr:dstaddr,
            proto:proto,
            signatureName:signatureName,
            sourceName:sourceName,
            destinationName:destinationName,
            riskLevel:riskLevel
        };
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert("操作成功", { icon: 6 });
						parent.selectEventlists();
                        break;
                    case 0:
                        layer.alert("操作失败", { icon: 5 });
                        layer.close(layerLoad);
                        break;
                }
            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportEventController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

ReportEventController.prototype.selectEventlists = function (pageIndex) {
    var html = "";
    html += '<thead>';
    html += '<tr><th class="th-check" style="width:80px;"><input type="checkbox" class="chinput" id="selectAll"><label for="selectAll" ></label>全选</th>';
    html += '<th>报告日期</th><th>报告名称</th><th style="width:250px">操作</th></tr>';
    html += '</thead>';
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_REPORT_EVENT ;
        var data = {page:pageIndex};
        var loadIndex = layer.load(2);
        var promise = URLManager.getInstance().ajaxCall(link,data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='4'>暂无数据</td></tr>";
            $(parent.pTdEventlistList).html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tbody><tr>";
                        html += "<td>"+"<input type='checkbox' class='chinput selflag' data-idx='"+result.rows[i][1]+"' data-id=\""+result.rows[i][0]+"\" id=\""+result.rows[i][0]+"\" /><label for=\""+result.rows[i][0]+"\"></label></td>";
                        html += "<td>" + result.rows[i][2] + "</td>";
                        html += "<td><span class='tomodify'>" + result.rows[i][1]+ "</span>";
                        html += "<input type='text' style='display:none;' class='form-control'  value='"+result.rows[i][1]+"' title='"+result.rows[i][1]+"' placeholder='长度不超过128' maxlength='128'></td>";
                        html += "<td><button style='margin-right:5px;' class='btn btn-default btn-xs btn-color-details Editfile' data-key='" + result.rows[i][0] + "' data-file='" + result.rows[i][6] + "'><i class='fa fa-edit' style='margin-right:3px;'></i>编辑</button>";
                        html += '<span class="editform" style="display:none;"><button class="btn btn-primary btn-xs btn-primary-s" data-key="' + result.rows[i][0] + '">确认</button><button class="btn btn-danger btn-xs btn-danger-s">取消</button></span>';
                        html += "<button style='margin-right:5px;' class='btn btn-default btn-xs btn-color-details Detailfile' data-key='" + result.rows[i][0] + "' data-file='" + result.rows[i][6] + "'><i class='fa fa-level-down' style='margin-right:3px;'></i>详情下载</button>";
                        html += "<button class='btn btn-default btn-xs btn-color-details Reportfile' data-key='" + result.rows[i][0] + "' data-file='" + result.rows[i][6] + "' ><i class='fa fa-level-down' style='margin-right:3px;'></i>报表下载</button></td>";
                        html += "</tr></tbody>";
                    }
                }
                else {
                    html += "<tbody><tr><td colspan='4'>暂无数据</td></tr></tbody>";
                }
            }
            else {
                html += "<tbody><tr><td colspan='4'>暂无数据</td></tr></tbody>";
            }
            $(parent.pTdEventlistList).html(html);
            layer.close(loadIndex);
            if (typeof (result.num) != "undefined") {
                $(parent.pLblTotalBlacklist).text(result.num);
            }
            //详情下载及报告下载按钮
            $(parent.pTdEventlistList).find("button.Detailfile").on("click", function (event) {
                var report_id=$(this).attr("data-key");
                window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].REPORT_ALARM_DETAIL_DOWNLOAD + report_id + '?loginuser=' + JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']).username);
            });
            $(parent.pTdEventlistList).find("button.Reportfile").on("click", function (event) {
                var report_id=$(this).attr("data-key");
                window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].REPORT_ALARM_DOWNLOAD + report_id + '?loginuser=' + JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']).username);
            });
            //编辑按钮
            $(parent.pTdEventlistList).find("button.Editfile").on("click", function (event) {
                $(this).parents('tr').find('.tomodify').hide().next().show();
                $(this).hide().next().show();
            });
            //取消
            $(parent.pTdEventlistList).find(".editform button:nth-child(2n)").on("click", function (event) {
                $(this).parents('tr').find('.tomodify').show().next().hide();
                $(this).parent().hide().prev().show();
            });
            //确认
            $(parent.pTdEventlistList).find(".editform button:nth-child(2n-1)").on("click", function (event) {
                var newName=$(this).parents('tr').find('.tomodify').next().val();
                if(newName==""){
                    layer.alert('报告名称不能为空',{icon:5});
                }else if(newName==$(this).parents('tr').find('.tomodify').text()){//名称相同不发请求
                    layer.alert('修改成功',{icon:6});
                    $(this).parents('tr').find('.tomodify').show().next().hide();
                    $(this).parent().hide().prev().show();
                }else{
                    var id=$(this).attr("data-key");
                    console.log($(this).attr("data-key"));
                    var loadIndex1 = layer.load(2),modpromise = URLManager.getInstance().ajaxCallByURL(link, "PUT", {id:id,report_name:newName});
                    modpromise.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                        layer.close(loadIndex1);
                    });
                    modpromise.done(function (result) {
                        if (result.status) {
                            layer.close(loadIndex1);layer.alert('修改成功',{icon:6});
                            parent.selectEventlists();
                        }else{
                            layer.close(loadIndex1);layer.alert(result.msg,{icon:5});
                            parent.selectEventlists();
                        }
                    });
                }
            });
            $("#selectAll").click(function(){
                parent.checkSwitch=!parent.checkSwitch;
                $(parent.pTdEventlistList).find('input').filter('.selflag').prop('checked',parent.checkSwitch);
            });
            /*$(parent.pTdEventlistList).find("button").on("click", function (event) {
                var id = $(this).attr("data-key");
                var date = $(this).attr("data-date");
                var filename1 = $(this).attr("data-name1");
                var filename = $(this).attr("data-name");
                parent.pDownloadFile = $(this).attr("data-file");
                var dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.REPORT_EVENT_DIALOG), {
                    elementId: parent.elementId + "_dialog"
                });
                var width = parent.pViewHandle.find(".row").width() - 10 + "px";
                var height = $(window).height() - parent.pViewHandle.find(".row").offset().top - 10 + "px";
                layer.open({
                    type: 1,
                    title: "安全事件",
                    area: [width, height],
                    offset: ["82px", "200px"],
                    shade: [0.5, '#393D49'],
                    content: dialogTemplate,
                    success: function (layero, index) {
                        parent.getEventDetails(layero, id, date, filename1);
                        $(parent.pBtnDetailDownload).on("click", function () {
                            parent.exportEvent(parent.pDownloadFile);
                        });
                        $(parent.pBtnReportDownload).on("click", function () {
                            parent.downloadEchart(parent.interfaceChart, filename);
                        });
                        $(window).on("resize", function () {
                            var pwidth = parent.pViewHandle.find(".row").width() - 10;
                            var pheight = $(window).height() - parent.pViewHandle.find(".row").offset().top - 10;
                            layero.width(pwidth);
                            layero.height(pheight);
                        })
                    }
                });

            });*/
            /*$(parent.pTdEventlistList).find("input[type='checkbox']").on("click", function (event) {
                var id = $(this).attr("data-key");
                var status = $(this).prop("checked") ? 1 : 0;
                parent.updateBlacklist(id, status, $(this), !$(this).prop("checked"));
            });*/
            if (parent.pEventlistPager == null) {
                parent.pEventlistPager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.selectEventlists(pageIndex);
                });
                parent.pEventlistPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tbody><tr><td colspan='4'>暂无数据</td></tr></tbody>";
        $(this.pTdEventlistList).html(html);
        console.error("ERROR - ReportEventController.selectEventlists() - Unable to get all events: " + err.message);
    }
}
ReportEventController.prototype.delReportList = function (delIds) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_REPORT_EVENT;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"DELETE",{id_list:delIds.join(',')});
        promise.fail(function (jqXHR, textStatus, err) {
            layer.alert("删除失败", { icon: 2 });
            console.log(textStatus + " - " + err.msg);
        });
        promise.done(function(res){
            if(res.status){
                layer.alert("删除成功", { icon: 6 });
                parent.selectEventlists();
                if($(parent.pSelectAll).is(':checked')){
                    $(parent.pSelectAll).prop('checked',false);
                    parent.checkSwitch=false;
                    $(parent.pTdEventlistList).find('input').prop('checked',parent.checkSwitch);
                }
            }else{
                layer.close(loadIndex);layer.alert("删除失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportEventController.delReportList() - Unable to delete eventReportList: " + err.message);
    }
}
/*ReportEventController.prototype.getEventDetails = function (viewHandler, id, date, filename1) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_REPORT_EVENTSTATIC;
        var data = {id:id};
        var dataAll = { PAlarm: { x: [], y: [] }, PStop: { x: [], y: [] } };
        var promise = URLManager.getInstance().ajaxSyncCall(link,data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.status) != "undefined" && typeof (result.rows) != "undefined") {
                switch (result.status) {
                    case 1:
                        for (var i = 0; i < result.rows.length; i++) {
                            dataAll.PAlarm.x.push(result.rows[i][0]);
                            dataAll.PAlarm.y.push(result.rows[i][1]);
                            dataAll.PStop.x.push(result.rows[i][0]);
                            dataAll.PStop.y.push(result.rows[i][2]);
                        }
                        parent.interfaceChart = parent.initLineChart('divFlowInterface', filename1 + "_" + date, dataAll);
                        break;
                }

            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportEventController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

ReportEventController.prototype.downloadEchart = function (myChart,title) {
    try {
        var img = new Image();
        img.src = myChart.getDataURL('png').replace("data:image/png;base64,", "data:image/jpeg;base64,");
        //if ($.browser.msie && ($.browser.version = "9.0"))
        //{
        //    imgData = img.src.replace(_fixType('jpg'), 'image/octet-stream');
        //    saveFile(imgData, title+".jpg");
        //}
        //else
        //{
            var ratio = ($("#divFlowInterface").height() / $("#divFlowInterface").width());
            var adjustedHeight = 810 * ratio;
            var options = {
                // MUST Have:
                data: [],
                fieldName: [],
                fieldIndex: [],
                // Optional:
                img: [img],
                fileName: title,
                title: title,
                chartW: 810,
                chartH: adjustedHeight,
                firstPageNum: 0,
                NumPerPage: 31,
                xOffset: 15,
                yOffset: 25,
                imgxOffset: 15,
                imgyOffset: 25 + (540 / 2) - (adjustedHeight / 2),
                lineH: 15,
                fontSize: 15,
                showPageNum: true,
                options: {
                    orientation: 'l',
                    unit: 'pt',
                    format: 'a4'
                },
                styles: "table, th, td { border-collapse: collapse; border: 0px solid black; text-align: left; } td: nth-child(1) { width: 65px; text-align: center; } td: nth-child(2) { width: 140px; text-align: left; } td: nth-child(3) { width: 150px; text-align: left; } td: nth-child(4) { text-align: left; }",
                theme: ""  //empty or default, blueL, blueD, greenL, greenD, redL, redD
            };
            getPdf(options, "");
        //}
      
    }
    catch (err) {
        console.error("ERROR - ReportEventController.downloadEchart() - Unable to download safe event information: " + err.message);
    }
}

ReportEventController.prototype.initLineChart = function (id, title, data) {
    var parent = this;
    var line = echarts.init(document.getElementById(id));
    var option = {
        title: {
            text: title,
            x: 'center'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['警告', '通知'],
            y: 'bottom'
        },
        toolbox: {
            show: true
        },
        calculable: true,
        xAxis: [
            {
                type: 'category',
                boundaryGap: true,
                splitLine: { show: false },
                data: data.PAlarm.x
            }
        ],
        yAxis: [
            {
                type: 'value',
            }
        ],
        series: [
            {
                name: '警告',
                type: 'bar',
                stack: 'sum',
                symbol: 'none',
                data: data.PAlarm.y
            },
            {
                name: '通知',
                type: 'bar',
                stack: 'sum',
                symbol: 'none',
                data: data.PStop.y
            }

        ]
    };


    line.setOption(option);

    return line;
}*/
ContentFactory.assignToPackage("tdhx.base.report.ReportEventController", ReportEventController);