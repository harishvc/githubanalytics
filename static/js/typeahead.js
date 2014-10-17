$(document).ready(function() {

var nbaTeams = new Bloodhound({
	  //datumTokenizer: Bloodhound.tokenizers.obj.whitespace('tokens'),
	  datumTokenizer: function(d) { return Bloodhound.tokenizers.whitespace(d.tokens.join(' ')); },
	  queryTokenizer: Bloodhound.tokenizers.whitespace,
	  limit: 10,
	  //prefetch: '/static/typeahead/repos.json',  //CONSOLE ERROR - TOO BIG!
	  remote: '/static/typeahead/repos.json' //WORKS
	});
	 
	var nhlTeams = new Bloodhound({
	  //datumTokenizer: Bloodhound.tokenizers.obj.whitespace('tokens'),
	   datumTokenizer: function(d) { return Bloodhound.tokenizers.whitespace(d.tokens.join(' ')); },
	  queryTokenizer: Bloodhound.tokenizers.whitespace,
	  limit: 10,
	  prefetch: '/static/typeahead/active.json'
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
	    header: '<h3 class="league-name">Respositories</h3>'
	  }
	},
	{
	  name: 'nhl-teams',
	  displayKey: 'label',
	  source: nhlTeams.ttAdapter(),
	  templates: {
	    header: '<h3 class="league-name">Active Listings</h3>'
	  }
	}
	)
	
	//TODO: Events for Analytics
	//http://ericsaupe.com/using-twitter-typeahead-js-custom-event-triggers/
	//.on('typeahead:opened', onOpened)
    //.on('typeahead:selected', onAutocompleted)
    //.on('typeahead:autocompleted', onSelected);
	//function onOpened($e) {
	  //  console.log('opened');
	//}
	 
	//function onAutocompleted($e, datum) {
	  //  console.log('autocompleted');
	   // console.log(datum);
	//}
	 
	//function onSelected($e, datum) {
	  //  console.log('selected');
	   // console.log(datum);
	//}


});