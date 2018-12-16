const moapp = require("./utils/moapp.js");

App({
    onLaunch: function(options) {
            var self = this;
            this.globalData.scene = options.scene || 0;
            this.globalData.withLogin = true;
            this.globalData.uiBaseAttr4Server = ['hidden', 'color', 'width', 'height', 'background', 'backgroundColor', 'left', 'top', 'right', 'bottom', 'fontSize', 'fontWeight', 'opacity', 'text'];
            this.globalData.env = 'test';
            this.globalData.signature = 'B7108240F055D3807040CA6575318F44B015F8AD';
            moapp.appBgmAllInOne(self)
        },
    globalData: {
        },
})