# FLAC Collection Integrity Checker

## Genesis

What is FLAC ? The [official FLAC site](https://pages.github.com/) says :

> FLAC stands for Free Lossless Audio Codec, an audio format similar to MP3, but lossless, meaning that audio is compressed in FLAC without any loss in quality.

If you consider FLAC, you should be concerned by music quality. To preserve music quality or even just to preserve files, you should also be concerned by file integrity. Aren't you ?

There is a bunch of handy tools to manipulate FLAC files. I've been using [Trader's Little Helper](http://tlh.easytree.org/) since a long time. Trader's Little Helper could notably check FLAC integrity of files in a directory (but not in subdirectories). 

As my FLAC collection growned up, I needed a global tool to check my files. I wanted :

* to check integrity of new files added in a directory and his subdirectories ;
* to check integrity of files modified in a directory and his subdirectories ;
* to check integrity of files regularly, beginning with the oldest checked file first.

Finally, I wrote a script that fulfils these needs.

## Usage

| Option                     | Description   |
| --------                   | -------- |
| `--help`                   | Shows usage help |
| `--flac <flac-path>`       | Path to the `flac` executable (**mandatory**) |
| `--folder <folder>`        | Root folder path to FLAC collection for recursive files search (**mandatory**) |
| `--report <report-path>`   | Path to the report file (**mandatory**) |
| `--age <number-minutes>`   | Age in minutes to identify files to check |
| `--min-percentage <number-percentage>`  | Minimum percentage of collection to check |
| `--max-percentage <number-percentage>`  | Maximum percentage of collection to check |

To identify files to check, a choice should be made among `--age`, `--min-percentage` and `--max-percentage` options.

`--age` option *can be used alone*. In that case, files not checked since a period of time will be checked. Periode of time must be expressed in minutes. To check files not checked since a week, use for example `--age=10080`. 

`--min-percentage` option *can be used alone*. To check 25% of your collection, use `--min-percentage=25`

`--max-percetage` option's purpose is to temper `--age` option only. `--max-percetage` option *can't be used alone* and must always be used with `--age` option.

`--age` option could be used in combination with `--min-percentage` or `--max-percentage`. 
* When `--age` option is combined with `--min-percentage` option, **at least the minimum** specified percentage of collection will be checked or **maybe more** if number of files identified by ``--age`` is larger. 
* When `--age` option is combined with `--max-percentage` option, **at most the maximum** specified percentage of collection will be checked or **maybe less** if the number of files identified by `--age` is smaller.

For example, 

| Files identified by `--age`  | Files identified by `--min-percentage`  | Files to check |
| --------                     | --------                                | --------  |
| 357 files                    | **761 files**                           | 761 files |
| **860 files**                | 252 files                               | 860 files |


| Files identified by `--age`  | Files identified by `--max-percentage`  | Files to check |
| --------                     | --------                                | -------- |
| 593 files                    | **247 files**                           | 247 files |
| **145 files**                | 465 files                               | 145 files |


## License

This project is licensed under the terms of the **MIT license**. Check [LICENCE file](/LICENCE.md) included in this package for more information.
