const app = getApp();
const moapp = require("../../utils/moapp.js"); 

Page({
    onInputChange_ovk5OK:  function(evt) {
                var self = this;
                
            self.setData({
                __input1_value: evt.detail.value
            })
            ;
                var evt_data = moapp.genEventData("wx4ecd2c3018e1dd6b", "first", self, evt.detail.value);
               
                Promise.resolve(evt_data).then( function(evt) {
            return evt;
        }
        ).catch( err => {/*console.log("Event exception, err:");console.log(JSON.stringify(err));*/})
            }
            ,
    onButtonTap_Oapzpx:  function(evt) {
                var self = this;
                var evt_data = moapp.genEventData("wx4ecd2c3018e1dd6b", "first", self, evt.currentTarget.dataset);
                Promise.resolve(evt_data).then( function(evt) {
                return moapp.requestCloudFunction(self, 'wx4ecd2c3018e1dd6b', 'test0602', 'helloMoApp', evt);
            }
            ).catch( err => {/*console.log("Event exception, err:");console.log(JSON.stringify(err));*/})
            }
            ,
    data: {
    "objects": [
        "input1"
    ],
    "__input1_placeholder": "\u8bf7\u8f93\u5165\u4f60\u7684\u540d\u5b57",
    "__input1_value": "",
    "__input1_width": "700rpx",
    "__input1_height": "70rpx",
    "__input1_left": "0rpx",
    "__input1_top": "180rpx",
    "__input1_right": "0rpx"
},
    onLoad: function(options) {
            for (let k in options){
                if(typeof(options[k]) == 'string') {
                    options[k] = decodeURIComponent(options[k])
                }
            }
            this.setData({
                options: options,
                createTime: parseInt(Date.now()/1000)
            });           
            moapp.bgmAllInOne(this, app);
            ;
        },
    bgmcontrol: function(){
            moapp.bgmControl(this, app)                
        },
    formIdHandler: function (e) {
                    console.log(e)
                    var appid= `wx4ecd2c3018e1dd6b`
                    console.log(appid)
                    moapp.submitFormId(appid, e.detail.formId)

                },
})