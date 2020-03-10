function RecoverStreamController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.pStreamController = controller;

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnFilter = "#" + this.elementId + "_btnFilter";
    this.pBtnSearch = "#" + this.elementId + "_btnSearch";
    this.pDivFilter = "#" + this.elementId + "_divFilter";

    this.pTxtIP = "#" + this.elementId + "_txtIP";
    this.pTxtProtocol = "#" + this.elementId + "_txtProtocol";
    this.pTxtStartDateTime = "#" + this.elementId + "_txtStartDateTime";
    this.pTxtEndDateTime = "#" + this.elementId + "_txtEndDateTime";
    this.pTxtKeywords = "#" + this.elementId + "_txtKeywords";

    this.pTdStreamList = "#" + this.elementId + "_tdStreamList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotalStream = "#" + this.elementId + "_lblTotalStream";

    this.pStreamPager = null;
    this.pDetailController = null;
    this.pFilters = "";
}

RecoverStreamController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.STREAM_RECOVER), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - RecoverStreamController.init() - Unable to initialize: " + err.message);
    }
}

RecoverStreamController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pBtnRefresh).on("click", function () {
            parent.pStreamPager = null;
            parent.searchStreams(1, parent.pFilters);
        });
        
        $(this.pBtnFilter).on("click", function () {
            $(parent.pTxtIP).val("");
            $(parent.pTxtProtocol).val("");
            $(parent.pTxtStartDateTime).val("");
            $(parent.pTxtEndDateTime).val("");
            $(parent.pTxtKeywords).val("");
            $(parent.pBtnFilter).toggleClass("butip");
            $(parent.pBtnFilter).toggleClass("butipon");
            $(parent.pDivFilter).toggle();
            $(parent.pTxtKeywords).toggle();
        });

        $(this.pBtnSearch).on("click", function () {
            parent.formatFilter();
            parent.pStreamPager = null;
            parent.searchStreams(1,parent.pFilters);
        });
    }
    catch (err) {
        console.error("ERROR - RecoverStreamController.initControls() - Unable to initialize control: " + err.message);
    }
}

RecoverStreamController.prototype.load = function () {
    try {
        this.formatFilter();
        this.searchStreams(1, this.pFilters);
    }
    catch (err) {
        console.error("ERROR - RecoverStreamController.load() - Unable to load: " + err.message);
    }
}

RecoverStreamController.prototype.searchStreams = function (pageIndex,filter) {
    var html = "";
    html += '<tr class="title">';
    html += '<td class="address" style="width:15%;">时间</td>';
    html += '<td class="address" style="width:25%;">IP地址</td>';
    html += '<td class="address" style="width:25%;">MAC地址</td>';
    html += '<td class="address" style="width:15%;">端口</td>';
    html += '<td class="time" style="width:10%;">协议类型</td>';
    html += '<td style="width:10%;">操作</td>';
    html += '</tr>';
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_STREAM_LIST + filter + "page=" + pageIndex;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='6'>暂无数据</td></tr>";
            $(parent.pTdStreamList).html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td style='width:15%;'>" + result.rows[i][6] + "</td>";
                        html += "<td style='width:25%;'>" + result.rows[i][0] +"<=>"+ result.rows[i][1] + "</td>";
                        html += "<td style='width:25%;'>" + result.rows[i][2] + "<=>" + result.rows[i][3] + "</td>";
                        html += "<td style='width:15%;'>" + result.rows[i][4] + "<=>" + result.rows[i][5] + "</td>";
                        html += "<td style='width:10%;'>" + result.rows[i][7] + "</td>";
                        html += "<td style='width:10%;'><button class='details' data-key='" + result.rows[i][9] + "' data='" + JSON.stringify(result.rows[i]) + "'>详情</button></td>";
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
                $(parent.pStreamController.pTotalStreamRecover).text(result.total);
                $(parent.pLblTotalStream).text(result.total);
            }
            $(parent.pTdStreamList).html(html);
            layer.close(loadIndex);
            $(parent.pTdStreamList).find("button").on("click", function (stream) {
                var id = $(this).attr("data-key");
                var data = JSON.parse($(this).attr("data"));

                if (data[7] == "ftp") {
                    parent.showFtpDialog(data);
                }
                else {
                    parent.showNormalDialog(data);
                }
            });

            if (parent.pStreamPager == null) {
                parent.pStreamPager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex,filters) {
                    parent.searchStreams(pageIndex, parent.pFilters);
                });
                parent.pStreamPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }

        });
    }
    catch (err) {
        html += "<tr><td colspan='6'>暂无数据</td></tr>";
        $(this.pTdStreamList).html(html);
        console.error("ERROR - RecoverStreamController.selectStreams() - Unable to search safe streams via filter: " + err.message);
    }
}

RecoverStreamController.prototype.formatFilter = function () {
    try {
        this.pFilters = "?starttime=" + $.trim($(this.pTxtStartDateTime).val()) + "&";
        this.pFilters += "endtime=" + $.trim($(this.pTxtEndDateTime).val()) + "&";
        this.pFilters += "ip=" + $.trim($(this.pTxtIP).val()) + "&";
        this.pFilters += "proto=" + $.trim($(this.pTxtProtocol).val()) + "&";
        this.pFilters += "keyword="+ $.trim($(this.pTxtKeywords).val())+"&";
    }
    catch (err) {
        console.error("ERROR - RecoverStreamController.formatFilter() - Unable to get filter for searching: " + err.message);
    }
}

RecoverStreamController.prototype.showFtpDialog = function (data) {
    try {
        var parent = this;
        var dialogHandler = $("<div />");
        var width = parent.pStreamController.pViewHandle.find(".eventinfo_box").width() - 10 + "px";
        var height = $(window).height() - parent.pStreamController.pViewHandle.find(".eventinfo_box").offset().top - 10 + "px";
        layer.open({
            type: 1,
            title: "详细信息",
            offset: ["82px", "200px"],
            area: [width, height],
            shade: [0.5, '#393D49'],
            content: dialogHandler.html(),
            success: function (layero, index) {
                parent.pDetailController = new tdhx.base.stream.RecoverStreamDialogController(parent, layero.find(".layui-layer-content"), parent.elementId + "_dialog", data);
                parent.pDetailController.init();
                //layero.find(".layui-layer-content").css("overflow", "visible");
                $(window).on("resize", function () {
                    var pwidth = parent.pStreamController.pViewHandle.find(".eventinfo_box").width() - 10 + "px";
                    var pheight = $(window).height() - parent.pStreamController.pViewHandle.find(".eventinfo_box").offset().top - 10 + "px";
                    layero.width(pwidth);
                    layero.height(pheight);
                })
            }
        });
    }
    catch (err) {
        console.error("ERROR - RecoverStreamController.showFtpDialog() - Unable to show dialog for dialog: " + err.message);
    }
}

RecoverStreamController.prototype.showNormalDialog = function (data) {
    try {
        var parent = this;
        var dialogHandler = $("<div />");
        var width = (parent.pStreamController.pViewHandle.find(".eventinfo_box").width() - 10) / 2 - 300
        var left =  (width==0?"100":width+100+ "px");
        var top = ($(window).height() - parent.pStreamController.pViewHandle.find(".eventinfo_box").offset().top - 10)/2-150+40 + "px";
        layer.open({
            type: 1,
            title: "详细信息",
            shade: [0.5, '#393D49'],
            area:['660px','280px'],
            offset: [top, left],
            content: dialogHandler.html(),
            success: function (layero, index) {
                parent.pDetailController = new tdhx.base.stream.DownloadStreamDialogController(parent, layero.find(".layui-layer-content"), parent.elementId + "_dialog", data);
                parent.pDetailController.init();
            }
        });
    }
    catch (err) {
        console.error("ERROR - RecoverStreamController.formatFilter() - Unable to show dialog: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.stream.RecoverStreamController", RecoverStreamController);