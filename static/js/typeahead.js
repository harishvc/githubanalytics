$(document).ready(function() {

	var bestPictures = new Bloodhound({
		  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
		  queryTokenizer: Bloodhound.tokenizers.whitespace,
		  prefetch: '/static/typeahead/queries.json',
		  remote: '/tsearch?q=%QUERY',
		  limit: 10 // limit to show only 10 results
		});
		 
		bestPictures.initialize();
		 
		$('#multiple-datasets .typeahead').typeahead({
			hint: true,
			highlight: true,
			minLength: 1 // send AJAX request only after user type in at least 1 characters
		}, {
			name: 'best-pictures',
			displayKey: 'value',
			source: bestPictures.ttAdapter()
		});
});
