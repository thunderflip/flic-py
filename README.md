# FLAC Collection Integrity Checker

## Genesis

What is FLAC ? Here is the description from the [official FLAC site](https://pages.github.com/) :

> FLAC stands for Free Lossless Audio Codec, an audio format similar to MP3, but lossless, meaning that audio is compressed in FLAC without any loss in quality.

If you consider FLAC, you should be concerned by music quality. To preserve music quality or even just to preserve files, you should be concerned by file integrity also. Aren't you ?

There is a bunch of handy tools to manipulate FLAC files. I've been using [Trader's Little Helper](http://tlh.easytree.org/) since a long time. Trader's Little Helper could notably check FLAC integrity of files in a directory (but not in subdirectories). 

As my FLAC collection growned up, I needed a more global tool to check my files. I wanted :

* to check integrity of new files added in a directory and his subdirectories ;
* to check integrity of files modified in a directory and his subdirectories ;
* to check integrity of files regularly, beginning with the oldest checked file ;

Finally, I wrote a script that fulfils these needs.
