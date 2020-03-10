function PcapController(controller,viewHandle, elementId) {
    this.controller = controller;    
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;
    this.isRebootSuccess = true;
    this.isResetSuccess = true;

    this.pPcapSize = "#" + this.elementId + "_divSize";
    this.pPcapTime = "#" + this.elementId + "_divTime";
    this.pPcapFilename = "#" + this.elementId + "_divFilename";

    this.pBtnStartPcap = "#" + this.elementId + "_btnStartPcap";
    this.pDivProgressbar = "#" + this.elementId + "_divProgressbar";

    this.pBtnRefresh="#" + this.elementId + "_btnRefresh";
    this.pBtnDelete="#" + this.elementId + "_btnDelList";

    this.pPcaplist="#" + this.elementId + "_tdPcapList";
    this.pSelectAll="#" + this.elementId + "_selectAll";
    this.pPcapCount="#" + this.elementId + "_lblPcapRuleCount";

    this.pDeviceController = controller;
}

PcapController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_PCAP), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - PcapController.init() - Unable to initialize: " + err.message);
    }
}

PcapController.prototype.initControls = function () {
    try {
        var parent = this;
        $(parent.pSelectAll).click(function(){
            parent.checkSwitch=!parent.checkSwitch;
            $(parent.pPcaplist).find('input').filter('.selflag').prop('checked',parent.checkSwitch);
        });
        $(parent.pBtnRefresh).click(function(){
            parent.selectPcapList();
        })
        $(parent.pBtnDelete).on("click", function () {
            parent.preDelete=[];
            $(parent.pPcaplist).find('tbody input[type=checkbox]').filter('.selflag').each(function(i,d){
                if($(d).prop('checked')){
                    parent.preDelete.push($(d).data('id'));
                }
            });
            var delIds=parent.preDelete;
            if(parent.preDelete.length<=0){
                layer.alert('请选择需要删除的文件！',{icon:2});
                return;
            }
            layer.confirm('确定要删除么？',{icon:7,title:'注意：'}, function(index) {
                layer.close(index);
                parent.delPcapList(delIds);
            })
        });
    }
    catch (err) {
        console.error("ERROR - PcapController.initControls() - Unable to initialize control: " + err.message);
    }
}

PcapController.prototype.load = function () {
    try {
        var parent = this;
        parent.getPcapStatus();
        parent.selectPcapList();
    }
    catch (err) {
        console.error("ERROR - PcapController.load() - Unable to load: " + err.message);
    }
}

PcapController.prototype.getPcapStatus = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_PCAP_STATUS;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        var cur_time = parseInt(result.pcap_cur_time);//当前下载时间
                        var orig_time = parseInt(result.pcap_orig_time);//期望下载时间
                        if (cur_time >= orig_time) {
                            parent.setupstatus(); 
                        }else{
                            $(parent.pPcapSize).val(parseInt(result.pcap_orig_size));
                            $(parent.pPcapTime).val(parent.SecToTime(orig_time));
                            $(parent.pPcapFilename).val(result.pcap_name.replace(/.pcap/g,''));
                            parent.setupProgress(orig_time,cur_time,result.pcap_cur_size);    
                        } 
                        break;
                    case 0: 
                        parent.setupstatus(); 
                        break;
                    default: 
                        layer.alert("获取学习状态失败", { icon: 5 }); 
                        parent.setupstatus(); 
                        break;
                }
            }
            else {
                parent.setupstatus(); 
                layer.alert("获取学习状态失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - PcapController.getPcapStatus() - Unable to get pcap status: " + err.message);
    }
}

PcapController.prototype.setupProgress = function (total, duration,file_size) {
    var parent = this;
    $(this.pDivProgressbar).css("display", "block");
    $(this.pBtnStartPcap).text("停止抓包").unbind("click");
    var progressbar = $("#progressbar");
    progressLabel = $(".progress-label");
    var label = "持续抓包时长:";
    var filesize=file_size;
    progressbar.progressbar({
        value: duration / total * 100,
        max: 100,
        min: 0,
        change:function(){
            progressLabel.text(label  + parent.SecToTime(duration));
            progressLabel.append(", 当前文件大小:<span id='file_size'>"+parent.KBtoMB(filesize)+"<span>")
        },
        complete: function () {
            parent.setupstatus();
            parent.selectPcapList();
        }
    });
    progressLabel.text(label  + parent.SecToTime(duration));
    progressLabel.append(", 当前文件大小:<span id='file_size'>"+parent.KBtoMB(filesize)+"<span>")
    parent.controller.pcapTimer = setInterval(function progress() { 
        if (duration < total) {
            $("#progressbar").progressbar("value", duration  / total * 100);
            if (duration >= total) {
                parent.setupstatus();
                parent.selectPcapList();
            }
            duration++;
        }
    }, 1000);
    parent.controller.watchstatus = setInterval(function progress() {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_PCAP_STATUS;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && result.status==0) {
                parent.setupstatus();
                parent.selectPcapList();
            }else{
                filesize=result.pcap_cur_size;
            }
        });
    }, 5000);
    $(parent.pBtnStartPcap).click(function () {
        clearInterval(parent.controller.pcapTimer);
        clearInterval(parent.controller.watchstatus);
        parent.stopPcap();
    });
}

PcapController.prototype.selectPcapList = function () {
    var html = "";
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].SELECT_PCAP_LIST;
        var loadIndex = layer.load(2);
        var promise = URLManager.getInstance().ajaxCall(link, this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='5'>暂无数据</td></tr>";
            $(parent.pPcaplist+">tbody").html(html);
            layer.close(loadIndex);            
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                $(parent.pPcapCount).text(result.total);
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>"+"<input type='checkbox' class='chinput selflag' data-id='"+result.rows[i].id+"' id='"+result.rows[i].id+"' /><label for='"+result.rows[i].id+"'></label></td>";
                        html += "<td style='text-align:left;' title='" + result.rows[i].pcap_name.replace(/.pcap/g,'') + "'>" + result.rows[i].pcap_name.replace(/.pcap/g,'') + "</td>";
                        html += "<td>" + parent.KBtoMB(result.rows[i].pcap_cur_size) + "</td>";
                        html += "<td>" + parent.SecToTime(result.rows[i].pcap_cur_time) + "</td>";
                        html += "<td><button class='btn btn-default btn-xs btn-color-details' data-name='"+result.rows[i].pcap_name+"' id='" + result.rows[i].id + "'><i class='fa fa-level-down'></i>下载</button></td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='5'>暂无数据</td></tr>";
                }
            }
            else{
                html += "<tr><td colspan='5'>暂无数据</td></tr>";
            }
            $(parent.pPcaplist + ">tbody").html(html);
            layer.close(loadIndex);
            $(parent.pPcaplist).find("button").on("click", function (event) {
                var filename=$(this).attr("data-name");
                window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].DOWNLOAD_PCAP  + '?loginuser='+JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']).username+'&pcap_name='+filename);
            });
        });
    }
    catch (err) {
        html += "<tr><td colspan='5'>暂无数据</td></tr>";
        $(parent.pPcaplist + ">tbody").html(html);
        console.error("ERROR - PcapController.selectPcapList() - Unable to get pcaplist: " + err.message);
    }
}

PcapController.prototype.startPcap = function () {
    var parent = this;
    try {
        var size=$(parent.pPcapSize).val();
        var time=$(parent.pPcapTime).val();
        var filename=$(parent.pPcapFilename).val();
        var timearr=time.split(":");
        var orig_time=parseInt(timearr[0])*60*60+parseInt(timearr[1])*60+parseInt(timearr[2]);
        if($.trim(size) == "") {
            layer.alert("文件大小不能为空", { icon: 5 });
            return;
        }
        if($.trim(size)>500) {
            layer.alert("文件大小不能超过500", { icon: 5 });
            $(parent.pPcapSize).val("");
            return;
        }
        if($.trim(time) == "") {
            layer.alert("抓包时长不能为空", { icon: 5 });
            return;
        }
        if($.trim(filename) == "") {
            layer.alert("文件名称不能为空", { icon: 5 });
            return; 
        }
        if(!/^\w+$/.test(filename)){
            layer.alert("仅允许输入数字、字母、下划线", { icon: 5 });
            $(parent.pPcapFilename).val('');
            return; 
        }
        if(orig_time>43200){
            layer.alert("抓包时长不超过12:00:00", { icon: 5 });
            $(parent.pPcapTime).val('12:00:00');
            return; 
        }
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var para = { pcap_orig_size: size, pcap_orig_time:orig_time, pcap_name: filename };
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].START_PCAP;
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
                        parent.getPcapStatus();
                        break;
                    default: 
                        layer.alert(result.msg, { icon: 5 }); 
                        parent.getPcapStatus();
                        break;
                }
            }
            else {
                layer.alert("开始抓包失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - PcapController.startPcap() - Unable to start pcap: " + err.message);
    }
}

PcapController.prototype.setupstatus = function () {
    var parent = this;
    $(this.pDivProgressbar).css("display", "none");
    $(this.pBtnStartPcap).text("开始抓包").unbind("click");
    $(parent.pBtnStartPcap).click(function(){
        parent.startPcap();
    });
    $(parent.pPcapSize).val('');
    $(parent.pPcapTime).val('');
    $(parent.pPcapFilename).val('');
    clearInterval(parent.controller.pcapTimer);
    clearInterval(parent.controller.watchstatus);
}

PcapController.prototype.SecToTime = function (secend) {
    var h=Math.floor(secend/60/60),
        m=Math.floor((secend-h*60*60)/60)
        s=secend-m*60-h*60*60;
    h=(/^\d$/g).test(h) ? `0${h}` : h;
    m=(/^\d$/g).test(m) ? `0${m}` : m;
    s=(/^\d$/g).test(s) ? `0${s}` : s;
    return h+":"+m+":"+s;
}
PcapController.prototype.KBtoMB = function (kb) {
    if(kb>1024){
        return (kb/1024).toFixed(2)+'MB';
    }else{
        return kb+'KB';
    } 
}

PcapController.prototype.delPcapList = function (delIds) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].DELETE_PCAP;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"DELETE",{id:delIds.join(',')});
        promise.fail(function (jqXHR, textStatus, err) {
            layer.alert("删除失败", { icon: 2 });
            layer.close(loadIndex);
            console.log(textStatus + " - " + err.msg);
        });
        promise.done(function(res){
            if(res.status){
                layer.alert("删除成功", { icon: 6 });
                parent.selectPcapList();
                if($(parent.pSelectAll).is(':checked')){
                    $(parent.pSelectAll).prop('checked',false);
                    parent.checkSwitch=false;
                    $(parent.pPcaplist).find('input').prop('checked',parent.checkSwitch);
                }
                layer.close(loadIndex);
            }else{
                layer.close(loadIndex);layer.alert("删除失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - PcapController.delPcap() - Unable to delete PcapList: " + err.message);
    }
}

PcapController.prototype.stopPcap = function () {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].STOP_PCAP;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            layer.alert("系统服务忙", { icon: 2 });
            layer.close(loadIndex);
            console.log(textStatus + " - " + err.msg);
        });
        promise.done(function(res){
            if(res.status){
                parent.getPcapStatus();
                parent.selectPcapList();
            }else{
                layer.close(loadIndex);
                layer.alert("停止抓包失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - PcapController.stopPcap() - Unable to stop pcap: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.PcapController", PcapController);