# Uploafer [WARNING: This tool is deprecated and VERY out of date. Please do not use. Code is here for reference. #
## For use by WM2 users only ##
### Stole a bit of code from here: https://bitbucket.org/whatbetter/autotunes ###

Automate your music uploads the right way. (and don't make the same mistake everyone else has)

### How does uploafer work? (tldr: it doesn't) ###
### NOTE THAT THESE FEATURES DO NOT YET FUNCTION ###

* Scans through your music directory, checking existing data against PTH for duplicates
* When an existing upload is found, it will download the existing torrent and compare the data hash with your local torrent
* If an exact hash match is made, it will attempt to use your local data to reseed the existing upload
* When an existing upload is not found, it will check your hashes to confirm data integrity
* When a hash matches and data integrity is confirmed, it parses ReleaseInfo.txt for release data
* It then weeds out potential reported uploads through analyzing the audio data and comparing with the release info
* If all checks out, it will ask you to confirm the accuracy of the data
* Once approved, it will create a torrent and upload to PTH automatically.

### How do I get set up? ###

* You don't.
* Yet

### How do I beta test? ###

* You definitely don't do that

### Disclaimer ###

* Don't try this at home

### Roadmap ###

* Everything

#### How do I beta test really? ####

* Find me
