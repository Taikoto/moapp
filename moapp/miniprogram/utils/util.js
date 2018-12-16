module.exports = {
    // 将json转换为url参数
    jsonToUrlParams: (json_data) => {
        let params = ''        
        for(var k in json_data || {}) {                     
            params += '&' + k + '=' + encodeURIComponent(json_data[k]);
        }

        return params.length == 0 ? '' : params.slice(1, params.length);
    }
}