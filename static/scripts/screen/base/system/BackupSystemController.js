function BackupSystemController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.controller = controller;
    this.pager = null;
    this.checked = false;
    this.checkedFiles = [];

    this.pRabAutoBackup = "#" + this.elementId + "_rabAutoBackup";
    this.pBtnManaul = "#" + this.elementId + "_btnManaul";
    this.pBtnDelete = "#" + this.elementId + "_btnDelete";

    this.pTdBackupList = "#" + this.elementId + "_tdBackupList";
}

BackupSystemController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_BACKUP), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - BackupSystemController.init() - Unable to initialize: " + err.message);
    }
}

BackupSystemController.prototype.initControls = function () {
    try {
        var parent = this;

        this.pViewHandle.find(this.pRabAutoBackup).on("click", function () {
            parent.updateBackupStatus();
        });

        this.pViewHandle.find(this.pBtnManaul).on("click", function () {
            parent.manualBackup();
        });

        this.pViewHandle.find(this.pBtnDelete).on("click", function () {
            if (parent.checkedFiles.length > 0){
                parent.deleteBackup();
            }
            else
            {
                layer.alert("请选择要删除的备份文件", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - BackupSystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

BackupSystemController.prototype.load = function () {
    try {
        this.getBackupStatus();
        this.selectBackup();
    }
    catch (err) {
        console.error("ERROR - BackupSystemController.load() - Unable to load: " + err.message);
    }
}

BackupSystemController.prototype.getBackupStatus = function () {
    var parent = this;
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_BACKUP_STATUS;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1) {
                parent.pViewHandle.find(parent.pRabAutoBackup).prop("checked", result.mode == 1 ? true : false);
            }
            else {
                layer.alert("无法获取自动备份状态", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - BackupSystemController.getBackupStatus() - Unable to get the auto backup status: " + err.message);
    }
}

BackupSystemController.prototype.updateBackupStatus = function () {
    var parent = this;
    try {
        var swtch = parent.pViewHandle.find(parent.pRabAutoBackup).prop("checked") ? 1 : 0;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_BACKUP_STATUS;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { auto: swtch });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1: layer.alert("自动备份设置成功", { icon: 6 }); break;
                    default: layer.alert("自动备份设置失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("自动备份设置失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - BackupSystemController.updateBackupStatus() - Unable to update the auto backup setting: " + err.message);
    }
}

BackupSystemController.prototype.manualBackup = function () {
    var parent = this;
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].MANAU_BACKUP;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1: layer.alert("备份成功", { icon: 6 }); parent.selectBackup(); break;
                    default: layer.alert("备份失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("备份失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - BackupSystemController.testPcap() - Unable to connect with this server: " + err.message);
    }
}

BackupSystemController.prototype.deleteBackup = function () {
    var parent = this;
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DELETE_BACKUP_LIST;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCallByURL(link, "GET", { id: this.checkedFiles });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.selectBackup();
                        parent.checkedFiles = [];
                        break;
                    default: layer.alert("删除失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("删除失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - BackupSystemController.exportPcap() - Unable to export these files: " + err.message);
    }
}

BackupSystemController.prototype.selectBackup = function () {
    var html = "";
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_BACKUP_LIST;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='5'>暂无数据</td></tr>";
            parent.pViewHandle.find(parent.pTdBackupList + ">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td><input type='checkbox' data-key='" + result.rows[i][0] + "' /></td>";
                        html += "<td>" + result.rows[i][1] + "</td>";
                        html += "<td>" + result.rows[i][3] + "</td>";
                        html += "<td title='" + result.rows[i][4] + "'>" + FormatterManager.stripText(result.rows[i][4], 32) + "</td>"
                        html += "<td>";
                        html += "<button type='button' class='btn btn-primary btn-xs' data-key='" + result.rows[i][0] + "' data-content='" + result.rows[i][4] + "'><i class='fa fa-pencil-square-o'></i>备注</button>";
                        html += "<a title='导出' href='" + APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].EXPORT_BACKUP_PATH + "/" + result.rows[i][3] +"?r=" + (Math.random() * (1000000 - 1) + 1)+ "&loginuser=" + AuthManager.getInstance().getUserName() + "' target='_blank' class='btn btn-info btn-xs' style='margin:0px 5px;'><i class='fa fa-level-down'></i>下载</a></td>";
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

            parent.pViewHandle.find(parent.pTdBackupList + ">tbody").html(html);
            layer.close(loadIndex);

            parent.pViewHandle.find(parent.pTdBackupList).find(":checkbox[data-type='allchecked']").on("change", function () {
                var checked = $(this).prop("checked");
                $(parent.pTdBackupList).find(":checkbox").prop("checked", checked);
                $(parent.pTdBackupList + ">tbody").find(":checkbox").each(function () {
                    var id = $(this).attr("data-key");
                    if (checked) {
                        var isExits = $.inArray(id, parent.checkedFiles);
                        if (isExits < 0) {
                            parent.checkedFiles.push(id);
                        }
                    }
                    else {
                        parent.checkedFiles.forEach(function (item, index) {
                            if (item == id) {
                                parent.checkedFiles.splice(index, 1);
                            }
                        });
                    }
                });
            });

            parent.pViewHandle.find(parent.pTdBackupList + ">tbody").find("input:checkbox").each(function () {
                var id = $(this).attr("data-key");
                var isExits = $.inArray(id, parent.checkedFiles);
                if (isExits >= 0) {
                    $(this).prop("checked", true);
                }
            });

            parent.pViewHandle.find(parent.pTdBackupList + ">tbody").find(":checkbox").on("change", function () {
                var checked = $(this).prop("checked");
                var id = $(this).attr("data-key");
                if (checked && id != "0") {
                    var isExits = $.inArray(id, parent.checkedFiles);
                    if (isExits < 0) {
                        parent.checkedFiles.push(id);
                    }
                }
                else {
                    parent.checkedFiles.forEach(function (item, index) {
                        if (item == id) {
                            parent.checkedFiles.splice(index, 1);
                        }
                    });
                }
            });

            parent.pViewHandle.find(parent.pTdBackupList).find("button").on("click", function () {
                var id = $(this).attr("data-key");
                var content = $(this).attr("data-content");
                var obj = $(this);
                layer.prompt({ title: '备注', formType: 2, value: content }, function (value, index, elem) {
                    parent.updateBackup(id, value, obj);
                });
            });
        });
    }
    catch (err) {
        html += "<tr><td colspan='5'>暂无数据</td></tr>";
        this.pViewHandle.find(this.pTdBackupList + ">tbody").html(html);
        console.error("ERROR - BackupSystemController.selectBackup() - Unable to search backup files: " + err.message);
    }
}

BackupSystemController.prototype.updateBackup = function (id, descrip, $obj) {
    var parent = this;
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_BACKUP;
        var data = {
            id: id,
            desc: descrip
        };
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", data);
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        $obj.parent().prev().text(FormatterManager.stripText(descrip, 32));
                        $obj.parent().context.attributes["data-content"].value = descrip;
                        $obj.parent().prev()[0].title = descrip;
                        layer.closeAll();
                        break;
                    default: layer.alert("备注添加失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("备注添加失败", { icon: 5 });
            }
            layer.closeAll();
        });
    }
    catch (err) {
        console.error("ERROR - BackupSystemController.updateBackup() - Unable to add description for this file: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.BackupSystemController", BackupSystemController);