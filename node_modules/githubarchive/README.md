### githubarchive -- Streaming parsers for the github archive.

###### Install

$ npm install githubarchive

###### Usage

```javascript
var archive = require('archive')
archive('http://data.githubarchive.org/2012-04-11-15.json.gz').languages(function (err, langs) {
  if (err) throw err
  console.log(langs) // a hash of the language count in that days activity
})
```

Or, alternatively from a file already downloaded.

```javascript
var archive = require('archive')
archive(path.join(__dirname, '2012-04-11-15.json.gz')).languages(function (err, langs) {
  if (err) throw err
  console.log(langs) // a hash of the language count in that days activity
})
```

###### More parsing.

I need more parsers! Pull requests welcome for anything even moderately useful, you can look at the code for the languages parser to see how simple it is, the JSON parsing is already taken care of.

###### In depth usage

All parsers are streams and expect to have a JSONStream piped to them. If you want to handle the acquisition yourself it would look like this.

```javascript
request(url).pipe(zlib.createGunzip()).pipe(jsonstream.parse()).pipe(githubarchive.languages(function (e, langs) {}))
```

Or, alternatively from a file.

```javascript
fs.createFileStream(path).pipe(zlib.createGunzip()).pipe(jsonstream.parse()).pipe(githubarchive.languages(function (e, langs) {}))
```
