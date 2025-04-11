// webpack.config.js
const path = require('path');

module.exports = {
  entry: '/src/workflow-designer.js',
  output: {
    filename: 'workflow-designer.js',
    path: path.resolve(__dirname, 'clio/static/workflows/js'),
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader']
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx']
  }
};