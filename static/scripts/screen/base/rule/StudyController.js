function StudyController(controller, viewHandle, elementId) {
    this.controller = controller;
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isAllChecked = false;
    this.allRules = [];
    this.checkedRules = [];

    this.pBtnDisable = "#" + this.elementId + "_btnDisable";
    this.pBtnEnable = "#" + this.elementId + "_btnEnable";
    this.pChkAll = "#" + this.elementId + "_chkAll";
    this.pBtnStudy = "#" + this.elementId + "_btnStudy";
    this.pChkFlag = "#" + this.elementId + "_chkFlag";
    this.pTxtStartDatetime = "#" + this.elementId + "_txtStartDateTime";
    this.pDdlStudyDurtion = "#" + this.elementId + "_ddlStudyDurtion";
    this.pDivProgressbar = "#" + this.elementId + "_divProgressbar";

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pTdWhitelist = "#" + this.elementId + "_tdWhitelistList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pDetailsPagerContent = "#" + this.elementId + "_details_pagerContent";
    this.pLblStudyRuleCount = "#" + this.elementId + "_lblStudyRuleCount";
    this.pLblTotal = "#" + this.elementId +'_lblTotal';

    this.pWhitelistPager = null;
    this.pDetailsWhitelistPager = null;
    this.pDetailViewHandle = null;
    this.pExpand = false;
    this.filter = {
        page:1
    };
    this.filter_rule = {
        page: 1,
        id:"",
        ip: "",
        mac: "",
        proto: ""
    };
    this.protocol = Constants.WHITELIST_PROTOCOL_LIST[APPCONFIG.PRODUCT];
}

StudyController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_WHITELIST_STUDY), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - StudyController.init() - Unable to initialize: " + err.message);
    }
}

StudyController.prototype.initControls = function () {
    try {
        var parent = this;
        $(parent.pTxtStartDatetime).val($('#spanSystemTime').text());

        $(this.pChkAll).on("click", function () {
            parent.checkedRules = [];
            parent.isAllChecked = ($(this).attr("isChecked") == "true");
            $(parent.pTdWhitelist).find("input:checkbox").prop("checked", parent.isAllChecked);
            if (parent.isAllChecked) {
                parent.allRules.forEach(function (item, idnex) {
                    parent.checkedRules.push(item);
                });
                $(this).html("<i class='fa fa-check-square-o'></i>取消");
                $(this).attr("isChecked", "false");
            }
            else {
                $(this).html("<i class='fa fa-square-o'></i>全选");
                $(this).attr("isChecked", "true");
            }
        });

        $(this.pBtnEnable).on("click", function () {
            parent.updateWhitelist(parent.checkedRules, 1);
        });

        $(this.pBtnDisable).on("click", function () {
            layer.confirm('确定要删除么？',{icon:7,title:'注意：'}, function(index) {
                layer.close(index);
                parent.updateWhitelist(parent.checkedRules, 0);
            })
        });

        $(this.pTxtStartDatetime).on("click", function () {
            var startTime = $("#spanSystemTime").text();
            return WdatePicker({ dateFmt: 'yyyy-MM-dd HH:mm:00', minDate: startTime });
        });

        $(this.pBtnRefresh).on("click", function () {
            parent.pWhitelistPager = null;
            parent.filter.page = 1;
            parent.resetCheckAllStatus();
            parent.selectWhitelist();
        });
        syncSysTime();
    }
    catch (err) {
        console.error("ERROR - StudyController.initControls() - Unable to initialize control: " + err.message);
    }
}

StudyController.prototype.load = function () {
    try {
            this.getStudyStatus();
            this.selectWhitelist();
    }
    catch (err) {
        console.error("ERROR - StudyController.load() - Unable to load: " + err.message);
    }
}

StudyController.prototype.getStudyStatus = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_WHITELIST_STUDY_STATU;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            parent.setupSlider();
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && typeof (result.start) != "undefined") {
                switch (result.status) {
                    case 1:
                        if (result.state == 1) {
                            var starttime = new Date(result.start.replace(/-/g, '/'));
                            var systime = new Date($("#spanSystemTime").text().replace(/-/g, '/'));
                            var duration = systime.getTime() - starttime.getTime();
                            if (duration > 0) {
                                var percent = Math.floor(duration / (result.dur * 60 * 1000) * 100);
                                if (percent >= 100) {
                                    parent.setupSlider();
                                }
                                else {
                                    parent.setupProgressbar(duration, result.dur * 60 * 1000, starttime);//单位：毫秒
                                }
                            }
                            else {
                                parent.setupProgressbar(duration, result.dur * 60 * 1000, starttime);//单位：毫秒
                            }
                        }
                        else {
                            parent.setupSlider();//单位：毫秒
                        }
                        break;
                    default: layer.alert("获取学习状态失败", { icon: 5 }); parent.setupSlider(); break;
                }
            }
            else {
                parent.setupSlider();
                layer.alert("获取学习状态失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        parent.setupSlider();
        console.error("ERROR - StudyController.getStudyStatus() - Unable to get study status: " + err.message);
    }
}

StudyController.prototype.setupSlider = function () {
    var parent = this;
    $(this.pDivProgressbar).css("display", "none");
    //$(".arrowsbox.pos-arrows02").css("display", "none");
    $(this.pBtnStudy).text("开始学习").unbind("click");
    $(this.pBtnStudy).on("click", function () {
        syncSysTime();
        parent.startStudyWhitelist();
    });
}

StudyController.prototype.setupProgressbar = function (duration, total, starttime) {
    var parent = this;
    $(this.pDivProgressbar).css("display", "block");
    $(this.pBtnStudy).text("停止学习").unbind("click");
    var progressbar = $("#progressbar");
    progressLabel = $(".progress-label");
    var label = "剩余学习时间:";
    var studyedTime = duration;
    if (duration < 0) {
        label = "距离开始时间:";
        studyedTime = 0;
    }
    progressbar.progressbar({
        value: studyedTime / total * 100,
        max: 100,
        min: 0,
        change: function () {
            var date = progressLabel.text().split(":");
            var hours = parseInt(date[1]);
            var minutes = parseInt(date[2]);
            var seconds = parseInt(date[3]);
            var milliseconds = seconds * 1000 + minutes * 60 * 1000 + hours * 60 * 60 * 1000 - 1000;
            var displayTime = FormatterManager.formatMilliseconds(milliseconds);
            progressLabel.text(label + displayTime);
        },
        complete: function () {
            clearInterval(parent.controller.studyTimer);
            parent.setupSlider();
            parent.resetCheckAllStatus();
            parent.selectWhitelist();
        }
    });
    if (duration < 0) {
        progressLabel.text(label + FormatterManager.formatMilliseconds(-1 * duration));
    }
    else {
        progressLabel.text(label + FormatterManager.formatMilliseconds(total - duration));
    }

    parent.controller.studyTimer = setInterval(function progress() {
        if (duration < 0) {
            var date = progressLabel.text().split(":");
            var hours = parseInt(date[1]);
            var minutes = parseInt(date[2]);
            var seconds = parseInt(date[3]);
            if (hours == 0 && minutes == 0 && seconds == 0) {
                duration = 0;
                clearInterval(parent.controller.studyTimer);
                parent.getStudyStatus();
            }
            else {
                var milliseconds = seconds * 1000 + minutes * 60 * 1000 + hours * 60 * 60 * 1000 - 1000;
                var displayTime = FormatterManager.formatMilliseconds(milliseconds);
                progressLabel.text(label + displayTime);
            }
        }
        else {
            var val = $("#progressbar").progressbar("option", "value");
            var curDatetime = new Date($("#spanSystemTime").text().replace(/-/g, '/'));
            if (starttime < curDatetime) {
                $("#progressbar").progressbar("option", "value", val + 1000 / total * 100);
                if (val == 100) {
                    clearInterval(parent.controller.studyTimer);
                }
            }
        }
    }, 1000);
    $(this.pBtnStudy).on("click", function () {
        clearInterval(parent.controller.studyTimer);
        parent.stopStudyWhitelist();
    });
}

StudyController.prototype.updateWhitelistAll = function (status) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_WHITELIST_STUDY_ALL;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link, { state: status });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert("操作成功", { icon: 6 });
                        break;
                    default: layer.alert("操作失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("操作失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - StudyController.updateWhitelist() - Unable to disable/enable whitelist: " + err.message);
    }
}

StudyController.prototype.updateWhitelist = function (sids, status) {
    try {
        var parent = this;

        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var data = {
            status: status,
            sids: sids
        };
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_WHITELIST_STUDY;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST",data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                var ope='';
                switch (result.status) {
                    case 1:
                        if (parent.pExpand == true) {
                            parent.filter_rule.page = 1;
                            parent.getWhitelistDetails();
                            parent.selectWhitelist();
                        }
                        else {
                            parent.resetCheckAllStatus();
                            //parent.getWhitelistDetails();
                            parent.selectWhitelist();
                        }
                        data.status?ope='应用成功':ope='删除成功';
                        //layer.alert("操作成功", { icon: 6 });
                        layer.open({
                            type:1,
                            title:'提示',
                            content:'<p style="text-align: center;margin: 15px 0 10px;">'+ope+'</p>',
                            closeBtn:false,
                            area:'300px',
                            shade:0.8,
                            btn:['确认'],
                            btnAlign:'c',
                            yes:function(res){
                                layer.closeAll();
                                parent.total?!status?$(parent.pLblTotal).text(parent.total):'':$(parent.pLblTotal).text(0);
                            }
                        });
                        break;
                    case 2: layer.alert("白名单正在学习中...请稍后操作.", { icon: 5 }); break;
                    default: layer.alert("操作失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("操作失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - StudyController.updateWhitelist() - Unable to disable/enable whitelist: " + err.message);
    }
}

StudyController.prototype.startStudyWhitelist = function () {
    var parent = this;
    try {
        var starttime = $(this.pTxtStartDatetime).val();
        var curDatetime = new Date($("#spanSystemTime").text().replace(/-/g, '/'));
        var dur = $(this.pDdlStudyDurtion).val();
        if ($.trim(starttime) == "") {
            layer.alert("请选择开始时间", { icon: 5 });
            return;
        }
       /* if (new Date($.trim(starttime).replace(/-/g, '/')) < curDatetime) {
            layer.alert("开始学习时间必须在系统时间之后", { icon: 5 });
            return;
        }*/
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var para = { start: starttime, dur: dur, flag: "0" };
        if ($(this.pChkFlag).prop("checked")) {
            para.flag = "1";
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].START_WHITELIST_STUDY;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST",para);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.getStudyStatus();
                        break;
                    default: layer.alert("开始学习设置失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("开始学习设置失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - StudyController.startStudyWhitelist() - Unable to start study rule: " + err.message);
    }
}

StudyController.prototype.stopStudyWhitelist = function () {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].STOP_WHITELIST_STUDY;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.getStudyStatus();
                        parent.pWhitelistPager = null;
                        parent.selectWhitelist();
                        break;
                    default: layer.alert("停止学习设置失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("停止学习设置失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - StudyController.stopStudyWhitelist() - Unable to stop study rule: " + err.message);
    }
}

StudyController.prototype.selectWhitelist = function () {
    var html = "";
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_WHITELIST_DEVICE;
        var loadIndex = layer.load(2);
        var promise = URLManager.getInstance().ajaxCall(link, this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='6'>暂无数据</td></tr>";
            $(parent.pTdWhitelist+">tbody").html(html);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                parent.total=result.total;
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>" + ((parent.filter.page - 1) * 10 + i + 1) + "</td>";
                        html += "<td style='text-align:left;' title='" + result.rows[i][1] + "'>" + FormatterManager.stripText(result.rows[i][1], 30) + "</td>";
                        html += "<td>" + result.rows[i][2] + "</td>";
                        html += "<td>" + result.rows[i][3].toUpperCase() + "</td>";
                        html += "<td>" + parent.protocol[result.rows[i][4]] + "</td>";
                        html += "<td><button class='btn btn-default btn-xs btn-color-details' id='" + result.rows[i][0] + "' status='0' ip='" + result.rows[i][2] + "' mac='" + result.rows[i][3] + "' proto='" + result.rows[i][4] + "'><i class='fa fa-file-text-o'></i>详情</button>&nbsp;&nbsp;</td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='6'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='6'>暂无数据</td></tr>";
            }
            if (typeof (result.total) != "undefined") {
                $(parent.pLblStudyRuleCount).text(result.num);
            }

            $(parent.pTdWhitelist + ">tbody").html(html);
            //$(".arrowsbox.pos-arrows02").show();
            layer.close(loadIndex);

            $(parent.pTdWhitelist).find(".btn-color-details").on("click", function (event) {
                if (parent.pExpand == false) {
                    parent.pExpand = true;
                }
                else {
                    parent.pExpand = false;
                }
                parent.filter_rule.page = 1;
                parent.filter_rule.mac = $(this).attr("mac");
                parent.filter_rule.proto = $(this).attr("proto");
                parent.filter_rule.id = $(this).attr("id");
                parent.filter_rule.ip = $(this).attr("ip");
                var status = $(this).attr("status");
                if (status == "0") {
                    parent.pDetailsWhitelistPager = null;
                    $(parent.pTdWhitelist).find(".btn-color-details").attr("status", "0");
                    $(parent.pTdWhitelist).find("td[colspan='6']").parent().remove();
                    var lastTr = $(this).parent().parent();
                    var html = '<tr><td colspan="6" align="center">';
                    html += '<div class="row-table-box" style="padding:5px 5px;margin-bottom:0px;">';
                    html += '<table class="table table-hover table-striped"></table>';
                    html += '</div>';
                    html += "<div class='row pagination-custom' style='padding-right:5px;margin-bottom:10px;'>";
                    html += "<div class='text-right col-xs-12' data-id='" + parent.elementId + "_details_pagerContent" + parent.filter_rule.id + "' id='" + parent.elementId + "_details_pagerContent" + parent.filter_rule.id + "'></div>";
                    html += '</div>';
                    html += '</td></tr>';
                    var viewHandler = lastTr.after(html).next().find("table");
                    parent.pDetailViewHandle = viewHandler;
                    parent.getWhitelistDetails();
                    $(this).attr("status", "1");
                }
                else {
                    $(this).parent().parent().next().remove();
                    $(this).attr("status", "0");
                }
            });
            if (parent.pWhitelistPager == null) {
                parent.checkedRules = result.checklist;
                parent.allRules = result.alllist;
            }
            if (parent.pWhitelistPager == null && result.rows.length >= 0) {//if (parent.pWhitelistPager == null && result.rows.length > 0) {
                parent.pWhitelistPager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectWhitelist();
                });
                parent.pWhitelistPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
                /*debugger;
                 !parent.total?$(parent.pLblTotal).text(0):'';*/
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='6'>暂无数据</td></tr>";
        $(parent.pTdWhitelist + ">tbody").html(html);
        console.error("ERROR - StudyController.selectWhitelist() - Unable to get whitelist: " + err.message);
    }
}

StudyController.prototype.getWhitelistDetails = function () {
    var parent = this;
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    var html = '';
    html += '<thead><tr>';
    html += '<td><input type="checkbox" id="chkWhitelistDetails' + this.filter_rule.id + '" data-key="0" /></td>';
    html += '<td>序号</td>';
    html += '<td>规则名</td>';
    html += '<td>操作码</td>';
    html += '<td>启用状态</td>';
    html += '</tr></thead><tbody></tbody>';
    parent.pDetailViewHandle.html(html);
    html = "";
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_WHITELIST_RULE;
        var promise = URLManager.getInstance().ajaxCall(link, this.filter_rule);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='5'>暂无数据</td></tr>";
            parent.pDetailViewHandle.find("tbody").html(html);
        });
        promise.done(function (result) {
            if (typeof (result.rows) != "undefined" && result.rows.length > 0) {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += '<td><input type="checkbox" data-key="' + result.rows[i][3] + '" /></td>';
                        html += "<td>" + ((parent.filter_rule.page - 1) * 10 + i + 1) + "</td>";
                        html += "<td title='" + result.rows[i][0] + "'>" + FormatterManager.stripText(result.rows[i][0], 40) + "</td>";
                        html += "<td style='text-align:left;' title='" + result.rows[i][1] + "'>" + FormatterManager.stripText(result.rows[i][1], 82) + "</td>";
                        html += "<td>" + (result.rows[i][2] == 1 ? "启用" : "禁用") + "</td>";
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

            parent.pDetailViewHandle.find("tbody").html(html);

            layer.close(loadIndex);

            parent.pDetailViewHandle.find("input:checkbox").each(function () {
                var id = parseInt($(this).attr("data-key"));
                var isExits = $.inArray(id, parent.checkedRules);
                if (isExits >= 0) {
                    $(this).prop("checked", true);
                }
            });

            parent.pDetailViewHandle.find("#chkWhitelistDetails" + parent.filter_rule.id).on("change", function () {
                var checked = $(this).prop("checked");
                $(parent.pDetailViewHandle).find("input:checkbox").prop("checked", checked);
                $(parent.pDetailViewHandle).find("input:checkbox").each(function () {
                    var id = parseInt($(this).attr("data-key"));
                    if (checked && id != "0") {
                        var isExits = $.inArray(id, parent.checkedRules);
                        if (isExits < 0) {
                            parent.checkedRules.push(id);
                        }
                    }
                    else {
                        parent.checkedRules.forEach(function (item, index) {
                            if (item == id) {
                                parent.checkedRules.splice(index, 1);
                            }
                        });
                    }
                });
            });

            parent.pDetailViewHandle.find("input:checkbox").on("change", function () {
                var checked = $(this).prop("checked");
                var id = parseInt($(this).attr("data-key"));
                if (checked && id != "0") {
                    var isExits = $.inArray(id, parent.checkedRules);
                    if (isExits < 0) {
                        parent.checkedRules.push(id);
                    }
                }
                else {
                    parent.checkedRules.forEach(function (item, index) {
                        if (item == id) {
                            parent.checkedRules.splice(index, 1);
                        }
                    });
                }
            });

            if (parent.pDetailsWhitelistPager == null && result.rows.length > 0) {
                parent.pDetailsWhitelistPager = new tdhx.base.utility.PagerController($(parent.pDetailsPagerContent + parent.filter_rule.id), parent.elementId + "_details", 10, result.total, function (pageIndex) {
                    parent.filter_rule.page = pageIndex;
                    parent.getWhitelistDetails();
                });
                parent.pDetailsWhitelistPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='5'>暂无数据</td></tr>";
        parent.pDetailViewHandle.find("tbody").html(html);
        console.error("ERROR - KnowStudyController.getWhitelistDetails() - Unable to get rule information: " + err.message);
    }
}

StudyController.prototype.resetCheckAllStatus = function () {
    try {
        this.checkedRules = [];
        $(this.pChkAll).html("<i class='fa fa-square-o'></i>全选");
        $(this.pChkAll).attr("isChecked", "true");
    }
    catch (err) {
        console.error("ERROR - StudyController.resetCheckAllStatus() - Unable to reset the checkAll control status: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.rule.StudyController", StudyController);