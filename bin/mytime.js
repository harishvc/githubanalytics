//References
//https://developer.github.com/v3/

var moment = require('moment');

//Convert ISO 8601 to epoch
//Example: 2014-08-23T15:05:36-07:00  => 1408831536000 
exports.tE = function (input) {
var a = moment.utc(input,moment.ISO_8601).valueOf();
//console.log (input + "====>" + a);
return (a);
}

//convert epoch to ISO8601
//Example: 1408831536000  => 2014-08-23T15:05:36-07:00 
function tISO8601(input) {
var a = moment(parseInt(input)).format();   
//console.log (input + "====>" + a);
return (a);
}

//http://stackoverflow.com/questions/25696573/moment-js-not-properly-converting-epoch-to-iso8601
function ISOEpoch() {
var input ="2014-08-23T15:05:36-07:00";
var a = moment(input,moment.ISO_8601).valueOf();
console.log ("convert ISO8601 to epoch time:" + input + "====>" + a);
var b = moment(parseInt(a)).format();
console.log ("convert epoch time to ISO8601:" + a + "====>" + b);
}

