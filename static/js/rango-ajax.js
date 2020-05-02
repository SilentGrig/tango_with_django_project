$(document).ready(function() {
	$('#like_btn').click(function() {
		const catecategoryIdVar = $(this).attr('data-categoryid');

		$.get('/rango/like_category/',
			{'category_id': catecategoryIdVar},
			function(data) {
				$('#like_count').html(data);
				$('#like_btn').hide();
			}
		);
	});

	$('#search-input').keyup(function() {
		const query = $(this).val();

		$.get('/rango/suggest/',
			{'suggestion': query},
			function(data) {
				$('#categories-listing').html(data);
			}
		);
	});
});