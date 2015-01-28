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

//Fetch GitHub Archives, parse  'PushEvent' event notifications and insert into MongoDB
//Sample JSON generated
//{"078d40cc5":{"created_at":"2014-08-23T15:05:37-07:00","full_name":"ssss"},
// "0b0084e21":{"created_at":"2014-08-23T15:05:37-07:00","full_name":yyyyy"}}
function GetParse() {
	var count = 0; //number of entries
	var rows = [];
	//var TimeNow = moment.utc().format();
	//console.log (TimeNow + " processing " + URL);
	//Time an hour ago in UTC
	var TimeAgo = moment.utc().subtract(1, 'hours').format("YYYY-MM-DD-H");
	var URL = "http://data.githubarchive.org/" + TimeAgo + ".json.gz";
	//TEST
	//var URL = "http://23.239.20.13/github-events/github-events-2015Jan19-sample1.json.gz";
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
    	console.log ("## entries generated fron githubarchive.org: " + numeral(count).format('0,0') );
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
    	console.log (connectURL);
    	console.log (mycollection);
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
		  //console.log ("insert begin ...");		          
		  var i = 1;
		  async.whilst(
		    function() { return i <= count },
		    function(callback) {
		    	var mydocument = rows.shift();
                        //TODO: Check for unique SHA before insert
		        col.insert(mydocument,function(error,result) {
		            if (error) {
		                console.log("insert error:" + error);
		                callback(error);
		                return;
		            }
		            //console.log ("inserted ...");
		            i++;
		            callback(error);
		        }); //end insert
		    },
		    function(error) {
		      callback(error,"insert sucess")
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
