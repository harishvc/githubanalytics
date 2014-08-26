var archive = require('../index')
  , path = require('path')
  , assert = require('assert')
  ;

// languages test
  
var valid =
{ PHP: 387,
  'C#': 82,
  R: 22,
  undefined: 819,
  JavaScript: 935,
  Java: 647,
  Python: 516,
  Shell: 132,
  Ruby: 660,
  'C++': 296,
  Assembly: 10,
  C: 288,
  Go: 7,
  Scala: 44,
  'DCPU-16 ASM': 2,
  'Visual Basic': 1,
  VimL: 54,
  'Objective-C': 93,
  Lua: 20,
  Groovy: 13,
  Perl: 44,
  CoffeeScript: 61,
  Clojure: 17,
  'Emacs Lisp': 34,
  'Common Lisp': 9,
  Racket: 1,
  Haskell: 25,
  Erlang: 14,
  AutoHotkey: 1,
  Rust: 8,
  Puppet: 13,
  ActionScript: 4,
  Matlab: 15,
  ColdFusion: 4,
  VHDL: 2,
  Scheme: 6,
  Delphi: 4,
  HaXe: 3,
  Elixir: 1,
  'F#': 1,
  OCaml: 2,
  D: 4,
  Kotlin: 2,
  'Pure Data': 1,
  Arduino: 1,
  Verilog: 1,
  Ada: 1,
  Prolog: 1,
  Apex: 1,
  'Standard ML': 1 
}

var test = archive(path.join(__dirname, '2012-04-11-15.json.gz'))
test.languages(function (err, languages) {
  assert.deepEqual(valid, languages)
})
