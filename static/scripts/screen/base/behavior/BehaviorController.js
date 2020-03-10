function BehaviorController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.protocol = "";

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnOnOff = "#" + this.elementId + "_btnOnOff";
    this.pBtnFilter = "#" + this.elementId + "_btnFilter";
    this.pDivFilter = "#" + this.elementId + "_divFilter";
    this.pBtnSearch = "#" + this.elementId + "_btnSearch";
    this.pTdProtocolList = "#" + this.elementId + "_tdProtocolList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";

    this.pTxtIP = "#" + this.elementId + "_txtIP";
    this.pTxtMac = "#" + this.elementId + "_txtMac";
    this.pTxtPort = "#" + this.elementId + "_txtPort";
    this.pTxtStartDateTime = "#" + this.elementId + "_txtStartDateTime";
    this.pTxtEndDateTime = "#" + this.elementId + "_txtEndDateTime";

    this.pTxtSourceName = "#" + this.elementId + "_txtSName";
    this.pTxtDestinationName = "#" + this.elementId + "_txtDName";

    this.pTxtDIP = "#" + this.elementId + "_txtDIP";
    this.pTxtDMac = "#" + this.elementId + "_txtDMac";
    this.pTxtDPort = "#" + this.elementId + "_txtDPort";
    this.pDdlProtocol = "#" + this.elementId + "_ddlProtocol";

    this.pager = null;
    this.filter = {
        page: 1,
        srcIp: "",
        srcPort: "",
        srcMac: "",
        destIp: "",
        destPort: "",
        destMac: "",
        protocol: "",
        //timeDelta: "",
        sourceName: "",
        destinationName: "",
        starttime:"",
        endtime:""
    };

    this.protocolList = Constants.AUDIT_PROTOCOL_LIST[APPCONFIG.PRODUCT];
}

BehaviorController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
            Constants.TEMPLATES.BEHAVIOR_DIALOG],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - BehaviorController.init() - Unable to initialize: " + err.message);
    }
}

BehaviorController.prototype.initShell = function () {
    try {
        var parent = this;

        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.BEHAVIOR_LIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - BehaviorController.initShell() - Unable to initialize: " + err.message);
    }
}

BehaviorController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pDdlProtocol).empty();
        $(this.pDdlProtocol).append("<option value=''>所有协议</option>");
        $.each(this.protocolList, function () {
            $(parent.pDdlProtocol).append("<option value='" + this.key + "'>" + this.name + "</option>");
        });

        this.pViewHandle.find(this.pBtnFilter).on("click", function () {
            parent.pViewHandle.find(parent.pTxtSourceName).val("");
            parent.pViewHandle.find(parent.pTxtDestinationName).val("");
            parent.pViewHandle.find(parent.pTxtIP).val("");
            parent.pViewHandle.find(parent.pTxtPort).val("");
            parent.pViewHandle.find(parent.pTxtMac).val("");
            parent.pViewHandle.find(parent.pTxtDIP).val("");
            parent.pViewHandle.find(parent.pTxtDPort).val("");
            parent.pViewHandle.find(parent.pTxtDMac).val("");
            parent.pViewHandle.find(parent.pDdlProtocol).val("");
            //parent.pViewHandle.find(parent.pDdlTime).val("0");
            parent.pViewHandle.find(parent.pTxtStartDateTime).val("");
            parent.pViewHandle.find(parent.pTxtEndDateTime).val("");
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            parent.pViewHandle.find(parent.pDivFilter).toggle();
        });

        this.pViewHandle.find(this.pBtnRefresh).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.formatFilter();
            parent.selectProtocol();
        });

        this.pViewHandle.find(this.pBtnSearch).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.formatFilter();
            parent.selectProtocol();
        });
        this.pViewHandle.find(this.pBtnOnOff).on("change", function () {
            parent.setProtocolStatus();
        });
    }
    catch (err) {
        console.error("ERROR - BehaviorController.initControls() - Unable to initialize control: " + err.message);
    }
}

BehaviorController.prototype.load = function () {
    try {
        this.formatFilter();
        this.selectProtocol();
    }
    catch (err) {
        console.error("ERROR - BehaviorController.load() - Unable to load: " + err.message);
    }
}

BehaviorController.prototype.selectProtocol = function () {
    var html = "";
    var parent = this;
    var loadIndex = layer.load(2);
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_BEHAVIOR_LIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST",this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='9'>暂无数据</td></tr>";
            parent.pViewHandle.find(parent.pTdProtocolList + ">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        var ip = parent.formatIP(result.rows[i][6], result.rows[i][8], result.rows[i][14]);
                        var mac = parent.formatMAC(result.rows[i][3], result.rows[i][4], result.rows[i][14]);
                        var port = parent.formatPort(result.rows[i][7], result.rows[i][9], result.rows[i][14]);
                        var time = FormatterManager.formatToLocaleDateTime(result.rows[i][2], result.rows[i][14]);
                        var name = parent.formatDeviceName(result.rows[i][16], result.rows[i][17], result.rows[i][14]);
                        var protocolItem = $.grep(parent.protocolList, function (item) { return item.key == result.rows[i][13] });
                        html += "<tr>";
                        html += "<td>" + ((parent.filter.page - 1) * 10 + (i + 1)) + "</td>";
                        html += "<td>" + result.rows[i][1] + "</td>";
                        html += "<td>" + time + "</td>";
                        html += "<td>" + name + "</td>";
                        html += "<td>" + ip + "</td>";
                        html += "<td>" + mac.toUpperCase() + "</td>";
                        html += "<td>" + port + "</td>";
                        html += "<td>" + ((protocolItem.length==0)?result.rows[i][13]:protocolItem[0].name) + "</td>";
                        html += "<td><button class='btn btn-default btn-xs btn-color-details' data-key='" + result.rows[i][0] + "' ip='" + ip + "' mac='" + mac + "' port='" + port + "' protocol='" + result.rows[i][13] + "' time='" + time + "' name='"+name+"'><i class='fa fa-file-text-o'></i>详情</button></td>";
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

            parent.pViewHandle.find(parent.pTdProtocolList + ">tbody").html(html);
            layer.close(loadIndex);

            parent.pViewHandle.find(parent.pTdProtocolList).find("button").on("click", function () {
                //parent.pDetailController = null;
                var id = $(this).attr("data-key");
                var ip = $(this).attr("ip");
                var mac = $(this).attr("mac");
                var port = $(this).attr("port");
                var name = $(this).attr("name");
                var time = $(this).attr("time");
                var dialogHandler = $("<div />");
                var width = parent.pViewHandle.width() - 10 + "px";
                var height = $(window).height() - parent.pViewHandle.offset().top - document.body.scrollTop - 10 + "px";
                /*var dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.BEHAVIOR_DIALOG), {
                    elementId: parent.elementId + "_dialog"
                });*/
                layer.open({
                    type: 1,
                    title: "详细信息",
                    area: [width, height],
                    offset: ["82px", "200px"],
                    shade: [0.5, '#393D49'],
                    content: dialogHandler.html(),
                    success: function (layero, index) {
                        parent.pDetailController = new tdhx.base.behavior.S7BehaviorController(parent,layero, parent.elementId + "_dialog", id, ip, mac, time, name,port);
                        parent.pDetailController.init();
                        $(window).on("resize", function () {
                            var pwidth = parent.pViewHandle.width() - 10;
                            var pheight = $(window).height() - parent.pViewHandle.offset().top - 10;
                            layero.width(pwidth);
                            layero.height(pheight);
                        })
                    }
                });
            });
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
        html += "<tr><td colspan='9'>暂无数据</td></tr>";
        this.pViewHandle.find(this.pTdProtocolList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - BehaviorController.selectProtocol() - Unable to get all events: " + err.message);
    }
}
BehaviorController.prototype.formatIP = function (sourcIP, destionIP, direction) {
    var result = "";
    if (typeof (sourcIP) != "undefined" && sourcIP != "" && sourcIP.toUpperCase() != "NULL") {
        result += sourcIP;
    }
    if (typeof (sourcIP) != "undefined" && sourcIP != "" && sourcIP.toUpperCase() != "NULL"
        && typeof (destionIP) != "undefined" && destionIP != "" && destionIP.toUpperCase() != "NULL") {
        if (direction == 1) {
            result += "--->";
        }
        else {
            result += "<--->";
        }
    }
    if (typeof (destionIP) != "undefined" && destionIP != "" && destionIP.toUpperCase() != "NULL") {
        result += destionIP;
    }

    return result;
}

BehaviorController.prototype.formatMAC = function (sourcMAC, destionMAC, direction) {
    var result = "";
    if (typeof (sourcMAC) != "undefined" && sourcMAC != "" && sourcMAC.toUpperCase() != "NULL") {
        result += sourcMAC;
    }
    if (typeof (sourcMAC) != "undefined" && sourcMAC != "" && sourcMAC.toUpperCase() != "NULL"
        && typeof (destionMAC) != "undefined" && destionMAC != "" && destionMAC.toUpperCase() != "NULL") {
        if (direction == 1) {
            result += "--->";
        }
        else {
            result += "<--->";
        }
    }
    if (typeof (destionMAC) != "undefined" && destionMAC != "" && destionMAC.toUpperCase() != "NULL") {
        result += destionMAC;
    }

    return result;
}

BehaviorController.prototype.formatPort = function (sourcePort, destionPort, direction) {
    var result = "";
    if (typeof (sourcePort) != "undefined" && sourcePort != "") {
        result += sourcePort;
    }
    if (typeof (sourcePort) != "undefined" && sourcePort != ""
        && typeof (destionPort) != "undefined" && destionPort != "") {
        if (direction == 1) {
            result += "--->";
        }
        else {
            result += "<--->";
        }
    }
    if (typeof (destionPort) != "undefined" && destionPort != "") {
        result += destionPort;
    }

    return result;
}

BehaviorController.prototype.formatDeviceName = function (sourceName, destionName, direction) {
    var result = "";
    if (typeof (sourceName) != "undefined" && sourceName != "") {
        result += sourceName;
    }
    if (typeof (sourceName) != "undefined" && sourceName != ""
        && typeof (destionName) != "undefined" && destionName != "") {
        if (direction == 1) {
            result += "--->";
        }
        else {
            result += "<--->";
        }
    }
    if (typeof (destionName) != "undefined" && destionName != "") {
        result += destionName;
    }

    return result;
}

BehaviorController.prototype.formatFilter = function () {
    try {
        this.filter.srcIp = $.trim(this.pViewHandle.find(this.pTxtIP).val());
        this.filter.srcPort = $.trim(this.pViewHandle.find(this.pTxtPort).val());
        this.filter.srcMac = $.trim(this.pViewHandle.find(this.pTxtMac).val());
        this.filter.destIp = $.trim(this.pViewHandle.find(this.pTxtDIP).val());
        this.filter.destPort = $.trim(this.pViewHandle.find(this.pTxtDPort).val());
        this.filter.destMac = $.trim(this.pViewHandle.find(this.pTxtDMac).val());
        this.filter.protocol = $.trim(this.pViewHandle.find(this.pDdlProtocol + " option:selected").val());
        //this.filter.timeDelta = $.trim(this.pViewHandle.find(this.pDdlTime + " option:selected").val());
        this.filter.starttime = $.trim(this.pViewHandle.find(this.pTxtStartDateTime).val());
        this.filter.endtime = $.trim(this.pViewHandle.find(this.pTxtEndDateTime).val());
        this.filter.sourceName = $.trim(this.pViewHandle.find(this.pTxtSourceName).val());
        this.filter.destinationName = $.trim(this.pViewHandle.find(this.pTxtDestinationName).val());
    }
    catch (err) {
        console.error("ERROR - BehaviorController.formatFilter() - Unable to get filter for searching: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.behavior.BehaviorController", BehaviorController);
