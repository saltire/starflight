$(function() {
	
	$('.dialogue').prop({scrollTop: $('.dialogue').prop('scrollHeight')});
	
	$('.command input').focus();
	
	$('.command').submit(function(e) {
		e.preventDefault();
		$.post('fetch', {command: $('.command input').val()}, function(json) {
			$('.command input').val('');
			$('.dialogue').append($('<p />').addClass('input').html(json.input));
			for (i in json.output) {
				var msg = json.output[i].replace(/\n/g, '<br />');
				$('.dialogue').append($('<p />').addClass('output').html(msg));
			}
			$('.dialogue').animate({scrollTop: $('.dialogue').prop('scrollHeight')});
		});
	});
	
	// open GET forms like links (i.e. without appending a query string)
	$('.goback, .help').submit(function(e) {
		e.preventDefault();
		window.location = $(this).attr('action');
	});
	
});