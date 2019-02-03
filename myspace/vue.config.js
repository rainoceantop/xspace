module.exports = {
    chainWebpack: config => {
        config.module
            .rule('fonts')
            .use('url-loader')
            .loader('url-loader')
            .tap(options => {
                options.limit = 15000
                return options
            })
    }
}