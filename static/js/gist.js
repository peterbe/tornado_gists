function L() {
   if (window.console && window.console.log)
      console.log.apply(console, arguments);
}

var Comments = (function() {
   var _comments;
   return {
      load_comments : function(comments) {
         _comments = comments;
      },
      display_all : function() {
         _comments.forEach(function(comment) {
            Comments.display(comment);
         });
         $('div.file-comments').fadeIn(400);
	 $('div.gist-file').each(function(i,e) {
	    if ($('div.comment', e).size() > 5) {
	       $('div.comment-link-bottom:hidden', e).show();
	    }
	 });
 
      },
      display : function(comment) {
         var container;
         if (comment.file) {
            $('div.file-comments').each(function(i, e) {
               if ($(e).attr('data-file') == comment.file) {
                  container = $(e);
               }
            });
         } else {
            container = $('div.file-comments').eq(0);
         }
         var c = $('<div/>').attr('id', 'comment-' + comment.id).addClass(
               'comment');
         var m = $('<p>').addClass('metadata');
         if (comment.user.gravatar_html) {
            $('<span>').addClass('gravatar').html(
                  comment.user.gravatar_html).appendTo(m);
         }
         $('<span>').addClass('user').html(comment.user.name).appendTo(m);
         $('<span>').addClass('ago').html(comment.ago + ' ago').appendTo(m);
         /*
          * $('<a href="#">') .addClass('comment') .text("Reply to this")
          * .attr('data-file', comment.file) .attr('data-id', comment.id)
          * .appendTo(m);
          */
         c.append(m);
         $('<div/>').html(comment.comment).appendTo(c);
         $('<div/>').addClass('clearer').appendTo(c);
         container.append(c);
      }
   }
})();

$(function() {
   $.getJSON('comments', function(response) {
      if (response.error) {
         return alert(response.error)
      }
      Comments.load_comments(response.comments);
      Comments.display_all();

      $('a.comment').each(
         function() {
            var self = $(this);
            self.qtip( {
               id : 'comment_qtip',
               content : {
                  text : $('#comment'),
                  title : {
                     text : 'Comment',
                     button : true
                  }
               },
               position : {
                  my : 'center',
                  at : 'center',
                  target : $(window)
               },
               show : {
                  event : 'click',
                  solo : true,
                  modal : true
               },
               hide : false,
               style : 'ui-tooltip-light ui-tooltip-rounded'
            });

            self.click(function() {                  
               $('input[name="file"]').val(self.attr('data-file'));
               $('#about-file code').text(self.attr('data-file'));
               $('textarea[name="comment"]').keyup(
                     _preview_comment_on_event);
               $('textarea[name="comment"]').bind('change',
                     _preview_comment_on_change);
               return false;
            });

         });
   });
});

function _preview_comment_on_change() {
   $('textarea[name="comment"]').unbind('change');
   _preview_comment(function(err) {
      if (!err) {
         // reattach
         $('textarea[name="comment"]').bind('change',
               _preview_comment_on_change);
      }
   });
}

function _preview_comment_on_event(event) {
   if (event.keyCode === 13) {
      $('textarea[name="comment"]').unbind('keyup');
      _preview_comment(function(err) {
         if (!err) {
            // reattach
            $('textarea[name="comment"]').keyup(_preview_comment_on_event);
         }
      });
   }
}

function _preview_comment(callback) {
   $.ajax('/preview_markdown', {
      cache : false,
      dataType : 'json',
      type : 'POST',
      data : {
         text : $('textarea[name="comment"]').val()
      },
      success : function(res) {
         if (res.html) {
            if ($('#preview_markdown:hidden').size()) {
               $('#preview_markdown').show();
            }
            $('#_preview').html(res.html)
         }
         callback(null, res.html);
      }
   });
}
