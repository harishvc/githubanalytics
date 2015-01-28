//Modified from: https://github.com/mikeal/githubarchive

var util = require('util')
  , stream = require('stream')
  , path = require('path')
  , fs = require('fs')
  , zlib = require('zlib')
  , jsonstream = require('JSONStream')
  , timezone = require('timezone')
  , request = require('request').defaults({pool:{maxSockets:1}})
  ;
var mytime = require('./mytime.js');

function CallbackStream (cb) {
  this.readable = true
  this.writable = true
  this.cb = cb
}
util.inherits(CallbackStream, stream.Stream)
CallbackStream.prototype.write = function (chunk) {
  this.emit('data', chunk)
}
CallbackStream.prototype.end = function () {
  this.emit('close')
  this.cb()
}
CallbackStream.prototype.destory = function () {}

module.exports = function (arg) {
  if (arg.slice(0, 'http://'.length) === 'http://' || arg.slice(0, 'http://'.length) === 'http://') {
    return module.exports.request(arg)
  }
  return module.exports.readFile(arg)
}

module.exports.languages = function (cb) {
  var languages = {}
  var s = new CallbackStream(function () {
    cb(null, languages)
  })
  s.languages = languages
  s.on('data', function (d) {
    if (!d.repository) return 
    if (!languages[d.repository.language]) languages[d.repository.language] = 0
    languages[d.repository.language] += 1
  })
  s.on('error', cb)
  return wrap(s)
}

module.exports.users = function (cb) {
  var users = {}
  var s = new CallbackStream(function () {
    cb(null, users)
  })
  s.users = users
  s.on('data', function (d) {
    if (!s.users[d.actor]) s.users[d.actor] = {}
  })
  s.on('error', cb)
  return wrap(s)
}

module.exports.MyParser = function (cb) {
  //console.log("1111111111111111");
  var commits = {};
  var s = new CallbackStream(function () {
    cb(null, commits)
  })
  s.commits = {}
  var actorname="";
  var organization="";
  s.on("data", function (d) {
	  //console.log("Found ......",d.type,d.repo.name);
    if (d.type === "PushEvent" && (d.repo)) {
     	//console.log ("processing commit");
    	d.payload.commits.forEach(function (sha) {
    		//console.log("#############" , sha);
            var info = {};
            info = { 
            		type: "PushEvent",
    				sha: sha['sha'],
                    created_at:mytime.tE(d.created_at),
    				full_name: d.repo.name,
    				url: "http://github.com/" + d.repo.name,
    				owner: d.actor.login,
    				actorname:  sha['author']['name'],
                    actoremail: sha['author']['email'],
                    comment: sha['message'],
                    ref: d.payload.ref,
    				//PATCH
    				name: d.repo.name,
    				language: "",
    				description: "",	
    				actorlogin: sha['author']['email']
    					
    				//MISSING - IMPORTANT
    				//language: d.repository.language,
    				//description: d.repository.description,
    				//actorlogin: sha['author']['email'],
                    /////////////////
    				//MISSING - IMPORTANT 2
                    //watchers: d.repository.watchers_count,
                    //stargazers: d.repository.stargazers_count,
                    //forks: d.repository.forks_count,
                    //issues: d.repository.open_issues_count,
                    //ref: d.payload.ref,
                    //master_branch: d.repository.master_branch,           
    				//actor: sha[3],
             };
           	if (typeof d.org !== 'undefined' && d.org.login !== 'null') 
       				{ info['organization'] = d.org.login;}
           	//Check formatted JSON
    		//http://jsonformatter.curiousconcept.com
    		//http://codebeautify.org/view/jsonviewer
    		s.commits[sha['sha']] = info;
    	}) //end foreach sha
    }  //end 'PushEvent'
  }) //end s.on('data')
  s.on('error', cb)
  return wrap(s)
}

function wrap (obj) {
  Object.keys(module.exports).forEach(function (i) {
    obj[i] = function () { return obj.pipe(module.exports[i].apply(module.exports, arguments)) }
  })
  obj.once('write', function () {
    Object.keys(module.exports).forEach(function (i) {
      obj[i] = function () { throw new Error('Cannot ask for new parsing after the first write.') }
    })
  })
  obj.on('end', function () {
    Object.keys(module.exports).forEach(function (i) {
      obj[i] = function () { throw new Error('Cannot ask for new parsing after the stream has ended.') }
    })
  })
  return obj
}

module.exports.request = function (url) {
  return wrap(request(url).pipe(zlib.createGunzip()).pipe(jsonstream.parse()))
}

module.exports.readFile = function (path, options) {
  var f = fs.createReadStream(path)
    , z = new zlib.createGunzip() 
    , j = jsonstream.parse()
  
  //if (options.gzip !== false) {
    //f.pipe(z)
    //z.pipe(j)
  //} else {
    //f.pipe(j)
  //}
  
  f.pipe(j)
  
  return wrap(j)
}

module.exports.range = function (start, end) {
  // I get Access Denied for any range I try to use in the HTTP interface
  // this is why we do a GET per hour and pipe them all together.
  // This also solves some timeout and throttling issues.
  var timestamps = []
  if (end < start) throw new Error('end is before start')
  console.log(start, end)
  var s = new Date(start)
  while (end > s) {
    timestamps.push(timezone(s, '%Y-%m-%d-%k').replace(/\ /g, ''))
    s.setHours(s.getHours()+1)
  }
  
  var output = new CallbackStream(function () {}) // noop for end
  
  timestamps.forEach(function (ts) {
    var r = request('http://data.githubarchive.org/'+ts+'.json.gz')
    r.on('response', function (resp) {
      output.emit('timerange', ts)
      if (resp.statusCode !== 200) {
        console.error('not 200', 'http://data.githubarchive.org/'+ts+'.json.gz')
        return
      }
      
      var z = new zlib.createGunzip()
        , j = jsonstream.parse()
        ;  
      j.on('data', function (obj) {
        var created = new Date(obj.created_at)
        if (created < start) return
        if (created > end) return
        output.emit('data', obj)
      })
      resp.pipe(z)
      z.pipe(j)
      
      if (timestamps.indexOf(ts) === timestamps.length - 1) j.on('end', output.end.bind(output))
    })
  })
  
  return wrap(output)
}


