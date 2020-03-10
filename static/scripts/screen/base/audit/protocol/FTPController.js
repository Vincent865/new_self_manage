function FTPController(controller, viewHandle, elementId, id, ip, mac, port, time, protocol) {
    this.controller = controller;
    this.pViewHandle = viewHandle;
    this.elementId = elementId
    this.id = id;
    this.ip = ip;
    this.mac = mac;
    this.port = port;
    this.time = time;
    this.protocol = protocol;

    this.pLblType = "#" + this.elementId + "_lblType";
    this.pLblTime = "#" + this.elementId + "_lblTime";
    this.pLblPort = "#" + this.elementId + "_lblPort";
    this.pLblIP = "#" + this.elementId + "_lblIP";
    this.pLblMAC = "#" + this.elementId + "_lblMAC";
    this.pTdProtocolList = "#" + this.elementId + "_tdProtocolList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";

    this.pager = null;
    this.filter = {
        page: 1,
        protocol: protocol,
        flowdataHeadId: id
    };
}

FTPController.prototype.init = function () {
    try {
        var parent = this;

        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.AUDIT_PROTOCOL_FTP), {
            elementId: parent.elementId
        });
        this.pViewHandle.find(".layui-layer-content").html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - FTPController.init() - Unable to initialize: " + err.message);
    }
}

FTPController.prototype.initControls = function () {
    try {
    }
    catch (err) {
        console.error("ERROR - FTPController.initControls() - Unable to initialize control: " + err.message);
    }
}

FTPController.prototype.load = function () {
    try {
        //details
        var parent = this;
        $(this.pLblIP).html(this.ip).attr("title",this.ip);
        $(this.pLblMAC).html(this.mac);
        $(this.pLblPort).html(this.port);
        $(this.pLblTime).html(this.time);
        $(this.pLblType).html($.grep(parent.controller.protocolList, function (item) { return item.key == parent.protocol })[0].name);
        //table
        this.selectProtocol();
    }
    catch (err) {
        console.error("ERROR - FTPController.load() - Unable to load: " + err.message);
    }
}

FTPController.prototype.selectProtocol = function () {
    var html = "";
    var parent = this;
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_PROTOCOL;
        var promise = URLManager.getInstance().ajaxCall(link,this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='3'>暂无数据</td></tr>";
            $(parent.pTdProtocolList + ">tbody").html(html);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td style='width:20%;'>" + result.rows[i][6] + "</td>";
                        html += "<td style='text-align:left;'>" + result.rows[i][2] + "</td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='3'>暂无数据</td></tr>";;
                }
            }
            else {
                html += "<tr><td colspan='3'>暂无数据</td></tr>";;
            }
            $(parent.pTdProtocolList + ">tbody").html(html);

            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectProtocol();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='3'>暂无数据</td></tr>";
        $(parent.pTdProtocolList + ">tbody").html(html);
        console.error("ERROR - FTPController.selectProtocol() - Unable to get all events: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.audit.FTPController", FTPController);