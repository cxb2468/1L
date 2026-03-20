// default-passive-events.js
// 使所有事件监听器默认使用 passive: true
(function() {
  var addEventListener = EventTarget.prototype.addEventListener;
  EventTarget.prototype.addEventListener = function(type, listener, options) {
    var passive = options;
    if (typeof options === 'object' && options !== null) {
      passive = options.passive;
    }
    // 对 wheel 事件默认使用 passive: true
    if (type === 'wheel' && passive === undefined) {
      options = Object.assign({}, options || {}, { passive: true });
    }
    // 对 touchstart 和 touchmove 事件也默认使用 passive: true
    if ((type === 'touchstart' || type === 'touchmove') && passive === undefined) {
      options = Object.assign({}, options || {}, { passive: true });
    }
    return addEventListener.call(this, type, listener, options);
  };
})();