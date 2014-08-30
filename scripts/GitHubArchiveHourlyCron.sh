#!/bin/sh
cd;cd ./github/githubanalytics
node ./scripts/FetchParseGitHubArchive.js  >> ./output/FetchParseGitHubArchive.log
