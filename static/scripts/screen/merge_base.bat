:: Merges contents of each file in /scripts/screen/base/* into base.js
rem screen\base.js
copy /b screen\base\utility\GuideController.js+^
	spacer.js+^
	screen\base\utility\PagerController.js+^
	spacer.js+^
	screen\base\utility\SessionTimeoutController.js+^
	spacer.js+^
	screen\base\user\UserController.js+^
	spacer.js+^
	screen\base\user\UkeyController.js+^
	spacer.js+^
	screen\base\audit\FlowAuditController.js+^
	spacer.js+^
	screen\base\audit\FlowDetailAuditController.js+^
	spacer.js+^
	screen\base\audit\ProtocolAuditController.js+^
	spacer.js+^
	screen\base\behavior\BehaviorController.js+^
    spacer.js+^
    screen\base\behavior\S7BehaviorController.js+^
	spacer.js+^
	screen\base\audit\protocol\DNP3Controller.js+^
	spacer.js+^
	screen\base\audit\protocol\ENIPIOController.js+^
	spacer.js+^
	screen\base\audit\protocol\ENIPTCPController.js+^
	spacer.js+^
	screen\base\audit\protocol\ENIPUDPController.js+^
	spacer.js+^
	screen\base\audit\protocol\FTPController.js+^
	spacer.js+^
	screen\base\audit\protocol\GOOSEController.js+^
	spacer.js+^
	screen\base\audit\protocol\HTTPController.js+^
	spacer.js+^
	screen\base\audit\protocol\IEC104Controller.js+^
	spacer.js+^
	screen\base\audit\protocol\MMSController.js+^
	spacer.js+^
	screen\base\audit\protocol\MODBUSController.js+^
	spacer.js+^
	screen\base\audit\protocol\OPCDAController.js+^
	spacer.js+^
	screen\base\audit\protocol\OPCUAController.js+^
	spacer.js+^
	screen\base\audit\protocol\PNRTDCPController.js+^
	spacer.js+^
	screen\base\audit\protocol\POP3Controller.js+^
	spacer.js+^
	screen\base\audit\protocol\PROFINETIOController.js+^
	spacer.js+^
	screen\base\audit\protocol\S7Controller.js+^
	spacer.js+^
	screen\base\audit\protocol\SMTPController.js+^
	spacer.js+^
	screen\base\audit\protocol\SNMPController.js+^
	spacer.js+^
	screen\base\audit\protocol\SVController.js+^
	spacer.js+^
	screen\base\audit\protocol\TELNETController.js+^
	spacer.js+^
	screen\base\audit\protocol\ORACLEController.js+^
	spacer.js+^
	screen\base\audit\protocol\FOCASController.js+^
	spacer.js+^
	screen\base\audit\protocol\SQLSERVERController.js+^
	spacer.js+^
	screen\base\audit\protocol\SIPController.js+^
	spacer.js+^
	screen\base\audit\protocol\CusProtocolController.js+^
	spacer.js+^
	screen\base\device\DeviceController.js+^
	spacer.js+^
	screen\base\device\BasicDeviceController.js+^
	spacer.js+^
	screen\base\device\RemoteDeviceController.js+^
	spacer.js+^
	screen\base\device\ProtocolDeviceController.js+^
	spacer.js+^
	screen\base\device\ManageDeviceController.js+^
	spacer.js+^
	screen\base\device\CentralizeDeviceController.js+^
	spacer.js+^
	screen\base\diagnosis\DiagnosisController.js+^
	spacer.js+^
	screen\base\diagnosis\DebugDiagnosisController.js+^
	spacer.js+^
	screen\base\diagnosis\PcapDiagnosisController.js+^
	spacer.js+^
	screen\base\system\SystemController.js+^
	spacer.js+^
	screen\base\system\LisenceSystemController.js+^
	spacer.js+^
	screen\base\system\UpgradeSystemController.js+^
	spacer.js+^
	screen\base\system\BackupSystemController.js+^
	spacer.js+^
    screen\base\system\ManagersSystemController.js+^
	spacer.js+^
    screen\base\system\SyslogSystemController.js+^
	spacer.js+^
    screen\base\system\SysDebugController.js+^
	spacer.js+^
	screen\base\system\PcapController.js+^
	spacer.js+^
	screen\base\system\DebugInfoController.js+^
	spacer.js+^
	screen\base\system\IptypeSystemController.js+^
	spacer.js+^
	screen\base\system\LogcollectSystemController.js+^
    spacer.js+^
	screen\base\system\SwitchSystemController.js+^
    spacer.js+^
	screen\base\system\ResetSystemController.js+^
	spacer.js+^
	screen\base\system\ConfExportController.js+^
    spacer.js+^
	screen\base\event\EventController.js+^
	spacer.js+^
	screen\base\event\EventFlowController.js+^
	spacer.js+^
	screen\base\log\CollectLogController.js+^
	spacer.js+^
	screen\base\log\LogController.js+^
	spacer.js+^
	screen\base\log\OperationLogController.js+^
	spacer.js+^
	screen\base\log\SystemLogController.js+^
	spacer.js+^
	screen\base\nettopo\NettopoController.js+^
	spacer.js+^
	screen\base\nettopo\TopolistController.js+^
	spacer.js+^
	screen\base\nettopo\SwitchlistController.js+^
	spacer.js+^
	screen\base\nettopo\SwitchallController.js+^
	spacer.js+^
	screen\base\nettopo\SwitchinfoController.js+^
	spacer.js+^
	screen\base\nettopo\TopographController.js+^
	spacer.js+^
	screen\base\nettopo\AssetlistController.js+^
	spacer.js+^
	screen\base\nettopo\FingerprintController.js+^
    spacer.js+^
	screen\base\report\ReportAuditController.js+^
	spacer.js+^
	screen\base\report\ReportAssetController.js+^
    spacer.js+^
	screen\base\report\ReportEventController.js+^
	spacer.js+^
	screen\base\report\ReportLogController.js+^
	spacer.js+^
	screen\base\rule\BlacklistController.js+^
	spacer.js+^
	screen\base\rule\MacRuleController.js+^
	spacer.js+^
	screen\base\rule\MacFilterRuleController.js+^
	spacer.js+^
	screen\base\rule\WhitelistController.js+^
	spacer.js+^
	screen\base\rule\StudyController.js+^
	spacer.js+^
	screen\base\rule\DefineController.js+^
	spacer.js+^
	screen\base\rule\DefineDialogController.js+^
	spacer.js+^
	screen\base\auditstrategy\AsController.js+^
	spacer.js+^
	screen\base\auditstrategy\ProtocolController.js+^
	spacer.js+^
	screen\base\auditstrategy\CusProtoController.js+^
    spacer.js+^
	screen\base\auditstrategy\PrototplController.js+^
    spacer.js+^
	screen\base\auditstrategy\RuleconfController.js+^
    spacer.js+^
	screen\base\auditstrategy\UtilityconfController.js+^
    spacer.js+^
	screen\base\auditstrategy\DATACController.js+^
	spacer.js+^
	screen\base\stream\StreamController.js+^
	spacer.js+^
	screen\base\stream\DownloadStreamDialogController.js+^
	spacer.js+^
	screen\base\stream\RecoverStreamController.js+^
	spacer.js+^
	screen\base\stream\RecoverStreamDialogController.js ^
	screen\base.js
