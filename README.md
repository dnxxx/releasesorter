## Release sorter
- Find all .mkv or .avi files in the root of sort dir
- Will only process TV episodes with a season and episode tag (S01E01, 1x01)
- Files modified in the last 20 min will not be processed
- If two or more episodes of the same series is found a series
dir and a season dir will be created if needed. Then all episodes
will be moved to the correct series and season dir
- If a series and season dir already exists the episode will be moved
to that location even if only one episode is found in sort dir
- In cleanup all dirs starting with _ (eg. _MOVIES/) will be ignored

## Example
This sort dir:

    Series.One.S01E01.720p.HDTV.x264.mkv
    Series.One.S01E02.720p.HDTV.x264.mkv
    Another.Series.S01E01.720p.HDTV.x264.mkv
    Another.Series.S01E02.720p.HDTV.x264.mkv
    Series.Three.S01E01.720p.HDTV.x264.mkv

Will be turned into:

    Series.One/Series.One.S01/Series.One.S01E01.720p.HDTV.x264.mkv
    Series.One/Series.One.S01/Series.One.S01E02.720p.HDTV.x264.mkv
    Another.Series/Another.Series.S01/Another.Series.S01E01.720p.HDTV.x264.mkv
    Another.Series/Another.Series.S01/Another.Series.S01E02.720p.HDTV.x264.mkv

Series.Three.S01E01.720p.HDTV.x264.mkv will be left in sort dir since it's a single episode.

## Usage
    releasesorter /path/to/dir

## Help
    usage: releasesorter [-h] [-d] [-s] [-l LOG] sort-dir

    Sort all unpacked TV release files (mkv, avi). If two or more episodes of the
    same series is found a series and a season directory will be created and the
    files are moved there. All empty directories in sort-dir will also be removed
    in cleanup.

    positional arguments:
      sort-dir

    optional arguments:
      -h, --help         show this help message and exit
      -d, --debug        Output debug info (default: False)
      -s, --silent       Disable console output (default: False)
      -l LOG, --log LOG  Log to file (default: None)

## Crontab example
    releasesorter --silent --log /path/to/log/dir/releasesorter.log /path/to/dir

## Install
Requires release module to run

    pip install git+https://github.com/dnxxx/pyrelease

then

    pip install git+https://github.com/dnxxx/releasesorter

## Warning
This hasn't been really battle tested yet, there will probably be bugs.

All empty directories in sort dir will be removed on run for cleanup purposes.
