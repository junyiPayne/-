const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  // 生产环境配置
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  outputDir: 'dist',
  assetsDir: 'static',
  // 生产环境关闭 source map 以提高性能和安全性
  productionSourceMap: false,
  // 开发服务器配置
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        ws: true
      },
      '/static': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    },
    client: {
      webSocketURL: 'ws://localhost:8080/ws',
    },
    allowedHosts: 'all'
  },
  // 构建优化
  configureWebpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            name: 'chunk-vendors',
            test: /[\\/]node_modules[\\/]/,
            priority: 10,
            chunks: 'initial'
          },
          elementPlus: {
            name: 'chunk-elementPlus',
            test: /[\\/]node_modules[\\/]_?element-plus(.*)/,
            priority: 20
          },
          echarts: {
            name: 'chunk-echarts',
            test: /[\\/]node_modules[\\/]_?echarts(.*)/,
            priority: 20
          }
        }
      }
    }
  },
  // 链式配置
  chainWebpack: config => {
    // 生产环境移除 console
    if (process.env.NODE_ENV === 'production') {
      config.optimization.minimizer('terser').tap(args => {
        args[0].terserOptions.compress.drop_console = true
        return args
      })
    }
  }
})

