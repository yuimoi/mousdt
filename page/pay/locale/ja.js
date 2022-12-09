(function (global, factory) {
  if (typeof define === "function" && define.amd) {
    define('element/locale/ja', ['module', 'exports'], factory);
  } else if (typeof exports !== "undefined") {
    factory(module, exports);
  } else {
    var mod = {
      exports: {}
    };
    factory(mod, mod.exports);
    global.ELEMENT.lang = global.ELEMENT.lang || {}; 
    global.ELEMENT.lang.ja = mod.exports;
  }
})(this, function (module, exports) {
  'use strict';

  exports.__esModule = true;
  exports.default = {
    el: {
      'checkout_counter': 'レジカウンター',
      'paid': '支払った',
      'copy': 'コピー',
      'remaining_time': '残り時間',
      'cancel': '取消',
      'confirm': '确定',
      'order_timeout': '订单超时',
      'please_select': '请选择',
      'total_amount': '合計金額',
      'address': 'アドレス',
      'network': 'ネットワーク',

      'tips1': '振込依頼が放送されるまでには1～3分かかります。ご入金確認の際は、十分な余裕を持ってご確認ください。注文完了後、まだ金額が届いていない場合は、サイト管理者までご連絡ください',
      'tips2': 'TRONネットワークを利用して、指定された金額を指定された時間内に上記アドレスに送金してください。',


    }
  };
  module.exports = exports['default'];
});