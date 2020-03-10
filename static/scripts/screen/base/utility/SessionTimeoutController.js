function SessionTimeoutController() {
	try {
		this.idleTime = 0;
	}
	catch (err) {
		console.error("ERROR - SessionTimeoutController() - Unable to instantiate class: " + err.message);
	}
}

SessionTimeoutController.prototype.init = function () {
    try {
        var parent = this;
        //Increment the idle time counter every minute.
        var timerIncrement = function () {
            parent.idleTime = parent.idleTime + 1;
            console.log("check idle time:" + parent.idleTime);
            if (parent.idleTime >= AuthManager.getInstance().getSessionTimeMin()) {
                AuthManager.timedOut = true;
                AuthManager.getInstance().logOut();
            }

        };
        var idleInterval = setInterval(timerIncrement, APPCONFIG.TOKEN_CHECK_INTERVAL); // 1 minute

        //Zero the idle timer on mouse movement.
        $(document).keypress(function (e) {
            parent.idleTime = 0;
        });
        $(document).click(function (e) {
            parent.idleTime = 0;
        });
    }
    catch (err) {
        console.error("ERROR - SessionTimeoutController.init() - Unable to initialize: " + err.message);
    }
};

/*
 * check token every 2 min
 */
SessionTimeoutController.prototype.startTokenValidatorRunner = function () {
	setInterval(SessionTimeoutController.tokenValidator, APPCONFIG.TOKEN_CHECK_INTERVAL);
	console.log("startTokenValidatorRunner");
};

SessionTimeoutController.tokenValidator = function () {
	console.log("tokenValidator called");
	var callback = function(){
		new tdhx.utility.SessionTimeoutModel().init();
	};
	AuthManager.getInstance().isSessionExpired(callback);
};

ContentFactory.assignToPackage("tdhx.base.utility.SessionTimeoutController", SessionTimeoutController);
