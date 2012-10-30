$(function() {
	
	$('.dialogue').prop({scrollTop: $('.dialogue').prop('scrollHeight')});
	
	$('.command input').focus();
	
	$('.command').submit(function(e) {
		e.preventDefault();
		var input = $('.command input').val()
		$.post('fetch', {command: input}, function(json) {
			$('.command input').val('');
			$('.dialogue').append($('<p />').addClass('input').html(input));
			for (i in json.output) {
				var msg = json.output[i].replace('\n', '<br />');
				$('.dialogue').append($('<p />').addClass('output').html(msg));
			}
			$('.dialogue').animate({scrollTop: $('.dialogue').prop('scrollHeight')});
		});
		
	});
	
});