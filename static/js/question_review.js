head.ready(function() {
   $('button[name="rating_button"]').click(function() {
      $('button.bold', '#rating_buttons').removeClass('bold');
      $(this).addClass('bold');
      $('#id_rating').val($(this).val());
   });
   $('button[name="verdict_button"]').click(function() {
      $('button.bold', '#verdict_buttons').removeClass('bold');
      $(this).addClass('bold');
      $('#id_verdict').val($(this).val());
   });
   
   if ($('#id_rating').val().length) {
      $('#rating_buttons button').each(function() {
	 if ($(this).val() == $('#id_rating').val()) {
	    $(this).click();
	 }
      });
   }
   
   if ($('#id_verdict').val().length) {
      $('#verdict_buttons button').each(function() {
	 if ($(this).val() == $('#id_verdict').val()) {
	    $(this).click();
	 }
      });
   }
   $('#question_actions form[method="post"]').submit(function() {
      L('submitting');
      if (!$('#id_rating').val().length) {
	 alert("Please choose a rating first");
	 return false;
      }
      if (!$('#id_verdict').val().length) {
	 alert("Please choose a verdict");
	 return false;
      } else if ('WRONG' == $('#id_verdict').val()) {
	 if (!$.trim($('#id_comment').val()).length) {
	    alert("With that verdict, please enter a comment.\nFor example a URL that shows the answer as being wrong.");
	    return false;
	 }
      }
      return true;
   });
});