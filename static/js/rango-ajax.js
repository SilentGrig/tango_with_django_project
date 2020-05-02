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

	$('.add-page').click(function() {
		const catecategoryIdVar = $(this).attr('data-categoryid');
		const dataPageTitle = $(this).attr('data-pagetitle');
		const dataPageUrl = $(this).attr('data-pageurl');
		const clickedButton = $(this);

		$.get("/rango/search_add_page/",
			{
				"category_id" : catecategoryIdVar,
				"page_title": dataPageTitle,
				"page_url": dataPageUrl
		},
		function(data) {
			$('#page-list').html(data);
			clickedButton.hide();
		}
		);
	});
});