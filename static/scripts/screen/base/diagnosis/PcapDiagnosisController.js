function PcapDiagnosisController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.controller = controller;
    this.pager = null;

    this.pRabEth = "#" + this.elementId + "_rabEth";
    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnFilter = "#" + this.elementId + "_btnFilter";
    this.pDivFilter = "#" + this.elementId + "_divFilter";
    this.pBtnSearch = "#" + this.elementId + "_btnSearch";
    this.pBtnExport = "#" + this.elementId + "_btnExport";
    this.pBtnDownload = "#" + this.elementId + "_btnDownload";
    this.pBtnSaveServer = "#" + this.elementId + "_btnSaveServer";
    this.pDivPort = "#" + this.elementId + "_divPort";
    this.pTxtStartDateTime = "#" + this.elementId + "_txtStartDateTime";
    this.pTxtEndDateTime = "#" + this.elementId + "_txtEndDateTime";

    this.pChkAll = "#" + this.elementId + "_chkAll";
    this.pDivServer = "#" + this.elementId + "_divServer";
    this.pTxtServer = "#" + this.elementId + "_txtServer";
    this.pTxtUserID = "#" + this.elementId + "_txtUserID";
    this.pTxtPassword = "#" + this.elementId + "_txtPassword";
    this.pBtnTest = "#" + this.elementId + "_btnTest";

    this.pTdPcapList = "#" + this.elementId + "_tdPcapList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";

    this.filter = {
        page: 1,
        interface: "",
        starttime: "",
        endtime: ""
    };
    this.checked = false;
    this.checkedFiles = [];
    this.noCheckedFiles = [];
    this.files = [];
    this.isAllChecked = false;
}

PcapDiagnosisController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.DIAGNOSIS_PCAP), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - PcapDiagnosisController.init() - Unable to initialize: " + err.message);
    }
}

PcapDiagnosisController.prototype.initControls = function () {
    try {
        var parent = this;

        this.pViewHandle.find(this.pBtnRefresh).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectPcap();
        });

        this.pViewHandle.find(this.pBtnFilter).on("click", function () {
            parent.pViewHandle.find(parent.pTxtStartDateTime).val("");
            parent.pViewHandle.find(parent.pTxtEndDateTime).val("");
            parent.pViewHandle.find(parent.pDdlExecuteStatus).val("");
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            parent.pViewHandle.find(parent.pDivFilter).toggle();
        });

        this.pViewHandle.find(this.pRabEth).on("click", function () {
            parent.updateSetting();
        });

        this.pViewHandle.find(this.pChkAll).on("click", function () {
            parent.isAllChecked = ($(this).attr("isChecked") == "true");
            $(parent.pTdPcapList).find("input:checkbox").prop("checked", parent.isAllChecked);
            if (parent.isAllChecked) {
                $(this).html("<i class='fa fa-check-square-o'></i>取消");
                $(this).attr("isChecked", "false");
                parent.checkedFiles = [];
            }
            else {
                parent.noCheckedFiles = [];
                //$(this).text("全选");
                $(this).html("<i class='fa fa-square-o'></i>全选");
                $(this).attr("isChecked", "true");
            }
        });

        this.pViewHandle.find(this.pBtnSearch).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectPcap();
        });

        this.pViewHandle.find(this.pBtnExport).on("click", function () {
            parent.exportPcap();
        });

        this.pViewHandle.find(this.pBtnDownload).on("click", function () {
            parent.downloadPcap();
        });

        this.pViewHandle.find(this.pBtnTest).on("click", function () {
            parent.testPcap();
        });

        this.pViewHandle.find(this.pBtnSaveServer).on("click", function () {
            parent.savePcapServer();
        });

    }
    catch (err) {
        console.error("ERROR - PcapDiagnosisController.initControls() - Unable to initialize control: " + err.message);
    }
}

PcapDiagnosisController.prototype.load = function () {
    try {
        this.getSetting();
        this.getInterface();
        this.getPcapServer();
        this.formatFilter();
        this.selectPcap();
    }
    catch (err) {
        console.error("ERROR - PcapDiagnosisController.load() - Unable to load: " + err.message);
    }
}

PcapDiagnosisController.prototype.getSetting = function () {
    var parent = this;
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PCAP_SETTING;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        $(parent.pRabEth).prop("checked", result.switch == 1 ? true : false);
                        break;
                    default: layer.alert("无法数据包存储设置", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("无法数据包存储设置", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - PcapDiagnosisController.getSetting() - Unable to get the pcap setting: " + err.message);
    }
}

PcapDiagnosisController.prototype.updateSetting = function () {
    var parent = this;
    var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
    try {
        var swtch = $(this.pRabEth).prop("checked") ? "1" : "0";
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_PCAP_SETTING;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", { 'switch': swtch });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1: layer.alert("审计追踪设置成功", { icon: 6 }); break;
                    default: layer.alert("审计追踪设置失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("审计追踪设置失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - PcapDiagnosisController.load() - Unable to update the setting: " + err.message);
    }
}

PcapDiagnosisController.prototype.getPcapServer = function () {
    var parent = this;
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PCAP_SERVER;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1) {
                parent.pViewHandle.find(parent.pTxtServer).val(result.host);
                parent.pViewHandle.find(parent.pTxtUserID).val(result.username);
                parent.pViewHandle.find(parent.pTxtPassword).val(result.password);
            }
            else {
                layer.alert("FTP服务器数据获取失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - PcapDiagnosisController.getPcapServer() - Unable to get ftp server information: " + err.message);
    }
}

PcapDiagnosisController.prototype.savePcapServer = function () {
    var parent = this;
    var loadIndex;
    try {
        var host = $.trim(this.pViewHandle.find(this.pTxtServer).val());
        var uid = $.trim(this.pViewHandle.find(this.pTxtUserID).val());
        var pwd = $.trim(this.pViewHandle.find(this.pTxtPassword).val());
        if (!Validation.validateIP(host)) {
            layer.alert("服务器地址错误", { icon: 5 });
            return false;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_PCAP_SERVER;
        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {
            host: host,
            username: uid,
            password:pwd
        });
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1) {
                layer.alert("保存FTP服务器数据成功", { icon: 6 });
            }
            else {
                layer.alert("保存FTP服务器数据失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - PcapDiagnosisController.savePcapServer() - Unable to save ftp server information: " + err.message);
    }
}

PcapDiagnosisController.prototype.testPcap = function () {
    var parent = this;
    var loadIndex;
    try {
        var host = $.trim(this.pViewHandle.find(this.pTxtServer).val());
        var uid = $.trim(this.pViewHandle.find(this.pTxtUserID).val());
        var pwd = $.trim(this.pViewHandle.find(this.pTxtPassword).val());
        if (!Validation.validateIP(host)) {
            layer.alert("服务器地址错误", { icon: 5 });
            return false;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].TEST_PCAP_LIST;
        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {
            host: host,
            username: uid,
            password: pwd,
            loginuser: AuthManager.getInstance().getUserName()
        }, true);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1 && typeof (result.result) != "undefined") {
                switch (result.result) {
                    case 1: layer.alert("连接成功", { icon: 6 }); break;
                    case 2: layer.alert("连接失败", { icon: 5 }); break;
                    default: layer.alert("用户名或者密码错误", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("连接失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - PcapDiagnosisController.testPcap() - Unable to connect with this server: " + err.message);
    }
}

PcapDiagnosisController.prototype.exportPcap = function () {
    var parent = this;
    var loadIndex;
    try {
        var host = $.trim(this.pViewHandle.find(this.pTxtServer).val());
        var uid = $.trim(this.pViewHandle.find(this.pTxtUserID).val());
        var pwd = $.trim(this.pViewHandle.find(this.pTxtPassword).val());
        if (!Validation.validateIP(host)) {
            layer.alert("服务器地址错误", { icon: 5 });
            return false;
        }
        if (parent.isAllChecked) {
            parent.files = parent.noCheckedFiles;
        }
        else {
            parent.files = parent.checkedFiles;
        }
        if (!parent.isAllChecked && this.files.length < 1) {
            layer.alert("你还没有选择任何文件，无法导出", { icon: 5 });
            return false;
        }
        var para = {
            host: host,
            username: uid,
            password: pwd,
            interface: parent.filter.interface,
            select_all: this.isAllChecked == true ? "1" : "0",
            starttime: this.filter.starttime,
            endtime: this.filter.endtime,
            files: this.files.toString(),
            loginuser: AuthManager.getInstance().getUserName()
        };
        parent.checkPcap(para, 1, function () {
            loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].EXPORT_PCAP_LIST;
            var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", para);
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                layer.close(loadIndex);
            });
            promise.done(function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1) {
                    switch (result.result) {
                        case 1: layer.alert("正在导出，请稍后查看文件...", { icon: 6 }); break;
                        case 2: layer.alert("服务器没有响应，请稍后重试", { icon: 5 }); break;
                        case 3: layer.alert("用户名或者密码错误", { icon: 5 }); break;
                        default: layer.alert("导出失败", { icon: 5 }); break;
                    }
                }
                else {
                    layer.alert("导出失败", { icon: 5 });
                }
                layer.close(loadIndex);
            });
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - PcapDiagnosisController.exportPcap() - Unable to export these files: " + err.message);
    }
}

PcapDiagnosisController.prototype.downloadPcap = function () {
    var parent = this;
    try {
        if (parent.isAllChecked) {
            parent.files = parent.noCheckedFiles;
        }
        else {
            parent.files = parent.checkedFiles;
        }
        if (!parent.isAllChecked && this.files.length < 1) {
            layer.alert("你还没有选择任何文件，无法导出", { icon: 5 });
            return false;
        }
        var para = {
            interface: this.filter.interface,
            select_all: this.isAllChecked == true ? "1" : "0",
            starttime: this.filter.starttime,
            endtime: this.filter.endtime,
            files: this.files.toString()
        };
        parent.checkPcap(para, 2, function () {
            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DOWNLOAD_PCAP_LIST;
            link += "?r=" + (Math.random() * (1000000 - 1) + 1)+"&loginuser=" + AuthManager.getInstance().getUserName();
            if (typeof (para) == "object") {
                for (var key in para) {
                    link += "&" + key + "=" + para[key];
                }
            }
            window.open(link);
        });
    }
    catch (err) {
        console.error("ERROR - PcapDiagnosisController.downloadPcap() - Unable to download these files: " + err.message);
    }
}

PcapDiagnosisController.prototype.checkPcap = function (para, type, callback) {
    var parent = this;
    var loadIndex;
    try {
        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].CHECK_PCAP_LIST_STATUS;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", para);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            layer.close(loadIndex);
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                var file_count = result.sum_count;
                var file_size = (result.sum_size / 1024 / 1024).toFixed(0) + "MB";
                var download_timespan = result.estimate_download_time + "秒";
                if (result.estimate_download_time > 3600) {
                    download_timespan = (result.estimate_download_time / 3600).toFixed(0) + "小时";
                } else if (result.estimate_download_time > 60) {
                    download_timespan = (result.estimate_download_time / 60).toFixed(0) + "分钟";
                }
                var max_file_size = (result.support_download_max_size / 1024 / 1024).toFixed(0) + "MB";
                var html = "<p>正在下载的文件总数量：" + file_count + "</p>";
                html += "<p>当前正在下载的文件总大小：" + file_size + "</p>";
                html += "<p>所需下载时间：" + download_timespan + "</p>";
                if (type == 1) {
                    layer.confirm("您确认继续导出到服务器吗？", {
                        title: "提示",
                        btn: ["确定", "取消"],
                        content: html,
                        btn1: function (index, layero) {
                            layer.close(index);
                            callback();
                        }
                    });
                }
                else {
                    html += "<p>当前设备支持的最大文件：" + max_file_size + "</p>";
                    if (APPCONFIG.PRODUCT.toLowerCase() == "kea-c200") {
                        html += "<p style='color:#ff0000;'>注意：下载期间，无法操作其他功能</p>";
                    }
                    layer.confirm("您确认继续导出到本机吗？", {
                        title: "提示",
                        btn: ["确定", "取消"],
                        content: html,
                        btn1: function (index, layero) {
                            layer.close(index);
                            switch (result.status) {
                                case 1:
                                    callback();
                                    break;
                                case 2:
                                    layer.alert("所要下载的文件包过大，请重新选择", { icon: 5 });
                                    break;
                                case 3:
                                    layer.alert("当前正在下载的任务过多，请稍后重试", { icon: 5 });
                                    break;
                            }
                        }
                    });
                }
            }
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - PcapDiagnosisController.checkPcap() - Unable to checked these files: " + err.message);
    }
}

PcapDiagnosisController.prototype.getInterface = function () {
    var parent = this;
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PCAP_INTERFACE;
        var promise = URLManager.getInstance().ajaxSyncCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.initPyhsicInterface(result.phy_interfaces);
                        break;
                    default: layer.alert("物理接口获取失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("物理接口获取失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - PcapDiagnosisController.getInterface() - Unable to get the physic interface: " + err.message);
    }
}

PcapDiagnosisController.prototype.selectPcap = function () {
    var html = "";
    var parent = this;
    var loadIndex = layer.load(2);
    try {
        this.pViewHandle.find(this.pTdPcapList + ">thead>tr>th:first").find("input").attr("data-type", "allchecked");
        this.pViewHandle.find(this.pTdPcapList + ">thead>tr>th:first").find("input").attr("data-key", "0");
        if (this.checked) {
            this.pViewHandle.find(this.pTdPcapList + ">thead>th>td:first").find("input").prop("checked", true);
        }
        else {
            this.pViewHandle.find(this.pTdPcapList + ">thead>th>td:first").find("input").prop("checked", false);
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PCAP_LIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='5'>暂无数据</td></tr>";
            parent.pViewHandle.find(parent.pTdPcapList + ">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td><input type='checkbox' data-key='" + result.rows[i][4] + "' /></td>";
                        html += "<td>" + result.rows[i][0] + "</td>";
                        html += "<td>" + result.rows[i][1] + "</td>";
                        html += "<td>" + result.rows[i][2] + "  ~  " + result.rows[i][3] + "</td>";
                        html += "<td>";
                        html += "<a title='下载到本机' target='_blank' href='/pcapfile/" + result.rows[i][1] + "/" + result.rows[i][0] + "?loginuser=" + AuthManager.getInstance().getUserName() + "&r=" + (Math.random() * (1000000 - 1) + 1) + "' class='btn btn-info btn-xs'><i class='fa fa-download'></i>下载</a>";
                        html += "&nbsp;&nbsp;<button class='btn btn-info btn-xs' data-key='" + result.rows[i][4] + "'><i class='fa fa-share'></i>导出</button>";
                        html+="</td>";
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

            parent.pViewHandle.find(parent.pTdPcapList + ">tbody").html(html);
            layer.close(loadIndex);

            parent.pViewHandle.find(parent.pTdPcapList).find("button[data-key]").on("click", function () {
                parent.exportSinglePcap($(this).attr("data-key"));
            });

            parent.pViewHandle.find(parent.pTdPcapList).find(":checkbox[data-type='allchecked']").on("change", function () {
                parent.checked = $(this).prop("checked");
                parent.pViewHandle.find(parent.pTdPcapList).find(":checkbox").prop("checked", parent.checked);
                parent.pViewHandle.find(parent.pTdPcapList).find(":checkbox").each(function () {
                    var id = $(this).attr("data-key");
                    if (parent.isAllChecked) {
                        if (parent.checked == false) {
                            if (id != "0") {
                                var isExits = $.inArray(id, parent.noCheckedFiles);
                                if (isExits < 0) {
                                    parent.noCheckedFiles.push(id);
                                }
                            }
                        }
                        else {
                            if (id != "0") {
                                parent.noCheckedFiles.forEach(function (item, index) {
                                    if (item == id) {
                                        parent.noCheckedFiles.splice(index, 1);
                                    }
                                });
                            }
                        }
                    }
                    else {
                        if (parent.checked == false) {
                            if (id != "0") {
                                parent.checkedFiles.forEach(function (item, index) {
                                    if (item == id) {
                                        parent.checkedFiles.splice(index, 1);
                                    }
                                });
                            }
                        }
                        else {
                            if (id != "0") {
                                var isExits = $.inArray(id, parent.checkedFiles);
                                if (isExits < 0) {
                                    parent.checkedFiles.push(id);
                                }
                            }
                        }

                    }
                });
            });

            parent.pViewHandle.find(parent.pTdPcapList).find("input:checkbox").each(function () {
                var id = $(this).attr("data-key");
                if (parent.isAllChecked) {
                    var isExits = $.inArray(id, parent.noCheckedFiles);
                    if (isExits >= 0) {
                        $(this).prop("checked", false);
                    }
                    else {
                        $(this).prop("checked", true);
                    }
                }
                else {
                    var isExits = $.inArray(id, parent.checkedFiles);
                    if (isExits >= 0) {
                        $(this).prop("checked", true);
                    }
                    else {
                        $(this).prop("checked", false);
                    }

                }
            });

            parent.pViewHandle.find(parent.pTdPcapList).find(":checkbox").on("change", function () {
                var checked = $(this).prop("checked");
                var id = $(this).attr("data-key");
                if (parent.isAllChecked) {
                    if (!checked) {
                        if (id != "0") {
                            var isExits = $.inArray(id, parent.noCheckedFiles);
                            if (isExits < 0) {
                                parent.noCheckedFiles.push(id);
                            }
                        }

                    }
                    else {
                        if (id != "0") {
                            parent.noCheckedFiles.forEach(function (item, index) {
                                if (item == id) {
                                    parent.noCheckedFiles.splice(index, 1);
                                }
                            });
                        }
                    }
                }
                else {
                    if (!checked) {
                        if (id != "0") {
                            parent.checkedFiles.forEach(function (item, index) {
                                if (item == id) {
                                    parent.checkedFiles.splice(index, 1);
                                }
                            });
                        }
                    }
                    else {
                        if (id != "0") {
                            var isExits = $.inArray(id, parent.checkedFiles);
                            if (isExits < 0) {
                                parent.checkedFiles.push(id);
                            }
                        }
                    }
                }

            });

            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectPcap();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='5'>暂无数据</td></tr>";
        this.pViewHandle.find(this.pTdPcapList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - PcapDiagnosisController.selectPcap() - Unable to search pcap files via filter: " + err.message);
    }
}

PcapDiagnosisController.prototype.exportSinglePcap = function (id) {
    var parent = this;
    var loadIndex;
    try {
        var host = $.trim(this.pViewHandle.find(this.pTxtServer).val());
        var uid = $.trim(this.pViewHandle.find(this.pTxtUserID).val());
        var pwd = $.trim(this.pViewHandle.find(this.pTxtPassword).val());
        if (!Validation.validateIP(host)) {
            layer.alert("服务器地址错误", { icon: 5 });
            return false;
        }
        var para = {
            host: host,
            username: uid,
            password: pwd,
            interface: "",
            select_all: "0",
            starttime: "",
            endtime: "",
            files: ""+id+"",
            loginuser: AuthManager.getInstance().getUserName()
        };
        loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].EXPORT_PCAP_LIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", para);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1) {
                switch (result.result) {
                    case 1: layer.alert("正在导出，请稍后查看文件...", { icon: 6 }); break;
                    case 2: layer.alert("服务器没有响应，请稍后重试", { icon: 5 }); break;
                    case 3: layer.alert("用户名或者密码错误", { icon: 5 }); break;
                    default: layer.alert("导出失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("导出失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        layer.close(loadIndex);
        console.error("ERROR - PcapDiagnosisController.exportSinglePcap() - Unable to export single file: " + err.message);
    }
}

PcapDiagnosisController.prototype.initPyhsicInterface = function (interfaces) {
    var parent = this;
    try {
        if (typeof (interfaces) == "object" && interfaces.length > 0) {
            var templates = "";
            var html = "<li><input type='checkbox' name='" + this.elementId + "_rabPhyInterface' id='" + this.elementId + "_rabPhyInterface{0}' data='{0}' checked />";
            html += "<label style='width:24px;' for='" + this.elementId + "_rabPhyInterface{0}'>{0}</label></li>";
            interfaces.forEach(function (item, index) {
                templates += html.replace(/\{0\}/g, item);
            });
            $(this.pDivPort).html(templates);
        }
    }
    catch (err) {
        console.error("ERROR - PcapDiagnosisController.initPyhsicInterface() - Unable to initizing the physic interface: " + err.message);
    }
}

PcapDiagnosisController.prototype.formatFilter = function () {
    try {
        var inters = "";
        this.pViewHandle.find(this.pDivPort).find(":checkbox").each(function () {
            if ($(this).prop("checked")) {
                inters += $(this).attr("data") + ',';
            }
        });
        if (inters.length > 0) {
            inters = inters.substr(0, inters.length - 1);
        }
        this.filter.interface = inters;
        this.filter.starttime = $.trim(this.pViewHandle.find(this.pTxtStartDateTime).val());
        this.filter.endtime = $.trim(this.pViewHandle.find(this.pTxtEndDateTime).val());
    }
    catch (err) {
        console.error("ERROR - PcapDiagnosisController.formatFilter() - Unable to get filter for searching: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.diagnosis.PcapDiagnosisController", PcapDiagnosisController);
