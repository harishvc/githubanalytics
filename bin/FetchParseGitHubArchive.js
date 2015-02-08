#!/usr/bin/env node 
//References & Resources
//http://www.spacjer.com/blog/2014/02/10/defining-node-dot-js-task-for-heroku-scheduler/
//http://stackoverflow.com/questions/25659134/insert-error-using-node-js-async-series
var archive = require('./mikeal-githubarchive.js');
var fs = require('fs');
var util = require('util');
var mongodb = require('mongodb');
var MongoClient = mongodb.MongoClient;
var async = require('async');
var assert = require('assert');
var underscore = require('underscore');
var moment = require('moment');
var path = require("path");
var numeral = require('numeral');

GetParse();

//Fetch GitHub Archives, parse events and insert into MongoDB
//Usage: crontab or command line
function GetParse() {
	var count = 0; //number of entries
	var rows = [];
	//var TimeNow = moment.utc().format();
	//console.log (TimeNow + " processing " + URL);
	//Time an hour ago in UTC
	var TimeAgo = moment.utc().subtract(2, 'hours').format("YYYY-MM-DD-H");
	var URL = "http://data.githubarchive.org/" + TimeAgo + ".json.gz";
	//TEST
	//var URL = "http://data.githubarchive.org/2015-01-28-0.json.gz";
	console.log("###############################################");
	console.log (moment().format("YYYY-MM-DD HH:mm:ss") + " start processing ... " + URL);
	var a = archive(URL, {gzip:true});
	var com = a.MyParser(function (err, commits) {
      	 if (err) return console.log(err);
    	  //console.log(JSON.stringify(com.commits)); //print {}
    	  var tmp = JSON.stringify(com.commits);
    	  var result = JSON.parse(tmp);
    	  //create array
    	  for(var k in result) {
    	    //console.log (k);          //print key
    	    count ++;
    	    rows.push(result[k]);       //create array
            //console.log (result[k]);  //print value
    	  }
    	console.log ("## entries generated from githubarchive.org: " + numeral(count).format('0,0') );
    	console.log (moment().format("YYYY-MM-DD HH:mm:ss") + " end processing");
    	//Insert into MongoDB
    	//console.log("## start insert: "+ moment().format());
    	console.log (moment().format("YYYY-MM-DD HH:mm:ss") + " start inserting to mongodb ");
    	MongoInsert(rows,count);
    	}
    ); //end MyParser
} //end GetParse()

function MongoInsert(rows,count)
{
    var connectURL, mycollection;
    if (process.env.deployEnv == "production") {
    	connectURL  = process.env.connectURL;
    	mycollection= process.env.mycollection;
    }
    else
    	{
    	connectURL   = process.env.connectURLdev;
    	mycollection = process.env.mycollectiondev;
    	console.log ("### DEVELOPMENT ###")
    }
	var db;
	var col;

	async.series([
	  // Connect to DB
	  function(callback) {
		  MongoClient.connect(connectURL,function(error, db2) {
			  if (error) {console.log("db connect error" + error);callback(error,"db connect error"); return;} 
			  db = db2;
			  callback(null,"connect success");
		  });
	  },
	  function(callback) {
		  col = db.collection(mycollection);
	      callback(null,"collection success");
	  },
	  function(callback) {
		  var i = 1;
		  async.whilst(
		    function() { return i <= count },
		    function(callback) {
		    	var mydocument = rows.shift();
		    	//Inserting events
		    	if (mydocument['type'] === 'CreateEvent' || mydocument['type'] === 'PushEvent' || mydocument['type'] === 'WatchEvent') {
		    		col.insert(mydocument,function(error,result) {
		        		if (error) {
		        			console.log("insert error:" + error);
		        			callback(error);
		        			return;
		        		}
		        		i++;
		        		callback(null,"insert success");
		        	}); //end insert
		        } //end if
		    },
		    function(error) {
		      callback(error,"insert error")
		    }
		  );
	  },
	  function (callback) {
		  //Delete entries older than 24 hours
		  var TimePeriod = moment().subtract(24, 'hours').valueOf();
		  //console.log ("Deleting entries older than " + moment(TimePeriod).format());
		  console.log ("Deleting entries older than " + TimePeriod);
		  col.remove({created_at: {'$lt': TimePeriod}},function(error,numberRemoved){
			  console.log("## deleted: " + numeral(numberRemoved).format('0,0')   );
			  callback(null,"delete sucess");
    	  });
	  },
	  function (callback) {
		  //Re-index
		  console.log ("start re-index");
		  col.reIndex({},function(error){
			  callback(null,"re-index sucess");
    	  });
      },
      function (callback) {
    	  //# documents
    	  col.count(function(err, count) {
            console.log("### documents:",numeral(count).format('0,0'));
            callback(null,"count");
          });
      },
	  function (callback){
		  //console.log ("close db");
		  db.close();
		  //console.log("## end insert: "+ moment().format());
		  console.log (moment().format("YYYY-MM-DD HH:mm:ss") + " end inserting to mongodb ");
		  callback(null,"connection closed");
	  }
	 ], function(error, results) {
			if (error) { console.log("error"); }
				//console.log(results);
		});	
}
