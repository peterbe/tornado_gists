head.ready(function() {
   $('form#reject').submit(function() {
      if ($('#reject_comment:hidden').size()) {
         $('#reject_comment').show();
         return false;
      }
   });
});