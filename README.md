# FLAC Library Integrity Check

## Genesis

[FLAC](https://pages.github.com/) is the audio format of choice for preserving pristine audio quality. But even the most beautiful melody can be marred by a corrupted file. That's why FLAC format embeds a cryptographic hash of the audio data. This hash acts as a fingerprint for verifying the integrity of the data. A `test` option can recalculate this hash and compare it to the stored value, confirming unaltered audio data.

Unfortunately, the command-line tools in the FLAC reference implementation don't make it easy to check an entire library of files for integrity. As my FLAC collection grew to more than 1000 albums, I needed a more comprehensive tool. Here's what I was looking for:

* check the integrity of new files added to a directory and its subdirectories
* check the integrity of modified files in a directory and its subdirectories
* perform regular integrity checks, starting with the oldest checked file first

Finally, I wrote a script that fulfils these needs. 

Want to keep your FLAC library flawless too? Download the script and start using it!


## Usage

| Option                     | Description   |
| --------                   | -------- |
| `--help`                   | Shows usage help |
| `--flac <path>`       | Path to the `flac` executable (**mandatory**) |
| `--folder <path>`        | Root folder path to FLAC collection for recursive files search (**mandatory**) |
| `--report <path>`   | Path to the report file (**mandatory**) |
| `--age <number>`   | Age in minutes to identify files to check |
| `--min-percentage <number>`  | Minimum percentage of collection to check |
| `--max-percentage <number>`  | Maximum percentage of collection to check |

To **identify files to check**, a choice should be made among `--age`, `--min-percentage` and `--max-percentage` options.

`--age` option *can be used alone*. In that case, files not checked since a period of time will be checked. Periode of time must be expressed in minutes. To check files not checked since a week, use for example `--age=10080`. 

`--min-percentage` option *can be used alone*. To check 25% of your collection, use `--min-percentage=25`

`--max-percetage` option's purpose is to temper `--age` option only. `--max-percetage` option *can't be used alone*.

`--age` option could be used in combination with `--min-percentage` or `--max-percentage`. 
* When `--age` option is combined with `--min-percentage` option, **at least the minimum** specified percentage of collection will be checked or **maybe more** if number of files identified by ``--age`` is larger. 
* When `--age` option is combined with `--max-percentage` option, **at most the maximum** specified percentage of collection will be checked or **maybe less** if the number of files identified by `--age` is smaller.

For example, 

| Files identified by `--age`  | Files identified by `--min-percentage`  | Files to check |
| --------                     | --------                                | --------  |
| 357 files                    | **761 files**                           | **761 files** since 761 > 357 |
| **860 files**                | 252 files                               | **860 files** since 860 > 252 |


| Files identified by `--age`  | Files identified by `--max-percentage`  | Files to check |
| --------                     | --------                                | -------- |
| 593 files                    | **247 files**                           | **247 files** since 247 < 593 |
| **145 files**                | 465 files                               | **145 files** since 145 < 465 |


## License

This project is licensed under the terms of the **MIT license**. Check [LICENCE file](/LICENCE.md) included in this package for more information.
