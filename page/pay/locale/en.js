(function (global, factory) {
  if (typeof define === "function" && define.amd) {
    define('element/locale/en', ['module', 'exports'], factory);
  } else if (typeof exports !== "undefined") {
    factory(module, exports);
  } else {
    var mod = {
      exports: {}
    };
    factory(mod, mod.exports);
    global.ELEMENT.lang = global.ELEMENT.lang || {}; 
    global.ELEMENT.lang.en = mod.exports;
  }
})(this, function (module, exports) {
  'use strict';

  exports.__esModule = true;
  exports.default = {
    el: {
      'checkout_counter': 'Checkout Counter',
      'paid': 'Paid',
      'copy': 'Copy',
      'remaining_time': 'remaining time',
      'cancel': 'cancel',
      'confirm': 'confirm',
      'order_timeout': 'order timeout',
      'please_select': 'please select',
      'total_amount': 'total amount',
      'address': 'address',
      'network': 'network',

      'tips1': 'It takes 1-3 minutes for the transfer request to be broadcast. Please allow enough time for confirmation when confirming the payment. If you still have not received the amount after the order is completed, please contact the website administrator',
      'tips2': 'Please use the TRON network to transfer the specified amount to the above address within the specified time'
    }
  };
  module.exports = exports['default'];
});