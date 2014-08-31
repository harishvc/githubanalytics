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

//http://nickfishman.com/post/49533681471/nodejs-http-requests-with-gzip-deflate-compression
var headers = {
  "accept-encoding" : "gzip,deflate",
}
 
var options = {
  headers: headers
}

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
  var commits = {}
  var s = new CallbackStream(function () {
    cb(null, commits)
  })
  s.commits = {}
  var actorname="";
  s.on("data", function (d) {
    if (d.type === "PushEvent") {
    	d.payload.shas.forEach(function (sha) {
	    //console.log("Processing ===> " + sha[0] + " " + d.actor_attributes.name + " URL ===> " + d.repository.url);
            var info = {};
            //Handle empty name attribute
            if (d.actor_attributes.name != null && d.actor_attributes.name != 'undefined'){
            	actorname = d.actor_attributes.name;
            }
            else {
            	actorname =  d.actor_attributes.login;
                //console.log ("### Caught no name " + d.actor_attributes.login); 
            }
    		info = { 
   				created_at: d.created_at,
                    full_name: d.repository.full_name,
    				name: d.repository.name,
    				url: d.repository.url,
    				language: d.repository.language,
    				description: d.repository.description,
                    watchers: d.repository.watchers_count,
                    stargazers: d.repository.stargazers_count,
                    forks: d.repository.forks_count,
                    issues: d.repository.open_issues_count,
                    owner: d.repository.owner,
                    organization: d.repository.organization,
                    //actor: sha[3],
                    actorlogin: d.actor_attributes.login,
                    actorname:  actorname,
                    ref: d.payload.ref,
                    master_branch: d.repository.master_branch,
                    comment: sha[2] 
    				};
    		//Check formatted JSON
    		//http://jsonformatter.curiousconcept.com
    		//http://codebeautify.org/view/jsonviewer
    		s.commits[sha[0]] = info;
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
  // http://nickfishman.com/post/49533681471/nodejs-http-requests-with-gzip-deflate-compression
  var headers = {
  "accept-charset" : "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
  "accept-language" : "en-US,en;q=0.8",
  "accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
  "accept-encoding" : "gzip,deflate",
  } 
  var options = {
  url: url,
  headers: headers
  }
  return wrap(request(options).pipe(zlib.createGunzip()).pipe(jsonstream.parse()))
}

module.exports.readFile = function (path, options) {


  var f = fs.createReadStream(path)
    , z = new zlib.createGunzip() 
    , j = jsonstream.parse()
  
  if (options.gzip !== false) {
    f.pipe(z)
    z.pipe(j)
  } else {
    f.pipe(j)
  }
  
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


