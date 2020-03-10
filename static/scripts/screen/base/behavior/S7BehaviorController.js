function S7BehaviorController(controller, viewHandle, elementId, id, ip, mac, time, name,port) {
    this.controller = controller;
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.id = id;
    this.ip = ip;
    this.mac = mac;
    this.time = time;
    this.name=name;
    this.port=port;

    this.pLblName = "#" + this.elementId + "_lblName";
    this.pLblTime = "#" + this.elementId + "_lblTime";
    this.pLblPort = "#" + this.elementId + "_lblPort";
    this.pLblIP = "#" + this.elementId + "_lblIP";
    this.pLblMAC = "#" + this.elementId + "_lblMAC";
    this.pTxtStartDateTimeD = "#" + this.elementId + "_txtStartDateTime";
    this.pTxtEndDateTimeD = "#" + this.elementId + "_txtEndDateTime";
    this.pTxtTypeD = "#" + this.elementId + "_txtType";
    this.pTdListDetail = "#" + this.elementId + "_tdProtocolList";
    this.pBtnRefreshD = "#" + this.elementId + "_btnRefresh";
    this.pBtnFilterD = "#" + this.elementId + "_btnFilter";
    this.pDivFilterD = "#" + this.elementId + "_divFilter";
    this.pBtnSearchD = "#" + this.elementId + "_btnSearch";
    this.pagerContent = "#" + this.elementId + "_pagerContent";

    this.pager = null;
    this.filter = {
        page: 1,
        flowdataHeadId:id,
        type: "",
        starttime:"",
        endtime:""
    };
}

S7BehaviorController.prototype.init = function () {
    try {
        var parent = this;

        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.BEHAVIOR_DIALOG), {
            elementId: parent.elementId
        });
        this.pViewHandle.find(".layui-layer-content").html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - S7BehaviorController.init() - Unable to initialize: " + err.message);
    }
}

S7BehaviorController.prototype.initControls = function () {
    try {
        var parent=this;
        /*$(parent.pBtnRefreshD).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.selectBehaviorDetail();
        });
        $(parent.pBtnFilterD).on("click", function () {
            $(parent.pTxtTypeD).val("");
            $(parent.pTxtStartDateTimeD).val("");
            $(parent.pTxtEndDateTimeD).val("");
            $(parent.pBtnFilterD).toggleClass("active");
            $(parent.pDivFilterD).toggle();
        });*/
        $(parent.pBtnSearchD).on("click", function () {
            parent.pager = null;
            parent.filter.page = 1;
            parent.filter.starttime = $.trim($(parent.pTxtStartDateTimeD).val());
            parent.filter.endtime = $.trim($(parent.pTxtEndDateTimeD).val());
            parent.filter.type = $.trim($(parent.pTxtTypeD).val());
            parent.selectBehaviorDetail();
        });
    }
    catch (err) {
        console.error("ERROR - S7BehaviorController.initControls() - Unable to initialize control: " + err.message);
    }
}

S7BehaviorController.prototype.load = function () {
    try {
        //details
        var parent = this;
        $(parent.pLblIP).html(this.ip);
        $(parent.pLblMAC).html(this.mac);
        $(parent.pLblPort).html(this.port);
        $(parent.pLblTime).html(this.time);
        $(parent.pLblName).html(this.name);
        parent.selectBehaviorDetail();
    }
    catch (err) {
        console.error("ERROR - S7BehaviorController.load() - Unable to load: " + err.message);
    }
}
S7BehaviorController.prototype.selectBehaviorDetail = function () {
    var html = "";
    var parent = this;
    try {
        var detaillink = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_BEHAVIOR_DIALOG_LIST;
        var detailpromise = URLManager.getInstance().ajaxCall(detaillink,this.filter);
        detailpromise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='3'>暂无数据</td></tr>";
            $(parent.pTdListDetail+">tbody").html(html);
        });
        detailpromise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td style='width:20%;'>" + result.rows[i][5] + "</td>";
                        html += "<td style='width:20%;'>" + result.rows[i][2] + "</td>";
                        html += "<td style='text-align:left;'>" + result.rows[i][3] + "</td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='3'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='3'>暂无数据</td></tr>";
            }
            $(parent.pTdListDetail + ">tbody").html(html);
            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController($(parent.pagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectBehaviorDetail();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
            console.log();
        });
    }
    catch (err) {
        html += "<tr><td colspan='3'>暂无数据</td></tr>";
        $(parent.pTdListDetail + ">tbody").html(html);
        console.error("ERROR - S7BehaviorController.selectBehaviorDetail() - Unable to get all events: " + err.message);
    }
}
/*S7BehaviorController.prototype.selectProtocol = function () {
    var html = "";
    var parent = this;
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_PROTOCOL;
        var promise = URLManager.getInstance().ajaxCall(link,this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='2'>暂无数据</td></tr>";
            $(parent.pTdProtocolList + ">tbody").html(html);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td style='width:20%;'>" + result.rows[i][(result.rows[i].length-6)] + "</td>";
                        html += "<td style='text-align:left;'>" + result.rows[i][2] + "</td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='2'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='2'>暂无数据</td></tr>";
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
        html += "<tr><td colspan='2'>暂无数据</td></tr>";
        $(parent.pTdProtocolList + ">tbody").html(html);
        console.error("ERROR - S7BehaviorController.selectProtocol() - Unable to get all events: " + err.message);
    }
}*/

ContentFactory.assignToPackage("tdhx.base.behavior.S7BehaviorController", S7BehaviorController);