function L() {
   if (window.console && window.console.log)
     console.log.apply(console, arguments);
}


head.ready(function() {
   $('a.account').fancybox({
         'autoDimensions': false,
         'width'         : 550,
         'height'        : 400,
         'transitionIn': 'none',
         'transitionOut': 'none',
         onComplete: function(array, index, opts) {
            head.js(JS_URLS.account);
            //$.getScript(JS_URLS.account);
         }
   });
});