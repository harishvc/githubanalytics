console.log ("0: I am here");
var archive = require('./mikeal-githubarchive.js');
console.log ("1: I am here");
var path = require('path');
var assert = require('assert');
var underscore = require('underscore');
var moment = require('moment');
var fs = require('fs');
console.log ("2: I am here");

TimeAgo = moment().subtract(2, 'hours').format("YYYY-MM-DD-HH");
console.log ("3: I am here");

//Testing
//TimeAgo ="2014-08-28-10"  
URL = "http://data.githubarchive.org/" + TimeAgo + ".json.gz";
console.log ("Processing: " + URL);

//Fetch GitHub Archives & Generate JSON file with 'PushEvent' event notifications
var a = archive(URL, {gzip:true});
var com = a.MyParser(function (err, commits) {
  //console.log(JSON.stringify(com.commits));
  fs.writeFile("./data/PushEvent.json", JSON.stringify(com.commits), function (err) {
	  if (err) return console.log(err);
	});
  if (err) return console.log(err);
})
