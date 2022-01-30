# Photometry
An easy-to-use photometry analysis program

## *Background*

Fiber photometry is an awesome new technique that is exploding in popularity among neuroscientists. The reason is simple - it allows us to measure multiple kinds of brain activity with high temporal resolution and terrific signal-to-noise ratio. Best of all - it's not that hard to do! The details of exactly how it works are [fascinating](https://web.archive.org/web/20190227164817id_/http://pdfs.semanticscholar.org/83b9/03db79f547c6c967fda02c1936ed7f6c979c.pdf), but beyond the scope of this document.

I recently set this technique up in my lab with the goal of using it to measure dopamine transmission in awake, behaving animals. Although running photometry experiments isn't particularly difficult, one area that consistently causes problems for almost every lab is analyzing the data. While there are plenty of examples of working code on github, these are not very accessible to researchers without *some* background in computer programming (which in my experience is most people!). Therefore, I decided to create an easy-to-use analysis program that is accessible to everyone regardless of coding background.

The application I created is a GUI written in python with pyqt and pandas. It takes several .csv files as input, performs the analysis to compute the final signal (called zdff), and outputs a .csv with the zdff signal to a directory of the users choice. This format allows people to use whatever other analysis tools they like to play with and visualize the data. My program also plots the final signal in a window so the user can quickly see "hey, does this look right?". 

Future additions will include a "frozen" version of the app that can be downloaded and used off-the-shelf. Also, we will include the ability to align the zdff signal to digital input and output (DIO) events so that we can see how brain activity correlates to environmental and behavioral events, a fundamental question in neuroscience!

## *In this repo...*
* **zdFF.py** A file containing all of the functions required to compute zdff from raw photometry data. Most of this code is forked from [this repo](https://github.com/PhilClarkPhD/Photometry_data_processing)
* **FP_GUI.py:** This file contains the code for running the application and was made by myself with help from Anthony Moreno-Sanchez. 

Please reach out with questions / comments!
