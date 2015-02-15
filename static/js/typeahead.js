$(document).ready(function() {
		var TQuestions = new Bloodhound({
		  datumTokenizer: function(d) { return Bloodhound.tokenizers.whitespace(d.tokens.join(' ')); },
		  queryTokenizer: Bloodhound.tokenizers.whitespace,
		  limit: 10,
		  prefetch: '/static/typeahead/queries.json'
		});

		var RQuestions = new Bloodhound({
		  datumTokenizer: function(d) { return Bloodhound.tokenizers.whitespace(d.tokens.join(' ')); },
		  queryTokenizer: Bloodhound.tokenizers.whitespace,
		  limit: 10,
		  remote: '/tsearch?q=%QUERY'
		});

		//Clear cache
		TQuestions.clearPrefetchCache();
		RQuestions.clearPrefetchCache();
		//Initialize
		TQuestions.initialize();
		RQuestions.initialize();
		$('#multiple-datasets .typeahead')
		.typeahead({
			hint: true,
			highlight: true
			//minLength: 1 
			},
			{
		  displayKey: 'label',
		  source: TQuestions.ttAdapter(),
		  templates: {
		    header: '<h3 class="league-name">Questions?</h3>'
		  }
		},
		{
		  displayKey: 'value',
		  source: RQuestions.ttAdapter(),
		  templates: {
		    header: '<h3 class="league-name">Repositories</h3>'
		  }
		}
		)
});