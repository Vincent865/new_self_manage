function BlacklistController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pBtnEnableAll = "#" + this.elementId + "_btnEnableAll";
    this.pBtnDisableAll = "#" + this.elementId + "_btnDisableAll";
    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.bBtnUpload = "#" + this.elementId + "_btnUpload";
    this.pDdlFilter = "#" + this.elementId + "_ddlFilter";
    this.pDeviceType = "#" + this.elementId + "_ddlDeviceType";
    this.pDeviceName = "#" + this.elementId + "_txtDeviceName";

    this.pFileUpload = "#" + this.elementId + "_fileUpload";
    this.pFormUpload = "#" + this.elementId + "_formUpload";
    this.pTdBlacklistList = "#" + this.elementId + "_tdBlacklistList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";

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
    this.pLblRuleContent = "#" + this.elementId + "_dialog_lblRuleContent";
    this.pLblFeatureName = "#" + this.elementId + "_dialog_lblFeatureName";
    this.pLblFeaturePriority = "#" + this.elementId + "_dialog_lblFeaturePriority";
    this.pLblFeatureRisk = "#" + this.elementId + "_dialog_lblFeatureRisk";
    this.pLblFeatureNo = "#" + this.elementId + "_dialog_lblFeatureNo";
    this.pDllEvent = "#" + this.elementId + "_dllEventAll";
    this.pager = null;

    this.pBtnFilter="#" + this.elementId + "_btnFilter";
    this.pAdvOpt='#' + this.elementId + "_divFilter";
    this.pBtnSearch='#' + this.elementId + "_btnSearch";

    this.filter = {
        page: 1,
        status:""
    };
}

BlacklistController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.RULE_BLACKLIST_DIALOG],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - BlacklistController.init() - Unable to initialize all templates: " + err.message);
    }
}

BlacklistController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_BLACKLIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - BlacklistController.initShell() - Unable to initialize: " + err.message);
    }
}

BlacklistController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pBtnEnableAll).on("click", function () {
            parent.enableBlacklist();
        });

        $(this.pBtnDisableAll).on("click", function () {
            parent.disableBlacklist();
        });

        $(this.pBtnRefresh).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.selectBlacklists();
        });
        $(this.pBtnFilter).bind({click:function(){
            $(parent.pAdvOpt).toggle();
        }});
        $(this.pFileUpload).on("change", function () {
            var fileName = $.trim($(this).val());
            if (fileName != "") {
                var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 3).toLowerCase();
                if (fieExtension == "zip") {
                    parent.uploadBlacklist();
                }
                else {
                    layer.alert("文件格式不对", { icon: 5 });
                }
            }
        });

        $(this.pBtnSearch).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.selectBlacklists();
        });

        $(this.pDllEvent).on("change", function () {
            parent.updateBlackEvent($(this).val());
        });
    }
    catch (err) {
        console.error("ERROR - BlacklistController.initControls() - Unable to initialize control: " + err.message);
    }
}

BlacklistController.prototype.load = function () {
    try {
        $("#loginuser").val(AuthManager.getInstance().getUserName());
        this.selectBlacklists();
    }
    catch (err) {
        console.error("ERROR - BlacklistController.load() - Unable to load: " + err.message);
    }
}

BlacklistController.prototype.uploadBlacklist = function () {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPLOAD_BLACKLIST_FILEPATH;
        jQuery.support.cors = true;
        $(this.pFormUpload).ajaxSubmit({
            type: 'post',
            url: link,
            success: function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 1:
                            setTimeout(function () { parent.selectBlacklists() }, 3000);
                            layer.alert("上传成功", { icon: 6 });
                            break;
                        default:
                            layer.alert("上传失败", { icon: 5 });
                            break;
                    }
                }
                else {
                    layer.alert("上传失败", { icon: 5 });
                }
                $(parent.pFileUpload).val("");
                layer.close(loadIndex);
            },
            error: function (XmlHttpRequest, textStatus, errorThrown) {
                layer.close(loadIndex);
                layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                $(parent.pFileUpload).val("");
            }
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - BlacklistController.flagBlacklist() - Unable to set all events to read status: " + err.message);
    }
}

BlacklistController.prototype.enableBlacklist = function () {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].ADD_BLACKLIST_ALL;
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
                        $(parent.pTdBlacklistList).find("input[type='checkbox']").prop("checked", true);
                        layer.alert("启用所有规则成功", { icon: 6 });
                        setTimeout(function () { parent.selectBlacklists(); }, 3000);
                        break;
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
        console.error("ERROR - BlacklistController.clearBlacklist() - Unable to clear all events: " + err.message);
    }
}

BlacklistController.prototype.disableBlacklist = function () {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].CLEAR_BLACKLIST_ALL;
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
                        $(parent.pTdBlacklistList).find("input[type='checkbox']").prop("checked", false);
                        layer.alert("禁用所有规则成功", { icon: 6 });
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
        console.error("ERROR - BlacklistController.clearBlacklist() - Unable to clear all events: " + err.message);
    }
}

BlacklistController.prototype.updateBlacklist = function (id, status, obj, v) {
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_BLACKLIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { sid: id, status: status });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            obj.prop("checked", v);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert("操作成功", { icon: 6 });
                        break;
                    default:
                        obj.prop("checked", v);
                        layer.alert("操作失败", { icon: 5 });
                        break;
                }
            }
            else {
                obj.prop("checked", v);
                layer.alert("操作失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        obj.prop("checked", v);
        layer.close(loadIndex);
        console.error("ERROR - BlacklistController.clearBlacklist() - Unable to clear all events: " + err.message);
    }
}

BlacklistController.prototype.selectBlacklists = function () {
    var html = "";
    try {
        var parent = this;
        this.filter.status=$(this.pDdlFilter).val(),
        this.filter.type=$(this.pDeviceType).val(),
        this.filter.name=$(this.pDeviceName).val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_BLACKLIST_LIST;
        var loadIndex = layer.load(2);
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST",this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='6'>暂无数据</td></tr>";
            $(parent.pTdBlacklistList+">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>" + ((parent.filter.page - 1) * 10 + 1 + i) + "</td>";
                        html += "<td style='text-align: left;padding-left:5px;' title='" + result.rows[i][0] + "'>" + FormatterManager.stripText(result.rows[i][0], 44) + "</td>";
                        html += "<td>" + result.rows[i][1] + "</td>";
                        html += "<td><span class='btn-on-box'><input type='checkbox' id='chk" + result.rows[i][4] + "' class='btn-on' data-key='" + result.rows[i][4] + "' " + parent.formatStatus(result.rows[i][2]) + " /><label for='chk" + result.rows[i][4] + "'></label></td>";
                        html += "<td>";
                        html += "<select class='form-control' data-key='" + result.rows[i][4] + "'>"
                          //+ "<option value='0' " + (result.rows[i][5] == 0 ? 'selected' : '') + ">通过</option>"
                          + "<option value='1' " + (result.rows[i][5] == 1 ? 'selected' : '') + ">警告</option>"
                          //+ "<option value='2' " + (result.rows[i][5] == 2 ? 'selected' : '') + ">阻断</option>"
                          + "</select>";
                        html += "</td>";
                        html += "<td style='width:12%'>高</td>";
                        html += "<td>" + parent.formatRuleType(result.rows[i][6]) + "</td>";
                        html += "<td style='width:10%'><button class='btn btn-default btn-xs btn-color-details' vultype='"+result.rows[i][6]+"' data-key='" + result.rows[i][4] + "'>详情</button></td>";
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
            $(parent.pTdBlacklistList + ">tbody").html(html);
            layer.close(loadIndex);

            $(parent.pTdBlacklistList).find("button").on("click", function (event) {
                var id = $(this).attr("data-key"),vulType=$(this).attr('vultype');
                var dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_BLACKLIST_DIALOG), {
                    elementId: parent.elementId + "_dialog"
                });
                var width = parent.pViewHandle.width() - 10 + "px";
                var height = $(window).height() - parent.pViewHandle.offset().top - 10 - document.body.scrollTop + "px";
                layer.open({
                    type: 1,
                    title: "详情",
                    area: [width, height],
                    offset: ["82px", "200px"],
                    shade: [0.5, '#393D49'],
                    content: dialogTemplate,
                    success: function (layero, index) {
                        parent.getBlacklistDetails(layero, id,vulType);
                        $(window).on("resize", function () {
                            var pwidth = parent.pViewHandle.width() - 10;
                            var pheight = $(window).height() - parent.pViewHandle.offset().top - 10- document.body.scrollTop;
                            layero.width(pwidth);
                            layero.height(pheight);
                        })
                    }
                });

            });

            $(parent.pTdBlacklistList).find("input[type='checkbox']").on("click", function (event) {
                var id = $(this).attr("data-key");
                var status = $(this).prop("checked") ? "1" : "0";
                parent.updateBlacklist(id, status, $(this), !$(this).prop("checked"));
            });

            $(parent.pTdBlacklistList).find("select").each(function () {
                if ($(this).find("option").length < 2) {
                    $(this).attr("disabled", "disabled");
                } else {
                    $(this).change(function () {
                        var id = $(this).attr("data-key");
                        var value = $(this).val();
                        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
                        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_BLACKLIST_EVENT;
                        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { action: value, sid: id });
                        promise.fail(function (jqXHR, textStatus, err) {
                            console.log(textStatus + " - " + err.message);
                            layer.alert("事件处理失败", { icon: 5 });
                            layer.close(loadIndex);
                        });
                        promise.done(function (result) {
                            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                                switch (result.status) {
                                    case 1:
                                        layer.alert("事件处理成功", { icon: 6 });
                                        break;
                                    default: layer.alert("事件处理失败", { icon: 5 }); break;
                                }
                            }
                            else {
                                layer.alert("事件处理失败", { icon: 5 });
                            }
                            layer.close(loadIndex);
                        });
                    });
                }
            });

            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectBlacklists();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='6'>暂无数据</td></tr>";
        $(this.pTdBlacklistList + ">tbody").html(html);
        console.error("ERROR - BlacklistController.selectBlacklists() - Unable to get all events: " + err.message);
    }
}

BlacklistController.prototype.getBlacklistDetails = function (viewHandler, id,type) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_BLACKLIST;
        var promise = URLManager.getInstance().ajaxCall(link, { recordid:id});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.rows) != "undefined" && result.rows.length > 0) {
                $(viewHandler).find(parent.pLblBugName).text(result.rows[0][0]);
                $(viewHandler).find(parent.pLblBugNo).text(result.rows[0][5]);
                $(viewHandler).find(parent.pLblBugType).text(parent.formatRuleType(parseInt(type)));
                $(viewHandler).find(parent.pLblBugSource).text("iSightPartners");
                $(viewHandler).find(parent.pLblBugTime).text(result.rows[0][2]);
                $(viewHandler).find(parent.pLblBugLevel).text("高");
                $(viewHandler).find(parent.pLblBugDevice).text("Genesis");
                $(viewHandler).find(parent.pLblBugRuleSource).text("漏洞库");
                $(viewHandler).find(parent.pLblBugEventHandle).text(parent.formatEventLevel(result.rows[0][4]));
                $(viewHandler).find(parent.pLblCompactCompany).text("Iconics");
                $(viewHandler).find(parent.pLblAttackCondition).text(result.rows[0][6]);
                $(viewHandler).find(parent.pLblRuleContent).html(result.rows[0][8]);
                $(viewHandler).find(parent.pLblFeatureName).text(result.rows[0][9]);
                $(viewHandler).find(parent.pLblFeaturePriority).text("1");
                $(viewHandler).find(parent.pLblFeatureRisk).text(parent.formatRiskLevel(result.rows[0][10]));
                $(viewHandler).find(parent.pLblFeatureNo).text(result.rows[0][11]);
            }
        });
    }
    catch (err) {
        console.error("ERROR - BlacklistController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

BlacklistController.prototype.formatDangerLevel = function (status) {
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
        console.error("ERROR - BlacklistController.formatDangerLevel() - Unable to get danger level via id: " + err.message);
    }
}

BlacklistController.prototype.formatEventLevel = function (status) {
    try {
        switch (status) {
            case 0:
                return "通过";
            case 2:
                return "阻断";
            case 1:
                return "警告";
            default:
                return "";
        }
    }
    catch (err) {
        console.error("ERROR - BlacklistController.formatEventLevel() - Unable to get event level via id: " + err.message);
    }
}

BlacklistController.prototype.formatRuleType = function (status) {
    try {
        switch (status) {
            case 1:
                return "缓冲区溢出攻击";
            case 2:
                return "代码执行攻击";
            case 3:
                return "僵尸网络攻击";
            case 4:
                return "扫描探测攻击";
            case 5:
                return "未知活动攻击"
            case 6:
                return "跨站脚本攻击"
            case 7:
                return "蠕虫病毒攻击"
            case 8:
                return "SQL注入攻击"
            case 9:
                return "信息泄露攻击"
            case 10:
                return "拒绝服务攻击"
            case 11:
                return "木马攻击"
            case 12:
                return "工控漏洞攻击"
            default:
                return "";
        }
    }
    catch (err) {
        console.error("ERROR - BlacklistController.formatEventLevel() - Unable to get event level via id: " + err.message);
    }
}

BlacklistController.prototype.formatRiskLevel = function (status) {
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
        console.error("ERROR - BlacklistController.formatRiskLevel() - Unable to get risk level via id: " + err.message);
    }
}

BlacklistController.prototype.formatStatus = function (status) {
    try {
        switch (status) {
            case 1:
                return "checked";
            default:
                return "";
        }
    }
    catch (err) {
        console.error("ERROR - BlacklistController.formatEventLevel() - Unable to get event level via id: " + err.message);
    }
}

BlacklistController.prototype.updateBlackEvent = function (operationId) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_BLACKLIST_ALLEVENT;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { action: operationId });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.selectBlacklists();
                        layer.alert("处理成功", { icon: 6 });
                        layer.close(loadIndex);
                        break;
                    default: layer.alert("设置失败", { icon: 5 });
                        layer.close(loadIndex);
                        break;
                }
            }
            else {
                layer.alert("设置失败", { icon: 5 });
                layer.close(loadIndex);
            }
        });
    }
    catch (err) {
        console.error("ERROR - WhitelistController.updateBlackEvent() - Unable to update backlist event: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.rule.BlacklistController", BlacklistController);
