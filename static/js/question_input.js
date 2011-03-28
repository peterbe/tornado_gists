/* Nothing yet */

var Form = (function() {
   function shuffle(o) { //v1.0
      for(var j, x, i = o.length; i; j = parseInt(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
      return o;
   };

   return {
      has_all_alternatives: function() {
         var count = 0;
         $('input[name="alternatives"]').each(function(i,e) {
            if ($(this).val().length) {
               count++;
            }
         });
         return count >= 4;
      },
      shuffle_alternatives: function(animate) {
         animate = animate != null ? animate : 15;
         var alts = [];
         $('input[name="alternatives"]').each(function(i,e) {
            alts.push($(this).val());
         });
         alts = shuffle(alts);
         $('input[name="alternatives"]').each(function(i,e) {
            $(this).val(alts[i]);
         });
         if (animate > 0) {
            setTimeout(function() {
               Form.shuffle_alternatives(animate - 1);
            }, 40 + (10 * (20 - animate)));
         }
      },
      add_shuffler: function() {
         $('<a>', {href:'#', text:'shuffle'})
           .addClass('shuffler')
             .click(function() {
                if (Form.has_all_alternatives) {
                   Form.shuffle_alternatives();
                }
                return false;
             })
               .insertAfter($('input[name="alternatives"]').eq(-1));
      }
   }
})();

var GENRE_NAMES;
head.js(JS_URLS.jquery_autocomplete, function() {
   $.getJSON('/questions/genre_names.json', function(r) {
      $('input[name="genre"]').autocomplete(r.names);
   });
});

head.ready(function() {
   if (Form.has_all_alternatives()) {
      Form.add_shuffler();
   }
   $('form[method="post"]', '#content_inner').submit(function() {
      var answer = $('input[name="answer"]').val();
      var alternatives = [];
      $('input[name="alternatives"]').each(function() {
         if ($(this).val().length) {
            alternatives.push($(this).val());
         }
      });
      if (alternatives.length >= 4) {
         if (-1 == alternatives.indexOf(answer)) {
            alert("One of the alternatives must be the answer");
            return false;
         }
      } else {
         alert("Please fill in 4 alternatives");
         return false;
      }
      return true;
   });
   $('input[name="alternatives"]').change(function() {
      if ($(this).val().length && Form.has_all_alternatives() && !$('.shuffler').size()) {
         Form.add_shuffler();
      }
   });
   $('input[name="answer"]').change(function() {
      if ($(this).val().length && ! Form.has_all_alternatives()) {
         var _added = false;
         $('input[name="alternatives"]').each(function(i, e) {
            if (!_added && !$(this).val().length) {
               $(this).val($('input[name="answer"]').val());
               _added = true;
            }
         });
      }
   });
   
   // on the Edit question page
   $('input[name="submit_question"]').click(function() {
      return confirm("Are you sure?\nQuestion can not be edited after this.");
   });
});