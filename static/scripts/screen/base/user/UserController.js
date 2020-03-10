function UserController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pUserName = "#" + this.elementId + "_userName";
    this.pUserForm = "#" + this.elementId + "_userForm";
    this.pNewUserForm = "#" + this.elementId + "_newUserForm";
    this.pNewPassword = "#" + this.elementId + "_newPassword";
    this.pNewPasswordInfo = "#" + this.elementId + "_newPasswordInfo";
    this.pNewPassword1 = "#" + this.elementId + "_newPassword1";
    this.pNewUserName = "#" + this.elementId + "_newUserName";
    this.pNewUserPassword = "#" + this.elementId + "_newUserPassword";
    this.pOldUserPassword = "#" + this.elementId + "_oldPassword";
    this.pNewUserPasswordInfo = "#" + this.elementId + "_newUserPasswordInfo";
    this.pNewUserPassword1 = "#" + this.elementId + "_newUserPassword1";
    this.pChangePassword = "#" + this.elementId + "_changePassword";
    this.pAddUser = "#" + this.elementId + "_addUser";
    this.pUserList = "#" + this.elementId + "_userList";
    this.pNewUserType="#" + this.elementId + "_newUserType";
    this.pSetPwdAging="#" + this.elementId + "_setPwdAging";
    this.pDdlPwdAging="#" + this.elementId + "_ddlPwdAging";

}

UserController.prototype.init = function () {
    try {
        var parent = this;

        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.USER_EDIT), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - UserController.init() - Unable to initialize: " + err.message);
    }
}

UserController.prototype.initControls = function () {
    try {
        var parent = this;
        //bind validate form
        $(this.pUserForm).Validform({
            tiptype: function (msg, o, cssctl) {
                if (!o.obj.is("form")) {
                    //页面上不存在提示信息的标签时，自动创建;
                    if (o.obj.parent().find(".Validform_checktip").length == 0) {
                        o.obj.parent().append("<span class='Validform_checktip' />");
                        o.obj.parent().next().find(".Validform_checktip").remove();
                    }
                    var objtip = o.obj.parent().find(".Validform_checktip");
                    cssctl(objtip, o.type);
                    objtip.text(o.obj.parent().find("input").attr("errormsg"));
                }
            },
        });
        $(this.pNewUserForm).Validform({
            tiptype: function (msg, o, cssctl) {
                if (!o.obj.is("form")) {
                    //页面上不存在提示信息的标签时，自动创建;
                    if (o.obj.parent().find(".Validform_checktip").length == 0) {
                        o.obj.parent().append("<span class='Validform_checktip' />");
                        o.obj.parent().next().find(".Validform_checktip").remove();
                    }
                    var objtip = o.obj.parent().find(".Validform_checktip");
                    cssctl(objtip, o.type);
                    objtip.text(o.obj.parent().find("input").attr("errormsg"));
                }
            }
        });

        //bind event
        $(this.pNewPassword1).on("change", function () {
            var newPassword = $(parent.pNewPassword).val();
            var newPassword1 = $(parent.pNewPassword1).val();
            if (newPassword != newPassword1) {
                $(parent.pNewPassword1).parent().find(".Validform_checktip").css("color", "#ff0000").addClass("Validform_wrong").text("两次输入的密码不一致");
            }else {
                $(parent.pNewPassword1).parent().find(".Validform_checktip").removeClass("Validform_wrong").css("color", "").text("");
            }
        });
        $(this.pNewPassword).on("change", function () {
            var newPassword = $(parent.pNewPassword).val();
            var oldPassword = $(parent.pOldUserPassword).val();
            if(newPassword==oldPassword){
                $(parent.pNewPassword).parent().find(".Validform_checktip").addClass("Validform_wrong").css("color", "#ff0000").text("原密码与新密码相同");
                return false;
            }else {
                $(parent.pNewPassword).parent().find(".Validform_checktip").removeClass("Validform_wrong").css("color", "").text("必须由字母、数字、特殊字符(@,!,#)组成，长度6到18位");
            }
        });
        $(this.pChangePassword).on("click", function () {
            var newPassword = $(parent.pNewPassword).val();
            var newPassword1 = $(parent.pNewPassword1).val();
            var oldPassword = $(parent.pOldUserPassword).val();
            if(newPassword==oldPassword){
                layer.alert("原密码与新密码相同", { icon: 5 });
                //$(parent.pNewPassword).parent().find(".Validform_checktip").addClass("Validform_wrong").css("color", "#ff0000").text("原密码与新密码相同");
                return false;
            }else if (newPassword != newPassword1) {
                layer.alert("两次输入的密码不一致", { icon: 5 });
                //$(parent.pNewPassword1).parent().find(".Validform_checktip").addClass("Validform_wrong").css("color", "#ff0000").text("两次输入的密码不一致");
                return false;
            }else {
                $(parent.pNewPassword1).parent().find(".Validform_checktip").removeClass("Validform_wrong").css("color", "").text("");
                if (!Validation.validatePassword(newPassword)) {
                    layer.alert("密码必须由字母、数字、特殊字符(@,!,#)组成，长度6到18位", { icon: 5 });
                    return false;
                }
                parent.changePassword(newPassword,oldPassword);
                return false;
            }
        });

        //add user
        $(this.pNewUserPassword1).on("change", function () {
            var newUserPassword = $(parent.pNewUserPassword).val();
            var newUserPassword1 = $(parent.pNewUserPassword1).val();
            if (newUserPassword != newUserPassword1) {
                $(parent.pNewUserPassword1).parent().find(".Validform_checktip").addClass("Validform_wrong").css("color", "#ff0000").text("两次输入的密码不一致");
            }
            else {
                $(parent.pNewUserPassword1).parent().find(".Validform_checktip").removeClass("Validform_wrong").css("color", "").text("");
            }
        });
        $(this.pAddUser).on("click", function () {
            var newUserName = $(parent.pNewUserName).val();
            var newUserPassword = $(parent.pNewUserPassword).val();
            var newUserType = $(parent.pNewUserType).val();
            var newUserPassword1 = $(parent.pNewUserPassword1).val();
            if (newUserPassword != newUserPassword1) {
                $(parent.newUserPassword1).parent().find(".Validform_checktip").addClass("Validform_wrong").css("color", "#ff0000").text("两次输入的密码不一致");
                return false;
            }
            else {
                $(parent.newUserPassword1).parent().find(".Validform_checktip").removeClass("Validform_wrong").css("color", "").text("");
                if (!Validation.validateUserName(newUserName))
                {
                    layer.alert("用户名必须为4-25个字符,必须以字母开头", { icon: 5 });
                    return false;
                }
                if (!Validation.validatePassword(newUserPassword)) {
                    layer.alert("密码必须由字母、数字、特殊字符(@,!,#)组成，长度6到18位", { icon: 5 });
                    return false;
                }
                parent.addUser(newUserName, newUserPassword,newUserType);
                return false;

            }
        });
        $(this.pSetPwdAging).on("click", function (){
            parent.setAging();
        });
    }
    catch (err) {
        console.error("ERROR - UserController.initControls() - Unable to initialize control: " + err.message);
    }
}

UserController.prototype.load = function () {
    this.authInfo=JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']),hidenode=$(this.pNewUserForm);
    try {
        this.getUser();
        this.selectUsers();
        this.getAging();
        if(this.authInfo['authority']!==mstat||this.authInfo['redirect']){
            hidenode.hide();
            hidenode.prev().hide();
            hidenode.next().hide();
            hidenode.next().next().hide();
            hidenode.next().next().next().hide();
            hidenode.next().next().next().next().hide();
            hidenode.next().next().next().next().next().hide();
        }
        if(this.authInfo['redirect']==1){
            $(".pwdTip").show();
        }
    }
    catch (err) {
        console.error("ERROR - UserController.load() - Unable to load: " + err.message);
    }
}

UserController.prototype.getUser = function () {
    try {
        $(this.pUserName).text(AuthManager.getInstance().getUserName());
    }
    catch (err) {
        console.error("ERROR - UserController.getUser() - Unable to get current user information: " + err.message);
    }
}

UserController.prototype.changePassword = function (pwd,oldPwd) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].CHANGE_USER_PWD;
        var data = {
            newpwd: pwd,
            oldpwd: oldPwd,
            username: AuthManager.getInstance().getUserName()
        };
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", data);
        var authInfo=JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            return false;
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 0:
                        layer.alert("原始密码错误，修改密码失败", { icon: 5 }); break;
                    case 1:
                        if(!authInfo['redirect']){
                            layer.alert("修改密码成功", { icon: 6 }); break;
                        }else{
                            layer.alert(
                                "修改密码成功，点击确认重新登录", {icon: 6},
                                function() {
                                    AuthManager.getInstance().logOut();
                                });
                            break;
                        }
                    default: layer.alert("修改密码失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("修改密码失败", { icon: 5 });
            }
            layer.close(loadIndex);
            return false;
        });
    }
    catch (err) {
        console.error("ERROR - UserController.changePassword() - Unable to change password for user: " + err.message);
        return false;
    }
}

UserController.prototype.addUser = function (uname, pwd,auth) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].ADD_USER;
        var data = {
            user: uname,
            password: pwd,
            authority:auth
        };
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            return false;
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 0: layer.alert("用户人数上限", { icon: 1 }); break;
                    case 1: layer.alert("用户已经存在", { icon: 2 }); break;
                    case 2:
                        layer.alert("添加用户成功", { icon: 6 });
                        $(parent.pNewUserName).val(''),$(parent.pNewUserPassword).val(''),$(parent.pNewUserPassword1).val('');
                        setTimeout(function () {
                            parent.selectUsers();
                        }, 3000);
                        break;
                    default: layer.alert("添加用户失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("添加用户失败", { icon: 5 });
            }
            layer.close(loadIndex);
            return false;
        });
    }
    catch (err) {
        console.error("ERROR - UserController.addUser() - Unable to add new user: " + err.message);
        return false;
    }
}

UserController.prototype.removeUser = function (id,$tr) {
    layer.confirm('确定删除该用户么？',{icon:7,title:'注意：'}, function(index) {
        layer.close(index);
        try {
            var parent = this;
            var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DELETE_USER;
            var loadIndex = layer.load(2, {shade: [0.4, '#fff']});
            var promise = URLManager.getInstance().ajaxCall(link, {id: id});
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                layer.close(loadIndex);
                layer.alert("系统服务忙，请稍后重试！", {icon: 2});
            });
            promise.done(function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 1:
                            layer.alert("删除用户成功", {icon: 6});
                            var userId = AuthManager.getInstance().getUserId();
                            if (typeof(userId) != "undefined" && userId != null && userId != 0 && userId == id) {
                                LocalStorageManager.getInstance().deleteProperty(APPCONFIG.LOGIN_RESPONSE);
                                AuthManager.timedOut = true;
                                AuthManager.getInstance().logOut();
                            }
                            $tr.remove();
                            break;
                        default:
                            layer.alert("删除用户失败", {icon: 5});
                            break;
                    }
                }
                else {
                    layer.alert("删除用户失败", {icon: 5});
                }
                layer.close(loadIndex);
            });
        }
        catch (err) {
            console.error("ERROR - UserController.removeUser() - Unable to remove user: " + err.message);
        }
    });
}

UserController.prototype.selectUsers = function () {
    var colspanRow = "<tr><td colspan='3'>暂无数据</td></tr>";
    var html = "";
    var userName=AuthManager.getInstance().getUserName().toLowerCase();
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_USER_LIST;
        var promise = URLManager.getInstance().ajaxCall(link, {page:1});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += colspanRow;
            $(parent.pUserList+">tbody").html(html);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>" + result.rows[i][1] + "</td>";
                        switch(result['rows'][i][3]){
                            case 1:
                                html += "<td>" + '系统管理员'+ "</td>";
                                break;
                            case 2:
                                html += "<td>" + '安全审计员'+ "</td>";
                                break;
                            case 3:
                                html += "<td>" + '安全管理员'+ "</td>";
                                break;
                        }
                        html += "<td>" + result.rows[i][2] + "</td>";
                        html += "<td>" + (result.rows[i][4]=='2000-01-01 00:00:00'?'---':result.rows[i][4]) + "</td>";
                        html += "<td>";
                        if (parent.authInfo['authority']==mstat && result.rows[i][3] !== 1) {
                            html += "<button class='btn btn-danger btn-xs' id='" + result.rows[i][0] + "'> <i class='fa fa-trash-o'></i>删除</button>";
                        }
                        html += "</td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += colspanRow;
                }
            }
            else {
                html += colspanRow;
            }
            $(parent.pUserList + ">tbody").html(html);
            $(parent.pUserList + ">tbody").find("button").on("click", function (event) {
                parent.removeUser($(this).attr("id"),$(this).parents("tr"));
                return false;
            });
        });
    }
    catch (err) {
        html += colspanRow;
        $(this.pUserList + ">tbody").html(html);
        console.error("ERROR - UserController.selectUsers() - Unable to load all users: " + err.message);
    }
}

UserController.prototype.getAging = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].PWD_AGING;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            $(parent.pDdlPwdAging).val(result.type);
        });
    }
    catch (err) {
        console.error("ERROR - UserController.selectUsers() - Unable to load all users: " + err.message);
    }
}
UserController.prototype.setAging = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].PWD_AGING;
        var agingTime=$(parent.pDdlPwdAging).val();
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCallByURL(link,'POST',{'type':agingTime});
        promise.fail(function (jqXHR, textStatus, err) {
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", {icon: 2});
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert("密码时效设置成功", {icon: 6});
                        break;
                    default:
                        layer.alert("密码时效设置失败", {icon: 5});
                        break;
                }
            }
            else {
                layer.alert("设置失败", {icon: 5});
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - UserController.selectUsers() - Unable to load all users: " + err.message);
    }
}

UserController.prototype.checkPasswordPriority = function (password) {
    try {
        var parent = this;
        var reg = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#]).{6,16}$/;
        if (reg.test(password)) {
            if (password.length >= 6 && password.length < 8) {
                return "low";
            }
            else if (password.length >= 8 && password.length < 12) {
                return "middle";
            }
            else if (password.length >= 12 && password.length <= 16) {
                return "high";
            }
            else {
                return "";
            }
        }
        return "";
    }
    catch (err) {
        console.error("ERROR - UserController.selectUsers() - Unable to load all users: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.user.UserController", UserController);

