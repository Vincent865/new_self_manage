﻿/**
 * GLOBAL CONSTANTS - APP CONFIGURATION FILE
 */
var APPCONFIG = {
    ENV: window.location.hostname.toLowerCase(),
    VERSION: 0.7,
    TOKEN_CHECK_INTERVAL: 60000,
    LOGIN_RESPONSE: "loginResponse",
    PRODUCT: "KEA-U1142",
    "KEA-U1000": {
        HTTP_METHOD: "GET",
        HTTP_URL: "",
        ID2URL: {
            //guide668,648,699,700
            "START_WHITELIST_STUDY": "/static/data/rule/whiteliststartstudy.json",
            "GET_WHITELIST": "/static/data/rule/whitelistShowDeploy.json",
            "GET_WHITELIST_DEVICE": "/static/data/rule/whitelistDevice.json",
            "GET_TOPO_DEVICES": "/static/data/nettopo/getAllTopdev.json"
        },
        LOGIN_URL: "/templates/login.html",
        HOMEPAGE_URL: "/templates/index.html",
        //local version
        GET_SYS_TIME: "/getSysTime",
        CHECK_USER: "/checkUser",
        LOGOUT: "/logout",
        GET_USER: "/getUser",
        GET_HOME_BASE: "/indexRefreshCount",
        GET_RAID_STATUS: "/raidStauasRes",
        //user
        CHANGE_USER_PWD: "/changePassword",
        DELETE_USER: "/deleteUser",
        ADD_USER: "/addUser",
        GET_USER_LIST: "/getAllUser",
        //event
        GET_EVENT_INFO: "/eventCountRefresh",
        //safe event
        GET_SAFE_EVENT_LIST: "/safeEventRes",
        SEARCH_SAFE_EVENT: "/safeEventSearch",
        GET_SAFE_EVENT: "/safeEventRecordDetail",
        FLAG_SAFE_EVENT_LIST: "/safeEventReadTag",
        DELETE_SAFE_EVENT_LIST: "/safeEventClearTag",
        FLAG_SAFE_EVENT: "/safeOneEventRead",
        EXPORT_SAFE_EVENT: "/safeEventExportData",
        SAFE_EVENT_FILEPATH: "/download/",
        //system event
        GET_SYS_EVENT_LIST: "/sysEventRes",
        SEARCH_SYS_EVENT: "/sysEventSearch",
        GET_SYS_EVENT: "/sysEventRecordDetail",
        FLAG_SYS_EVENT_LIST: "/sysEventReadTag",
        DELETE_SYS_EVENT_LIST: "/sysEventClearTag",
        FLAG_SYS_EVENT: "/sysOneEventRead",
        EXPORT_SYS_EVENT: "/sysEventExportData",
        SYS_EVENT_FILEPATH: "/download/",
        //log
        GET_LOG_INFO: "/getLogCount",
        //login log
        GET_LOGIN_LOG_LIST: "/loginLogRes",
        EXPORT_LOGIN_LOG: "/loginLogExportData",
        SEARCH_LOGIN_LOG_LIST: "/loginLogSearch",
        LOGIN_LOG_FILEPATH: "/download/",
        //operation log
        GET_LOGIN_OPER_LIST: "/operLogRes",
        EXPORT_OPER_LOG: "/operLogExportData",
        SEARCH_OPER_LOG_LIST: "/operLogSearch",
        OPER_LOG_FILEPATH: "/download/",
        //device
        //basice setting
        GET_DEVICE_INFO: "/getDeviceInfo",
        UPDATE_DEVICE_IP: "/setDpiIp",
        UPDATE_DEVICE_TIME_MANUAL: "/setTimeSynManualInput",
        UPDATE_DEVICE_TIME_AUTO: "/setTimeSynAuto",
        GET_DEVICE_LOGIN_INFO: "/getLoginPara",
        UPDATE_DEVICE_LOGIN_SETTING: "/loginSetting",
        UPGRADE_DEVICE: "/dpiUpdate",
        //advance setting 
        REBOOT_DEVICE: "/rebootDpi",
        SHUTDOWN_DEVICE: "/closeDpi",
        RESET_DEVICE: "/defaultPara",
        GET_DEVICE_REMOTE: "/isOpenRemoteCtl",
        UPDATE_DEVICE_REMOTE: "/updateCtlFlag",
        GET_DEVICE_NET: "/getTimeSynDestIp",
        GET_DEVICE_REMOTE_LIST: "/accessIp",
        ADD_DEVICE_REMOTE_IP: "/addAccessIp",
        DEPLOY_DEVICE_REMOTE_IP: "/deployAccessIp",
        DELETE_DEVICE_REMOTE_IP: "/deleteAccessIp",
        GET_DEVICE_MODE: "/getCurMode",
        CHANGE_DEVICE_MODE: "/changeModelRes",
        /*2016-10-19 Add*/
        GET_DEVICE_LOGGING: "/get_device_logging",
        UPDATE_DEVICE_LOGGING: "/update_device_logging",
        //rule
        //ip/mac
        GET_RULE_MAC_LIST: "/ipMacRes",
        ADD_RULE_MAC: "/addIpMac",
        ENABLE_RULE_MAC: "/startAllIpMac",
        DISABLE_RULE_MAC: "/clearAllIpMac",
        UPDATE_RULE_MAC: "/startIpMacOne",
        DELETE_RULE_MAC: "/deleteIpMac",
        //blacklist
        UPLOAD_BLACKLIST_FILEPATH: "/black-list-add.html",
        GET_BLACKLIST_LIST: "/blacklistSearch",//漏洞库
        //GET_BLACKLIST_LIST: "/blacklistRes",//漏洞库
        GET_BLACKLIST: "/blacklistDetail",//漏洞库详情
        ADD_BLACKLIST_ALL: "/startAllBlacklist",//启用所有黑名单
        CLEAR_BLACKLIST_ALL: "/deleteAllBlacklist",//清除所有黑名单
        UPDATE_BLACKLIST: "/startOneBlacklist",//更新单个黑名单
        GET_BLACKLIST_COUNT: "/getdeployNum",
        UPDATE_BLACKLIST_ALLEVENT: "/blacklistSetAll",
        UPDATE_BLACKLIST_EVENT: "/blacklistUpdate",
        //whitelist
        GET_WHITELIST: "/whitelistShowDeploy",
        CLEAR_WHITELIST: "/whitelistClear",
        GET_WHITELIST_DEVICE: "/whitelistDevice",
        GET_WHITELIST_RULE: "/whitelistRes",
        START_WHITELIST_STUDY: "/whiteliststartstudy",
        STOP_WHITELIST_STUDY: "/whiteliststopstudy",
        GET_WHITELIST_STUDY_STATU: "/whiteliststatus",
        UPDATE_WHITELIST_STUDY: "/whitelistDeploy",
        UPDATE_WHITELIST_STUDY_ALL: "/whitelistStartAll",
        //2016-10-14 ADD
        EXPORT_WHITELIST: "/exportWhitelistRules",
        EXPORT_WHITELIST_FILEPATH: "/download/",
        UPLOAD_WHITELIST: "/wlitelistUpload",
        //2016-12-05 ADD
        GET_DEFINED_PROTOCOL_LIST: "/get_protocol_list",
        DELETE_DEFINED_PROTOCOL_LIST: "/delete_defined_protocol",
        ADD_DEFINE_WHITELIST: "/add_new_white_rule",
        ADD_DEFINE_WHITELIST: "/add_new_white_rule",
        UPDATE_DEFINE_WHITELIST: "/edit_manual_white_list",
        GET_DEFINE_WHITELIST: "/manual_white_list_res",
        UPDATE_SELECTED_DEFINE_WHITELIST_ACTION: "/manual_white_list_action_update_all",
        UPDATE_SINGLE_DEFINE_WHITELIST_ACTION: "/manual_white_list_action_update_one",
        UPDATE_SINGLE_DEFINE_WHITELIST_STATUS: "/manual_white_list_deploy_one",
        DELETE_SELECTED_DEFINE_WHITELIST: "/manual_white_list_delete_some",
        DELETE_SINGLE_DEFINE_WHITELIST: "/manual_white_list_delete_one",
        //TopoList
        GET_TOPO_DEVICES: "/getAllTopdev",//获取所有TOPO设备信息
        SAVE_TOPO_DEVICES: "/updateTopdevInfo",//获取所有TOPO设备信息
        GET_TOPO_PATH: "/getTopdevPath",//获取所有TOPO
        //Audit
        //Protocol 
        GET_PROTOCOL_LIST: "/getFlowDataHeadSearch",
        GET_PROTOCOL: "/getDetail",
        GET_TOTAL_FLOW: "/getCurTimeTraffic",
        GET_TOTAL_FLOW_POINT: "/getCurTimeTrafficLatestPoint",
        GET_PROTOCOL_TOTAL_FLOW: "/getProtTrafficPercent",
        GET_DEVICE_TOTAL_FLOW: "/getDevTrafficPercent",
        GET_FLOW_LIST: "/getDevTrafficTable",
        GET_DEVICE_FLOW: "/getDevDetailTraffic",
        GET_DEVICE_PROTOCOL_FLOW: "/getDevDetailProtPer",
        GET_DEVICE_FLOW_LIST: "/getDevDetailProtTable",
        GET_DEVICE_FLOW_POINT: "/getDevDetailTrafficLatestPoint",
        GET_DEVICE_FLOW_NEW: "/getDevDetailTrafficNew",
        GET_DEVICE_PROTOCOL_FLOW_NEW: "/getDevDetailTrafficLatestPointNew",
        SET_DEVICE_RANGE_NEW: "/setDevTrafficBandRange",
        GET_DEVICE_DETAIL_FLOW_NEW: "/trafficEventRecordDetail",
        DELETE_DEVICE_VALUE_NEW: "/delDevTrafficBandRange",

        //stream 2016-11-01 Add
        GET_STREAM_STATUS: "/flowAuditGetFullFlag",
        DELETE_STREAM: "/flowAuditDeleteAll",
        GET_STREAM_LIST: "/flowAuditRes",
        GET_STREAM_FILE_DETAIL: "/flowAuditGetFTPFileDetail",
        GET_STREAM_SESSION_DETAIL: "/flowAuditGetFTPCtlDetail",
        EXPORT_STREAM_FILEPATH: "/flowAuditFileDownload",
        GET_STREAM_FILE_FOLDER_PATH: "/streamdownload/",
        //pcap
        GET_PCAP_SETTING: "/getPcapSave",
        UPDATE_PCAP_SETTING: "/setPcapSave",
        GET_PCAP_INTERFACE: "/getPhyInterface",
        GET_PCAP_LIST: "/getPcapInfo",
        GET_PCAP_SERVER: "/getPcapSaveExportServer",
        UPDATE_PCAP_SERVER: "/savePcapSaveExportServer",
        TEST_PCAP_LIST: "/testFtpServer",
        EXPORT_PCAP_LIST: "/pcapExport2Ftp",
        CHECK_PCAP_LIST_STATUS: "/request_download_or_export_multi_pcaps",
        DOWNLOAD_PCAP_LIST: "/download_multi_pcaps",
        //basic device 
        GET_DEVICE_DELETE_POLICY: "/getdbcleanconfig",
        UPDATE_DEVICE_DELETE_POLICY: "/setdbcleanconfig",
        CHECK_UPGRADED_FILESIZE: "/checkupdatespace",        
        //protocol
        GET_PROTOCOL_SWITCH: "/protoSwitchRes",
        UPDATE_PROTOCOL_SWITCH: "/protoSwitchSet",
        //debug
        GET_DEBUG_INFO: "/dbgCollectRes",
        RECOVERY_DEBUG_INFO: "/dbgCollectReq",
        GET_DEBUG_INFO_PATH: "/dbgdownload/",
        //backup
        GET_BACKUP_STATUS: "/sysBackupModeRes",
        UPDATE_BACKUP_STATUS: "/sysBackupSetmode",
        MANAU_BACKUP: "/sysBackuphdl",
        DELETE_BACKUP_LIST: "/sysBackupDel",
        GET_BACKUP_LIST: "/sysBackupRes",
        UPDATE_BACKUP: "/sysBackupModDesc",
        EXPORT_BACKUP_PATH: "/sysbackupdownload",
        //Setting
        GET_SETTING: "/confSaveRes",
        UPDATE_SETTING: "/confSaveOper",
        //db
        GET_DB_STATUS: "/getdbstatus",
        //TEST_PROJECT_NODE:"/TESTPROJECTNODE"
        //FunctionModel
        GET_FUNCTION_MODE: "/getFunctionRunMode",
        SET_FUNCTION_MODE: "/setFuncRunMode",
        GET_PROTOCOL_SWITCH_STATUS: "/get_protocol_switch_status",
        SET_PROTOCOL_SWITCH_STATUS: "/set_protocol_switch_status",

        //report
        GET_REPORT_EVENT: "/reportGenAlarmInfo",
        GET_REPORT_EVENTMODEL: "/reportGenAlarmGetmode",
        GET_REPORT_EVENTSTATIC: "/reportGenAlarmStaticsRes",
        SET_REPORT_EVENTMODEL: "/reportGenAlarmSetmode",
        SET_REPORT_DOWNLOADDETAIL: "/RptalarmDownload/",
        //audit
        GET_AUDIT_EVENT: "/reportGenProtoInfo",
        GET_AUDIT_EVENTMODEL: "/reportGenProtoGetmode",
        GET_AUDIT_EVENTSTATIC: "/reportGenProtoStaticsRes",
        SET_AUDIT_EVENTMODEL: "/reportGenProtoSetmode",
        SET_AUDIT_DOWNLOADDETAIL: "/RptprotoDownload/",
        //log
        GET_LOG_EVENT: "/reportGenLogInfo",
        GET_LOG_EVENTMODEL: "/reportGenLogGetmode",
        GET_LOG_OPERATESTATIC: "/reportGenOperlogStaticsRes",
        GET_LOG_SYSTEMSTATIC: "/reportGenSyslogStaticsRes",
        SET_LOG_EVENTMODEL: "/reportGenLogSetmode",
        SET_LOG_DOWNLOADDETAIL: "/RptlogDownload/"
    },
    "KEA-U1142": {
        HTTP_METHOD: "GET",
        HTTP_URL: "",
        ID2URL:{
            //guide
            "START_WHITELIST_STUDY": "/static/data/rule/whiteliststartstudy.json",
            "GET_WHITELIST": "/static/data/rule/whitelistShowDeploy.json",
            "GET_WHITELIST_DEVICE": "/static/data/rule/whitelistDevice.json",
            "GET_TOPO_DEVICES": "/static/data/nettopo/getAllTopdev.json"
        },
        LOGIN_URL: "/templates/login.html",
        HOMEPAGE_URL: "/templates/index.html",
        //local version
        GET_SYS_TIME: "/getSysTime",
        LOGOUT: "/logout",
        CHECK_USER: "/checkUser",
        GET_USER: "/getUser",
        IS_PIN_ACTION: "/setUserLoginAuthAction",
        GET_HOME_BASE: "/indexRefreshCount",
        GET_RAID_STATUS: "/raidStauasRes",
        //user
        CHANGE_USER_PWD: "/changePassword",
        DELETE_USER: "/deleteUser",
        ADD_USER: "/addUser",
        GET_USER_LIST: "/getAllUser",
        PWD_AGING: "/pwd_aging",
        //event
        GET_EVENT_INFO: "/eventCountRefresh",
        //tip
        GET_TIP_STATUS:"/safeEventRefresh",
        //safe event
        GET_SAFE_EVENT_LIST: "/safeEventRes",
        SEARCH_SAFE_EVENT: "/safeEventSearch",
        GET_SAFE_EVENT: "/safeEventRecordDetail",
        GET_INVALID_EVENT: "/safeEventDetail",
        GET_ASSET_EVENT: "/devEventRecordDetail",
        FLAG_SAFE_EVENT_LIST: "/safeEventReadTag",
        DELETE_SAFE_EVENT_LIST: "/safeEventClearTag",
        FLAG_SAFE_EVENT: "/safeOneEventRead",
        EXPORT_SAFE_EVENT: "/safeEventExportData",
        SAFE_EVENT_FILEPATH: "/download/",
        //system event
        GET_SYS_EVENT_LIST: "/sysEventRes",
        SEARCH_SYS_EVENT: "/sysEventSearch",
        GET_SYS_EVENT: "/sysEventRecordDetail",
        FLAG_SYS_EVENT_LIST: "/sysEventReadTag",
        DELETE_SYS_EVENT_LIST: "/sysEventClearTag",
        FLAG_SYS_EVENT: "/sysOneEventRead",
        EXPORT_SYS_EVENT: "/sysEventExportData",
        SYS_EVENT_FILEPATH: "/download/",
        //log
        GET_LOG_INFO: "/getLogCount",
        //login log
        GET_LOGIN_LOG_LIST: "/loginLogRes",
        EXPORT_LOGIN_LOG: "/loginLogExportData",
        SEARCH_LOGIN_LOG_LIST: "/loginLogSearch",
        LOGIN_LOG_FILEPATH: "/download/",
        //operation log
        GET_LOGIN_OPER_LIST: "/operLogRes",
        EXPORT_OPER_LOG: "/operLogExportData",
        SEARCH_OPER_LOG_LIST: "/operLogSearch",
        OPER_LOG_FILEPATH: "/download/",
        //device
        COLLECT_LOG:"/SetLogAudit",
        COLLECT_LOG_LIST:"/LogAuditSearch",
        GET_ROUTE_LIST:"/routes",
        //basice setting
        GET_DEVICE_INFO: "/getDeviceInfo",
        UPDATE_DEVICE_IP: "/setDpiIp",
        UPDATE_DEVICE_IP6: "/setDpiIp6",
        UPDATE_DEVICE_TIME_MANUAL: "/setTimeSynManualInput",
        UPDATE_DEVICE_TIME_AUTO: "/setTimeSynAuto",
        GET_DEVICE_LOGIN_INFO: "/getLoginPara",
        UPDATE_DEVICE_LOGIN_SETTING: "/loginSetting",
        UPGRADE_DEVICE: "/dpiUpdate",
        GET_LISENCE_STATUS: "/license_cur_status",
        GET_DEVICE_CODE: "/license_machine_code",
        UPLOAD_LICENSE_FILE:"/license_file_upload",
        //advance setting 
        REBOOT_DEVICE: "/rebootDpi",
        SHUTDOWN_DEVICE: "/closeDpi",
        RESET_DEVICE: "/defaultPara",
        GET_DEVICE_REMOTE: "/isOpenRemoteCtl",
        UPDATE_DEVICE_REMOTE: "/updateCtlFlag",
        PIN_STATUS:"/setUserLoginAuthAction",
        CHANGE_PIN_PWD:"/changeUkeyAuthPasswd",
        GET_DEVICE_NET: "/getTimeSynDestIp",
        GET_DEVICE_REMOTE_LIST: "/accessIp",
        ADD_DEVICE_REMOTE_IP: "/addAccessIp",
        DEPLOY_DEVICE_REMOTE_IP: "/deployAccessIp",
        DELETE_DEVICE_REMOTE_IP: "/deleteAccessIp",
        GET_DEVICE_MODE: "/getCurMode",
        CHANGE_DEVICE_MODE: "/changeModelRes",
        /*2016-10-19 Add*/
        GET_DEVICE_LOGGING: "/get_device_logging",
        UPDATE_DEVICE_LOGGING: "/update_device_logging",
        //rule
        //ip/mac
        GET_RULE_MAC_LIST: "/ipMacRes",
        ADD_RULE_MAC: "/addIpMac",
        ENABLE_RULE_MAC: "/startAllIpMac",
        DISABLE_RULE_MAC: "/clearAllIpMac",
        UPDATE_RULE_MAC: "/startIpMacOne",
        DELETE_RULE_MAC: "/deleteIpMac",
        MAC_ALL_EXPORT: "/ipmacExport",
        MAC_ALL_IMPORT: "/ipmacImport",
        //MAC_FILTER
        RULE_MACFILTER:"/macfilter",
        MACFILTER_ALL:"/macfilterall",
        //cusproto
        CUS_PROTO_LIST: "/customProtocol",
        DEPLOY_CUS_PROTO: "/deployCustomProto",
        GET_RULES_LIST: "/getContent",
        GET_RULES_TPL: "/contentModel",
        GET_UTILITY_LIST:"/customValue",
        GET_UTILITY_TPL:"/getValue",

		//datac
	    MW_AUDITSTRATEGY_ADD:"/addAuditstrategy",
	    MW_AUDITSTRATEGY_SEARCH:"/auditstrategySearch",
	    MW_AUDITSTRATEGY_DEL:"/delAuditstrategy",
	    MW_AUDITSTRATEGY_DEPLOY:"/deployAuditstrategy",
        //blacklist
        UPLOAD_BLACKLIST_FILEPATH: "/black-list-add.html",
        GET_BLACKLIST_LIST: "/blacklistSearch",
        //GET_BLACKLIST_LIST: "/blacklistRes",//漏洞库
        GET_BLACKLIST: "/blacklistDetail",//漏洞库详情
        ADD_BLACKLIST_ALL: "/startAllBlacklist",//启用所有黑名单
        CLEAR_BLACKLIST_ALL: "/deleteAllBlacklist",//清除所有黑名单
        UPDATE_BLACKLIST: "/startOneBlacklist",//更新单个黑名单
        GET_BLACKLIST_COUNT: "/getdeployNum",
        UPDATE_BLACKLIST_ALLEVENT: "/blacklistSetAll",
        UPDATE_BLACKLIST_EVENT: "/blacklistUpdate",
        //whitelist
        GET_WHITELIST: "/whitelistShowDeploy",
        CLEAR_WHITELIST: "/whitelistClear",
        GET_WHITELIST_DEVICE: "/whitelistDevice",
        GET_WHITELIST_RULE: "/whitelistRes",
        START_WHITELIST_STUDY: "/whiteliststartstudy",
        STOP_WHITELIST_STUDY: "/whiteliststopstudy",
        GET_WHITELIST_STUDY_STATU: "/whiteliststatus",
        UPDATE_WHITELIST_STUDY: "/whitelistDeploy",
        UPDATE_WHITELIST_STUDY_ALL: "/whitelistStartAll",
        //2016-10-14 ADD
        EXPORT_WHITELIST: "/exportWhitelistRules",
        EXPORT_WHITELIST_FILEPATH: "/download/",
        UPLOAD_WHITELIST: "/wlitelistUpload",
        //2016-12-05 ADD
        GET_DEFINED_PROTOCOL_LIST: "/get_protocol_list",
        DELETE_DEFINED_PROTOCOL_LIST: "/delete_defined_protocol",
        ADD_DEFINE_WHITELIST: "/add_new_white_rule",
        ADD_DEFINE_WHITELIST: "/add_new_white_rule",
        UPDATE_DEFINE_WHITELIST: "/edit_manual_white_list",
        GET_DEFINE_WHITELIST: "/manual_white_list_res",
        UPDATE_SELECTED_DEFINE_WHITELIST_ACTION: "/manual_white_list_action_update_all",
        UPDATE_SINGLE_DEFINE_WHITELIST_ACTION: "/manual_white_list_action_update_one",
        UPDATE_SINGLE_DEFINE_WHITELIST_STATUS: "/manual_white_list_deploy_one",
        DELETE_SELECTED_DEFINE_WHITELIST: "/manual_white_list_delete_some",
        DELETE_SINGLE_DEFINE_WHITELIST: "/manual_white_list_delete_one",
        //TopoList
        GET_TOPO_DEVICES: "/getAllTopdev",//获取所有TOPO设备信息
        SAVE_TOPO_DEVICES: "/updateTopdevInfo",//获取所有TOPO设备信息
        GET_TOPO_PATH: "/getTopdevPath",//获取所有TOPO

        GET_ASSET_LIST:"/topo/get_topdev_list",
        OPER_ASSET_DEVICE:"/topo/topdev_info",
        UNADD_TOPO_LIST:"/topo/get_add_device",
        GET_RELA_DEVS:"/topo/get_topdev_detail",
        GET_RULE_DETAIL:"/topo/get_topdev_rule_detail",
        GET_TOPEVENT_DETAIL:"/topo/get_topdev_inc_detail",
        GET_TOPAUDIT_DETAIL:"/topo/get_topdev_audit_detail",
        GET_TOPAUDIT1_DETAIL:"/topo/get_topdev_audit_proto",
        SHIFT_STATUS_TOPO:"/topo/join_toposhow",
        IS_INTO_IPMAC_RULE:"/topo/add_to_ipmac",
        GET_TOPO_ASSET:"/topo/topo_show_info",

        GET_SWITCH_LIST:"/switch_info",
        GET_SWITCH_INFO_LIST:"/switch_mac_port_list",
        SWITCH_IMPORT:"/import_switch_info",
        SWITCH_EXPORT:"/export_switch_info",
        GET_SWITCH_MAC_INFO:"/get_switch_info_by_mac",

        GET_DEVICE_TYPE:"/topo/device_type",
        TOPO_ALL_EXPORT: "/topo/dev_listExport",
        TOPO_ALL_IMPORT: "/topo/dev_listImport",
        TOPO_VENDOR_IMPORT: "/topo/vendor_fileImport",
        TOPO_VENDOR_EXPORT: "/topo/vendor_fileExport",
        //topo_fingerprint
        TOPO_FINGER_PRINT: "/topo/dev_fingerprint",
        TOPO_CUSPROTO_LIST: "/topo/get_selfproto",
        //Audit
        //Protocol 
        GET_PROTOCOL_LIST: "/getFlowDataHeadSearch",
        GET_BEHAVIOR_DIALOG_LIST: "/getBhvDetail",
        GET_BEHAVIOR_LIST: "/getBhvDataHeadSearch",
        GET_PROTOCOL: "/getDetail",
        GET_TOTAL_FLOW: "/getCurTimeTraffic",
        GET_TOTAL_FLOW_POINT: "/getCurTimeTrafficLatestPoint",
        GET_PROTOCOL_TOTAL_FLOW: "/getProtTrafficPercent",
        GET_DEVICE_TOTAL_FLOW: "/getDevTrafficPercent",
        GET_EVENT_PERCENT: "/safeeventPercent",
        GET_FLOW_LIST: "/getDevTrafficTable",
        GET_DEVICE_FLOW: "/getDevDetailTraffic",
        GET_DEVICE_PROTOCOL_FLOW: "/getDevDetailProtPer",
        GET_PROTOCOL_INFO_FLOW: "/getProtocolInfoByDev",
        GET_PROTOCOL_CUS_INFO_FLOW: "/getcusProtocolInfoByDev",
        GET_PROTOCOL_INFO_RRFRESH: "/getProtocolInfoRefresh",
        GET_CUS_PROTOCOL_INFO_RRFRESH: "/getcusProtocolInfoRefresh",
        GET_PROTOCOL_CUS_INFO_RRFRESH: "/getProtocolInfoRefresh",
        GET_DEVICE_FLOW_LIST: "/getDevDetailProtTable",
        GET_DEVICE_FLOW_POINT: "/getDevDetailTrafficLatestPoint",
 	    GET_DEVICE_FLOW_NEW: "/getDevDetailTrafficNew",
        GET_DEVICE_PROTOCOL_FLOW_NEW: "/getDevDetailTrafficLatestPointNew",
        SET_DEVICE_RANGE_NEW: "/setDevTrafficBandRange",
        GET_DEVICE_DETAIL_FLOW_NEW: "/trafficEventRecordDetail",
	    DELETE_DEVICE_VALUE_NEW: "/delDevTrafficBandRange",
        //stream 2016-11-01 Add
        GET_STREAM_STATUS: "/flowAuditGetFullFlag",
        DELETE_STREAM: "/flowAuditDeleteAll",
        GET_STREAM_LIST: "/flowAuditRes",
        GET_STREAM_FILE_DETAIL: "/flowAuditGetFTPFileDetail",
        GET_STREAM_SESSION_DETAIL: "/flowAuditGetFTPCtlDetail",
        EXPORT_STREAM_FILEPATH: "/flowAuditFileDownload",
        GET_STREAM_FILE_FOLDER_PATH: "/streamdownload/",
        //pcap
        GET_PCAP_SETTING: "/getPcapSave",
        UPDATE_PCAP_SETTING: "/setPcapSave",
        GET_PCAP_INTERFACE: "/getPhyInterface",
        GET_PCAP_SERVER: "/getPcapSaveExportServer",
        UPDATE_PCAP_SERVER: "/savePcapSaveExportServer",
        GET_PCAP_LIST: "/getPcapInfo",
        TEST_PCAP_LIST: "/testFtpServer",
        CHECK_PCAP_LIST_STATUS: "/request_download_or_export_multi_pcaps",
        DOWNLOAD_PCAP_LIST: "/download_multi_pcaps",
        EXPORT_PCAP_LIST: "/pcapExport2Ftp",
        //sys_pcap
        GET_PCAP_STATUS: "/search_status_pcap",
        SELECT_PCAP_LIST: "/detail_pcap",
        START_PCAP: "/start_pcap",
        DELETE_PCAP: "/delete_pcap",
        STOP_PCAP: "/stop_pcap",
        DOWNLOAD_PCAP: "/download_pcap",
        //debug_info
        DEBUG_INFO_COLLECT:"/debugInfo",
        //basic device 
        GET_DEVICE_DELETE_POLICY: "/getdbcleanconfig",
        UPDATE_DEVICE_DELETE_POLICY: "/setdbcleanconfig",
        CHECK_UPGRADED_FILESIZE: "/checkupdatespace",
        //protocol
        GET_PROTOCOL_SWITCH: "/protoSwitchRes",
        UPDATE_PROTOCOL_SWITCH: "/protoSwitchSet",
        //debug
        GET_DEBUG_INFO: "/dbgCollectRes",
        RECOVERY_DEBUG_INFO: "/dbgCollectReq",
        GET_DEBUG_INFO_PATH: "/dbgdownload/",
        //backup
        GET_BACKUP_STATUS: "/sysBackupModeRes",
        UPDATE_BACKUP_STATUS: "/sysBackupSetmode",
        MANAU_BACKUP: "/sysBackuphdl",
        DELETE_BACKUP_LIST: "/sysBackupDel",
        GET_BACKUP_LIST: "/sysBackupRes",
        UPDATE_BACKUP: "/sysBackupModDesc",
        EXPORT_BACKUP_PATH: "/sysbackupdownload",
        //Setting
        GET_SETTING: "/confSaveRes",
        UPDATE_SETTING: "/confSaveOper",
        //download_file
        DOWNLOAD_FILE:"/download_user_manual",
        //db
        GET_DB_STATUS: "/getdbstatus",
        //TEST_PROJECT_NODE:"/TESTPROJECTNODE"
        //FunctionModel
        GET_FUNCTION_MODE: "/getFunctionRunMode",
        SET_FUNCTION_MODE: "/setFuncRunMode",
        GET_PROTOCOL_SWITCH_STATUS: "/get_protocol_switch_status",
        SET_PROTOCOL_SWITCH_STATUS: "/set_protocol_switch_status",
        //IPV6Switch
        GET_IPV6_SWITCH: "/ipv6FunctionSwitch",
        //FlowSwitch
        GET_FLOW_SWITCH: "/flow_switch",
        //DevStatus
        GET_DEV_STATUS: "/dev_checktime",
        //managerCenter
        TEST_SERVER_STATUS:"/testCentreServerStatus",
        CONNECT_DEVICE:'/connectCentreServer',
        DISCONNECT_DEVICE:'/disconnectCentreServer',
        GET_REGISTER_STATUS:'/getCentreServerConfig',
        //syslogConfig
        GET_SYSLOG_CONF:"/getSyslogServerConfig",
        PUT_SYSLOG_CONF:"/saveSyslogServerConfig",
        //report
        GET_REPORT_EVENT: "/reportGenAlarmInfo",
        GET_REPORT_EVENTMODEL: "/reportGenAlarmGetmode",
        GET_REPORT_EVENTSTATIC: "/reportGenAlarmStaticsRes",
        SET_REPORT_EVENTMODEL: "/reportGenAlarmSetmode",
        REPORT_ALARM_DOWNLOAD: "/RptalarmDownload/",
        REPORT_ALARM_DETAIL_DOWNLOAD: "/RptalarmdetailDownload/",
	    REPORT_ALARM_MANUAL:"/reportGenAlarmManual",
        //audit
        GET_AUDIT_EVENT: "/reportGenProtoInfo",
        GET_AUDIT_EVENTMODEL: "/reportGenProtoGetmode",
        GET_AUDIT_EVENTSTATIC: "/reportGenProtoStaticsRes",
        SET_AUDIT_EVENTMODEL: "/reportGenProtoSetmode",
	    REPORT_PROTO_MANUAL: "/reportGenProtoManual",
        SET_AUDIT_DOWNLOADDETAIL: "/RptprotoDownload/",
        REPORT_PROTO_DOWNLOAD: "/RptprotoDownload/",
        REPORT_PROTO_DETAIL_DOWNLOAD: "/RptprotodetailDownload/",
        //assetReport
        REPORT_ASSET_MANUAL: "/reportGenAssetsManual",
        SET_ASSET_MODEL: "/reportGenAssetsSetmode",
        GET_ASSET_MODEL: "/reportGenAssetsGetmode",
        GET_ASSET_REPORT_LIST:"/reportGenAssetsInfo",
        REPORT_ASSET_DETAIL_DOWNLOAD: "/RptassetsdetailDownload/",
        REPORT_ASSET_DOWNLOAD: "/RptassetsDownload/",
        //log
        GET_LOG_EVENT: "/reportGenLogInfo",
        GET_LOG_EVENTMODEL: "/reportGenLogGetmode",
        GET_LOG_OPERATESTATIC: "/reportGenOperlogStaticsRes",
        GET_LOG_SYSTEMSTATIC: "/reportGenSyslogStaticsRes",
        SET_LOG_EVENTMODEL: "/reportGenLogSetmode",
	    REPORT_LOG_MANUAL: "/reportGenLogManual",
        SET_LOG_DOWNLOADDETAIL: "/RptlogDownload/",
        REPORT_LOG_DOWNLOAD: "/RptlogDownload/",
        REPORT_LOG_DETAIL_DOWNLOAD: "/RptlogdetailDownload/",
		//sessionNum
	    GET_SESSION_ALL_NUM:"/getallsessionnum",
	    GET_SESSION_ONE_NUM:"/getonesessionnum",
        UPLOAD_CONFIG_FILE:"/device_data_migration"
    },

    "KEA-C200": {
        HTTP_METHOD: "GET",
        HTTP_URL: "",
        ID2URL: {
            //guide
            "START_WHITELIST_STUDY": "/static/data/rule/whiteliststartstudy.json",
            "GET_WHITELIST": "/static/data/rule/whitelistShowDeploy.json",
            "GET_WHITELIST_DEVICE": "/static/data/rule/whitelistDevice.json",
            "GET_TOPO_DEVICES": "/static/data/nettopo/getAllTopdev.json"
        },
        LOGIN_URL: "login.html",
        HOMEPAGE_URL: "index.html",
        //local version
        GET_SYS_TIME: "/getSysTime",
        CHECK_USER: "/checkUser",
        GET_USER: "/getUser",
        GET_HOME_BASE: "/indexRefreshCount",
        GET_RAID_STATUS: "/raidStauasRes",
        //user
        CHANGE_USER_PWD: "/changePassword",
        DELETE_USER: "/deleteUser",
        ADD_USER: "/addUser",
        GET_USER_LIST: "/getAllUser",
        //event
        GET_EVENT_INFO: "/eventCountRefresh",
        //safe event
        GET_SAFE_EVENT_LIST: "/safeEventRes",
        SEARCH_SAFE_EVENT: "/safeEventSearch",
        GET_SAFE_EVENT: "/safeEventRecordDetail",
        FLAG_SAFE_EVENT_LIST: "/safeEventReadTag",
        DELETE_SAFE_EVENT_LIST: "/safeEventClearTag",
        FLAG_SAFE_EVENT: "/safeOneEventRead",
        EXPORT_SAFE_EVENT: "/safeEventExportData",
        SAFE_EVENT_FILEPATH: "/download/",
        //system event
        GET_SYS_EVENT_LIST: "/sysEventRes",
        SEARCH_SYS_EVENT: "/sysEventSearch",
        GET_SYS_EVENT: "/sysEventRecordDetail",
        FLAG_SYS_EVENT_LIST: "/sysEventReadTag",
        DELETE_SYS_EVENT_LIST: "/sysEventClearTag",
        FLAG_SYS_EVENT: "/sysOneEventRead",
        EXPORT_SYS_EVENT: "/sysEventExportData",
        SYS_EVENT_FILEPATH: "/download/",
        //log
        GET_LOG_INFO: "/getLogCount",
        //login log
        GET_LOGIN_LOG_LIST: "/loginLogRes",
        EXPORT_LOGIN_LOG: "/loginLogExportData",
        SEARCH_LOGIN_LOG_LIST: "/loginLogSearch",
        LOGIN_LOG_FILEPATH: "/download/",
        //operation log
        GET_LOGIN_OPER_LIST: "/operLogRes",
        EXPORT_OPER_LOG: "/operLogExportData",
        SEARCH_OPER_LOG_LIST: "/operLogSearch",
        OPER_LOG_FILEPATH: "/download/",
        //device
        //basice setting
        GET_DEVICE_INFO: "/getDeviceInfo",
        UPDATE_DEVICE_IP: "/setDpiIp",
        UPDATE_DEVICE_TIME_MANUAL: "/setTimeSynManualInput",
        UPDATE_DEVICE_TIME_AUTO: "/setTimeSynAuto",
        GET_DEVICE_LOGIN_INFO: "/getLoginPara",
        UPDATE_DEVICE_LOGIN_SETTING: "/loginSetting",
        UPGRADE_DEVICE: "/dpiUpdate",
        //advance setting 
        REBOOT_DEVICE: "/rebootDpi",
        SHUTDOWN_DEVICE: "/closeDpi",
        RESET_DEVICE: "/defaultPara",
        GET_DEVICE_REMOTE: "/isOpenRemoteCtl",
        UPDATE_DEVICE_REMOTE: "/updateCtlFlag",
        GET_DEVICE_NET: "/getTimeSynDestIp",
        GET_DEVICE_REMOTE_LIST: "/accessIp",
        ADD_DEVICE_REMOTE_IP: "/addAccessIp",
        DEPLOY_DEVICE_REMOTE_IP: "/deployAccessIp",
        DELETE_DEVICE_REMOTE_IP: "/deleteAccessIp",
        GET_DEVICE_MODE: "/getCurMode",
        CHANGE_DEVICE_MODE: "/changeModelRes",
        /*2016-10-19 Add*/
        GET_DEVICE_LOGGING: "/get_device_logging",
        UPDATE_DEVICE_LOGGING: "/update_device_logging",
        //rule
        //ip/mac
        GET_RULE_MAC_LIST: "/ipMacRes",
        ADD_RULE_MAC: "/addIpMac",
        ENABLE_RULE_MAC: "/startAllIpMac",
        DISABLE_RULE_MAC: "/clearAllIpMac",
        UPDATE_RULE_MAC: "/startIpMacOne",
        DELETE_RULE_MAC: "/deleteIpMac",
        //blacklist
        UPLOAD_BLACKLIST_FILEPATH: "/black-list-add.html",
        GET_BLACKLIST_LIST: "/blacklistSearch",
        //GET_BLACKLIST_LIST: "/blacklistRes",//漏洞库
        GET_BLACKLIST: "/blacklistDetail",//漏洞库详情
        ADD_BLACKLIST_ALL: "/startAllBlacklist",//启用所有黑名单
        CLEAR_BLACKLIST_ALL: "/deleteAllBlacklist",//清除所有黑名单
        UPDATE_BLACKLIST: "/startOneBlacklist",//更新单个黑名单
        GET_BLACKLIST_COUNT: "/getdeployNum",
        UPDATE_BLACKLIST_ALLEVENT: "/blacklistSetAll",
        UPDATE_BLACKLIST_EVENT: "/blacklistUpdate",
        //whitelist
        GET_WHITELIST: "/whitelistShowDeploy",
        CLEAR_WHITELIST: "/whitelistClear",
        GET_WHITELIST_DEVICE: "/whitelistDevice",
        GET_WHITELIST_RULE: "/whitelistRes",
        START_WHITELIST_STUDY: "/whiteliststartstudy",
        STOP_WHITELIST_STUDY: "/whiteliststopstudy",
        GET_WHITELIST_STUDY_STATU: "/whiteliststatus",
        UPDATE_WHITELIST_STUDY: "/whitelistDeploy",
        UPDATE_WHITELIST_STUDY_ALL: "/whitelistStartAll",
        //2016-10-14 ADD
        EXPORT_WHITELIST: "/exportWhitelistRules",
        EXPORT_WHITELIST_FILEPATH: "/download/",
        UPLOAD_WHITELIST: "/wlitelistUpload",
        //2016-12-05 ADD
        GET_DEFINED_PROTOCOL_LIST: "/get_protocol_list",
        DELETE_DEFINED_PROTOCOL_LIST: "/delete_defined_protocol",
        ADD_DEFINE_WHITELIST: "/add_new_white_rule",
        ADD_DEFINE_WHITELIST: "/add_new_white_rule",
        UPDATE_DEFINE_WHITELIST: "/edit_manual_white_list",
        GET_DEFINE_WHITELIST: "/manual_white_list_res",
        UPDATE_SELECTED_DEFINE_WHITELIST_ACTION: "/manual_white_list_action_update_all",
        UPDATE_SINGLE_DEFINE_WHITELIST_ACTION: "/manual_white_list_action_update_one",
        UPDATE_SINGLE_DEFINE_WHITELIST_STATUS: "/manual_white_list_deploy_one",
        DELETE_SELECTED_DEFINE_WHITELIST: "/manual_white_list_delete_some",
        DELETE_SINGLE_DEFINE_WHITELIST: "/manual_white_list_delete_one",
        //TopoList
        GET_TOPO_DEVICES: "/getAllTopdev",//获取所有TOPO设备信息
        SAVE_TOPO_DEVICES: "/updateTopdevInfo",//获取所有TOPO设备信息
        GET_TOPO_PATH: "/getTopdevPath",//获取所有TOPO
        //Audit
        //Protocol 
        GET_PROTOCOL_LIST: "/getFlowDataHeadSearch",
        GET_PROTOCOL: "/getDetail",
        GET_TOTAL_FLOW: "/getCurTimeTraffic",
        GET_TOTAL_FLOW_POINT: "/getCurTimeTrafficLatestPoint",
        GET_PROTOCOL_TOTAL_FLOW: "/getProtTrafficPercent",
        GET_DEVICE_TOTAL_FLOW: "/getDevTrafficPercent",
        GET_FLOW_LIST: "/getDevTrafficTable",
        GET_DEVICE_FLOW: "/getDevDetailTraffic",
        GET_DEVICE_PROTOCOL_FLOW: "/getDevDetailProtPer",
        GET_DEVICE_FLOW_LIST: "/getDevDetailProtTable",
        GET_DEVICE_FLOW_POINT: "/getDevDetailTrafficLatestPoint",
        GET_DEVICE_FLOW_NEW: "/getDevDetailTrafficNew",
        GET_DEVICE_PROTOCOL_FLOW_NEW: "/getDevDetailTrafficLatestPointNew",
        SET_DEVICE_RANGE_NEW: "/setDevTrafficBandRange",
        GET_DEVICE_DETAIL_FLOW_NEW: "/trafficEventRecordDetail",
        DELETE_DEVICE_VALUE_NEW: "/delDevTrafficBandRange",

        //stream 2016-11-01 Add
        GET_STREAM_STATUS: "/flowAuditGetFullFlag",
        DELETE_STREAM: "/flowAuditDeleteAll",
        GET_STREAM_LIST: "/flowAuditRes",
        GET_STREAM_FILE_DETAIL: "/flowAuditGetFTPFileDetail",
        GET_STREAM_SESSION_DETAIL: "/flowAuditGetFTPCtlDetail",
        EXPORT_STREAM_FILEPATH: "/flowAuditFileDownload",
        GET_STREAM_FILE_FOLDER_PATH: "/streamdownload/",
        //pcap
        GET_PCAP_SETTING: "/getPcapSave",
        UPDATE_PCAP_SETTING: "/setPcapSave",
        GET_PCAP_INTERFACE: "/getPhyInterface",
        GET_PCAP_LIST: "/getPcapInfo",
        GET_PCAP_SERVER: "/getPcapSaveExportServer",
        UPDATE_PCAP_SERVER: "/savePcapSaveExportServer",
        TEST_PCAP_LIST: "/testFtpServer",
        EXPORT_PCAP_LIST: "/pcapExport2Ftp",
        CHECK_PCAP_LIST_STATUS: "/request_download_or_export_multi_pcaps",
        DOWNLOAD_PCAP_LIST: "/download_multi_pcaps",
        //basic device 
        GET_DEVICE_DELETE_POLICY: "/getdbcleanconfig",
        UPDATE_DEVICE_DELETE_POLICY: "/setdbcleanconfig",
        CHECK_UPGRADED_FILESIZE: "/checkupdatespace",
        //protocol
        GET_PROTOCOL_SWITCH: "/protoSwitchRes",
        UPDATE_PROTOCOL_SWITCH: "/protoSwitchSet",
        //debug
        GET_DEBUG_INFO: "/dbgCollectRes",
        RECOVERY_DEBUG_INFO: "/dbgCollectReq",
        GET_DEBUG_INFO_PATH: "/dbgdownload/",
        //backup
        GET_BACKUP_STATUS: "/sysBackupModeRes",
        UPDATE_BACKUP_STATUS: "/sysBackupSetmode",
        MANAU_BACKUP: "/sysBackuphdl",
        DELETE_BACKUP_LIST: "/sysBackupDel",
        GET_BACKUP_LIST: "/sysBackupRes",
        UPDATE_BACKUP: "/sysBackupModDesc",
        EXPORT_BACKUP_PATH: "/sysbackupdownload",
        //Setting
        GET_SETTING: "/confSaveRes",
        UPDATE_SETTING: "/confSaveOper",
        //db
        GET_DB_STATUS: "/getdbstatus",
        //TEST_PROJECT_NODE:"/TESTPROJECTNODE"
        //FunctionModel
        GET_FUNCTION_MODE: "/getFunctionRunMode",
        SET_FUNCTION_MODE: "/setFuncRunMode",
        GET_PROTOCOL_SWITCH_STATUS: "/get_protocol_switch_status",
        SET_PROTOCOL_SWITCH_STATUS: "/set_protocol_switch_status",

        //report
        GET_REPORT_EVENT: "/reportGenAlarmInfo",
        GET_REPORT_EVENTMODEL: "/reportGenAlarmGetmode",
        GET_REPORT_EVENTSTATIC: "/reportGenAlarmStaticsRes",
        SET_REPORT_EVENTMODEL: "/reportGenAlarmSetmode",
        SET_REPORT_DOWNLOADDETAIL: "/RptalarmDownload/",
        //audit
        GET_AUDIT_EVENT: "/reportGenProtoInfo",
        GET_AUDIT_EVENTMODEL: "/reportGenProtoGetmode",
        GET_AUDIT_EVENTSTATIC: "/reportGenProtoStaticsRes",
        SET_AUDIT_EVENTMODEL: "/reportGenProtoSetmode",
        SET_AUDIT_DOWNLOADDETAIL: "/RptprotoDownload/",
        //log

        GET_LOG_EVENT: "/reportGenLogInfo",
        GET_LOG_EVENTMODEL: "/reportGenLogGetmode",
        GET_LOG_OPERATESTATIC: "/reportGenOperlogStaticsRes",
        GET_LOG_SYSTEMSTATIC: "/reportGenSyslogStaticsRes",
        SET_LOG_EVENTMODEL: "/reportGenLogSetmode",
        SET_LOG_DOWNLOADDETAIL: "/RptlogDownload/"
    }
};
