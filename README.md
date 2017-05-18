the PICOtron
============

To update to latest version
---------------------------

Run `git pull` from the command line


Clinical answers from systematic reviews
----------------------------------------

As described in [this presentation](http://www.slideshare.net/mavergames/sustainability-and-cochrane-reviews-how-technology-can-help-12207716)

The *PICOtron* produces summaries of systematic reviews.
Specifically, files from [RevMan 5](http://tech.cochrane.org/revman) are batch processed to HTML files.

To produce summaries, the *PICOtron* does the following:
  - retrieves intervention names from free text in Cochrane Reviews
  - calculates estimates of the absolute effects of interventions (using individual trial data in the review)
  - produces standardised, plain language, summaries of the effects of each intervention on key outcomes

This software is used by the Cochrane Collaboration, and forms the basis of [Cochrane Clinical Answers](http://cochraneclinicalanswers.com), 

contact: mail@ijmarshall.com

Instructions
------------

1. Save the Revman input to the `input/` folder
2. Export the topic map excel file to CSV format, also in the `input/` folder, saving under the name `topics.csv`
3. From the command line, run `python cca.py`
4. Wait for the timer to finish, then the output files will be in the `output/` directory
5. If any files are not possible to process, an error will be displayed, and a log text file saved in the `output/` directory


To 'commit' changes
-------------------
1. Type `git add ` followed by the file you have edited
2. Type `git commit -m 'some description of change'`
3. Type `git push`





