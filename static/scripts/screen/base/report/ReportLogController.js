function ReportLogController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.pTotalOperationLog = "#" + this.elementId + "_dialog_totalOperationLog";
    this.pTotalSystemEvent = "#" + this.elementId + "_dialog_totalSystemEvent";

    this.pBtnSetting = "#" + this.elementId + "_btnSetting";
    this.pTdEventlistList = "#" + this.elementId + "_tdEventlistList";
    this.pDdlDurtion = "#" + this.elementId + "_ddlDurtion";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pBtnDetailDownload = "#btnDetailDownload";
    this.pBtnReportDownload = "#btnReportDownload";
    this.pBtnDelete = "#" + this.elementId + "_btnDelete";

    this.pBtnGenerate = "#" + this.elementId + "_btnGenerate";
    this.pTxtLogStrateTime = "#" + this.elementId + "_txtLogStartTime";
    this.pTxtLogEndTime = "#" + this.elementId + "_txtLogEndTime";

    this.pBtnFilter="#" + this.elementId + '_event_btnFilter';
    this.pAdvOpt='#' + this.elementId + "_advOpt";

    this.status = "operate";
    this.interfaceChart = null;
    this.pEventlistPager = null;
}

ReportLogController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.REPORT_LOG_DIALOG],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - ReportLogController.init() - Unable to initialize all templates: " + err.message);
    }
}

ReportLogController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.REPORT_LOG), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - ReportLogController.initShell() - Unable to initialize: " + err.message);
    }
}

ReportLogController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pBtnSetting).on("click", function () {
            parent.setReportEventModel($(parent.pDdlDurtion).val());
        });
        $(this.pBtnGenerate).on("click", function () {
            parent.setReportAlarmModel();
        });
        $(this.pBtnFilter).bind({click:function(){
            parent.pViewHandle.find(parent.pTxtLogStrateTime).val("");
            parent.pViewHandle.find(parent.pTxtLogEndTime).val("");
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
        console.error("ERROR - ReportLogController.initControls() - Unable to initialize control: " + err.message);
    }
}

/*ReportLogController.prototype.exportEvent = function (file) {
    try {
        window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].SET_LOG_DOWNLOADDETAIL + file);
    }
    catch (err) {
        console.error("ERROR - SystemReportLogController.exportEvent() - Unable to export all events: " + err.message);
    }
}*/

ReportLogController.prototype.load = function () {
    try {
        this.getReportEventModel();
        this.selectEventlists(1);
    }
    catch (err) {
        console.error("ERROR - ReportLogController.load() - Unable to load: " + err.message);
    }
}

ReportLogController.prototype.setReportAlarmModel = function (freq) {
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
        var starttime = $.trim($(this.pTxtLogStrateTime).val());
        var endtime  = $.trim($(this.pTxtLogEndTime).val());
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
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].REPORT_LOG_MANUAL;
        var data = { starttime: starttime, endtime:endtime};
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
ReportLogController.prototype.getReportEventModel = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_LOG_EVENTMODEL;
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
        console.error("ERROR - ReportLogController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

ReportLogController.prototype.setReportEventModel = function (freq) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].SET_LOG_EVENTMODEL;
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
        console.error("ERROR - ReportLogController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

ReportLogController.prototype.selectEventlists = function (pageIndex) {
    var html = "";
    html += '<thead>';
    html += '<tr><th class="th-check" style="width:80px;"><input type="checkbox" class="chinput" id="selectAll"><label for="selectAll" ></label>全选</th>';
    html += '<th>报告日期</th><th>报告名称</th><th style="width:250px">操作</th></tr>';
    html += '</thead>';
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_LOG_EVENT;
        var data = {page:pageIndex};
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link, data);
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
                window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].REPORT_LOG_DETAIL_DOWNLOAD + report_id + '?loginuser='+JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']).username);
            });
            $(parent.pTdEventlistList).find("button.Reportfile").on("click", function (event) {
                var report_id=$(this).attr("data-key");
                window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].REPORT_LOG_DOWNLOAD + report_id + '?loginuser='+JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']).username);
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
                var filename = $(this).attr("data-name");
                var date = $(this).attr("data-date");
                var file1 = $(this).attr("data-file1");
                var file2 = $(this).attr("data-file2");
                var filename1 = $(this).attr("data-name1");
                var filename2 = $(this).attr("data-name2");
                var dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.REPORT_LOG_DIALOG), {
                    elementId: parent.elementId + "_dialog"
                });
                var width = parent.pViewHandle.find(".row").width() - 10 + "px";
                var height = $(window).height() - parent.pViewHandle.find(".row").offset().top - 10 + "px";
                layer.open({
                    type: 1,
                    title: "日志详情",
                    area: [width, height],
                    offset: ["82px", "200px"],
                    shade: [0.5, '#393D49'],
                    content: dialogTemplate,
                    success: function (layero, index) {
                        parent.getEventDetails(layero, id, date, parent.status, filename);
                        $(parent.pBtnDetailDownload).on("click", function () {
                            if (parent.status == "system")
                                parent.exportEvent(file2);
                            else
                                parent.exportEvent(file1);
                        });
                        $(".row-cutbox>ul>li").on("click", function () {
                            parent.currentTabId = "#" + $(this).attr("data-id");
                            switch (parent.currentTabId) {
                                case parent.pTotalSystemEvent:
                                    parent.status = "system"
                                    parent.getEventDetails(layero, id, date, "system", filename);
                                    break;
                                case parent.pTotalOperationLog:
                                    parent.status = "operate"
                                    parent.getEventDetails(layero, id, date, "operate", filename);
                                    break;
                            }
                            $(".row-cutbox>ul>li").removeClass("active");
                            $(this).addClass("active");
                        });
                        $(parent.pBtnReportDownload).on("click", function () {
                            if (parent.status == "system")
                                parent.downloadEchart(parent.interfaceChart, filename2);
                            else
                                parent.downloadEchart(parent.interfaceChart, filename1);
                            
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

           /* $(parent.pTdEventlistList).find("input[type='checkbox']").on("click", function (event) {
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
        console.error("ERROR - ReportLogController.selectEventlists() - Unable to get all events: " + err.message);
    }
}
ReportLogController.prototype.delReportList = function (delIds) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_LOG_EVENT;
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
                //$(parent.pLblTotal).text(parent.total-delIds.length);
            }else{
                layer.close(loadIndex);layer.alert("删除失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportLogController.delReportList() - Unable to delete logReportList: " + err.message);
    }
}
/*ReportLogController.prototype.getEventDetails = function (viewHandler, id, date, status, filename) {
    try {
        var parent = this;
        var link = "";
        var data = "";
        if (status == "operate") {
            link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_LOG_OPERATESTATIC;
        }
        else {
            link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_LOG_SYSTEMSTATIC;
        }
        data = { id: id };
        var dataAll = { D1: { x: [], y: [] }, D2: { x: [], y: [] }, D3: { x: [], y: [] }, D4: { x: [], y: [] }, D5: { x: [], y: [] } };
        var promise = URLManager.getInstance().ajaxCall(link,data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.status) != "undefined" ) {
                switch (result.status) {
                    case 1:
                        if (status == "operate") {
                            var arrTitle = [];
                            for (var i = 0; i < result.userstatics.length; i++) {
                                arrTitle.push(result.userstatics[i][0]);
                                switch (i)
                                {
                                    case 0:
                                        for (var j = 0 ; j < result.userstatics[i][1].length; j++) {
                                            var arry = result.userstatics[i][1];
                                            dataAll.D1.x.push(arry[j][0]);
                                            dataAll.D1.y.push(arry[j][1]);
                                        }
                                        break;
                                    case 1:
                                        for (var j = 0 ; j < result.userstatics[i][1].length; j++) {
                                            var arry = result.userstatics[i][1];
                                            dataAll.D2.x.push(arry[j][0]);
                                            dataAll.D2.y.push(arry[j][1]);
                                        }
                                        break;
                                    case 2:
                                        for (var j = 0 ; j < result.userstatics[i][1].length; j++) {
                                            var arry = result.userstatics[i][1];
                                            dataAll.D3.x.push(arry[j][0]);
                                            dataAll.D3.y.push(arry[j][1]);
                                        }
                                        break;
                                    case 3:
                                        for (var j = 0 ; j < result.userstatics[i][1].length; j++) {
                                            var arry = result.userstatics[i][1];
                                            dataAll.D4.x.push(arry[j][0]);
                                            dataAll.D4.y.push(arry[j][1]);
                                        }
                                        break;
                                    case 4:
                                        for (var j = 0 ; j < result.userstatics[i][1].length; j++) {
                                            var arry = result.userstatics[i][1];
                                            dataAll.D5.x.push(arry[j][0]);
                                            dataAll.D5.y.push(arry[j][1]);
                                        }
                                        break;
                                 
                                }
                                
                            }
                            parent.interfaceChart = parent.initLineChart('divFlowInterface', '操作日志_' + filename + "_" + date, dataAll, arrTitle);
                        }
                        else {
                            var arrTitle = ["设备", "接口", "系统", "业务", "所有"];
                            for (var i = 0; i < result.device.length; i++)
                            {
                                dataAll.D1.x.push(result.device[i][0]);
                                dataAll.D1.y.push(result.device[i][1]);
                                dataAll.D2.x.push(result.interface[i][0]);
                                dataAll.D2.y.push(result.interface[i][1]);
                                dataAll.D3.x.push(result.system[i][0]);
                                dataAll.D3.y.push(result.system[i][1]);
                                dataAll.D4.x.push(result.service[i][0]);
                                dataAll.D4.y.push(result.service[i][1]);
                                dataAll.D5.x.push(result.all[i][0]);
                                dataAll.D5.y.push(result.all[i][1]);
                            }
                            parent.interfaceChart = parent.initLineChart('divFlowInterface', '系统日志_' + filename + "_" + date, dataAll, arrTitle);
                        }
                        break;
                }

            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportLogController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

ReportLogController.prototype.downloadEchart = function (myChart, title) {
    try {
        var img = new Image();
        img.src = myChart.getDataURL('png').replace("data:image/png;base64,", "data:image/jpeg;base64,");
        //if ($.browser.msie && ($.browser.version = "9.0")) {
        //    imgData = img.src.replace(_fixType('jpg'), 'image/octet-stream');
        //    saveFile(imgData, title + ".jpg");
        //}
        //else {
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
        console.error("ERROR - EventController.downloadEchart() - Unable to download safe event information: " + err.message);
    }
}

ReportLogController.prototype.initLineChart = function (id, title, data, arryTitle) {
    var parent = this;
    var line = echarts.init(document.getElementById(id));
    var option = {
        title: {
            text: title,
            x: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            },
            formatter: function (params) {
                var str = params[0].name + '<br/>'
                for (var i = 0; i < params.length; i++) {
                    if (params[i].seriesName != "") {
                        str = str + params[i].seriesName + ' : ' + params[i].value + '<br/>';
                    }

                }
                return str;

            }

        },
        legend: {
            data: arryTitle,
            y: 'bottom'
        },
        toolbox: {
            show: true
        },
        calculable: true,
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: data.D1.x
            }
        ],
        yAxis: [
            {
                type: 'value',
            }
        ],
        series: [
                    {
                    name: arryTitle[0],
                    type: 'line',
                    symbol: 'none',
                    data: data.D1.y
                    },
                    {
                    name: arryTitle[1],
                    type: 'line',
                    symbol: 'none',
                    data: data.D2.y
                    },
                    {
                        name: arryTitle[2],
                        type: 'line',
                        symbol: 'none',
                        data: data.D3.y
                    },
                    {
                        name: arryTitle[3],
                        type: 'line',
                        symbol: 'none',
                        data: data.D4.y
                    },
                    {
                        name: arryTitle[4],
                        type: 'line',
                        symbol: 'none',
                        data: data.D5.y
                    }

        ]
    };


    line.setOption(option);

    return line;
}*/

ContentFactory.assignToPackage("tdhx.base.report.ReportLogController", ReportLogController);