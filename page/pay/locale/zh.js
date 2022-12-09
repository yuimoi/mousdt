(function (global, factory) {
  if (typeof define === "function" && define.amd) {
    define('element/locale/zh', ['module', 'exports'], factory);
  } else if (typeof exports !== "undefined") {
    factory(module, exports);
  } else {
    var mod = {
      exports: {}
    };
    factory(mod, mod.exports);
    global.ELEMENT.lang = global.ELEMENT.lang || {}; 
    global.ELEMENT.lang.zh = mod.exports;
  }
})(this, function (module, exports) {
  'use strict';

  exports.__esModule = true;
  exports.default = {
    el: {
      'checkout_counter': '收银台',
      'paid': '已付',
      'copy': '复制',
      'remaining_time': '剩余时间',
      'cancel': 'キャンセル',
      'confirm': '確認',
      'order_timeout': '注文タイムアウト',
      'please_select': '選んでください',
      'total_amount': '支付总数',
      'address': '地址',
      'network': '主网',

      'tips1': '转账请求需要1-3分钟时间广播，请在确定支付时预留足够的确认时间，若订单结束后仍然没有到账，请联系网站管理员',
      'tips2': '请在规定时间内使用TRON主网向上述地址转账规定金额'

    }
  };
  module.exports = exports['default'];
});