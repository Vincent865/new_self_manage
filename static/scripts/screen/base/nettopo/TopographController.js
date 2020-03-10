/**
 * Created by 刘写辉 on 2018/11/12.
 */
function TopographController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;
    this.isRebootSuccess = true;
    this.isResetSuccess = true;
    this.pRulePagerContent = '#ruleList_pagerContent';
    this.pEvtPagerContent = '#evtList_pagerContent';
    this.pHisflowPagerContent = '#hisflowList_pagerContent';
    this.pCurflowPagerContent = '#curflowList_pagerContent';
    this.pAuditPagerContent = '#auditList_pagerContent';
    this.ruleListId = '_rule';
    this.evtListId = '_event';
    this.hisflowListId = '_hisflow';
    this.curflowListId = '_curflow';
    this.auditListId = '_audit';
    this.pDivFilter = "#" +this.elementId + '_dialog_divFilter';
    this.pBtnFilter = "#" +this.elementId + '_dialog_btnFilter';
    this.pDdlTime2 = "#" + this.elementId + "_dialog_ddlTime2";
    this.pDivPieChart = this.elementId + "_dialog_divPieChart";
    this.pTdFlowList = "#" + this.elementId + "_dialog_tdFlowList";
    this.pDivLineChart = this.elementId + "_dialog_divLineChart";
    this.pCusDivLineChart = this.elementId + "_dialog_cusDivLineChart";
    this.detailProtoList = Constants.AUDIT_PROTOCOL_LIST[APPCONFIG.PRODUCT];
    this.protocolList = Constants.WHITELIST_PROTOCOL_LIST[APPCONFIG.PRODUCT];
    this.pSelectAll='#'+elementId+'_dialog_selectAll';
    this.pIntoBtns= "#" + this.elementId + "_dialog_intobtns";
    this.pIntopoBtn = "#" + this.elementId + "_intopo";
    this.pDeviceList = "#" + this.elementId + "_dialog_tdDeviceList";
    this.pProtodlg='#'+this.elementId+'_dialog_intopo_dialog';
    this.preDelId=[];
    this.color = ['#3994d3', '#f98665', '#fac767', '#28daca', '#9569f9', '#e36585'];
    this.pDeviceController = controller;
    this.filter = {
        ip: '',
        mac: '',
        name: '',
        type: '',
        is_topo: 0,
        unknown:'',
        vender: ''
    };
}

TopographController.prototype.init = function () {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.TOPO_INTOTOPO,
                Constants.TEMPLATES.TOPO_TOPODETAIL],
            function (templateResults) {
                parent.initShell();
            }
        );
    }
    catch (err) {
        console.error("ERROR - ReportAuditController.init() - Unable to initialize all templates: " + err.message);
    }
}

TopographController.prototype.initShell = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.TOPO_TOPOGRAPH), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - ReportAuditController.initShell() - Unable to initialize: " + err.message);
    }
}


TopographController.prototype.initControls = function () {
    try {
        var parent = this;
        var devlink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_TYPE,devpromise;
        devpromise=URLManager.getInstance().ajaxCallByURL(devlink,'GET');
        devpromise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert('获取设备类型失败',{icon:5});
            layer.close(loadIndex);
        });
        devpromise.done(function (result) {
            if (result.data){
                for(var i=0;i<result.data.length;i++){
                    $("#txtDeviceType").append("<option value="+result.data[i].id+">"+result.data[i].name+"</option>")
                }
                $('#txtDeviceType').val('');
                $('#txtAccessStatus').val('');
            }else{
                layer.alert('获取设备类型失败',{icon:5});
            }
        });
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

TopographController.prototype.graphDetail = function (pcell) {
    try {
        var sourceparent=this,dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.TOPO_TOPODETAIL), {
            elementId: sourceparent.elementId + "_dialog"
        });
        var loadIdx=layer.load(2,{shade:[0.4, '#fff']}),dev_id=0;sourceparent.rulepage=1;sourceparent.evtpage=1;sourceparent.auditpage=1;sourceparent.flowpage=1;
        delete sourceparent.pRulelistPager;
        delete sourceparent.pEventlistPager;
        delete sourceparent.pHisflowListPager;
        delete sourceparent.pAuditlistPager;
        var width = sourceparent.pViewHandle.width() - 10 + "px";
        var link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_RELA_DEVS,promise;
        var rulelink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_RULE_DETAIL,rulepromise;
        var evtlink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_TOPEVENT_DETAIL,evtpromise;
        var auditlink1=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_TOPAUDIT1_DETAIL,auditpromise1;
        var auditlink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_TOPAUDIT_DETAIL,auditpromise;
        var switchlink = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_SWITCH_MAC_INFO,switchpromise;
        var height = $(window).height() - sourceparent.pViewHandle.offset().top - $(window).height()/10 + "px";
        var tmplay = layer.open({
            type: 1,
            title: '详情信息',
            area: [parseInt(width)+'px',$(window).height()*0.85+'px'],
            //offset: ["82px", "200px"],
            shade: [0.5, '#393D49'],
            content: dialogTemplate,
            success: function (layero, index) {
                var perentNode='#topo_detail',tags=$(perentNode+" .row-cutbox>ul>li");
                $(tags).each(function(i,d){
                    tags.eq(i).click(function(){
                        tags.removeClass('active');
                        $(this).addClass('active');
                        $(perentNode+" .row-cutcontent").css({display:'none'});
                        $(perentNode+" .row-cutcontent").eq(i).css({display:'block'});
                    })
                });
                var requestId = 0;
                var loadIndex = layer.load(2),allAsset=[];
                promise = URLManager.getInstance().ajaxCallByURL(link,"GET",{ip:pcell.device_info.ip_addr,mac:pcell.device_info.mac_addr,num:10});
                promise.fail(function (jqXHR, textStatus, err) {
                    console.log(textStatus + " - " + err.message);
                    layer.close(loadIndex);
                });
                promise.done(function (result) {
                    //获取交换机信息
                    var switchList='';
                    switchpromise = URLManager.getInstance().ajaxCallByURL(switchlink,"POST", {mac:pcell.device_info.mac_addr});
                    switchpromise.done(function (swlist) {
                        for (var i = 0; i < swlist.rows.length; i++) {
                            switchList += swlist.rows[i][0] + " # ";
                            switchList += swlist.rows[i][2] + " # ";
                            switchList += swlist.rows[i][1];
                            if(i!=swlist.rows.length-1){
                                switchList += ";<br>";
                            }
                        }
                        if(swlist.num==0) switchList += "无";
                        if (result.rows) {
                            dev_id=result.dev_id;
                            layer.close(loadIndex);
                            main($(perentNode+" .row-cutcontent").eq(0).children()[0]);
                            function main(container)
                            {
                                // Checks if browser is supported
                                if (!mxClient.isBrowserSupported())
                                {
                                    // Displays an error message if the browser is
                                    // not supported.
                                    mxUtils.error('Browser is not supported!', 200, false);
                                }
                                else
                                {
                                    // Speedup the animation
                                    //mxText.prototype.enableBoundingBox = false;

                                    // Creates the graph inside the given container
                                    var graph = new mxGraph(container);

                                    // Disables all built-in interactions
                                    graph.setEnabled(false);
                                    graph.setCellsResizable(false);

                                    // Handles clicks on cells
                                    /*graph.addListener(mxEvent.CLICK, function(sender, evt)
                                     {
                                     var cell = evt.getProperty('cell');

                                     if (cell != null)
                                     {
                                     load(graph, cell);
                                     }
                                     });*/

                                    // Changes the default vertex style in-place
                                    /*var style = graph.getStylesheet().getDefaultVertexStyle();
                                     style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_ELLIPSE;
                                     style[mxConstants.STYLE_PERIMETER] = mxPerimeter.EllipsePerimeter;
                                     style[mxConstants.STYLE_GRADIENTCOLOR] = 'white';*/
                                    var style = new Object();
                                    style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_IMAGE;
                                    style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_LABEL;
                                    style[mxConstants.STYLE_PERIMETER] = mxPerimeter.RectanglePerimeter;
                                    style[mxConstants.STYLE_VERTICAL_ALIGN] = mxConstants.ALIGN_TOP;
                                    style[mxConstants.STYLE_ROUNDED] = true;
                                    style[mxConstants.STYLE_ARCSIZE] = 10;
                                    style[mxConstants.STYLE_IMAGE_VERTICAL_ALIGN] = mxConstants.ALIGN_MIDDLE;
                                    style[mxConstants.STYLE_IMAGE_ALIGN] = mxConstants.ALIGN_CENTER;
                                    style[mxConstants.STYLE_FONTSIZE] = 12;
                                    style[mxConstants.STYLE_FONTCOLOR] = '#000000';
                                    style[mxConstants.STYLE_FILLCOLOR] = 'rgba(255,255,255,0)';
                                    //style[mxConstants.STYLE_FILL_OPACITY] = 0;
                                    style[mxConstants.STYLE_STROKEWIDTH] =1;
                                    style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
                                    style[mxConstants.STYLE_IMAGE_WIDTH] = '85';
                                    style[mxConstants.STYLE_IMAGE_HEIGHT] ='110';
                                    style[mxConstants.STYLE_SPACING_TOP] = '88';
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/unknown.png';
                                    graph.getStylesheet().putCellStyle('unknown', style);

                                    style = mxUtils.clone(style);
                                    /*delete style[mxConstants.STYLE_IMAGE_VERTICAL_ALIGN];
                                     style[mxConstants.STYLE_IMAGE_VERTICAL_ALIGN] = mxConstants.ALIGN_BOTTOM;
                                     style[mxConstants.STYLE_FILLCOLOR] = 'green';
                                     style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/server.png';
                                     style[mxConstants.STYLE_IMAGE_ALIGN] = mxConstants.ALIGN_RIGHT;
                                     delete style[mxConstants.STYLE_SPACING_TOP];*/
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/RTU.png';
                                    graph.getStylesheet().putCellStyle('RTU', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/engineer.png';
                                    graph.getStylesheet().putCellStyle('engineer', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/hmi.png';
                                    graph.getStylesheet().putCellStyle('hmi', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/operater.png';
                                    graph.getStylesheet().putCellStyle('operater', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/pc.png';
                                    graph.getStylesheet().putCellStyle('pc', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/plc.png';
                                    graph.getStylesheet().putCellStyle('plc', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/netdevice.png';
                                    graph.getStylesheet().putCellStyle('netdevice', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/dcs.png';
                                    graph.getStylesheet().putCellStyle('dcs', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/server.png';
                                    graph.getStylesheet().putCellStyle('server', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/opcser.png';
                                    graph.getStylesheet().putCellStyle('opcser', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/secdev.png';
                                    graph.getStylesheet().putCellStyle('secdev', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/IED.png';
                                    graph.getStylesheet().putCellStyle('ied', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/cusdev.png';
                                    graph.getStylesheet().putCellStyle('cusdev', style);
                                    style = mxUtils.clone(style);
                                    style[mxConstants.STYLE_IMAGE_WIDTH] = '241';
                                    style[mxConstants.STYLE_IMAGE_HEIGHT] ='15';
                                    style[mxConstants.STYLE_SPACING_TOP] = '0';
                                    style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/devicegroup.png';
                                    graph.getStylesheet().putCellStyle('netgroup', style);

                                    var style1 = graph.getStylesheet().getDefaultEdgeStyle();
                                    style1[mxConstants.STYLE_ROUNDED] = true;
                                    //style1[mxConstants.STYLE_EDGE] = 'orthogonalEdgeStyle';
                                    style1[mxConstants.STYLE_STROKEWIDTH] = 2;
                                    style1[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
                                    style1[mxConstants.STYLE_ENDARROW]=mxConstants.ARROW_OVAL;
                                    style1[mxConstants.STYLE_STARTARROW]=mxConstants.ARROW_OVAL;
                                    graph.alternateEdgeStyle = 'elbow=vertical';
                                    style1[mxConstants.STYLE_CURVED] = '0';

                                    var edge='perimeterSpacing=4;strokeWidth=4;labelBackgroundColor=white;fontStyle=1';

                                    // Gets the default parent for inserting new cells. This
                                    // is normally the first child of the root (ie. layer 0).
                                    var parent = graph.getDefaultParent();

                                    var cx = graph.container.clientWidth / 5;
                                    var cy = graph.container.clientHeight / 2;

                                    switch(pcell.device_info.type_name){
                                        case '未知':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'unknown');
                                            break;
                                        case 'PC':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'pc');
                                            break;
                                        case '工程师站':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'engineer');
                                            break;
                                        case '操作员站':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'operater');
                                            break;
                                        case 'PLC':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'plc');
                                            break;
                                        case 'RTU':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'RTU');
                                            break;
                                        case 'HMI':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'hmi');
                                            break;
                                        case '网络设备':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'netdevice');
                                            break;
                                        case '服务器':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'server');
                                            break;
                                        case 'OPC服务器':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'opcser');
                                            break;
                                        case 'DCS':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'dcs');
                                            break;
                                        case '安全设备':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'secdev');
                                            break;
                                        case 'IED':
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'ied');
                                            break;
                                        default:
                                            var cell = graph.insertVertex(parent,pcell.id, pcell.value, cx - 20, cy - 15, 110, 110,'cusdev');
                                            break;
                                    }
                                    cell.dataInfo=pcell.device_info;
                                    cell.dataInfo.dev_name=pcell.value;
                                    // Animates the changes in the graph model
                                    /*graph.getModel().addListener(mxEvent.CHANGE, function(sender, evt)
                                     {
                                     var changes = evt.getProperty('edit').changes;
                                     mxEffects.animateChanges(graph, changes);
                                     });*/
                                    graph.isPart = function(cell)
                                    {
                                        var state = this.view.getState(cell);
                                        var style = (state != null) ? state.style : this.getCellStyle(cell);

                                        return style['constituent'] == '1';
                                    };
                                    load(graph, cell,pcell);
                                }
                            };

                            // Loads the links for the given cell into the given graph
                            // by requesting the respective data in the server-side
                            // (implemented for this demo using the server-function)
                            function load(graph, cell,pcell)
                            {
                                if (graph.getModel().isVertex(cell))
                                {
                                    var cx = graph.container.clientWidth / 2;
                                    var cy = graph.container.clientHeight / 2;

                                    // Gets the default parent for inserting new cells. This
                                    // is normally the first child of the root (ie. layer 0).
                                    var parent = graph.getDefaultParent();

                                    // Adds cells to the model in a single step
                                    graph.getModel().beginUpdate();
                                    try
                                    {
                                        var xml = server(cell.id);
                                        var doc = mxUtils.parseXml(xml);
                                        var dec = new mxCodec(doc);
                                        var model = dec.decode(doc.documentElement);

                                        // Removes all cells which are not in the response
                                        for (var key in graph.getModel().cells)
                                        {
                                            var tmp = graph.getModel().getCell(key);

                                            if (tmp != cell &&
                                                graph.getModel().isVertex(tmp))
                                            {
                                                graph.removeCells([tmp]);
                                            }
                                        }

                                        // Merges the response model with the client model
                                        graph.getModel().mergeChildren(model.getRoot().getChildAt(0), parent);

                                        // Moves the given cell to the center
                                        var geo = graph.getModel().getGeometry(cell);

                                        if (geo != null)
                                        {
                                            geo = geo.clone();
                                            geo.x = cx - geo.width / 2;
                                            geo.y = cy - geo.height / 2;

                                            graph.getModel().setGeometry(cell, geo);
                                        }

                                        // Creates a list of the new vertices, if there is more
                                        // than the center vertex which might have existed
                                        // previously, then this needs to be changed to analyze
                                        // the target model before calling mergeChildren above
                                        var vertices = [];

                                        for (var key in graph.getModel().cells)
                                        {
                                            var tmp = graph.getModel().getCell(key);

                                            if (tmp != cell && model.isVertex(tmp))
                                            {
                                                vertices.push(tmp);

                                                // Changes the initial location "in-place"
                                                // to get a nice animation effect from the
                                                // center to the radius of the circle
                                                var geo = model.getGeometry(tmp);

                                                if (geo != null)
                                                {
                                                    geo.x = cx - geo.width / 2;
                                                    geo.y = cy - geo.height / 2;
                                                }
                                            }
                                        }
                                        console.log(switchList)
                                        var spans=$('.topostatus>ul li>span:last-child');
                                        spans.eq(0).text(pcell.value);
                                        spans.eq(1).text(pcell.device_info.ip_addr);
                                        spans.eq(2).text(pcell.device_info.mac_addr);
                                        spans.eq(3).attr({title:pcell.device_info.type_name}).text(pcell.device_info.type_name);
                                        spans.eq(4).text(pcell.device_info.mode);
                                        spans.eq(5).text(pcell.device_info.unknown?'非法接入':'正常接入');
                                        spans.eq(6).text(pcell.device_info.vender_info);
                                        spans.eq(7).html(switchList);
                                        spans.eq(8).text(pcell.device_info.desc);
                                        graph.addMouseListener(
                                            {
                                                currentState: null,
                                                currentIconSet: null,
                                                mouseDown: function(sender, me)
                                                {
                                                    // Hides icons on mouse down
                                                    if (me.state.cell&&me.state.cell.dataInfo)
                                                    {
                                                        var infos=me.state.cell.dataInfo;
                                                        spans.eq(0).text(infos.dev_name);
                                                        spans.eq(1).text(infos.ip_addr);
                                                        spans.eq(2).text(infos.mac_addr);
                                                        spans.eq(3).attr({title:pcell.device_info.type_name}).text(infos.type_name);
                                                        spans.eq(4).text(infos.mode);
                                                        spans.eq(5).text(infos.unknown?'非法接入':'正常接入');
                                                        spans.eq(6).text(infos.vender_info);
                                                        spans.eq(7).text(infos.desc);
                                                        //this.dragLeave(me.getEvent(), this.currentState);
                                                        //var cell=this.currentState.cell;
                                                        this.currentState = null;
                                                    }
                                                },
                                                mouseMove: function(sender, me)
                                                {

                                                },
                                                mouseUp: function(sender, me) { },
                                                dragEnter: function(evt, state)
                                                {
                                                    if (this.currentIconSet == null)
                                                    {
                                                        //this.currentIconSet = new mxIconSet(state);

                                                        //graph.getTooltipForCell(state);
                                                    }
                                                },
                                                dragLeave: function(evt, state)
                                                {
                                                    if (this.currentIconSet != null)
                                                    {
                                                        this.currentIconSet.destroy();
                                                        this.currentIconSet = null;
                                                    }
                                                }
                                            });


                                        // Arranges the response in a circle
                                        var cellCount = vertices.length;
                                        var phi = 2 * Math.PI / cellCount;
                                        var r = Math.min(graph.container.clientWidth / 2.5,
                                            graph.container.clientHeight / 2.5);

                                        for (var i = 0; i < cellCount; i++)
                                        {
                                            var geo = graph.getModel().getGeometry(vertices[i]);

                                            if (geo != null)
                                            {
                                                geo = geo.clone();
                                                geo.x += r * Math.sin(i * phi);
                                                geo.y += r * Math.cos(i * phi);

                                                graph.getModel().setGeometry(vertices[i], geo);
                                            }
                                        }
                                    }
                                    finally
                                    {
                                        // Updates the display
                                        graph.getModel().endUpdate();
                                    }
                                }
                            };

                            // Simulates the existence of a server that can crawl the
                            // big graph with a certain depth and create a graph model
                            // for the traversed cells, which is then sent to the client
                            function server(cellId)
                            {
                                // Increments the request ID as a prefix for the cell IDs
                                requestId++;

                                // Creates a local graph with no display
                                var graph = new mxGraph();

                                // Gets the default parent for inserting new cells. This
                                // is normally the first child of the root (ie. layer 0).
                                var parent = graph.getDefaultParent();

                                // Adds cells to the model in a single step
                                graph.getModel().beginUpdate();
                                try
                                {
                                    var v0 = graph.insertVertex(parent, cellId, 'Dummy', 0, 0, 110, 110);
                                    var cellCount = result.rows;//parseInt(Math.random() * 16) + 4;

                                    // Creates the random links and cells for the response
                                    for (var i = 0; i < cellCount.length; i++)
                                    {
                                        switch(cellCount[i].type_name){
                                            case '未知':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'unknown');
                                                break;
                                            case 'PC':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'pc');
                                                break;
                                            case '工程师站':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'engineer');
                                                break;
                                            case '操作员站':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'operater');
                                                break;
                                            case 'PLC':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'plc');
                                                break;
                                            case 'RTU':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'RTU');
                                                break;
                                            case 'HMI':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'hmi');
                                                break;
                                            case '网络设备':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'netdevice');
                                                break;
                                            case '服务器':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'server');
                                                break;
                                            case 'OPC服务器':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'opcser');
                                                break;
                                            case 'DCS':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'dcs');
                                                break;
                                            case 'IED':
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'ied');
                                                break;
                                            default:
                                                var v = graph.insertVertex(parent, null, cellCount[i].dev_name, 0, 0, 110, 110,'cusdev');
                                                break;
                                        }
                                        v.dataInfo=cellCount[i];
                                        var e = graph.insertEdge(parent, null, ' ', v0, v);
                                    }
                                }
                                finally
                                {
                                    // Updates the display
                                    graph.getModel().endUpdate();
                                }

                                var enc = new mxCodec();
                                var node = enc.encode(graph.getModel());

                                return mxUtils.getXml(node);
                            };
                            sourceparent.getCurflowList();
                            sourceparent.getHisflowList();
                        }
                    })

                });

                sourceparent.getRuleList=function(){
                    var html = "";
                    rulepromise = URLManager.getInstance().ajaxCallByURL(rulelink,"GET",{ip:pcell.device_info.ip_addr,mac:pcell.device_info.mac_addr,page:sourceparent.rulepage});
                    rulepromise.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                        html += "<tr><td colspan='9'>暂无数据</td></tr>";
                        $(perentNode+" .row-cutcontent").eq(1).find("tbody").html(html);
                    });
                    rulepromise.done(function (result) {
                        if (result.rows) {
                            for (var i = 0; i < result.rows.length; i++) {
                                html += "<tr>";
                                html += "<td style='width:5%'>" + ((sourceparent.rulepage - 1) * 10 + i + 1) + "</td>";
                                html += "<td style='width:20%'>" + result.rows[i][0] + "</td>";
                                html += "<td>" + result.rows[i][1] + "</td>";
                                // html += "<td style='width:10%'>" + sourceparent.formatEventType(result.rows[i][2]) + "</td>";
                                html += "<td style='width:10%'>" + sourceparent.protocolList[result.rows[i][3]] + "</td>";
                                //html += "<td>" + result.rows[i][4] + "</td>";
                                //html += "<td style='width:200px'>" + (result.device_list[i]['desc']?result.device_list[i]['desc']:'') + "</td>";
                                html += "</tr>";
                            }
                        }
                        else {
                            html += "<tr><td colspan='9'>暂无数据</td></tr>";
                        }
                        $(perentNode+" .row-cutcontent").eq(1).find("tbody").html(html);
                        if (sourceparent.pRulelistPager == null && result.rows.length >= 0) {
                            sourceparent.pRulelistPager = new tdhx.base.utility.PagerController($(sourceparent.pRulePagerContent), sourceparent.ruleListId, 10, result.total, function (pageIndex) {
                                sourceparent.rulepage = pageIndex;
                                sourceparent.getRuleList();
                            });
                            sourceparent.pRulelistPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
                        }
                    });
                };
                sourceparent.getRuleList();

                sourceparent.getEvtList=function(){
                    var html = "";
                    evtpromise = URLManager.getInstance().ajaxCallByURL(evtlink,"GET",{ip:pcell.device_info.ip_addr,mac:pcell.device_info.mac_addr,page:sourceparent.evtpage});
                    evtpromise.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                        html += "<tr><td colspan='9'>暂无数据</td></tr>";
                        $(perentNode+" .row-cutcontent").eq(2).find("tbody").html(html);
                    });
                    evtpromise.done(function (result) {
                        if (result.rows) {
                            for (var i = 0; i < result.rows.length; i++) {
                                html += "<tr>";
                                html += "<td>" + FormatterManager.formatDateTime(Number(result.rows[i][3])*1000,'yyyy-MM-dd HH:mm:ss') + "</td>";
                                html += "<td>" + result.rows[i][13] + "</td>";
                                html += "<td>" + result.rows[i][14] + "</td>";
                                html += "<td>" + result.rows[i][0] + "</td>";
                                html += "<td>" + (result.rows[i][1]?result.rows[i][1]:'NA') + "</td>";
                                html += "<td>" + (isNaN(result.rows[i][2])?'NA':sourceparent.protocolList[result.rows[i][2]])+ "</td>";
                                html += "<td>" + sourceparent.formatEventType(result.rows[i][4]) + "</td>";
                                html += "<td>" + sourceparent.formatEventSource(Number(result.rows[i][7])) + "</td>";
                                html += "</tr>";
                            }
                        }
                        else {
                            html += "<tr><td colspan='9'>暂无数据</td></tr>";
                        }
                        $(perentNode+" .row-cutcontent").eq(2).find("tbody").html(html);
                        if (sourceparent.pEventlistPager == null && result.rows.length >= 0) {
                            sourceparent.pEventlistPager = new tdhx.base.utility.PagerController($(sourceparent.pEvtPagerContent), sourceparent.evtListId, 10, result.total, function (pageIndex) {
                                sourceparent.evtpage = pageIndex;
                                sourceparent.getEvtList();
                            });
                            sourceparent.pEventlistPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
                        }
                    });
                };
                sourceparent.getEvtList();

                sourceparent.getHisflowList=function(){
                    sourceparent.selectDeviceProtocol = function (pageIndex) {
                        var html = "";
                        html += '<thead>';
                        html += '<tr><th>协议名</th><th style="width:40%;">平均流量百分比(一周)</th><th style="width:20%;">更新时间</th></tr>';
                        html += '</thead>';
                        try {
                            var loadIndex = layer.load(2);
                            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_FLOW_LIST;
                            var data = {page:pageIndex,ip:pcell.device_info.ip_addr,deviceId:dev_id};
                            var promise = URLManager.getInstance().ajaxCall(link, data);
                            promise.fail(function (jqXHR, textStatus, err) {
                                console.log(textStatus + " - " + err.message);
                                html += "<tr><td colspan='3'>暂无数据</td></tr>";
                                $(sourceparent.pTdFlowList).html(html);
                                layer.close(loadIndex);
                            });
                            promise.done(function (result) {
                                if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                                    if (result.rows.length) {
                                        //result={"page": 1, "rows": [["OPCDA", 0.5782, "2018-12-11 10:00:00"], ["S7", 0.1651, "2018-12-11 10:00:00"], ["\u7f51\u7edc\u901a\u7528\u534f\u8bae", 0.0935, "2018-12-11 10:00:00"], ["MMS", 0.0865, "2018-12-11 10:00:00"], ["IEC104", 0.044, "2018-12-11 10:00:00"], ["DNP3", 0.0197, "2018-12-11 10:00:00"], ["Modbus-TCP", 0.0079, "2018-12-11 10:00:00"], ["PROFINET-IO", 0.005, "2018-12-11 10:00:00"]], "total": 8};
                                        for (var i = 0; i < result.rows.length; i++) {
                                            html += "<tbody><tr>";
                                            html += "<td style='text-align:center;padding-left:5px;'>" + result.rows[i][0] + "</td>";
                                            html += "<td style='width:40%;text-align:center;'>" + (result.rows[i][1] * 100).toFixed(2) + "%</td>";
                                            html += "<td style='width:20%;'>" + result.rows[i][2] + "</td>";
                                            html += "</tr></tbody>";
                                        }
                                    }
                                    else {
                                        html += "<tr><td colspan='3'>暂无数据</td></tr>";
                                    }
                                }
                                else {
                                    html += "<tr><td colspan='3'>暂无数据</td></tr>";
                                }
                                if (typeof (result.total) != "undefined") {
                                    $(sourceparent.pLblTotalFlow).text(result.total);
                                }

                                $(sourceparent.pTdFlowList).html(html);
                                layer.close(loadIndex);

                                if (sourceparent.pHisflowListPager == null) {
                                    sourceparent.pHisflowListPager = new tdhx.base.utility.PagerController($(sourceparent.pHisflowPagerContent), sourceparent.hisflowListId, 10, result.total, function (pageIndex, filters) {
                                        sourceparent.selectDeviceProtocol(pageIndex);
                                    });
                                    sourceparent.pHisflowListPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
                                }
                            });
                        }
                        catch (err) {
                            html += "<tr><td colspan='3'>暂无数据</td></tr>";
                            $(sourceparent.pTdFlowList).html(html);
                            console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
                        }
                    }

                    sourceparent.selectDeviceProtocolPerc = function () {
                        var html = "";
                        try {
                            var data = {
                                name: [],
                                item: []
                            };
                            var timeFlag = $(sourceparent.pDdlTime2 + " option:selected").val();
                            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_PROTOCOL_FLOW;
                            var dt = { timeDelta: timeFlag ,ip:pcell.device_info.ip_addr,mac:dev_id};
                            var promise = URLManager.getInstance().ajaxSyncCall(link,dt);
                            promise.fail(function (jqXHR, textStatus, err) {
                                console.log(textStatus + " - " + err.message);
                            });
                            promise.done(function (result) {
                                if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                                //result={"rows": [["OPCDA", 0.597], ["S7", 0.1705], ["MMS", 0.0893], ["\u7f51\u7edc\u901a\u7528\u534f\u8bae", 0.0641], ["IEC104", 0.0454], ["\u5176\u4ed6", 0.03369999999999995]]};
                                    for (var i = 0; i < result.rows.length; i++) {
                                        if (result.rows[i][1] != 0) {
                                            var color = sourceparent.color[i];
                                            if (result.rows[i][0].toLowerCase() == "其他") {
                                                color = sourceparent.color[5];
                                            }
                                            var item = sourceparent.createPieStruct(result.rows[i][0], result.rows[i][1], color);
                                            data.name.push(result.rows[i][0]);
                                            data.item.push(item);
                                        }
                                    }
                                }
                            });

                            return data;
                        }
                        catch (err) {
                            console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
                            return data;
                        }
                    }

                    sourceparent.initPieChart = function (id, data) {
                        var ow=$('#'+id).parents('#topo_detail').width(),oh=$('#'+id).parents('#topo_detail').height();
                        $('#'+id).css({width:ow*0.7,height:200});
                        var pie = echarts.init($('#'+id)[0]);
                        var option = {
                            tooltip: {
                                trigger: 'item',
                                formatter: "{d}%"
                            },
                            legend: {
                                orient: 'vertical',
                                x: 'right',
                                data: data.name
                            },
                            calculable: true,
                            series: [
                                {
                                    name: 'pie',
                                    type: 'pie',
                                    radius: ['50%', '80%'],
                                    center: ['40%', '50%'],
                                    data: data.item
                                }
                            ]
                        };

                        pie.setOption(option);

                        return pie;
                    }

                    sourceparent.createPieStruct = function (name, value, color) {
                        return {
                            name: name,
                            value: value,
                            itemStyle: {
                                normal:
                                {
                                    color: color,
                                    label: {
                                        show: false,
                                        formatter: '{d}%',
                                        textStyle: {
                                            fontSize: 14,
                                            fontFamily: "微软雅黑"
                                        },
                                        position: 'inner'
                                    },
                                    labelLine: {
                                        show: false
                                    }
                                }
                            }
                        }
                    }

                    $(sourceparent.pDdlTime2).off().on("change", function () {
                        sourceparent.pieChart = sourceparent.initPieChart(sourceparent.pDivPieChart, sourceparent.selectDeviceProtocolPerc());
                    });
                    sourceparent.pieChart = sourceparent.initPieChart(sourceparent.pDivPieChart, sourceparent.selectDeviceProtocolPerc());
                    $(window).resize(function () {
                        sourceparent.pieChart.resize();
                    });
                    sourceparent.selectDeviceProtocol(1);
                };

                sourceparent.getCurflowList=function(){
                    sourceparent.selectRealFlow = function (pageIndex) {
                        try {
                            var data = {
                                name: [],
                                item: [],
                                time: []
                            };
                            var order_list=[];
                            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PROTOCOL_INFO_FLOW;
                            var promise = URLManager.getInstance().ajaxSyncCall(link,{deviceId:dev_id});
                            promise.fail(function (jqXHR, textStatus, err) {
                                console.log(textStatus + " - " + err.message);
                            });
                            promise.done(function (result) {
                                if (typeof (result) != "undefined" && typeof (result.time) != "undefined") {
                                    data.time=result.time;
                                    var show_num=0;
                                    for (var i = 0; i < result.data.length; i++) {
                                        var pro=result.data[i][0][0];
                                        order_list.push(pro);
                                        var name= pro=='tradition_pro'?'通用网络协议':pro=='unknown'?'未知':pro;
                                        data.name.push(name);
                                        var item ={name:name,data:result.data[i][1],type:'line'};
                                        data.item.push(item);
                                        if(result.data[i][2]!=0) show_num++;
                                    }
                                }
                                sourceparent.LineChart=sourceparent.initLineChart(sourceparent.pDivLineChart,data,show_num);
                                sourceparent.flowcharts(result.nexttime,order_list);
                            });
                        }
                        catch (err) {
                            console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
                        }
                    };
                    sourceparent.selectCusRealFlow = function (pageIndex) {
                        try {
                            var data = {
                                name: [],
                                item: [],
                                time: []
                            };
                            var order_list=[];
                            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PROTOCOL_CUS_INFO_FLOW;
                            var promise = URLManager.getInstance().ajaxSyncCall(link,{deviceId:dev_id});
                            promise.fail(function (jqXHR, textStatus, err) {
                                console.log(textStatus + " - " + err.message);
                            });
                            promise.done(function (result) {
                                if (typeof (result) != "undefined" && typeof (result.time) != "undefined") {
                                    data.time=result.time;
                                    var show_num=0;
                                    for (var i = 0; i < result.data.length; i++) {
                                        var pro=result.data[i][0][0];
                                        order_list.push(result.data[i][3]);
                                        var name= pro=='tradition_pro'?'通用网络协议':pro=='unknown'?'未知':pro;
                                        data.name.push(name);
                                        var item ={name:name,data:result.data[i][1],type:'line'};
                                        data.item.push(item);
                                        if(result.data[i][2]!=0) show_num++;
                                    }
                                }
                                sourceparent.cusLineChart=sourceparent.initLineChart(sourceparent.pCusDivLineChart,data,show_num);
                                sourceparent.cusflowcharts(result.nexttime,order_list);
                            });
                        }
                        catch (err) {
                            console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
                        }
                    };
                    sourceparent.initLineChart = function (id, data,show_num) {
                        var ow=$('#'+id).parents('#topo_detail').width(),oh=$('#'+id).parents('#topo_detail').height();
                        $('#'+id).css({width:ow*0.92,height:400});
                        var line = echarts.init($('#'+id)[0]);
                        var selectedList={};
                        for(var i=show_num;i<=data.name.length;i++){
                            var name=data.name[i];
                            selectedList[name]=false;
                        }
                        var option = {
                            tooltip: {
                                trigger: 'axis',
                                confine:true,
                                enterable:true,
                                textStyle:{
                                    fontSize:13
                                }
                            },
                            legend: {
                                data:data.name,
                                selected:selectedList
                            },
                            grid: {
                                left: '3%',
                                right: '4%',
                                bottom: '3%',
                                containLabel: true
                            },
                            xAxis: [{
                                type: 'category',
                                boundaryGap: false,
                                data: data.time
                            }],
                            yAxis: [
                                {
                                    type : 'value',
                                    name: '速率（Kbps）'
                                }
                            ],
                            series:data.item
                        };
                        line.setOption(option);
                        return line;
                    }

                    sourceparent.flowcharts = function (nexttime,proto_order) {
                        try {
                            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_PROTOCOL_INFO_RRFRESH;
                            var nexttimeL=nexttime;
                            gloTimer.FlowTimer = setInterval(function () {
                                var promise = URLManager.getInstance().ajaxSyncCall(link,{deviceId:dev_id,nexttime:nexttimeL,proto_order:proto_order});
                                promise.fail(function (jqXHR, textStatus, err) {
                                    console.log(textStatus + " - " + err.message);
                                });
                                promise.done(function (result) {
                                    if(result.refersh==0){
                                        nexttimeL=result.nexttime;
                                        //var addData=[],n=,item=[];
                                        for(var i=1;i<=result.time.length;i++){  //按时间点循环
                                            var addData=[];
                                            for(var j=0;j<result.data.length;j++){
                                                addData.push([
                                                    j,
                                                    result.data[j][1][i-1],
                                                    false,
                                                    false
                                                ]);
                                            }
                                            addData[0][4]=result.time[i-1];
                                            sourceparent.LineChart.addData(addData);
                                        };
                                    }else{
                                        clearInterval(gloTimer.FlowTimer);
                                        sourceparent.selectRealFlow();
                                    }
                                });
                            }, 20000);
                        }
                        catch (err) {
                            console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
                        }
                    };
                    sourceparent.cusflowcharts = function (nexttime,proto_order) {
                        try {
                            var parent = this;
                            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_CUS_PROTOCOL_INFO_RRFRESH;
                            var nexttimeL=nexttime;
                            gloTimer.cusFlowTimer = setInterval(function () {
                                var promise = URLManager.getInstance().ajaxSyncCall(link,{deviceId:dev_id,nexttime:nexttimeL,proto_order:proto_order});
                                promise.fail(function (jqXHR, textStatus, err) {
                                    console.log(textStatus + " - " + err.message);
                                });
                                promise.done(function (result) {
                                    if(result.refersh==0){
                                        nexttimeL=result.nexttime;
                                        //var addData=[],n=,item=[];
                                        for(var i=1;i<=result.time.length;i++){  //按时间点循环
                                            var addData=[];
                                            for(var j=0;j<result.data.length;j++){
                                                addData.push([
                                                    j,
                                                    result.data[j][1][i-1],
                                                    false,
                                                    false
                                                ]);
                                            }
                                            addData[0][4]=result.time[i-1];
                                            parent.cusLineChart.addData(addData);
                                        }
                                    }else{
                                        clearInterval(gloTimer.cusFlowTimer);
                                        parent.selectCusRealFlow();
                                        return;
                                    }
                                });
                            }, 20000);
                        }
                        catch (err) {
                            console.error("ERROR - FlowDetailAuditController.selectProtocolFlow() - Unable to get all events: " + err.message);
                        }
                    };
                    sourceparent.selectRealFlow();
                    sourceparent.selectCusRealFlow();
                };

                sourceparent.getAuditList=function(){
                    var html = "";
                    auditpromise = URLManager.getInstance().ajaxCallByURL(auditlink,"GET",{ip:pcell.device_info.ip_addr,mac:pcell.device_info.mac_addr,page:sourceparent.auditpage});
                    auditpromise.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                        html += "<tr><td colspan='9'>暂无数据</td></tr>";
                        $(perentNode+" .row-cutcontent").eq(5).find("tbody").html(html);
                    });
                    auditpromise.done(function (result) {
                        if (result.rows) {
                            for (var i = 0; i < result.rows.length; i++) {
                                var idx=$(sourceparent.detailProtoList).map(function(idx,d){
                                    if(d.key==result.rows[i][13]){
                                        return idx;
                                    }});
                                html += "<tr>";
                                html += "<td>" + FormatterManager.formatDateTime(Number(result.rows[i][2]*1000),'yyyy-MM-dd HH:mm:ss') + "</td>";
                                html += "<td>" + (result.rows[i][16]+'<--->'+result.rows[i][17]) + "</td>";
                                html += "<td>" + (result.rows[i][6]+'<--->'+result.rows[i][8])+ "</td>";
                                html += "<td>" + (result.rows[i][3]+'<--->'+result.rows[i][4])+ "</td>";
                                html += "<td>" + (result.rows[i][7]+'<--->'+result.rows[i][9])+ "</td>";
                                html += "<td>" + sourceparent.detailProtoList[idx[0]]['name']+ "</td>";
                                html += "</tr>";
                            }
                        }
                        else {
                            html += "<tr><td colspan='9'>暂无数据</td></tr>";
                        }
                        $(perentNode+" .row-cutcontent").eq(5).find("tbody").html(html);
                        if (sourceparent.pAuditlistPager == null && result.rows.length >= 0) {
                            sourceparent.pAuditlistPager = new tdhx.base.utility.PagerController($(sourceparent.pAuditPagerContent), sourceparent.auditListId, 10, result.total, function (pageIndex) {
                                sourceparent.auditpage = pageIndex;
                                sourceparent.getAuditList();
                            });
                            sourceparent.pAuditlistPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
                        }
                    });
                };
                //sourceparent.getAuditList();

                sourceparent.getAuditGraph=function(){
                    var ow=$('#device_category_chart').parents('#topo_detail').width()*0.93,
                        oh=$('#device_category_chart').parents('#topo_detail').height()*0.9,
                        ty='20';
                    var option = {
                        title : {
                            y:ty,
                            text: '资产关联分布图'
                        },
                        color : ['#3994d3', '#f98665', '#fac767', '#28daca', '#9569f9', '#e36585','#3994d3', '#f98665', '#fac767', '#28daca', '#9569f9', '#e36585','#e36585'],
                        tooltip : {
                            trigger: 'axis'
                        },
                        grid: {
                            x: '5%',
                            y: '20%',
                            x2: '0%',
                            y2: '10%'
                        },
                        calculable : false,
                        legend: {
                            //x:ow*0.6,
                            y:'20',
                            padding:0,
                            data:['邮件营销','联盟广告','视频广告']
                        },
                        xAxis : [
                            {
                                type : 'category',
                                splitLine : {show : false},
                                data : ['周一','周二','周三','周四','周五','周六','周日']
                            }
                        ],
                        yAxis : [
                            {
                                type : 'value',
                                position: 'left'
                            }
                        ],
                        series : [
                            {
                                name:'邮件营销',
                                type:'bar',
                                tooltip : {trigger: 'item'},barGap: '30%',barMaxWidth:Math.floor(100/7*0.3)/100*ow,
                                stack: '协议总数',
                                data:[120, 132, 101, 134, 90, 230, 210]
                            },
                            {
                                name:'联盟广告',
                                type:'bar',
                                tooltip : {trigger: 'item'},barGap: '30%',barMaxWidth:Math.floor(100/7*0.3)/100*ow,
                                stack: '协议总数',
                                data:[220, 182, 191, 234, 290, 330, 310]
                            },
                            {
                                name:'视频广告',
                                type:'bar',
                                tooltip : {trigger: 'item'},barGap: '30%',barMaxWidth:Math.floor(100/7*0.3)/100*ow,
                                stack: '协议总数',
                                data:[150, 232, 201, 154, 190, 330, 410]
                            }
                        ]
                    };
                    $('#device_category_chart').height(oh/2).width(ow);
                    var chart=echarts.init($('#device_category_chart')[0]);

                    var opts = {
                        title : {
                            text: '资产协议分布图',
                            y:ty
                        },
                        tooltip : {
                            trigger: 'item',
                            formatter: "{a} <br/>{b} : {c} ({d}%)"
                        },
                        color : ['#3994d3', '#f98665', '#fac767', '#28daca', '#9569f9', '#e36585','#3994d3', '#f98665', '#fac767', '#28daca', '#9569f9', '#e36585','#e36585'],
                        legend: {
                            orient : 'vertical',
                            x : '40',
                            y : '60',
                            data:['直接访问','邮件营销','联盟广告','视频广告','搜索引擎']
                        },
                        calculable : false,
                        series : [
                            {
                                name:'资产协议',
                                type:'pie',
                                radius : '55%',
                                center: ['50%', '60%'],
                                data:[
                                    {value:335, name:'直接访问'},
                                    {value:310, name:'邮件营销'},
                                    {value:234, name:'联盟广告'},
                                    {value:135, name:'视频广告'},
                                    {value:1548, name:'搜索引擎'}
                                ]
                            }
                        ]
                    };
                    $('#protocol_category_chart').height(oh/2).width(ow);
                    var chart1=echarts.init($('#protocol_category_chart')[0]);

                    auditpromise = URLManager.getInstance().ajaxCallByURL(auditlink,"GET",{ip:pcell.device_info.ip_addr,mac:pcell.device_info.mac_addr,page:sourceparent.auditpage});
                    auditpromise.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                    });
                    auditpromise.done(function (result) {
                        if (result.status&&result.rows.length) {
                            option.legend.data=[];option.xAxis[0].data=result.rows[0].data.devs.reverse();option.series = [];
                            $(result.rows).each(function(i,d){
                                option.legend.data.push(d.prot);
                                option.series.push({
                                    name: d.prot,
                                    type:'bar',
                                    tooltip : {trigger: 'item'},barGap: '30%',barMaxWidth:Math.floor(100/7*0.3)/100*ow,
                                    stack: '协议总数',
                                    data: d.data.val.reverse()
                                });
                            });
                        }else{
                            option.color= ['#dddddd'];
                            option.legend.data=['暂无数据'];
                            option.xAxis[0].data=['暂无数据'];
                            option.series = [
                                {
                                    name:'noprotocol',
                                    type:'bar',
                                    tooltip : {trigger: 'item'},barGap: '30%',barMaxWidth:Math.floor(100/7*0.3)/100*ow,
                                    stack: '协议总数',
                                    data:[0]
                                }
                            ];
                        }
                        chart.setOption(option);
                    });
                    auditpromise1 = URLManager.getInstance().ajaxCallByURL(auditlink1,"GET",{ip:pcell.device_info.ip_addr,mac:pcell.device_info.mac_addr,page:sourceparent.auditpage});
                    auditpromise1.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                    });
                    auditpromise1.done(function (result) {
                        opts.series[0].data=[];
                        if (result.status&&result.rows.vals.length) {
                            opts.legend.data=result.rows.prots;
                            $(result.rows.vals).each(function(i,d){
                                opts.series[0].data[i]={name:result.rows.prots[i],value:d};
                            });
                        }else{
                            opts.color= ['#dddddd'];
                            opts.legend.data=['暂无数据'];opts.series[0].data[0]={name:'暂无数据',value:0};
                        }
                        chart1.setOption(opts);
                    });
                };
                sourceparent.getAuditGraph();
            }});
    }
    catch (err) {
        console.error("ERROR - OperationLogController.load() - Unable to load: " + err.message);
    }
};


TopographController.prototype.formatEventSource = function (status) {
    try {
        switch (status) {
            case 1: return "白名单";
            case 2: return "黑名单";
            case 3: return "IP/MAC";
            case 4: return "流量告警";
            case 5: return "MAC过滤";
            case 6: return "资产告警";
            case 7: return "不合规报文告警";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - EventController.formatReadStatus() - Unable to format ReadStaus: " + err.message);
    }
}

TopographController.prototype.formatEventType = function (status) {
    try {
        switch (status) {
            case 1: return "警告";
            case 0: return "通过";
            case 2: return "阻断";
            case 3: return "通知";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - EventController.formatEventType() - Unable to format event type: " + err.message);
    }
}

TopographController.prototype.formatFilter = function () {
    try {
        var ipts=$(this.pDivFilter).find('input'),selts=$(this.pDivFilter).find('select');
        this.filter.ip = $.trim(ipts.eq(1).val());
        this.filter.mac = $.trim(ipts.eq(2).val());
        this.filter.name = ipts.eq(0).val();
        this.filter.type = selts.eq(1).val();
        this.filter.is_topo = 0;
        this.filter.unknown = selts.eq(0).val();
        this.filter.vender = '';
    }
    catch (err) {
        console.error("ERROR - OperationLogController.formatFilter() - Unable to get filter: " + err.message);
    }
}

TopographController.prototype.intoGraph = function (addModal) {
    try {
        var parent=this,dialogTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.TOPO_INTOTOPO), {
            elementId: parent.elementId + "_dialog"
        });
        var width = parent.pViewHandle.width() - 10 + "px";
        var link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UNADD_TOPO_LIST,promise;
        var linknew=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_ASSET_LIST,newpromise;
        var slink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].SHIFT_STATUS_TOPO,spromise;
        var height = $(window).height() - parent.pViewHandle.offset().top - $(window).height()/10 + "px";
        var tmplay = layer.open({
            type: 1,
            title: '加入拓扑',
            area: ["1100px",height],
            //offset: ["82px", "200px"],
            shade: [0.5, '#393D49'],
            content: dialogTemplate,
            success: function (layero, index) {
                var btns = $(parent.pIntoBtns+' button'),html = "",loadIndex = layer.load(2),allAsset=[];
                var selts=$(parent.pDivFilter).find('select'),ipts=$(parent.pDivFilter).find('input'),searchBtn=$(parent.pDivFilter).find('button');
                promise = URLManager.getInstance().ajaxCall(link,"GET");
                promise.fail(function (jqXHR, textStatus, err) {
                    console.log(textStatus + " - " + err.message);
                    layer.close(loadIndex);
                });
                promise.done(function (result) {
                    if (result.status) {
                        var unaddData=result.device_list;
                        $(parent.pBtnFilter).click(function(){
                            $(parent.pDivFilter).toggle();
                            $(parent.pDivFilter).find('select').val('');
                            $(parent.pDivFilter).find('input').val('');
                            parent.filter = {
                                ip: '',
                                mac: '',
                                name: '',
                                type: '',
                                is_topo: 0,
                                unknown:'',
                                vender: ''
                            };
                            rankData();
                        });
                        searchBtn.click(function(){
                            parent.formatFilter();
                            rankData();
                        });
                        parent.filter = {
                            ip: '',
                            mac: '',
                            name: '',
                            type: '',
                            is_topo: 0,
                            unknown:'',
                            vender: ''
                        };
                        rankData();
                        function rankData(){

                            newpromise = URLManager.getInstance().ajaxCallByURL(linknew,"POST",parent.filter),html='';
                            newpromise.fail(function (jqXHR, textStatus, err) {
                                console.log(textStatus + " - " + err.message);
                                html += "<tr><td colspan='9'>暂无数据</td></tr>";
                                parent.pViewHandle.find(parent.pDeviceList+">tbody").html(html);
                                layer.close(loadIndex);
                            });
                            newpromise.done(function (result) {
                                if (result.rows.length) {
                                    allAsset=result.rows;
                                    for (var i = 0; i < allAsset.length; i++) {
                                        html += "<tr>";
                                        html += "<td style='width:70px'>" + "<input type='checkbox' class='chinput selflag' data-id=\"" + allAsset[i][0] + "\" id=\"into" + allAsset[i][0] + "\" /><label for=\"into" + allAsset[i][0] + "\"></label></td>";
                                        html += "<td style='width:280px' class='hide_long' title='" + allAsset[i][1] + "'>" + allAsset[i][1] + "</td>";
                                        html += "<td style='width:260px' class='hide_long' title='" + allAsset[i][2] + "'>" + allAsset[i][2] + "</td>";
                                        html += "<td style='width:150px' class='hide_long' title='" + allAsset[i][3] + "'>" + allAsset[i][3] + "</td>";
                                        html += "<td style='width:150px'>" + (allAsset[i][9]?'非法接入':'正常接入') + "</td>";
                                        html += "<td class='hide_long' title='" + allAsset[i][12] + "'>" + allAsset[i][12] + "</td>";
                                        html += "</tr>";
                                    }
                                }
                                else {
                                    html += "<tr><td colspan='9'>暂无数据</td></tr>";
                                }
                                layer.close(loadIndex);
                                $(parent.pDeviceList + ">tbody").html(html);
                                $(parent.pSelectAll).click(function () {
                                    parent.checkSwitch=!parent.checkSwitch;
                                    $(parent.pDeviceList).find('input').filter('.selflag').prop('checked', parent.checkSwitch);
                                });
                            });
                        }

                        btns.eq(0).click(function(){
                            var pickdev=[],pickData=[];
                            $(parent.pDeviceList).find('input:checked').each(function(i,d){
                                    var id=$(d).data('id');
                                    pickdev.push(id);
                                    $(unaddData).each(function(ii,dd){
                                        if(id==dd.id){
                                            pickData.push(dd);
                                        }
                                    });
                            });
                            if(!pickdev.length){
                                layer.alert('请至少选择设备再试', {icon: 5});
                                return false;
                            }
                            var ids=pickdev.join(',');
                            spromise=URLManager.getInstance().ajaxCallByURL(slink,'POST',{id:ids,is_topo:1});
                            var loadIdx=layer.load(2,{shade:[0.4, '#fff']});
                            spromise.done(function(result) {
                                if (result.status > 0) {
                                    layer.close(loadIdx);
                                    layer.alert(result.msg, {icon: 6});
                                    layer.close(tmplay);
                                    addModal&&addModal(pickData);
                                } else {
                                    layer.alert( result.msg, {icon: 5});
                                    layer.close(loadIdx);
                                }
                            });
                            spromise.fail(function (jqXHR, textStatus, err) {
                                console.log(textStatus + '-' + err.msg);
                                layer.alert(err.msg, {icon: 5});
                                layer.close(loadIdx);
                            });
                        });


                    }
                });

                btns.eq(1).click(function () {
                    layer.close(tmplay);
                });
            }});
    }
    catch (err) {
        console.error("ERROR - OperationLogController.load() - Unable to load: " + err.message);
    }
}

TopographController.prototype.num2type = function (num) {
    switch(num){
        case 0:return '未知';
        case 1:return 'PC';
        case 2:return '工程师站PC';
        case 3:return '操作员PC';
        case 4:return 'PLC';
        case 5:return 'RTU';
        case 6:return 'HMI';
        case 7:return '网络设备';
    }
}

TopographController.prototype.main = function (data,xml,container) {
    var straigeparent=this,xmllink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_TOPO_ASSET,
    promise,slink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].SHIFT_STATUS_TOPO,spromise,
        updateLink=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].OPER_ASSET_DEVICE;
        // Checks if the browser is supported
    var ipts=$('#assetsInfoDetail').find('input[type=text]'),selt=$('#assetsInfoDetail').find('select'),btns=$('#assetsInfoDetail').find('button');
        if (!mxClient.isBrowserSupported())
        {
            // Displays an error message if the browser is not supported.
            mxUtils.error('Browser is not supported!', 200, false);
        }
        else
        {
            // Creates the graph inside the given container
            var graph = new mxGraph(container);
            var outline = document.getElementById('outlineContainer');
            graph.setConnectable(true);
            graph.setTooltips(true);
            graph.setPanning(true);//remove stage
            graph.setCellsEditable(false);//edit text of block
            mxGraphHandler.prototype.guidesEnabled = true;//启用线定位
            graph.setMultigraph(false);//repeat link disallow
            graph.setCellsResizable(false);//disable resize for node
            mxEvent.disableContextMenu(container);
            graph.setAllowLoops(false);// allow target and source are same cell

            var outln = new mxOutline(graph, outline);
            var keyHandler = new mxKeyHandler(graph);
            var swi;
            $('.collapsebtn>button').click(function(){
                if(swi){
                    $('.nettopo-inputbox').show();
                    $('.nettopo-box').removeClass('col-md-12').addClass('col-md-9');
                    graph.center();
                }else{
                    $('.nettopo-inputbox').hide();
                    $('.nettopo-box').removeClass('col-md-9').addClass('col-md-12');
                    graph.center();
                }
                swi=!swi;
            });
            /*$('.nettopo-inputbox').mouseenter(function(e){
                $('.collapsebtn').fadeIn();
            });
            $('.nettopo-inputbox').mouseleave(function(e){
                clearTimeout(timer);
                var timer=setTimeout(function(){$('.collapsebtn').fadeOut();},2000);
            });*/
            keyHandler.bindKey(46, function(evt)
            {
                /*if (graph.isEnabled()&&graph.selectionModel.cells.length)//&&!cell.subNode
                {
                    $(graph.selectionModel.cells).each(function(i,d){
                        straigeparent.preDelId.push(d.id);
                    });
                    graph.removeCells();
                    graph.refresh();
                }*/
                $(graph.selectionModel.cells).each(function(i,d){
                    if(d.alarm_info)
                    straigeparent.preDelId.push(d.unitId);
                });
                graph.removeCells();
            });
            graph.popupMenuHandler.factoryMethod = function(menu, cell, evt)
            {
                return createPopupMenu(graph, menu, cell, evt);
            };
            function createPopupMenu(graph, menu, cell, evt)
            {
                var model = graph.getModel();

                if (cell != null)
                {
                    /*if (model.isVertex(cell))
                     {
                     menu.addItem('Add child', 'editors/images/overlays/check.png', function()
                     {
                     addChild(graph, cell);
                     });
                     }

                     menu.addItem('Edit label', 'editors/images/text.gif', function()
                     {
                     graph.startEditingAtCell(cell);
                     });*/
                    if(!cell.subNode){
                        if ((model.isEdge(cell)||model.isVertex(cell))&&!cell.subNode&&cell.device_info)
                        {
                            menu.addItem('查看详情', '/static/themes/skin/kea-u1142/images/diagram.gif', function()
                            {
                                straigeparent.graphDetail(cell);
                            });
                        }
                        if ((model.isEdge(cell)||model.isVertex(cell))&&!cell.subNode)
                        {
                            menu.addItem('删除', '/static/themes/skin/kea-u1142/images/delete.gif', function()
                            {
                                straigeparent.preDelId.push(cell.unitId);
                                graph.removeCells([cell]);
                                //deleteSubtree(graph, cell);
                            });
                        }
                    }
                }
                menu.addItem('资产加入', '/static/themes/skin/kea-u1142/images/plus.png', function()
                {
                    straigeparent.addAsset();
                });
                menu.addSeparator();
                menu.addItem('放大', '/static/themes/skin/kea-u1142/images/zoomin.gif', function()
                {
                    graph.zoomIn();
                });
                menu.addItem('缩小', '/static/themes/skin/kea-u1142/images/zoomout.gif', function()
                {
                    graph.zoomOut();
                });
                menu.addItem('显示所有', '/static/themes/skin/kea-u1142/images/zoom.gif', function()
                {
                    graph.fit();
                });

                menu.addItem('实际大小', '/static/themes/skin/kea-u1142/images/zoomactual.gif', function()
                {
                    graph.zoomActual();
                });

                //menu.addSeparator();

                /*menu.addItem('导出图片', '/static/themes/skin/kea-u1142/images/print.gif', function()
                {
                    var preview = new mxPrintPreview(graph, graph.zoomFactor/1.5);
                    preview.open();
                });

                menu.addItem('打印', '/static/themes/skin/kea-u1142/images/print.gif', function()
                {
                    var pageCount = mxUtils.prompt('Enter maximum page count', '1');

                    if (pageCount != null)
                    {
                        var scale = mxUtils.getScaleForPageCount(pageCount, graph);
                        var preview = new mxPrintPreview(graph, scale);
                        preview.open();
                    }
                });*/
            };
            function deleteSubtree(graph, cell)
            {
                // Gets the subtree from cell downwards
                var cells = [];
                graph.traverse(cell, true, function(vertex)
                {
                    cells.push(vertex);

                    return true;
                });

                graph.removeCells(cells);
            };


            graph.getSecondLabel = function(cell)
            {
                if (!this.model.isEdge(cell))
                {
                    // Possible to return any string here
                    return cell.unread!==undefined?cell.unread:'';
                }

                return null;
            };

            var secondLabelVisible = true;
            // Creates the shape for the shape number and puts it into the draw pane



            var redrawShape = graph.cellRenderer.redrawShape;
            graph.cellRenderer.redrawShape = function(state, force, rendering)
            {

                var result = redrawShape.apply(this, arguments);

                if (result && secondLabelVisible && state.cell.geometry != null && !state.cell.geometry.relative)
                {
                    var secondLabel = graph.getSecondLabel(state.cell);

                    if (secondLabel != null && state.shape != null && state.secondLabel == null)
                    {
                        state.secondLabel = new mxText(secondLabel, new mxRectangle(),
                            mxConstants.ALIGN_LEFT, mxConstants.ALIGN_BOTTOM);


                        // Styles the label
                        state.secondLabel.color = 'rgb(255,255,255)';
                        state.secondLabel.opacity = state.cell.unread?100:0;
                        state.secondLabel.family = 'Verdana';
                        state.secondLabel.size = 16;
                        //state.secondLabel.fontStyle = mxConstants.FONT_ITALIC;
                        state.secondLabel.background = 'red';
                        /*if(state.cell.value!='设备组'){
                         state.secondLabel.border = 'black';
                         }else{
                         delete state.secondLabel.border;
                         }*/
                        state.secondLabel.spacing = 10;
                        state.secondLabel.spacingTop = 10;
                        state.secondLabel.spacingLeft = 10;
                        state.secondLabel.spacingBottom = 10;
                        state.secondLabel.spacingRight = 10;
                        state.secondLabel.valign = 'bottom';
                        state.secondLabel.dialect = state.shape.dialect;
                        state.secondLabel.dialect = mxConstants.DIALECT_STRICTHTML;
                        state.secondLabel.wrap = true;
                        graph.cellRenderer.initializeLabel(state, state.secondLabel);
                    }
                }

                if (state.secondLabel != null)
                {
                    var scale = graph.getView().getScale();
                    var bounds = new mxRectangle(state.x + state.width - 8 * scale, state.y + 8 * scale, 35, 0);
                    state.secondLabel.state = state;
                    state.secondLabel.value = graph.getSecondLabel(state.cell);
                    state.secondLabel.scale = scale;
                    state.secondLabel.bounds = bounds;
                    state.secondLabel.redraw();
                }

                return result;
            };

            // 销毁图形编号
            var destroy = graph.cellRenderer.destroy;
            graph.cellRenderer.destroy = function(state)
            {
                destroy.apply(this, arguments);

                if (state.secondLabel != null)
                {
                    state.secondLabel.destroy();
                    state.secondLabel = null;
                }
            };

            var style = new Object();
            style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_IMAGE;
            style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_LABEL;
            style[mxConstants.STYLE_PERIMETER] = mxPerimeter.RectanglePerimeter;
            style[mxConstants.STYLE_VERTICAL_ALIGN] = mxConstants.ALIGN_TOP;
            style[mxConstants.STYLE_ROUNDED] = true;
            style[mxConstants.STYLE_ARCSIZE] = 10;
            style[mxConstants.STYLE_IMAGE_VERTICAL_ALIGN] = mxConstants.ALIGN_MIDDLE;
            style[mxConstants.STYLE_IMAGE_ALIGN] = mxConstants.ALIGN_CENTER;
            style[mxConstants.STYLE_FONTSIZE] = 12;
            style[mxConstants.STYLE_FONTCOLOR] = '#000000';
            style[mxConstants.STYLE_FILLCOLOR] = 'rgba(255,255,255,0)';
            //style[mxConstants.STYLE_FILL_OPACITY] = 0;
            style[mxConstants.STYLE_STROKEWIDTH] =1;
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE_WIDTH] = '85';
            style[mxConstants.STYLE_IMAGE_HEIGHT] ='110';
            style[mxConstants.STYLE_SPACING_TOP] = '88';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/unknown.png';
            graph.getStylesheet().putCellStyle('unknown', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/unknown.gif';
            graph.getStylesheet().putCellStyle('unknown_G', style);
            style = mxUtils.clone(style);
            /*delete style[mxConstants.STYLE_IMAGE_VERTICAL_ALIGN];
            style[mxConstants.STYLE_IMAGE_VERTICAL_ALIGN] = mxConstants.ALIGN_BOTTOM;
            style[mxConstants.STYLE_FILLCOLOR] = 'green';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/server.png';
            style[mxConstants.STYLE_IMAGE_ALIGN] = mxConstants.ALIGN_RIGHT;
            delete style[mxConstants.STYLE_SPACING_TOP];*/
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/RTU.png';
            graph.getStylesheet().putCellStyle('RTU', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/RTU.gif';
            graph.getStylesheet().putCellStyle('RTU_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/engineer.png';
            graph.getStylesheet().putCellStyle('engineer', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/engineer.gif';
            graph.getStylesheet().putCellStyle('engineer_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/hmi.png';
            graph.getStylesheet().putCellStyle('hmi', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/hmi.gif';
            graph.getStylesheet().putCellStyle('hmi_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/operater.png';
            graph.getStylesheet().putCellStyle('operater', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/operater.gif';
            graph.getStylesheet().putCellStyle('operater_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/pc.png';
            graph.getStylesheet().putCellStyle('pc', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/pc.gif';
            graph.getStylesheet().putCellStyle('pc_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/plc.png';
            graph.getStylesheet().putCellStyle('plc', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/plc.gif';
            graph.getStylesheet().putCellStyle('plc_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/netdevice.png';
            graph.getStylesheet().putCellStyle('netdevice', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/netdevice.gif';
            graph.getStylesheet().putCellStyle('netdevice_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/dcs.png';
            graph.getStylesheet().putCellStyle('dcs', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/dcs.gif';
            graph.getStylesheet().putCellStyle('dcs_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/server.png';
            graph.getStylesheet().putCellStyle('server', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/server.gif';
            graph.getStylesheet().putCellStyle('server_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/opcser.png';
            graph.getStylesheet().putCellStyle('opcser', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/opcser.gif';
            graph.getStylesheet().putCellStyle('opcser_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/secdev.png';
            graph.getStylesheet().putCellStyle('secdev', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/secdev.gif';
            graph.getStylesheet().putCellStyle('secdev_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/IED.png';
            graph.getStylesheet().putCellStyle('ied', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/IED.gif';
            graph.getStylesheet().putCellStyle('ied_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/cusdev.png';
            graph.getStylesheet().putCellStyle('cusdev', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_STROKECOLOR] = '#dddddd';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/cusdev.gif';
            graph.getStylesheet().putCellStyle('cusdev_G', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/netdevice.png';
            graph.getStylesheet().putCellStyle('specialDev', style);
            style = mxUtils.clone(style);
            style[mxConstants.STYLE_IMAGE_WIDTH] = '241';
            style[mxConstants.STYLE_IMAGE_HEIGHT] ='15';
            style[mxConstants.STYLE_SPACING_TOP] = '0';
            style[mxConstants.STYLE_IMAGE] = '/static/themes/skin/kea-u1142/images/devicegroup.png';
            graph.getStylesheet().putCellStyle('netgroup', style);

            var style1 = graph.getStylesheet().getDefaultEdgeStyle();
            style1[mxConstants.STYLE_ROUNDED] = true;
            style1[mxConstants.STYLE_EDGE] = mxEdgeStyle.ElbowConnector;//'orthogonalEdgeStyle';;
            style1[mxConstants.STYLE_STROKEWIDTH] = 2;
            style1[mxConstants.STYLE_STROKECOLOR] = '#6482b9';
            style1[mxConstants.STYLE_ENDARROW]=mxConstants.ARROW_OVAL;
            style1[mxConstants.STYLE_STARTARROW]=mxConstants.ARROW_OVAL;
            graph.alternateEdgeStyle = 'elbow=vertical';
            style1[mxConstants.STYLE_CURVED] = '0';

            var edge='perimeterSpacing=4;strokeWidth=4;labelBackgroundColor=white;fontStyle=1';
            // Defines the tolerance before removing the icons
            var iconTolerance = 20;


            var textNode='<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="2" value="hello" style="image" vertex="1" parent="1"><mxGeometry x="50" y="50" width="80" height="130" as="geometry"/><Object a="whoami" b="123" as="data"/></mxCell><mxCell id="3" value="World!" style="top" vertex="1" parent="1"><mxGeometry x="200" y="150" width="80" height="130" as="geometry"/></mxCell><mxCell id="4" value="" edge="1" parent="1" source="2" target="3"><mxGeometry relative="1" as="geometry"/></mxCell></root></mxGraphModel>';
            var textNode='<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="2" value="hello" style="image" parent="1" vertex="1"><mxGeometry x="50" y="50" width="80" height="130" as="geometry"/><Object a="whoami" b="123" as="data"/></mxCell><mxCell id="3" value="World!" style="top" parent="1" vertex="1"><mxGeometry x="210" y="250" width="80" height="130" as="geometry"/></mxCell><mxCell id="4" value="" parent="1" source="2" target="3" edge="1"><mxGeometry relative="1" as="geometry"/></mxCell><mxCell id="5" value="hello" style="image" vertex="1" parent="1"><mxGeometry x="340" width="80" height="130" as="geometry"/><Object a="whoami" b="123" as="data"/></mxCell><mxCell id="6" edge="1" parent="1" source="2" target="5"><mxGeometry relative="1" as="geometry"/></mxCell></root></mxGraphModel>';
            var textNode='<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCebll id="11" value="工作站1" style="image" parent="1" vertex="1"><mxGeometry width="80" height="130" as="geometry"/><Object name="工作站1" type="1" as="data"><Array as="info"><add value="0"/><add value="0"/><add value="0"/></Array></Object></mxCebll><mxCell id="22" value="集控室1" style="image" parent="1" vertex="1"><mxGeometry x="80" width="80" height="130" as="geometry"/><Object name="集控室1" type="0" as="data"><Array as="info"><add value="0"/><add value="0"/><add value="0"/></Array></Object></mxCell><mxCell id="33" value="工程师站1" style="image" parent="1" vertex="1"><mxGeometry x="160" width="80" height="130" as="geometry"/><Object name="工程师站1" type="1" as="data"><Array as="info"><add value="0"/><add value="0"/><add value="0"/></Array></Object></mxCell><mxCell id="44" value="调度室1" style="image" parent="1" vertex="1"><mxGeometry x="330" y="200" width="80" height="130" as="geometry"/><Object name="调度室1" type="0" as="data"><Array as="info"><add value="0"/><add value="0"/><add value="0"/></Array></Object></mxCell><mxCell id="66" value="集控室1" style="image" parent="1" vertex="1"><mxGeometry x="320" width="80" height="130" as="geometry"/><Object name="集控室1" type="0" as="data"><Array as="info"><add value="0"/><add value="0"/><add value="0"/></Array></Object></mxCell><mxCell id="77" value="工程师站1" style="image" parent="1" vertex="1"><mxGeometry x="470" y="160" width="80" height="130" as="geometry"/><Object name="工程师站1" type="1" as="data"><Array as="info"><add value="0"/><add value="0"/><add value="0"/></Array></Object></mxCell><mxCell id="88" value="调度室1" style="image" parent="1" vertex="1"><mxGeometry x="480" width="80" height="130" as="geometry"/><Object name="调度室1" type="0" as="data"><Array as="info"><add value="0"/><add value="0"/><add value="0"/></Array></Object></mxCell><mxCell id="55" value="分配站1" style="image" parent="1" vertex="1"><mxGeometry x="560" width="80" height="130" as="geometry"/><Object name="分配站1" type="1" as="data"><Array as="info"><add value="0"/><add value="0"/><add value="0"/></Array></Object></mxCell><mxCell id="90" parent="1" source="33" target="66" edge="1"><mxGeometry relative="1" as="geometry"/></mxCell><mxCell id="91" parent="1" source="66" target="44" edge="1"><mxGeometry relative="1" as="geometry"/></mxCell><mxCell id="92" parent="1" source="66" target="77" edge="1"><mxGeometry relative="1" as="geometry"/></mxCell></root></mxGraphModel>';
            var textNode='';

            /*// 居中缩放
            graph.centerZoom = true;
            // 放大按钮
            document.body.appendChild(mxUtils.button('放大 +', function(evt){
                graph.zoomIn();
            }));
            // 缩小按钮
            document.body.appendChild(mxUtils.button('缩小 -', function(evt){
                graph.zoomOut();
            }));
            // 还原按钮
            document.body.appendChild(mxUtils.button('还原 #', function(evt){
                graph.zoomActual();
                graph.zoomFactor = 1.2;
                input.value = 1.2;
            }));
            var input = document.createElement("input");
            input.type = "text";
            input.value = graph.zoomFactor;
            input.addEventListener("blur", function(){
                graph.zoomFactor = parseFloat(this.value, 10);
            });
            document.body.appendChild(input);*/
            graph.isCellFoldable = function(cell)
            {
                return false;
            }//don't show collapse btn

            graph.isPart = function(cell)
            {
                var state = this.view.getState(cell);
                var style = (state != null) ? state.style : this.getCellStyle(cell);

                return style['constituent'] == '1';
            };
            var graphHandlerGetInitialCellForEvent = mxGraphHandler.prototype.getInitialCellForEvent;
            mxGraphHandler.prototype.getInitialCellForEvent = function(me)
            {
                var cell = graphHandlerGetInitialCellForEvent.apply(this, arguments);

                if (this.graph.isPart(cell))
                {
                    cell = this.graph.getModel().getParent(cell)
                }

                return cell;
            };//cann't move parent out

            var zoomin = document.getElementById('zoomin');
            var zoomout = document.getElementById('zoomout');
            var recover = document.getElementById('recover');
            var actual = document.getElementById('actual');
            var showall = document.getElementById('showall');
            var sourceInput = document.getElementById('source');
            var exportInput = document.getElementById('export');
            var resetInput = document.getElementById('clear');
            var addgroup = document.getElementById('addgroup');
            var intoTopo = document.getElementById('intopograph');
            mxEvent.addListener(zoomin, 'click', function()
            {
                graph.zoomIn();
            });
            mxEvent.addListener(zoomout, 'click', function()
            {
                graph.zoomOut();
            });
            mxEvent.addListener(actual, 'click', function()
            {
                graph.zoomActual();
                graph.zoomFactor = 1.2;
                //input.value = 1.2;
            });
            mxEvent.addListener(showall, 'click', function()
            {
                graph.fit();
            });
            mxEvent.addListener(resetInput, 'click', function()
            {
                textNode='<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>';
                var doc = mxUtils.parseXml(textNode);
                var dec = new mxCodec(doc);
                dec.decode(doc.documentElement, graph.getModel());
                var link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_TOPO_ASSET,promise = URLManager.getInstance().ajaxCall(link);
                var loadIdx=layer.load(2,{shade:[0.4, '#fff']});
                promise.fail(function (jqXHR, textStatus, err) {
                    layer.alert(err.msg, { icon: 2 });
                    console.log(textStatus + " - " + err.msg);
                });
                promise.done(function(res){
                    if(res.status){
                        layer.close(loadIdx);
                        straigeparent.preDelId=[];
                        $(res.dev_info).each(function(i,d){
                            straigeparent.preDelId.push(d.id);
                        });
                    }else{
                        layer.alert(res.msg, { icon: 5 });
                        layer.close(loadIdx);
                    }
                });
            });
            mxEvent.addListener(recover, 'click', function()
            {
                straigeparent.preDelId=[];
                straigeparent.init();
            });

            straigeparent.addNetDev=function(){

            }

            mxEvent.addListener(addgroup, 'click', function()
            {
                var cell = new mxCell('', new mxGeometry(Math.random()*300+10, Math.random()*100+10, 241, 10), 'rounded=1;strokeColor=#6482b9;fillColor=#6482b9;');
                /*cell.geometry.setTerminalPoint(new mxPoint(50, 150), true);
                cell.geometry.setTerminalPoint(new mxPoint(150, 50), false);*/
                cell.geometry.setTerminalPoint(new mxPoint(0.25, 0), true);
                cell.geometry.setTerminalPoint(new mxPoint(0.5, 0), true);
                cell.geometry.setTerminalPoint(new mxPoint(0.75, 0), true);
                cell.geometry.setTerminalPoint(new mxPoint(0, 0.25), true);
                cell.geometry.setTerminalPoint(new mxPoint(0, 0.5), true);
                cell.geometry.setTerminalPoint(new mxPoint(0, 0.75), true);
                cell.geometry.setTerminalPoint(new mxPoint(1, 0.25), true);
                cell.geometry.setTerminalPoint(new mxPoint(1, 0.5), true);
                cell.geometry.setTerminalPoint(new mxPoint(1, 0.75), true);
                cell.geometry.setTerminalPoint(new mxPoint(0.25, 1), true);
                cell.geometry.setTerminalPoint(new mxPoint(0.5, 1), true);
                cell.geometry.setTerminalPoint(new mxPoint(0.75, 1), true);
                cell.vertex = true;
                cell = graph.addCell(cell);
                graph.refresh();
                var loadIdx=layer.load(2,{shade:[0.4, '#fff']});
                var enc = new mxCodec();
                var node = enc.encode(graph.getModel());
                textNode = mxUtils.getPrettyXml(node);
                textNode=textNode.replace(/[\t\r\n]|\s{2}/g,'');
                textNode=textNode=='<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>'?'':textNode;
                promise=URLManager.getInstance().ajaxCallByURL(xmllink,'PUT',{xml_info:textNode});
                promise.done(function(result) {
                    if (result.status > 0) {
                        layer.close(loadIdx);
                    } else {
                        layer.alert('保存失败(updatexml)', {icon: 5});
                        layer.close(loadIdx);
                    }
                });
                promise.fail(function (jqXHR, textStatus, err) {
                    console.log(textStatus + '-' + err.msg);
                    layer.alert(err.msg, {icon: 5});
                    layer.close(loadIdx);
                });
            });

            /*mxEvent.addListener(sourceInput, 'click', function()
            {
                textNode=textNode?textNode:'<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>';
                var doc = mxUtils.parseXml(textNode);
                var dec = new mxCodec(doc);
                dec.decode(doc.documentElement, graph.getModel());
                //var v1 = graph.insertVertex(parent, 80, 80, 80, 0, 80, 130,'image');
            });*/

            mxEvent.addListener(exportInput, 'click', function()
            {
                var loadIdx=layer.load(2,{shade:[0.4, '#fff']});
                var enc = new mxCodec();
                var node = enc.encode(graph.getModel());

                textNode = mxUtils.getPrettyXml(node);
                textNode=textNode.replace(/[\t\r\n]|\s{2}/g,'');
                textNode=textNode=='<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>'?'':textNode;
                //console.log(textNode);
                spromise=URLManager.getInstance().ajaxCallByURL(slink,'POST',{id:straigeparent.preDelId.join(','),is_topo:0});
                spromise.done(function(result) {
                    if (result.status > 0) {
                        promise=URLManager.getInstance().ajaxCallByURL(xmllink,'PUT',{xml_info:textNode});
                        promise.done(function(result) {
                            if (result.status > 0) {
                                layer.close(loadIdx);
                                layer.alert('保存成功', {icon: 6});
                            } else {
                                layer.alert('保存失败', {icon: 5});
                                layer.close(loadIdx);
                            }
                        });
                        promise.fail(function (jqXHR, textStatus, err) {
                            console.log(textStatus + '-' + err.msg);
                            layer.alert(err.msg, {icon: 5});
                            layer.close(loadIdx);
                        });
                    } else {
                        layer.alert( '保存时出错（未能删除）', {icon: 5});
                        layer.close(loadIdx);
                    }
                });
                spromise.fail(function (jqXHR, textStatus, err) {
                    console.log(textStatus + '-' + err.msg);
                    layer.alert(err.msg, {icon: 5});
                    layer.close(loadIdx);
                });
            });

            straigeparent.addAsset=function(){
                straigeparent.intoGraph(function(ids){
                    var la=0;
                    var overlay = new mxCellOverlay(new mxImage('/static/themes/skin/kea-u1142/images/green-dot.gif', 24, 24), '<div>1231</div>','right','button');
                    var overlay1 = new mxCellOverlay(new mxImage('/static/themes/skin/kea-u1142/images/dot.gif', 24, 24), '<div>1231</div>','right','bottom');
                    $(ids).each(function(i,d){
                        switch(d.device_info.type_name){
                            case '未知':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'unknown'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'unknown_G');
                                break;
                            case 'PC':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'pc'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'pc_G');
                                break;
                            case '工程师站':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'engineer'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'engineer_G');
                                break;
                            case '操作员站':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'operater'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'operater_G');
                                break;
                            case 'PLC':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'plc'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'plc_G');
                                break;
                            case 'RTU':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'RTU'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'RTU_G');
                                break;
                            case 'HMI':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'hmi'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'hmi_G');
                                break;
                            case '网络设备':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'netdevice'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'netdevice_G');
                                break;
                            case '服务器':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'server'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'server_G');
                                break;
                            case 'OPC服务器':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'opcser'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'opcser_G');
                                break;
                            case 'DCS':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'dcs'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'dcs_G');
                                break;
                            case '安全设备':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'secdev'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'secdev_G');
                                break;
                            case 'IED':
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'ied'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'ied_G');
                                break;
                            default:
                                var cell = d.device_info.online?new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'cusdev'):new mxCell(d.name, new mxGeometry(la, 10, 110, 110), 'cusdev_G');
                                break;

                        }
                        if(d.device_info.unknown){
                            var scell = graph.insertVertex(cell, null, '', 1, 1, 13, 13, 'shape=label;spacingLeft=6;spacingRight=6;align=left;strokeWidth=1;strokeColor=white;fillColor=white;verticalAlign=top;imageAlign=center;imageWidth=13;imageHeight=13;imageVerticalAlign=middle;image=/static/themes/skin/kea-u1142/images/warning.gif;', true);
                            scell.geometry.offset = new mxPoint(-8, -8);
                            scell.subNode=true;
                            scell.setConnectable(false);
                        }
                        cell.id= d.id;
                        cell.geometry.setTerminalPoint(new mxPoint(50, 150), true);
                        cell.geometry.setTerminalPoint(new mxPoint(150, 50), false);
                        cell.vertex = true;
                        //d.device_info.online?null:graph.setCellWarning(cell, 'Tooltip');
                        cell.alarm_info=d.alarm_info,cell.device_info=d.device_info,cell.unread=d.unread,cell.unitId= d.id;
                        //cell.data={name:'device: '+ d.name+'\ncount: '+ d.info[0]+'\nblacklist: '+ d.info[1]+'\nwhiteList: '+ d.info[2]};
                        la+=110;

                        //graph.addCellOverlay(cell, d.device_info.online?overlay:overlay1);
                        cell = graph.addCell(cell);
                    });
                    graph.refresh();
                    var loadIdx=layer.load(2,{shade:[0.4, '#fff']});
                    var enc = new mxCodec();
                    var node = enc.encode(graph.getModel());
                    textNode = mxUtils.getPrettyXml(node);
                    textNode=textNode.replace(/[\t\r\n]|\s{2}/g,'');
                    textNode=textNode=='<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>'?'':textNode;
                    promise=URLManager.getInstance().ajaxCallByURL(xmllink,'PUT',{xml_info:textNode});
                    promise.done(function(result) {
                        if (result.status > 0) {
                            layer.close(loadIdx);
                        } else {
                            layer.alert('保存失败(updatexml)', {icon: 5});
                            layer.close(loadIdx);
                        }
                    });
                    promise.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + '-' + err.msg);
                        layer.alert(err.msg, {icon: 5});
                        layer.close(loadIdx);
                    });
                });
            };


            straigeparent.updateByTime = function (updateCells) {


                var link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_TOPO_ASSET;
                var promise = URLManager.getInstance().ajaxCall(link);
                promise.fail(function (jqXHR, textStatus, err) {
                    console.log(textStatus + " - " + err.msg);
                });
                promise.done(function(res){
                    if(res.status){
                        updateCells&&updateCells(res.dev_info);
                    }
                });

            };

            mxEvent.addListener(intoTopo, 'click', function()
            {
                straigeparent.addAsset();
            });
            /*mxEvent.addListener(resetInput, 'click', function()
            {
                /!*var tempNode='<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>';
                 var doc = mxUtils.parseXml(tempNode);
                 var dec = new mxCodec(doc);
                 dec.decode(doc.documentElement, graph.getModel());*!/

                console.log();


                var data=[
                    {name:'调度间1',id:23,type:0,info:[60,600,55]},
                    {name:'调度间2',id:24,type:1,info:[60,600,55]}
                ];
                var la=0;
                var overlay = new mxCellOverlay(new mxImage('/static/themes/skin/kea-u1142/images/green-dot.gif', 24, 24), '<div>1231</div>','right','middle');
                var overlay1 = new mxCellOverlay(new mxImage('/static/themes/skin/kea-u1142/images/dot.gif', 24, 24), '<div>1231</div>','right','middle');
                $(data).each(function(i,d){
                    if(d.type){
                        var cell = new mxCell(d.name, new mxGeometry(la, 10, 80, 130), 'image');
                    }else{
                        var cell = new mxCell(d.name, new mxGeometry(la, 10, 80, 130), 'top');
                    }
                    var overlay = new mxCellOverlay(new mxText(d.name, new mxRectangle(), mxConstants.ALIGN_LEFT, mxConstants.ALIGN_BOTTOM));
                    cell.id= String(d.id);
                    cell.geometry.setTerminalPoint(new mxPoint(50, 150), true);
                    cell.geometry.setTerminalPoint(new mxPoint(150, 50), false);
                    cell.vertex = true;
                    cell.data={name: d.name,info: d.info,type: d.type};
                    //cell.data={name:'device: '+ d.name+'\ncount: '+ d.info[0]+'\nblacklist: '+ d.info[1]+'\nwhiteList: '+ d.info[2]};
                    la+=85;

                    graph.addCellOverlay(cell, overlay);
                    cell = graph.addCell(cell);

                });

                var data1=[
                    {name:'工作站1',id:11,type:1,power:1,info:[0,0,0]},
                    {name:'集控室1',id:22,type:0,power:1,info:[0,0,0]},
                    {name:'工程师站1',id:33,type:1,power:1,info:[0,0,0]},
                    {name:'调度室1',id:44,type:0,power:1,info:[0,0,0]},
                    {name:'集控室1',id:66,type:0,power:0,info:[0,0,0]},
                    {name:'工程师站1',id:77,type:1,power:1,info:[0,0,0]},
                    {name:'调度室1',id:88,type:0,power:1,info:[0,0,0]},
                    {name:'分配站1',id:55,type:1,power:1,info:[0,0,0]}];
                $.each(graph.model.cells,function(k,v){
                    $(data1).each(function(ii,dd){
                        if(k==dd.id){
                            graph.model.setValue(v, dd.name);
                            graph.model.setStyle(v, 'image');


                            graph.clearCellOverlays(v);
                            graph.addCellOverlay(v, overlay1);
                            dd.power?null:graph.setCellWarning(v, 'Tooltip');
                            //graph.addCellOverlay(v, overlay);
                            //graph.removeCellOverlay(v, overlay);
                            v.data={name: dd.name,info: dd.info,type: dd.type}
                        }
                    });
                });

                /!*var cell = new mxCell('工作站', new mxGeometry(0, 0, 80, 130), 'image');
                 cell.geometry.setTerminalPoint(new mxPoint(50, 150), true);
                 cell.geometry.setTerminalPoint(new mxPoint(150, 50), false);*!/

                //cell.geometry.relative = true;
                //cell.vertex = true;
                //cell.edge = true;

                //cell = graph.addCell(cell);
                //graph.fireEvent(new mxEventObject('cellsInserted', 'cells', [cell]));


                /!*graph.getModel().beginUpdate();
                 var state = graph.insertVertex(parent,80, 'hi',  80, 0, 80, 130,'image');
                 graph.getModel().endUpdate();

                 var s = graph.gridSize;
                 graph.setSelectionCells(graph.moveCells([state.cell], s, s, true));*!/
                /!*mxEvent.consume(evt);
                 this.destroy();*!/



                //parseNode('',data);

                //graph.refresh();


            });*/

            graph.addMouseListener(
                {
                    currentState: null,
                    currentIconSet: null,
                    mouseDown: function(sender, me)
                    {
                        // Hides icons on mouse down
                        if (this.currentState != null)
                        {
                            //this.dragLeave(me.getEvent(), this.currentState);
                            var cell=this.currentState.cell;
                            if(!cell.value){
                                ipts.eq(0).val(''),ipts.eq(1).val(''),ipts.eq(2).val(''),ipts.eq(3).val(''),ipts.eq(4).val('');selt.val('');
                                btns.eq(1).off().prop({disabled:false});
                                return;
                            }
                            ipts.eq(0).val(cell.value),ipts.eq(1).val(cell.device_info.ip_addr),ipts.eq(2).val(cell.device_info.mac_addr),ipts.eq(3).val(cell.device_info.vender_info),ipts.eq(4).val(cell.device_info.mode);selt.eq(0).val(cell.device_info.dev_type);selt.eq(1).val(cell.device_info.unknown);
                            if(!cell.device_info.unknown){
                                selt.eq(1).addClass('dis');
                                selt.eq(1).prop({disabled:true});
                            }else{
                                selt.eq(1).removeClass('dis');
                                selt.eq(1).prop({disabled:false});
                            }
                            btns.eq(0).unbind().bind('click',function(){
                                if(!ipts.eq(0).val()||!ipts.eq(2).val()){return;}
                                straigeparent.graphDetail(cell);
                            });
                            btns.eq(1).unbind().bind('click',function(){
                                var loadIdx=layer.load(2,{shade:[0.4, '#fff']});
                                if(!ipts.eq(0).val()||!ipts.eq(2).val()){layer.close(loadIdx);return;}
                                //判断厂商、类型、型号是否有变化
                                if( (cell.device_info.vender_info!=ipts.eq(3).val()) || (cell.device_info.type_name!=selt.eq(0).find("option:selected").text()) || (cell.device_info.mode!=ipts.eq(4).val())){
                                    cell.device_info.auto_flag=0;
                                }
                                var promise=URLManager.getInstance().ajaxCallByURL(updateLink,'PUT',{
                                    id:Number(cell.unitId),
                                    ip:ipts.eq(1).val(),
                                    mac:ipts.eq(2).val(),
                                    name:ipts.eq(0).val(),
                                    type:Number(selt.eq(0).val()),
                                    vender:ipts.eq(3).val(),
                                    unknown:Number(selt.eq(1).val()),
                                    mode:ipts.eq(4).val(),
                                    auto_flag:cell.device_info.auto_flag
                                });
                                promise.done(function(result) {
                                    if (result.status > 0) {
                                        layer.close(loadIdx);
                                        graph.model.setValue(cell, ipts.eq(0).val());
                                        if(Number(selt.eq(0).val())>12){
                                            cell.device_info.online?graph.model.setStyle(cell, 'cusdev'):graph.model.setStyle(cell, 'cusdev_G');
                                        }else{
                                            switch(Number(selt.eq(0).val())){
                                                case 0:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'unknown'):graph.model.setStyle(cell, 'unknown_G');
                                                    break;
                                                case 1:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'pc'):graph.model.setStyle(cell, 'pc_G');
                                                    break;
                                                case 2:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'engineer'):graph.model.setStyle(cell, 'engineer_G');
                                                    break;
                                                case 3:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'operater'):graph.model.setStyle(cell, 'operater_G');
                                                    break;
                                                case 4:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'plc'):graph.model.setStyle(cell, 'plc_G');
                                                    break;
                                                case 5:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'RTU'):graph.model.setStyle(cell, 'RTU_G');
                                                    break;
                                                case 6:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'hmi'):graph.model.setStyle(cell, 'hmi_G');
                                                    break;
                                                case 7:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'netdevice'):graph.model.setStyle(cell, 'netdevice_G');
                                                    break;
                                                case 8:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'server'):graph.model.setStyle(cell, 'server_G');
                                                    break;
                                                case 9:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'opcser'):graph.model.setStyle(cell, 'opcser_G');
                                                    break;
                                                case 10:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'dcs'):graph.model.setStyle(cell, 'dcs_G');
                                                    break;
                                                case 11:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'secdev'):graph.model.setStyle(cell, 'secdev_G');
                                                    break;
                                                case 12:
                                                    cell.device_info.online?graph.model.setStyle(cell, 'ied'):graph.model.setStyle(cell, 'ied_G');
                                                    break;
                                            }
                                        }
                                        cell.device_info.dev_type=selt.val();
                                        cell.device_info.type_name=selt.eq(0).find("option:selected").text();
                                        cell.device_info.vender_info=ipts.eq(3).val();
                                        cell.device_info.mode=ipts.eq(4).val();
                                        if(!parseInt(selt.eq(1).val())&&cell.children){
                                            cell.device_info.unknown=0;
                                            graph.removeCells(cell.children);
                                            selt.eq(1).addClass('dis');
                                            selt.eq(1).prop({disabled:true});
                                        }
                                        var enc = new mxCodec();
                                        var node = enc.encode(graph.getModel());
                                        textNode = mxUtils.getPrettyXml(node);
                                        textNode=textNode.replace(/[\t\r\n]|\s{2}/g,'');
                                        textNode=textNode=='<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>'?'':textNode;
                                        promise=URLManager.getInstance().ajaxCallByURL(xmllink,'PUT',{xml_info:textNode});
                                        promise.done(function(result) {
                                            if (result.status > 0) {
                                                layer.close(loadIdx);
                                                layer.alert('修改成功', {icon: 6});
                                            } else {
                                                layer.alert(result.msg, {icon: 5});
                                                layer.close(loadIdx);
                                            }
                                        });
                                        promise.fail(function (jqXHR, textStatus, err) {
                                            console.log(textStatus + '-' + err.msg);
                                            layer.alert(err.msg, {icon: 5});
                                            layer.close(loadIdx);
                                        });
                                    } else {
                                        layer.alert(result.msg, {icon: 5});
                                        layer.close(loadIdx);
                                    }
                                });
                                promise.fail(function (jqXHR, textStatus, err) {
                                    console.log(textStatus + '-' + err.msg);
                                    layer.alert(err.msg, {icon: 5});
                                    layer.close(loadIdx);
                                });
                            });
                            this.currentState = null;
                        }else{
                            ipts.eq(0).val(''),ipts.eq(1).val(''),ipts.eq(2).val(''),ipts.eq(3).val(''),ipts.eq(4).val('');selt.val('');
                        }
                    },
                    mouseMove: function(sender, me)
                    {
                        if (this.currentState != null && (me.getState() == this.currentState ||
                            me.getState() == null))
                        {
                            var tol = iconTolerance;
                            var tmp = new mxRectangle(me.getGraphX() - tol,
                                me.getGraphY() - tol, 2 * tol, 2 * tol);

                            if (mxUtils.intersects(tmp, this.currentState))
                            {
                                return;
                            }
                        }

                        var tmp = graph.view.getState(me.getCell());

                        // Ignores everything but vertices
                        if (graph.isMouseDown || (tmp != null && !graph.getModel().isVertex(tmp.cell)))
                        {
                            tmp = null;
                        }

                        if (tmp != this.currentState)
                        {
                            if (this.currentState != null)
                            {
                                this.dragLeave(me.getEvent(), this.currentState);
                            }

                            this.currentState = tmp;

                            if (this.currentState != null)
                            {
                                this.dragEnter(me.getEvent(), this.currentState);
                            }
                        }
                    },
                    mouseUp: function(sender, me) { },
                    dragEnter: function(evt, state)
                    {
                        if (this.currentIconSet == null)
                        {
                            //this.currentIconSet = new mxIconSet(state);

                            //graph.getTooltipForCell(state);
                        }
                    },
                    dragLeave: function(evt, state)
                    {
                        if (this.currentIconSet != null)
                        {
                            this.currentIconSet.destroy();
                            this.currentIconSet = null;
                        }
                    }
                });

            // Enables rubberband selection
            new mxRubberband(graph);

            // Gets the default parent for inserting new cells. This
            // is normally the first child of the root (ie. layer 0).
            var parent = graph.getDefaultParent();

            // 给物体添加报警
            var addOverlay = function(id, state){
                // 获取ID单元
                var cell = graph.getModel().getCell(id);
                // 修改有报警物体的样式
                graph.setCellStyles(mxConstants.STYLE_FILLCOLOR, "#FF5500", [cell]);
                graph.setCellStyles(mxConstants.STYLE_FONTCOLOR, "#FFFFFF", [cell]);
                // 添加告警
                graph.addCellOverlay(cell, createOverlay(graph.warningImage, '状态: '+state));
            };

            // 创建告警信息
            var createOverlay = function(image, tooltip){
                //function mxCellOverlay(image,tooltip,align,verticalAlign,offset,cursor)
                //image图片，tooltip提示，align位置，verticalAlign竖直位置
                var overlay = new mxCellOverlay(image, tooltip);
                overlay.addListener(mxEvent.CLICK, function(sender, evt){
                    mxUtils.alert(tooltip);
                });
                return overlay;
            };


            // Adds cells to the model in a single step
            graph.getModel().beginUpdate();
            try
            {
                function parseNode(textNode,data){
                    if(textNode){
                        var doc = mxUtils.parseXml(textNode);
                        var dec = new mxCodec(doc);
                        dec.decode(doc.documentElement, graph.getModel());
                        straigeparent.launchStatusCheck=function() {
                            straigeparent.updateByTime(function (newDate) {
                                $.each(graph.model.cells, function (k, v) {
                                    $(newDate).each(function (i, dd) {
                                        var cell = v;
                                        if (v.unitId == dd.id) {
                                            switch (dd.device_info.type_name) {
                                                case '未知':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'unknown') : graph.model.setStyle(cell, 'unknown_G');
                                                    break;
                                                case 'PC':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'pc') : graph.model.setStyle(cell, 'pc_G');
                                                    break;
                                                case '工程师站':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'engineer') : graph.model.setStyle(cell, 'engineer_G');
                                                    break;
                                                case '操作员站':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'operater') : graph.model.setStyle(cell, 'operater_G');
                                                    break;
                                                case 'PLC':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'plc') : graph.model.setStyle(cell, 'plc_G');
                                                    break;
                                                case 'RTU':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'RTU') : graph.model.setStyle(cell, 'RTU_G');
                                                    break;
                                                case 'HMI':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'hmi') : graph.model.setStyle(cell, 'hmi_G');
                                                    break;
                                                case '网络设备':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'netdevice') : graph.model.setStyle(cell, 'netdevice_G');
                                                    break;
                                                case '服务器':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'server') : graph.model.setStyle(cell, 'server_G');
                                                    break;
                                                case 'OPC服务器':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'opcser') : graph.model.setStyle(cell, 'opcser_G');
                                                    break;
                                                case 'DCS':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'dcs') : graph.model.setStyle(cell, 'dcs_G');
                                                    break;
                                                case '安全设备':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'secdev') : graph.model.setStyle(cell, 'secdev_G');
                                                    break;
                                                case 'IED':
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'ied') : graph.model.setStyle(cell, 'ied_G');
                                                    break;
                                                default:
                                                    dd.device_info.online ? graph.model.setStyle(cell, 'cusdev') : graph.model.setStyle(cell, 'cusdev_G');
                                                    break;
                                            }
                                            cell.alarm_info = dd.alarm_info, cell.device_info = dd.device_info, cell.unread = dd.unread, cell.name=dd.name,cell.value=dd.name,cell.unitId = dd.id;
                                        }
                                    })
                                });
                                graph.refresh();
                            });
                        };
                        clearInterval(gloTimer.updateTopoTimer);
                        gloTimer.updateTopoTimer=setInterval(straigeparent.launchStatusCheck,30000);
                        straigeparent.launchStatusCheck();
                    }else{
                        var la=0;
                        $(data).each(function(i,d){
                            var overlay = new mxCellOverlay(new mxImage('/static/themes/skin/kea-u1142/images/green-dot.gif', 24, 24), '<div>1231</div>','right','bottom');
                            var overlay1 = new mxCellOverlay(new mxImage('/static/themes/skin/kea-u1142/images/dot.gif', 24, 24), '<div>1231</div>','right','bottom');

                            //overlay.align = mxConstants.ALIGN_RIGHT;
                            //overlay.verticalAlign = mxConstants.ALIGN_TOP;
                            switch(d.device_info.type_name){
                                case '未知':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'unknown'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'unknown_G');
                                    break;
                                case 'PC':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'pc'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'pc_G');
                                    break;
                                case '工程师站':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'engineer'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'engineer_G');
                                    break;
                                case '操作员站':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'operater'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'operater_G');
                                    break;
                                case 'PLC':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'plc'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'plc_G');
                                    break;
                                case 'RTU':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'RTU'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'RTU_G');
                                    break;
                                case 'HMI':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'hmi'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'hmi_G');
                                    break;
                                case '网络设备':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'netdevice'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'netdevice_G');
                                    break;
                                case '服务器':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'server'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'server_G');
                                    break;
                                case 'OPC服务器':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'opcser'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'opcser_G');
                                    break;
                                case 'DCS':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'dcs'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'dcs_G');
                                    break;
                                case '安全设备':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'secdev'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'secdev_G');
                                    break;
                                case 'IED':
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'ied'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'ied_G');
                                    break;
                                default:
                                    var v1 = d.device_info.online?graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'cusdev'):graph.insertVertex(parent,d.id, d.name, la, 10, 110, 110,'cusdev_G');
                                    break;
                            }
                            if(d.device_info.unknown){
                                var scell = graph.insertVertex(v1, null, '', 1, 1, 13, 13, 'align=left;strokeWidth=1;strokeColor=white;shape=ellipse;verticalAlign=top;fillColor=white;image=/static/themes/skin/kea-u1142/images/operater.png;spacingLeft=6;spacingRight=6', true);
                                scell.geometry.offset = new mxPoint(-8, -8);
                                scell.subNode=true;
                                scell.setConnectable(false);
                            }
                            //d.device_info.online?null:graph.setCellWarning(v1, 'Tooltip');
                            v1.alarm_info=d.alarm_info,v1.device_info=d.device_info,v1.unread=d.unread,v1.unitId= d.id;

                            //graph.addCellOverlay(v1, d.device_info.online?overlay:overlay1);
                            /*overlay.addListener(mxEvent.CLICK, mxUtils.bind(this, function(sender, evt)
                            {
                                //addChild(graph, cell);
                                graph.getTooltipForCell(v1);
                            }));*/
                            la+=110;
                        });
                    }
                }
                parseNode(xml,data);
                /*var v2 = graph.insertVertex(parent, 7, 'World!', 200, 150, 80, 130,'top');
                 v2.data={name:'v3openElement',value:1231};
                 var v2 = graph.insertVertex(parent, 8, 'World!', 230, 180, 80, 130,'top');
                 v2.data={name:'v2openElement',value:1231};
                 var e1 = graph.insertEdge(parent, null, '', v1, v2);*/

            }
            finally
            {
                // Updates the display
                graph.getModel().endUpdate();
            }
        }
}

TopographController.prototype.load = function () {
    try {

        var parent=this,link=APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_TOPO_ASSET;
        var promise = URLManager.getInstance().ajaxCall(link);
        var loadIdx=layer.load(2,{shade:[0.4, '#fff']});

        // Defines an icon for creating new connections in the connection handler.
        // This will automatically disable the highlighting of the source vertex.
        mxConnectionHandler.prototype.connectImage = new mxImage('/static/themes/skin/kea-u1142/images/connector.gif', 16, 16);

        // Defines a new class for all icons
        function mxIconSet(state)
        {
            this.images = [];
            var graph = state.view.graph;

            // Icon1
            var img = mxUtils.createImage('/static/themes/skin/kea-u1142/images/copy.png');
            img.setAttribute('title', 'Duplicate');
            img.style.position = 'absolute';
            img.style.cursor = 'pointer';
            img.style.width = '16px';
            img.style.height = '16px';
            img.style.left = (state.x + state.width) + 'px';
            img.style.top = (state.y + state.height) + 'px';

            mxEvent.addGestureListeners(img,
                mxUtils.bind(this, function(evt)
                {
                    var s = graph.gridSize;
                    graph.setSelectionCells(graph.moveCells([state.cell], s, s, true));
                    mxEvent.consume(evt);
                    this.destroy();
                })
            );

            state.view.graph.container.appendChild(img);
            this.images.push(img);

            // Delete
            var img = mxUtils.createImage('/static/themes/skin/kea-u1142/images/delete2.png');
            img.setAttribute('title', 'Delete');
            img.style.position = 'absolute';
            img.style.cursor = 'pointer';
            img.style.width = '16px';
            img.style.height = '16px';
            img.style.left = (state.x + state.width) + 'px';
            img.style.top = (state.y - 16) + 'px';

            mxEvent.addGestureListeners(img,
                mxUtils.bind(this, function(evt)
                {
                    // Disables dragging the image
                    mxEvent.consume(evt);
                })
            );

            mxEvent.addListener(img, 'click',
                mxUtils.bind(this, function(evt)
                {
                    graph.removeCells([state.cell]);
                    mxEvent.consume(evt);
                    this.destroy();
                })
            );

            state.view.graph.container.appendChild(img);
            this.images.push(img);
        };

        mxIconSet.prototype.destroy = function()
        {
            if (this.images != null)
            {
                for (var i = 0; i < this.images.length; i++)
                {
                    var img = this.images[i];
                    img.parentNode.removeChild(img);
                }
            }

            this.images = null;
        };

        // Program starts here. Creates a sample graph in the
        // DOM node with the specified ID. This function is invoked
        // from the onLoad event handler of the document (see below).
        mxGraph.prototype.getTooltip=function(state,node,x,y){
            if(!state.cell.subNode){
                if(state.cell.vertex){
                    var d=state.cell.alarm_info?state.cell.alarm_info:"";
                    return d?'安全事件总数: '+ d.evt_count+'\n黑名单告警: '+ d.bl_count+'\n白名单告警: '+
                    d.wl_count+'\nIP/MAC告警: '+ d.im_count+'\nMAC过滤告警: '+
                    d.mf_count+'\n流量告警: '+ d.flow_count+'\n资产告警: '+ d.dev_count+'\n不合规报文告警: '+ d.pcap_count:'设备组';
                }else{
                    return (state.cell.source.value?state.cell.source.value:'设备组')+'<===>'+(state.cell.target.value?state.cell.target.value:'设备组');
                }
            }
        };
        mxShape.prototype.constraints = [
            new mxConnectionConstraint(new mxPoint(0.25, 0), true),
            new mxConnectionConstraint(new mxPoint(0.5, 0), true),
            new mxConnectionConstraint(new mxPoint(0.75, 0), true),
            new mxConnectionConstraint(new mxPoint(0, 0.25), true),
            new mxConnectionConstraint(new mxPoint(0, 0.5), true),
            new mxConnectionConstraint(new mxPoint(0, 0.75), true),
            new mxConnectionConstraint(new mxPoint(1, 0.25), true),
            new mxConnectionConstraint(new mxPoint(1, 0.5), true),
            new mxConnectionConstraint(new mxPoint(1, 0.75), true),
            new mxConnectionConstraint(new mxPoint(0.25, 1), true),
            new mxConnectionConstraint(new mxPoint(0.5, 1), true),
            new mxConnectionConstraint(new mxPoint(0.75, 1), true)];
        /*mxGraph.prototype.getTooltipForCell=function(cell){
         if(cell.cell){
         return 'hello world!';
         }
         }*/

        promise.fail(function (jqXHR, textStatus, err) {
            layer.alert(err.msg, { icon: 2 });
            console.log(textStatus + " - " + err.msg);
        });
        promise.done(function(res){
            if(res.status){
                layer.close(loadIdx);
                parent.main(res.dev_info,res.xml_info,document.getElementById('graphContainer'));
            }else{
                layer.alert(res.msg, { icon: 5 });
                layer.close(loadIdx);
            }
        });

    }
    catch (err) {
        console.error("ERROR - ResetSystemController.load() - Unable to load: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.topo.TopographController", TopographController);