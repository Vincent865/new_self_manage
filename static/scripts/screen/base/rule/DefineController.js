function DefineController(controller, viewHandle, elementId) {
    this.controller = controller;
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isAllChecked = false;
    this.allRules = [];
    this.checkedRules = [];

    this.action = ["通过", "告警", "阻断"];
    this.checkedStatus = ["", "checked"];
    this.protocol = ['dcerpcudp', 'modbus', 'dcerpc', 'dnp3', 'iec104', 'mms', 'opcua_tcp', 'ENIP-TCP', 'snmp', 'ENIP-UDP', 's7', 'ENIP-IO', 'hexagon', 'goose', 'sv', 'pnrtdcp', 'telnet', 'ssh', 'https', 'http', 'oracle', 'ftp', 'focas'];

    this.pBtnAdd = "#" + this.elementId + "_btnAdd";
    this.pBtnCheckAll = "#" + this.elementId + "_btnCheckAll";
    this.pBtnDelete = "#" + this.elementId + "_btnDelete";
    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pFileUpload = "#" + this.elementId + "_fileUpload";
    this.pFormUpload = "#" + this.elementId + "_formUpload";
    this.pDdlOperation = "#" + this.elementId + "_ddlOperation";
    this.pTdDefineWhitelist = "#" + this.elementId + "_tdDefineWhitelist";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pDetailController = null;
    this.pWhitelistPager = null;

}

DefineController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_WHITELIST_IPS_DEFINE), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - DefineController.init() - Unable to initialize: " + err.message);
    }
}

DefineController.prototype.initControls = function () {
    try {
        var parent = this;

        $(".rule-single-select").ruleSingleSelect();

        $(this.pBtnAdd).on("click", function () {
            parent.showDefineDialog(0);/*0--->Add, 1--->Edit*/
        });

        $(this.pBtnDelete).on("click", function () {
            parent.deleteSelectedDefineWhitelist(parent.checkedRules);
        });

        $(this.pBtnCheckAll).on("click", function () {
            parent.isAllChecked = ($(this).attr("isChecked") == "true");
            $(parent.pTdDefineWhitelist).find(":checkbox[class!='status']").prop("checked", parent.isAllChecked);
            if (parent.isAllChecked) {
                parent.checkedRules = parent.allRules;
                $(this).text("取消");
                $(this).removeClass("but_off");
                $(this).addClass("but_all");
                $(this).attr("isChecked", "false");
            }
            else {
                parent.checkedRules = [];
                $(this).text("全选");
                $(this).removeClass("but_all");
                $(this).addClass("but_off");
                $(this).attr("isChecked", "true");
            }
        });

        $(this.pFileUpload).on("change", function () {
            var fileName = $.trim($(this).val());
            if (fileName != "") {
                var fieExtension = fileName.substr(fileName.lastIndexOf('.') + 1, 3).toLowerCase();
                if (fieExtension == "csv") {
                    parent.uploadDefineWhitelist();
                }
                else {
                    layer.alert("文件格式不对", { icon: 5 });
                }
            }
        });

        $(this.pBtnRefresh).on("click", function () {
            parent.pWhitelistPager = null;
            parent.resetCheckAllStatus();
            parent.selectDefineWhitelist(1);
        });

        $(this.pDdlOperation).on("change", function () {
            var action = $(parent.pDdlOperation).val();
            parent.updateSelectedDefineWhitelistState(action);
        });
    }
    catch (err) {
        console.error("ERROR - DefineController.initControls() - Unable to initialize control: " + err.message);
    }
}

DefineController.prototype.load = function () {
    try {
        this.controller.studyTimer = null;
        this.selectDefineWhitelist(1);
    }
    catch (err) {
        console.error("ERROR - DefineController.load() - Unable to load: " + err.message);
    }
}

DefineController.prototype.showDefineDialog = function (id, src, dst, protocol, status, action) {
    try {
        var parent = this;
        this.pDetailController = null;
        var dialogHandler = $("<div />");
        var width = '600px';//parent.pViewHandle.parents(".eventinfo_box").width() - 10 + "px";
        var height = '400px';//$(window).height() - parent.pViewHandle.parents(".eventinfo_box").offset().top - 10 + "px";
        layer.open({
            type: 1,
            title: "手写规则",
            area: ['560px', '430px'],
            shade: [0.5, '#393D49'],
            content: dialogHandler.html(),
            success: function (layero, index) {
                parent.pDetailController = new tdhx.base.rule.DefineDialogController(parent, layero.find(".layui-layer-content"), parent.elementId + "_dialog", id, src, dst, protocol, status, action);
                parent.pDetailController.init();
            },
            end: function (layero, index) {
                parent.resetCheckAllStatus();
                parent.selectDefineWhitelist(1);
            }
        });
    }
    catch (err) {
        console.error("ERROR - DefineController.addDefineWhitelist() - added whitelist failed: " + err.message);
    }
}

/*upload rules*/
DefineController.prototype.uploadDefineWhitelist = function () {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPLOAD_WHITELIST;
        jQuery.support.cors = true;
        $(this.pFormUpload).ajaxSubmit({
            type: 'post',
            url: link,//"/default.aspx",
            success: function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 1:
                            setTimeout(function () {
                                parent.pWhitelistPager = null;
                                parent.resetCheckAllStatus();
                                parent.selectDefineWhitelist(1);
                            }, 5000);
                            $(parent.pFileUpload).val("");
                            layer.alert("导入成功", { icon: 6 });
                            break;
                        case 2:
                            $(parent.pFileUpload).val("");
                            layer.alert("白名单正在学习中，无法导入...", { icon: 5 });
                            break;
                        default:
                            $(parent.pFileUpload).val("");
                            layer.alert(result.errmsg, { icon: 5, title: "导入失败" });
                            break;
                    }
                }
                else {
                    $(parent.pFileUpload).val("");
                    layer.alert("导入失败", { icon: 5 });
                }
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
        $(parent.pFileUpload).val("");
        console.error("ERROR - DefineController.uploadDefineWhitelist() - upload whitelist failed: " + err.message);
    }
}

/*update single rule action*/
DefineController.prototype.updateDefineWhitelistState = function (id, action) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_SINGLE_DEFINE_WHITELIST_ACTION + "?action=" + action + "&sid=" + id;
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
                        layer.alert("操作成功", { icon: 6 });
                        break;
                    case 3:
                        layer.alert("白名单正在学习中，无法操作...", { icon: 5 });
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
        console.error("ERROR - DefineController.updateWhitelist() - Unable to disable/enable whitelist: " + err.message);
    }
}

/*update seleted rules action*/
DefineController.prototype.updateSelectedDefineWhitelistState = function (action) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_SELECTED_DEFINE_WHITELIST_ACTION + "?action=" + action;
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
                        $(parent.pTdDefineWhitelist).find(".select-note").val(action);
                        $(parent.pTdDefineWhitelist).find(".rule-single-select").ruleSingleSelect();
                        layer.alert("操作成功", { icon: 6 });
                        break;
                    case 2:
                        layer.alert("白名单正在学习中，无法操作...", { icon: 5 });
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
        console.error("ERROR - DefineController.updateWhitelist() - Unable to disable/enable whitelist: " + err.message);
    }
}

/*delete seleted rules*/
DefineController.prototype.deleteSelectedDefineWhitelist = function (ids) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var data = {
            sids: ids
        };
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].DELETE_SELECTED_DEFINE_WHITELIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        setTimeout(function () {
                            parent.pWhitelistPager = null;
                            parent.resetCheckAllStatus();
                            parent.selectDefineWhitelist(1);
                        }, 3000);
                        layer.alert("删除选中的规则成功", { icon: 6 });
                        break;
                    case 2:
                        layer.alert("白名单正在学习中，无法删除...", { icon: 5 });
                        break;
                    default: layer.alert("删除选中的规则失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("删除选中的规则失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - DefineController.updateWhitelist() - Unable to disable/enable whitelist: " + err.message);
    }
}

/*delete single rules*/
DefineController.prototype.deleteDefineWhitelist = function (id, tr) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].DELETE_SINGLE_DEFINE_WHITELIST + "?sid=" + id;
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
                        setTimeout(function () {
                            parent.pWhitelistPager = null;
                            parent.selectDefineWhitelist(1);
                            parent.resetCheckAllStatus();
                        }, 3000);
                        layer.alert("删除规则成功", { icon: 6 });
                        break;
                    case 2:
                        layer.alert("白名单正在学习中，无法删除...", { icon: 5 });
                        break;
                    default: layer.alert("删除规则失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("删除规则失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - DefineController.updateWhitelist() - Unable to disable/enable whitelist: " + err.message);
    }
}

/*update single rule status*/
DefineController.prototype.updateDefineWhitelistStatus = function (id, status, obj) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_SINGLE_DEFINE_WHITELIST_STATUS + "?status=" + status + "&sid=" + id;
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
                        layer.alert("操作成功", { icon: 6 });
                        break;
                    case 2:
                        layer.alert("白名单正在学习中，无法操作...", { icon: 5 });
                        break;
                    default:
                        obj.prop("checked", !obj.prop("checked"));
                        layer.alert("操作失败", { icon: 5 });
                        break;
                }
            }
            else {
                obj.prop("checked", !obj.prop("checked"));
                layer.alert("操作失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - DefineController.updateWhitelist() - Unable to disable/enable whitelist: " + err.message);
    }
}

DefineController.prototype.selectDefineWhitelist = function (pageIndex) {
    var html = "";
    html += '<tr class="title">';
    html += '<td class="list"><input type="checkbox" id="chkWhitelist" /></td>';
    html += '<td class="list" style="width:6%;">序号</td>';
    html += '<td class="list" style="width:17%;">起源地址</td>';
    html += '<td class="list" style="width:17%;">目标地址</td>';
    html += '<td class="list" style="width:10%;">协议名称</td>';
    html += '<td class="list" style="width:10%;">操作码</td>';
    html += '<td class="list" style="width:8%;">规则处理</td>';
    html += '<td class="list" style="width:7%;">启用状态</td>';
    html += '<td class="list" style="width:18%;">操作</td>';
    html += '</tr>';
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEFINE_WHITELIST + "?page=" + pageIndex;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='9'>暂无数据</td></tr>";;
            $(parent.pTdDefineWhitelist).html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += '<td><input type="checkbox" class="chktmp" data-key="' + result.rows[i][6] + '"></td>';
                        html += "<td style='width:6%;'>" + ((pageIndex - 1) * 10 + i + 1) + "</td>";
                        html += "<td style='width:17%;text-align:left;padding-left:10px;'>" + result.rows[i][0] + "</td>";
                        html += "<td style='width:17%;';text-align:left;padding-left:10px;'>" + result.rows[i][1] + "</td>";
                        html += "<td style='width:10%;text-align:left;padding-left:10px;' title='" + result.rows[i][2] + "'>" + result.rows[i][2] + "</td>";
                        html += "<td style='width:10%;text-align:left;padding-left:10px;' title='" + result.rows[i][3] + "'>" + result.rows[i][3] + "</td>";
                        html += "<td style='width:8%;'>";
                        html += "<div class='rule-single-select'><select class='select-note' data-key='" + result.rows[i][6] + "'>"
                            + "<option value='0' " + (result.rows[i][4] == 0 ? 'selected' : '') + ">通过</option>"
                            + "<option value='2' " + (result.rows[i][4] == 2 ? 'selected' : '') + ">阻断</option>"
                            + "</select></div>";
                        html += "</td>";
                        html += "<td style='width:7%'><input type='checkbox' class='status' data-key='" + result.rows[i][6] + "' " + parent.checkedStatus[result.rows[i][5]] + " /></td>";
                        html += "<td style='width:18%;'>";
                        if (typeof (result.rows[i][3]) != "undefined" && $.trim(result.rows[i][3]) == "") {
                            html += "<button class='button_copy button_small' src='" + result.rows[i][0] + "' dst='"
                                 + result.rows[i][1] + "' protocol='" + result.rows[i][2] + "' action='" + result.rows[i][4]
                                 + "' status='" + result.rows[i][3] + "'>复制</button>&nbsp;&nbsp;";
                            html += "<button class='button_edit button_small' src='" + result.rows[i][0] + "' dst='"
                                 + result.rows[i][1] + "' protocol='" + result.rows[i][2] + "' action='" + result.rows[i][4]
                                 + "' status='" + result.rows[i][3] + "'  data-key='" + result.rows[i][6] + "'>编辑</button>&nbsp;&nbsp;";
                        }
                        html += "<button class='button_delete button_small' data-key='" + result.rows[i][6] + "'>删除</button>";
                        html += "</td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='9'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='9'>暂无数据</td></tr>";
            }
            if (typeof (result.total) != "undefined") {
                $(parent.pLblStudyRuleCount).text(result.total);
            }
            if (typeof (result.sid_list) != "undefined") {
                parent.allRules = result.sid_list;
            }
            $(parent.pTdDefineWhitelist).html(html);
            layer.close(loadIndex);

            $(parent.pTdDefineWhitelist).find(".rule-single-select").ruleSingleSelect();

            $(parent.pTdDefineWhitelist).find(".select-note").on("change", function () {
                var id = $(this).attr("data-key");
                var state = $(this).val();
                parent.updateDefineWhitelistState(id, state);
            });

            $(parent.pTdDefineWhitelist).find(":checkbox[class='status']").on("change", function () {
                var id = $(this).attr("data-key");
                var status = $(this).prop("checked") == true ? 1 : 0;
                parent.updateDefineWhitelistStatus(id, status, $(this));
            });

            $(parent.pTdDefineWhitelist).find(".button_copy.button_small").on("click", function (event) {
                var src = $(this).attr("src");
                var dst = $(this).attr("dst");
                var protocol = $(this).attr("protocol");
                var status = $(this).attr("status");
                var action = $(this).attr("action");
                parent.showDefineDialog(0, src, dst, protocol, status, action);
            });

            $(parent.pTdDefineWhitelist).find(".button_edit.button_small").on("click", function (event) {
                var src = $(this).attr("src");
                var dst = $(this).attr("dst");
                var protocol = $(this).attr("protocol");
                var status = $(this).attr("status");
                var action = $(this).attr("action");
                var id = $(this).attr("data-key");
                parent.showDefineDialog(id, src, dst, protocol, status, action);
            });

            $(parent.pTdDefineWhitelist).find(".button_delete.button_small").on("click", function (event) {
                var id = $(this).attr("data-key");
                parent.deleteDefineWhitelist(id, $(this).parents("tr"));
            });

            $(parent.pTdDefineWhitelist).find(":checkbox[class!='status'][data-key]").each(function () {
                var id = parseInt($(this).attr("data-key"));
                var isExits = $.inArray(id, parent.checkedRules);
                if (isExits >= 0) {
                    $(this).prop("checked", true);
                }
            });

            $(parent.pTdDefineWhitelist).find("#chkWhitelist").on("change", function () {
                var checked = $(this).prop("checked");
                $(parent.pTdDefineWhitelist).find(":checkbox[class!='status']").prop("checked", checked);
                $(parent.pTdDefineWhitelist).find(":checkbox[class!='status']").each(function () {
                    var id = parseInt($(this).attr("data-key"));
                    if (checked && typeof (id) != "undefined") {
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

            $(parent.pTdDefineWhitelist).find(":checkbox[class!='status'][data-key]").on("change", function () {
                var checked = $(this).prop("checked");
                var id = parseInt($(this).attr("data-key"));
                if (checked && typeof (id) != "undefined") {
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

            if (parent.pWhitelistPager == null) {
                parent.pWhitelistPager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex, filters) {
                    parent.selectDefineWhitelist(pageIndex);
                });
                parent.pWhitelistPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='9'>暂无数据</td></tr>";
        $(this.pTdDefineWhitelist).html(html);
        layer.close(loadIndex);
        console.error("ERROR - DefineController.selectDefineWhitelist() - Unable to get define whitelist: " + err.message);
    }
}

DefineController.prototype.resetCheckAllStatus = function () {
    try {
        this.checkedRules = [];
        $(this.pBtnCheckAll).text("全选");
        $(this.pBtnCheckAll).removeClass("but_all");
        $(this.pBtnCheckAll).addClass("but_off");
        $(this.pBtnCheckAll).attr("isChecked", "true");
    }
    catch (err) {
        console.error("ERROR - DefineController.resetCheckAllStatus() - Unable to reset the checkAll control status: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.rule.DefineController", DefineController);