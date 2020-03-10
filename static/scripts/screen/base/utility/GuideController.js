function GuideController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.step = 1;
    this.displayTextTimer = null;

    this.pBtnPrev = ".btn-guidestyle.btn-g-pre";
    this.pBtnNext = "#" + this.elementId + "_btnNext";
    this.pBtnOver = ".btn-guidestyle.btn-g-over";
    this.pBtnClose = ".btn-g-style.btn-g-close";
    this.pBtnAgain = ".btn-g-style.btn-g-again";
    this.pBtnEvent = ".arrowsbox";

}

GuideController.prototype.init = function (templateId) {
    try {
        var parent = this;
        TemplateManager.getInstance().requestTemplates([
                Constants.TEMPLATES.UTILITY_GUIDE_STEP_START,
                Constants.TEMPLATES.UTILITY_GUIDE_STEP1,
                Constants.TEMPLATES.UTILITY_GUIDE_STEP2,
                Constants.TEMPLATES.UTILITY_GUIDE_STEP3,
                Constants.TEMPLATES.UTILITY_GUIDE_STEP4,
                Constants.TEMPLATES.UTILITY_GUIDE_STEP5,
                Constants.TEMPLATES.UTILITY_GUIDE_STEP6,
                Constants.TEMPLATES.UTILITY_GUIDE_STEP7,
                Constants.TEMPLATES.UTILITY_GUIDE_STEP_END],
            function (templateResults) {
                parent.initShell(templateId);
                $(".nav-list li .nav-title").removeClass("active");
                $(".second-nav-list>li").removeClass("on");
                $(".second-nav").slideUp(300, function () {
                    $(".arrowsbox.pos-arrows01").css("top", $("ul.nav-list>li").eq(7).find(".fa.fa-cogs").offset().top-10 + "px");
                });
            }
        );
    }
    catch (err) {
        console.error("ERROR - GuideController.init() - Unable to initialize all templates: " + err.message);
    }
}

GuideController.prototype.initShell = function (templateId) {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(templateId), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
    }
    catch (err) {
        console.error("ERROR - GuideController.initShell() - Unable to initialize: " + err.message);
    }
}

GuideController.prototype.initControls = function () {
    try {
        var parent = this;

        $(this.pBtnPrev).on("click", function () {
            parent.step--;
            if (parent.step == 5) {
                parent.step = 3;
                $(".second-nav").eq(3).slideUp(300);
                $(".nav-list li .nav-title").removeClass("active");
                $(".nav-list>li").eq(7).find(".second-nav-list>li").eq(0).trigger("click");
            }
            parent.initShell(parent.getTemplateId(parent.step));
            parent.redictPage(parent.step);
        });
        $(this.pBtnNext).on("click", function () {
            parent.step++;
            parent.initShell(parent.getTemplateId(parent.step));
            parent.redictPage(parent.step);
        });
        $(this.pBtnClose).on("click", function () {
            parent.step = 1;
            parent.pViewHandle.html("");
            $("body").unbind("scroll");
            $(window).unbind("resize");
            parent.redictPage(parent.step);
        });
        $(this.pBtnOver).on("click", function () {
            parent.step = 1;
            parent.pViewHandle.html("");
            $("body").unbind("scroll");
            $(window).unbind("resize");
            parent.redictPage(parent.step);
        });
        $(this.pBtnAgain).on("click", function () {
            parent.step = 1;
            parent.initShell(parent.getTemplateId(parent.step));
            parent.redictPage(parent.step);
        });
        $(this.pBtnEvent).on("click", function () {
            parent.step++;
            parent.initShell(parent.getTemplateId(parent.step));
            parent.redictPage(parent.step);
        });

        $("body").on("scroll", function () {
            if (parent.step == 1) {
                $(".arrowsbox.pos-arrows01").css("top", $("ul.nav-list>li").eq(7).find(".fa.fa-cogs").offset().top - 10 + "px");
                $(".arrowsbox.pos-arrows01").css("left", $("ul.nav-list>li").eq(7).find(".fa.fa-cogs").offset().left + 60 + "px");
            }
            else if (parent.step == 2) {
                $(".arrowsbox.pos-arrows02").css("top", $("#device_basic_btnIPSetting").offset().top + "px");
                $(".arrowsbox.pos-arrows02").css("left", $("#device_basic_btnIPSetting").offset().left + "px");
            } else if (parent.step == 3) {
                $(".arrowsbox.pos-arrows03").css("top", $("#device_basic_btnDateTimeSetting").offset().top + "px");
                $(".arrowsbox.pos-arrows03").css("left", $("#device_basic_btnDateTimeSetting").offset().left + "px");
            } else if (parent.step == 4) {
                $(".arrowsbox.pos-arrows04").css("top", $("ul.nav-list>li").eq(3).find(".fa.fa-list").offset().top + "px");
                $(".arrowsbox.pos-arrows04").css("left", $("ul.nav-list>li").eq(3).find(".fa.fa-list").offset().left + "px");
            } else if (parent.step == 5) {
                $(".arrowsbox.pos-arrows041").css("top", $("ul.nav-list>li").eq(3).find("li").eq(0).offset().top + "px");
                $(".arrowsbox.pos-arrows041").css("left", $("ul.nav-list>li").eq(3).find("li").eq(0).offset().left + 50 + "px");
            } else if (parent.step == 6) {
                $(".arrowsbox.pos-arrows05").css("top", $("#whitelist_study_btnStudy").offset().top + "px");
                $(".arrowsbox.pos-arrows05").css("left", $("#whitelist_study_btnStudy").offset().left + "px");
            } else if (parent.step == 7) {
                $(".arrowsbox.pos-arrows06").css("top", $("#whitelist_study_chkAll").offset().top + "px");
                $(".arrowsbox.pos-arrows06").css("left", $("#whitelist_study_chkAll").offset().left + "px");
            } else if (parent.step == 8) {
                $(".arrowsbox.pos-arrows07").css("top", $("#whitelist_study_btnEnable").offset().top + "px");
                $(".arrowsbox.pos-arrows07").css("left", $("#whitelist_study_btnEnable").offset().left + "px");
            }
        });
        $(window).on("resize", function () {
            if (parent.step == 1) {
                $(".arrowsbox.pos-arrows01").css("top", $("ul.nav-list>li").eq(7).find(".fa.fa-cogs").offset().top-10 + "px");
                $(".arrowsbox.pos-arrows01").css("left", $("ul.nav-list>li").eq(7).find(".fa.fa-cogs").offset().left + 60 + "px");
            }
            else if (parent.step == 2) {
                $(".arrowsbox.pos-arrows02").css("top", $("#device_basic_btnIPSetting").offset().top + "px");
                $(".arrowsbox.pos-arrows02").css("left", $("#device_basic_btnIPSetting").offset().left + "px");
            } else if (parent.step == 3) {
                $(".arrowsbox.pos-arrows03").css("top", $("#device_basic_btnDateTimeSetting").offset().top + "px");
                $(".arrowsbox.pos-arrows03").css("left", $("#device_basic_btnDateTimeSetting").offset().left + "px");
            } else if (parent.step == 4) {
                $(".arrowsbox.pos-arrows04").css("top", $("ul.nav-list>li").eq(3).find(".fa.fa-list").offset().top + "px");
                $(".arrowsbox.pos-arrows04").css("left", $("ul.nav-list>li").eq(3).find(".fa.fa-list").offset().left+60 + "px");
            } else if (parent.step == 5) {
                $(".arrowsbox.pos-arrows041").css("top", $("ul.nav-list>li").eq(3).find("li").eq(0).offset().top + "px");
                $(".arrowsbox.pos-arrows041").css("left", $("ul.nav-list>li").eq(3).find("li").eq(0).offset().left+50 + "px");
            } else if (parent.step == 6) {
                $(".arrowsbox.pos-arrows05").css("top", $("#whitelist_study_btnStudy").offset().top + "px");
                $(".arrowsbox.pos-arrows05").css("left", $("#whitelist_study_btnStudy").offset().left + "px");
            } else if (parent.step == 7) {
                $(".arrowsbox.pos-arrows06").css("top", $("#whitelist_study_chkAll").offset().top + "px");
                $(".arrowsbox.pos-arrows06").css("left", $("#whitelist_study_chkAll").offset().left + "px");
            } else if (parent.step == 8) {
                $(".arrowsbox.pos-arrows07").css("top", $("#whitelist_study_btnEnable").offset().top + "px");
                $(".arrowsbox.pos-arrows07").css("left", $("#whitelist_study_btnEnable").offset().left + "px");
            }
            $(".btn-guidestyle.btn-g-pre").css("bottom", "90px");
            $(".btn-guidestyle.btn-g-over").css("position", "absolute").css("bottom", "20px");
        });
    }
    catch (err) {
        console.error("ERROR - GuideController.initControls() - Unable to initialize control: " + err.message);
    }
}

GuideController.prototype.redictPage = function (step) {
    try {
        var parent = this;
        switch (step) {
            case 1:
                if (parent.displayTextTimer != null) {
                    clearInterval(parent.displayTextTimer);
                }
                $(".second-nav").slideUp(300);
                $(".nav-list li .nav-title").removeClass("active");
                $(".second-nav-list>li").removeClass("on");
                $(".nav-list>li .nav-title").eq(0).trigger("click");
                break;
            case 2:
                $(".second-nav").eq(3).slideDown(300);
                $(".nav-list li .nav-title").removeClass("active");
                $(".nav-list li .nav-title").eq(7).addClass("active");
                $(".nav-list>li").eq(7).find(".second-nav-list>li").eq(0).trigger("click");
                $(".arrowsbox.pos-arrows02").css("display", "none");
                clearInterval(parent.displayTextTimer);
                var tmpTimer = setInterval(function () {
                    var divIP = $("#device_basic_formIP>div");
                    if (divIP.length > 1) {
                        //取消原有事件按钮
                        $("input").attr("disabled", "disabled");
                        $("#viewContainer").find("button").unbind("click");
                        $("#viewContainer").find("button").on("click", function () {                            
                            return false;
                        });
                        $("#viewContainer .row-cutbox>ul>li").unbind("click");
                        $("#viewContainer .row-cutbox>ul>li").on("click", function () {
                            return false;
                        });
                        clearInterval(tmpTimer);
                        $("#device_basic_formDatetime>div").eq(1).removeClass("highlight-border");
                        $("#device_basic_formIP>div").eq(1).addClass("highlight-border");
                        parent.displayTextTimer = setInterval(function () {
                            $("#device_basic_formIP>div").eq(1).toggleClass("highlight-border");
                        }, 500);
                        $("#device_basic_formIP>div input[type='text']").eq(0).typetype('192.168.1.100', {
                            e: 0.04,
                            t: 100,
                            callback: function () {
                                $("#device_basic_formIP>div input[type='text']").eq(1).typetype('255.255.255.0', {
                                    e: 0.04,
                                    t: 100,
                                    callback: function () {
                                        $("#device_basic_formIP>div input[type='text']").eq(2).typetype('192.168.1.1', {
                                            e: 0.04,
                                            t: 100,
                                            callback: function () {
                                                $(".arrowsbox.pos-arrows02").show();
                                                $(".arrowsbox.pos-arrows02").css("left", $("#device_basic_btnIPSetting").offset().left + "px");
                                                $(".arrowsbox.pos-arrows02").css("top", $("#device_basic_btnIPSetting").offset().top + "px");
                                                clearInterval(parent.displayTextTimer);
                                                $("#device_basic_formIP>div").eq(1).removeClass("highlight-border");
                                            }
                                        });
                                    }
                                });
                            }
                        });
                    }
                }, 500);
                break;
            case 3:
                $(".second-nav").eq(3).slideDown(300);
                $(".nav-list li .nav-title").removeClass("active");
                $(".nav-list li .nav-title").eq(7).addClass("active");
                $(".nav-list>li").eq(7).find(".second-nav-list>li").eq(0).addClass("on");
                clearInterval(parent.displayTextTimer);
                $(".arrowsbox.pos-arrows03").css("display", "none");
                $(".arrowsbox.pos-arrows03").hide();
                var tmpTimer = setInterval(function () {
                    var divIP = $("#device_basic_formDatetime>div");
                    if (divIP.length > 1) {
                        //取消原有事件按钮
                        $("input").attr("disabled", "disabled");
                        $("#viewContainer").find("button").unbind("click");
                        $("#viewContainer").find("button").on("click", function () {                            
                            return false;
                        });
                        $("#viewContainer .tabtitle>ul>li").unbind("click");
                        $("#viewContainer .tabtitle>ul>li").on("click", function () {                            
                            return false;
                        });
                        clearInterval(tmpTimer);
                        $("#device_basic_formIP>div").eq(1).removeClass("highlight-border");
                        $("#device_basic_formDatetime>div").eq(1).addClass("highlight-border");
                        parent.displayTextTimer = setInterval(function () {
                            $("#device_basic_formDatetime>div").eq(1).toggleClass("highlight-border");
                        }, 500);
                        var now = new Date($("#spanSystemTime").text().replace(/-/g, '/'));
                        $("#device_basic_formDatetime>div input[type='text']").eq(0).typetype(FormatterManager.formatDateFromLocale(now, "yyyy-MM-dd HH:mm:ss"), {
                            e: 0.04,
                            t: 100,
                            callback: function () {
                                $("#device_basic_formDatetime>div").eq(1).removeClass("highlight-border");
                                $(".arrowsbox.pos-arrows03").show();
                                $(".arrowsbox.pos-arrows03").css("left", $("#device_basic_btnDateTimeSetting").offset().left + "px");
                                $(".arrowsbox.pos-arrows03").css("top", $("#device_basic_btnDateTimeSetting").offset().top + "px");
                                clearInterval(parent.displayTextTimer);
                            }
                        });
                    }
                }, 500);
                break;
            case 4:
                $(".second-nav").slideUp(300);
                $(".nav-list li .nav-title").removeClass("active");
                $(".second-nav-list>li").removeClass("on");
                $(".arrowsbox.pos-arrows04").css("top", $("ul.nav-list>li").eq(3).find(".fa.fa-list").offset().top + "px");
                break;
            case 5:
                $(".second-nav").eq(0).slideDown(300);
                $(".nav-list li .nav-title").removeClass("active");
                $(".nav-list li .nav-title").eq(3).addClass("active");
                $(".arrowsbox.pos-arrows04").removeClass("pos-arrows04");
                $(".arrowsbox").addClass("pos-arrows041");
                $(".arrowsbox.pos-arrows041").css("top", $("ul.nav-list>li").eq(3).find("li").eq(0).offset().top + "px");
                break;
            case 6:
                $(".nav-list>li").eq(3).find(".second-nav-list>li").eq(0).trigger("click");
                $(".arrowsbox.pos-arrows05").hide();
                clearInterval(parent.displayTextTimer);
                var tmpTimer = setInterval(function () {
                    var div = $("#whitelist_study_tdWhitelistList");
                    if (div.length > 0) {
                        //取消原有事件按钮
                        $("input,select").attr("disabled", "disabled");
                        $("#viewContainer").find("button").unbind("click");
                        $("#viewContainer").find("button").on("click", function () {                            
                            return false;
                        });
                        clearInterval(tmpTimer);
                        $("#whitelist_study_txtStartDateTime").parent().parent().parent().addClass("highlight-border");
                        parent.displayTextTimer = setInterval(function () {
                            $("#whitelist_study_txtStartDateTime").parent().parent().parent().toggleClass("highlight-border");
                        }, 500);
                        var now = new Date($("#spanSystemTime").text().replace(/-/g, '/'));
                        now.setSeconds(now.getSeconds() - 280);
                        var myDate = FormatterManager.formatDateFromLocale(now,"yyyy-MM-dd HH:mm:ss");
                        $("#whitelist_study_txtStartDateTime").typetype(myDate, {
                            e: 0.04,
                            t: 100,
                            callback: function () {
                                clearInterval(parent.displayTextTimer);
                                $(".arrowsbox.pos-arrows05").show();
                                $(".arrowsbox.pos-arrows05").css("top", $("#whitelist_study_btnStudy").offset().top + "px");
                                $(".arrowsbox.pos-arrows05").css("left", $("#whitelist_study_btnStudy").offset().left + "px");
                                $("#whitelist_study_txtStartDateTime").parent().parent().parent().removeClass("highlight-border");
                            }
                        });
                    }
                },500);
                break;
            case 7:
                $(".arrowsbox.pos-arrows06").hide();
                View.getInstance().controller.pStudyWhitelistController.getStudyStatus();
                clearInterval(parent.displayTextTimer);
                parent.displayTextTimer = setInterval(function () {
                    var data_length = $("#whitelist_study_tdWhitelistList>tbody>tr").length;
                    if (data_length > 1) {
                        $(".arrowsbox.pos-arrows06").css("left", ($("#whitelist_study_chkAll").offset().left + 10) + "px");
                        $(".arrowsbox.pos-arrows06").css("top", $("#whitelist_study_chkAll").offset().top + "px");
                        $(".arrowsbox.pos-arrows06").show();
                        clearInterval(parent.displayTextTimer);
                    }
                },500);
                break;
            case 8:
                $(".arrowsbox.pos-arrows07").css("left", ($("#whitelist_study_btnEnable").offset().left + 10) + "px");
                $(".arrowsbox.pos-arrows07").css("top", $("#whitelist_study_btnEnable").offset().top + "px");
                break;
            case 9:
                $(".second-nav").slideUp(300, function () {
                    $(".nav-list li .nav-title").removeClass("active");
                    $(".second-nav-list>li").removeClass("on");
                    $(".arrowsbox.pos-arrows08").css("top", $("ul.nav-list>li").eq(5).find(".fa.fa-sitemap").offset().top-10 + "px");
                });
                break;
            case 10:
                $(".nav-list>li .nav-title").eq(5).trigger("click");
                break;
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - GuideController.getTemplateId() - Unable to get template id for guide: " + err.message);
    }
}

GuideController.prototype.getTemplateId = function (step) {
    try {
        switch (step) {
            case 1:
                return Constants.TEMPLATES.UTILITY_GUIDE_STEP_START;
            case 2:
                return Constants.TEMPLATES.UTILITY_GUIDE_STEP1;
            case 3:
                return Constants.TEMPLATES.UTILITY_GUIDE_STEP2;
            case 4:
                return Constants.TEMPLATES.UTILITY_GUIDE_STEP3;
            case 5:
                return Constants.TEMPLATES.UTILITY_GUIDE_STEP3;
            case 6:
                return Constants.TEMPLATES.UTILITY_GUIDE_STEP4;
            case 7:
                return Constants.TEMPLATES.UTILITY_GUIDE_STEP5;
            case 8:
                return Constants.TEMPLATES.UTILITY_GUIDE_STEP6;
            case 9:
                return Constants.TEMPLATES.UTILITY_GUIDE_STEP7;
            default:
                return Constants.TEMPLATES.UTILITY_GUIDE_STEP_END;
        }
    }
    catch (err) {
        console.error("ERROR - GuideController.getTemplateId() - Unable to get template id for guide: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.utility.GuideController", GuideController);
