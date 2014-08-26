var archive = require('./lib/mikeal-githubarchive.js');
var path = require('path');
var assert = require('assert');
var underscore = require('underscore');
var moment = require('moment');
var fs = require('fs');

TimeAgo = moment().subtract(2, 'hours').format("YYYY-MM-DD-HH");
URL = "http://data.githubarchive.org/" + TimeAgo + ".json.gz";
console.log ("Processing: " + URL);

//Fetch GitHub Archives & Generate JSON file with 'PushEvent' event notifications
var a = archive(URL, {gzip:true});
var com = a.MyParser(function (err, commits) {
  //console.log(JSON.stringify(com.commits));
  fs.writeFile("./app/data/PushEvent.json", JSON.stringify(com.commits), function (err) {
	  if (err) return console.log(err);
	});
  if (err) return console.log(err);
})
