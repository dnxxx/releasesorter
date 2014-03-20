import os
import logging
from datetime import datetime, timedelta

from unipath import Path, FILES, DIRS
from ago import human

from release import Release


log = logging.getLogger(__name__)


class ReleaseSorterError(Exception):
    pass


class ReleaseSorter(object):
    def __init__(self, sort_dir):
        self.sort_dir = Path(sort_dir)

        # Make sure the sort dir is a dir and cd into it
        if not self.sort_dir.isdir():
            raise ReleaseSorterError('Invalid sort-dir {}'.format(sort_dir))
        os.chdir(sort_dir)

        self.files_to_sort = {}

    def relative_path(self, path, root_path):
        relative_path = path.replace(root_path, '')
        if relative_path[0:1] == '/':
            return relative_path[1:]
        else:
            return relative_path

    def check_extension(self, extension):
        if extension in ('.mkv', '.avi'):
            return True
        else:
            return False

    def check_modified_time(self, time_since_modified):
        if time_since_modified < timedelta(minutes=20):
            return False
        else:
            return True

    def create_series_folders(self, sorter_file):
        if sorter_file.series_dir and not sorter_file.series_dir.exists():
            log.info('Creating series dir {}'.format(
                sorter_file.relative_path(sorter_file.series_dir)))
            sorter_file.series_dir.mkdir()

        if sorter_file.season_dir and not sorter_file.season_dir.exists():
            log.info('Creating season dir {}'.format(
                sorter_file.relative_path(sorter_file.season_dir)))
            sorter_file.season_dir.mkdir()

    def move_subtitle_files(self, sorter_file):
        """Check for existing subtitle files matching media file and move
        them to sort folder too.
        """

        for ext in ('.srt', '.sub', '.idx'):
            subtitle_path = Path(sorter_file.path.parent, '{}{}'.format(
                sorter_file.path.stem, ext))

            if subtitle_path.exists():
                log.info('Moving subtitle file {} to {}'.format(
                    self.relative_path(subtitle_path, self.sort_dir),
                    sorter_file.season_dir))
                subtitle_path.move(Path(self.sort_dir,
                                   sorter_file.season_dir))

    def move_sorter_file(self, sorter_file):
        log.info('Moving {} to {}'.format(sorter_file.relative_path(),
                                          sorter_file.season_dir))
        sorter_file.path.move(Path(self.sort_dir, sorter_file.season_dir))

    def get_sorter_files(self):
        """List sort dir and find all files to sort"""

        log.debug('Sorting dir {}'.format(self.sort_dir))

        file_list = self.sort_dir.listdir(filter=FILES)

        for file in file_list:
            sorter_file = SorterFile(file, self.sort_dir)

            # File extension
            if not self.check_extension(sorter_file.extension):
                log.debug('Skipping {}, wrong file extension'.format(
                    sorter_file.relative_path()))
                continue

            # Modifed time, only process files who hasen't been modified the
            # in the last 20 min
            time_since_modified = datetime.now() - sorter_file.mtime
            if not self.check_modified_time(time_since_modified):
                log.debug('Skipping {}, has been modified in the last 20 min '
                          '({})'.format(sorter_file.relative_path(),
                                        human(time_since_modified)))
                continue

            # Skip if file is not a TV release
            if not sorter_file.release.tv_release:
                log.debug('Skipping {}, not a TV release'.format(
                    sorter_file.relative_path()))
                continue

            # Add file to sorter list
            series_name = sorter_file.release.tv_series_data['series_name']
            series_episodes = self.files_to_sort.get(series_name)
            if not series_episodes:
                series_episodes = {}
            series_episodes[unicode(sorter_file)] = sorter_file
            self.files_to_sort[series_name] = series_episodes

    def sort_files(self):
        # If a season dir already exist use that when sorting. Else if there
        # is only one file found for the series skip processing and moving.
        for series in self.files_to_sort.keys():
            series_episodes = self.files_to_sort[series]

            for episode_file in series_episodes:
                sorter_file = series_episodes[episode_file]
                # Episode already has a season dir
                if sorter_file.season_dir.exists():
                    log.info('Season dir for {} already exists {}'.format(
                        episode_file, sorter_file.season_dir))
                # No season dir for episode. Skip if only one episode was found
                else:
                    # Skip if only one episode was found
                    if len(series_episodes) < 2:
                        log.debug('Skipping {}, only one episode found'.format(
                            series_episodes.iterkeys().next()))

                        del(self.files_to_sort[series])

        # Loop remaining files for folder creating and moving
        for series in self.files_to_sort:
            series_episodes = self.files_to_sort[series]

            for episode_file in series_episodes:
                sorter_file = series_episodes[episode_file]

                # Create series folder if needed
                self.create_series_folders(sorter_file)

                # Move the file
                self.move_sorter_file(sorter_file)

                # Move subtitle files
                self.move_subtitle_files(sorter_file)

    def sort(self):
        self.get_sorter_files()
        self.sort_files()

    def cleanup_empty_folders(self):
        log.debug('Cleanup empty folders in {}'.format(self.sort_dir))

        dirs_to_check_for_removal = []
        for dir in self.sort_dir.walk(filter=DIRS, top_down=False):
            # Skip all dirs in _ dir
            if '/_' in dir:
                log.debug('Skipping cleanup on {}, _ dir'.format(dir))
                continue

            dirs_to_check_for_removal.append(dir)

        for dir in dirs_to_check_for_removal:
            # If dir is empty, remove it
            if dir.isdir() and len(dir.listdir()) == 0:
                log.info('Removing empty dir {}'.format(self.relative_path(
                    dir, self.sort_dir)))
                dir.rmtree()


class SorterFile(object):
    def __init__(self, path, sort_dir):
        self.path = path
        self.sort_dir = sort_dir
        self.release = Release(path.stem)

    def __unicode__(self):
        return self.relative_path()

    def __repr__(self):
        return '<SorterFile: {} ({})>'.format(self.relative_path(),
                                              self.sort_dir)

    def relative_path(self, path=None):
        if not path:
            path = self.path

        relative_path = path.replace(self.sort_dir, '')
        if relative_path[0:1] == '/':
            return relative_path[1:]
        else:
            return relative_path

    @property
    def extension(self):
        return self.path.ext

    @property
    def mtime(self):
        return datetime.fromtimestamp(self.path.mtime())

    @property
    def series_dir(self):
        """If release is a TV release return the relative path to series dir"""

        if not self.release.tv_release:
            return False

        return Path(
            self.release.tv_series_data['series_name'].replace(' ', '.'))

    @property
    def season_dir(self):
        """If release is a TV release return the relative path to season dir"""

        if not self.release.tv_release:
            return False

        return Path(self.series_dir, '{}.S{}'.format(
            self.series_dir, self.release.tv_series_data['season']))
