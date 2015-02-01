$(document).ready(function() {

var nbaTeams = new Bloodhound({
	  //datumTokenizer: Bloodhound.tokenizers.obj.whitespace('tokens'),
	  datumTokenizer: function(d) { return Bloodhound.tokenizers.whitespace(d.tokens.join(' ')); },
	  queryTokenizer: Bloodhound.tokenizers.whitespace,
	  limit: 10,
	  prefetch: '/static/typeahead/count.json'
	});

	var nhlTeams = new Bloodhound({
	  //datumTokenizer: Bloodhound.tokenizers.obj.whitespace('tokens'),
	  datumTokenizer: function(d) { return Bloodhound.tokenizers.whitespace(d.tokens.join(' ')); },
	  queryTokenizer: Bloodhound.tokenizers.whitespace,
	  limit: 10,
	  prefetch: '/static/typeahead/reports.json'
	});

	//Clear cache
	nbaTeams.clearPrefetchCache();
	nhlTeams.clearPrefetchCache();
	//Initialize
	nbaTeams.initialize();
	nhlTeams.initialize();
	$('#multiple-datasets .typeahead')
	.typeahead({
		highlight: true
		},
		{
	  name: 'nba-teams',
	  displayKey: 'label',
	  source: nbaTeams.ttAdapter(),
	  templates: {
	    header: '<h3 class="league-name">Questions?</h3>'
	  }
	},
	{
	  name: 'nhl-teams',
	  displayKey: 'label',
	  source: nhlTeams.ttAdapter(),
	  templates: {
	    header: '<h3 class="league-name">What&#39s Happening now?</h3>'
	  }
	}
	)

	//TODO: Events for Analytics
	//http://ericsaupe.com/using-twitter-typeahead-js-custom-event-triggers/
	
});
