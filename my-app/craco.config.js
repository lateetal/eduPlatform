module.exports = {
  // 对 webpack 的配置进行扩展
  webpack: {
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/, // 匹配 js 和 jsx 文件
          exclude: /node_modules/, // 排除 node_modules 文件夹
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env', '@babel/preset-react'], // 使用的 Babel presets
            },
          },
        },
      ],
    },
    resolve: {
      alias: {
        'react/jsx-runtime': 'react/jsx-runtime.js', // 添加 alias 配置
      },
    },
  },

  // 如果你有其他配置需求，可以在这里继续添加
  plugins: [], // 插件配置（可选）

  // 添加其他自定义配置（如开发服务器、环境变量等）
  devServer: {
    historyApiFallback: true, // 如果使用 React Router，确保可以处理历史 API
  },
};