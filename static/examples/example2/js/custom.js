// M is a container for everything
M = {};
M.env = {};
M.env.is_ios =  /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
M.env.is_cordova = !!window.cordova;

// M configuration parameters
M.config = {};
M.config.url = 'http://127.0.0.1:8080/static/examples/complex/';

// service variables
M.ini = {};
M.ini.page = 'home';
M.ini.vars = {};
M.ini.status = ''; // loading or ready
M.ini.iocount = 0; // number ajax requests in progress
// user defined variables
M.ini.user = { username: '', email: '', logged: false };
M.ini.keyword = '';
M.ini.items = [];

// service methgods
M.methods = {};
M.methods.done = function(page, vars) { M.vue.page = page; M.vue.vars = vars; M.vue.status='ready'; };
M.methods.go = function(page, vars) { M.vue.status = 'loading'; console.log(M.pages[page]); M.pages[page](page, vars); };
// user defined methods
M.methods.login = function() { M.vue.user.logged = true; M.methods.go('home'); };
M.methods.logout = function() { M.vue.user = { username: '', email: '', logged: false }; M.methods.go('home'); };
M.methods.reload_package = function() { STARTUP.upgrade(); };

// user defined pages
M.pages = {};
M.pages.home = function(page) { M.methods.done(page);};
M.pages.login = function(page) { M.methods.done(page);};
M.pages.search = function(page) { 
    M.vue.keyword=''; 
    M.methods.done(page);
};
M.pages.results = function(page, keyword) { 
    keyword = keyword.toLowerCase();
    M.vue.items = [];
    axios.get(M.config.url+'names.json').then(function(res){
            M.vue.items = res.data.filter(function(item){ 
                    return item.toLowerCase().indexOf(keyword)>=0; 
                });
            M.methods.done(page, keyword);
        }, function(){ M.methods.done(M.vue.page, M.vue.vars); }); // on error stay on current page
};

// other system functions
M.before_start = function() {};
M.after_start = function() {};
M.on_app_paused = function() {};
M.on_app_resumed = function() {};
M.on_notification_received = function(data) { };
M.on_notification_opened = function(data) { };
M.on_device_ready = function() {
    // device info: device.manufacturer, device.model, device.platform, device.version
    // on iOS do not let keyborad scroll text
    if(M.env.is_ios && M.env.is_cordova && cordova.plugins.Keyboard) cordova.plugins.Keyboard.disableScroll(true);
    // user inappbrowser
    window.open = cordova.InAppBrowser.open;
    // if onesgnal present, register device
    if(M.config.onesignal_id && window.plugins && window.plugins.OneSignal) {
        var OS = window.plugins.OneSignal;
        OS.startInit(M.config.onesignal_id)
            .inFocusDisplaying(os.OSInFocusDisplayOption.Notification)
            .handleNotificationReceived(M.on_notificatoion_received)
            .os.handleNotificationOpened(M.on_notification_opened)
            .endInit();
        OS.getIds(function(ids) {
                if(ids && ids.userId) {
                    window.localStorage.storeItem('onesignal', JSON.stringify(ids));
                    os.registerForPushNotifications();
                }
            });
    }
    M.after_start();
};

M.on_app_start = function() {
    M.before_start();
    M.vue = new Vue({el:'#app', data:M.ini, methods:M.methods});
    document.addEventListener("backbutton", M.on_backbutton, false);
    document.addEventListener("pause", M.on_app_paused, false);
    document.addEventListener("resume", M.on_app_resumed, false); 
    if(M.env.is_cordova) {
        if(window.STARTUP) {
            M.on_device_ready();
        } else {
            document.addEventListener('deviceready', M.on_device_ready, false);
        }
    } else {
        M.after_start();
    }
};

M.on_app_start();