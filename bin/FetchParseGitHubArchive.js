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

GetParse();

//Fetch GitHub Archives, parse  'PushEvent' event notifications and insert into MongoDB
//Sample JSON generated
//{"078d40cc5":{"created_at":"2014-08-23T15:05:37-07:00","full_name":"ssss"},
// "0b0084e21":{"created_at":"2014-08-23T15:05:37-07:00","full_name":yyyyy"}}
function GetParse() {
	var count = 0; //number of entries
	var rows = [];
	var TimeNow = moment().format();
	var TimeAgo = moment().subtract(2, 'hours').format("YYYY-MM-DD-H");
	
	//Test 1 - fetch prior URL
	//TimeAgo ="2014-08-28-10"  //10345  
	
	var URL = "http://data.githubarchive.org/" + TimeAgo + ".json.gz";
	console.log (TimeNow + " processing " + URL);
	var a = archive(URL, {gzip:true});

	//Test 2 - read test file
    //var npath = path.join(__dirname, '2014-sample.json')
    //console.log ("Testing sample json ..." + npath);
    //var a = archive.readFile(npath, {gzip:false});

    var com = a.MyParser(function (err, commits) {
    	if (err) return console.log(err);
    	//console.log(JSON.stringify(com.commits));
    	var tmp = JSON.stringify(com.commits);
    	var result = JSON.parse(tmp);
    	//create array
    	for(var k in result) {
    	    //console.log (k);          //print keys
    	    count ++;
    	    rows.push(result[k]);       //create array
            //console.log (result[k]);  //print values
    	}
    	console.log ("## entries: " + count);
    	//Insert into MongoDB
    	console.log("## start insert: "+ moment().format());
    	MongoInsert(rows,count);
	 
    //Debug - store to external file
	//var tmp_dir = path.join(process.cwd(), "output/");
	//if (!fs.existsSync(tmp_dir))
	    //fs.mkdirSync(tmp_dir);
	//var p = tmp_dir + 'PushEvent.json';	
	//fs.writeFile(p, JSON.stringify(com.commits), function (err) {
		//if (err) return console.log(err);
	//});
    }); //end MyParser

} //end GetParse()

function MongoInsert(rows,count)
{
	var connectURL  = process.env.connectURL;
	var mycollection= process.env.mycollection;
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
	  function (callback){
		  //console.log ("close db");
		  db.close();
		  console.log("## end insert: "+ moment().format());
		  callback(null,"connection closed");
	  }
	 ], function(error, results) {
			if (error) { console.log("error"); }
				//console.log(results);
		});	
}
