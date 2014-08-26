var util = require('util')
  , stream = require('stream')
  , path = require('path')
  , fs = require('fs')
  , zlib = require('zlib')
  , jsonstream = require('JSONStream')
  , request = require('request')
  ;

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
  s.on('data', function (d) {
    if (!d.repository) return 
    if (!languages[d.repository.language]) languages[d.repository.language] = 0
    languages[d.repository.language] += 1
  })
  s.on('error', cb)
  return wrap(s)
}

function wrap (obj) {
  Object.keys(module.exports).forEach(function (i) {
    obj[i] = function () { obj.pipe(module.exports[i].apply(module.exports, arguments)) }
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

module.exports.readFile = function (path) {
  return wrap(fs.createReadStream(path).pipe(new zlib.createGunzip()).pipe(jsonstream.parse()))
}


