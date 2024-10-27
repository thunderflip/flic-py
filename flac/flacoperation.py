import logging
import re
import subprocess

# https://xiph.org/flac/documentation_tools_metaflac.html
# https://xiph.org/flac/documentation_tools_flac.html
# https://github.com/xiph/flac/blob/9b3826006a3fc27b34d9297a9a8194accacc2c44/src/flac/main.c

class FlacOperation:

    def __init__(self, flac_path : str, metaflac_path : str, file : str):
        self.log = logging.getLogger('FlacOperation')

        self.flac_path = flac_path
        self.metaflac_path = metaflac_path
        self.file = file

    def add_tag(self, tag : str, value : str):
        result = False

        name_value = tag + "=" + value
        cmd = [self.metaflac_path, '--set-tag=' + name_value, self.file]
        process = subprocess.run(cmd, capture_output=True, universal_newlines=True)

        self.log.debug("METAFLAC exited with code: %d", process.returncode)
        if process.returncode != 0:
            self.log.critical("METAFLAC exited with error code: %d", process.returncode)
        else:
            self.log.debug("METAFLAC added tag successfully")
            result = True

        return result

    def get_hash(self):
        hash = None
        cmd = [self.metaflac_path, '--show-md5sum', self.file]
        process = subprocess.run(cmd, capture_output=True, universal_newlines=True)

        self.log.debug("METAFLAC exited with code: %d", process.returncode)
        if process.returncode != 0:
            self.log.critical("METAFLAC exited with error code: %d", process.returncode)
        else:
            metaflac_output = process.stdout
            m = re.match(r'(^\S*)\S+.*', metaflac_output)
            if m is not None and len(m.groups()) == 1:
                hash = m.group(1)

        return hash

    def get_tag(self, tag : str):
        tag_value = None
        cmd = [self.metaflac_path, '--show-tag=' + tag, self.file]
        process = subprocess.run(cmd, capture_output=True, universal_newlines=True)

        self.log.debug("METAFLAC exited with code: %d", process.returncode)
        if process.returncode != 0:
            self.log.critical("METAFLAC exited with error code: %d", process.returncode)
        else:
            metaflac_output = process.stdout.strip()
            if metaflac_output.startswith(tag + '='):
                tag_value = metaflac_output[len(tag) + 1:]

        return tag_value

    def reencode(self):
        result = False

        cmd = [self.flac_path, '--force', '--no-error-on-compression-fail', '--no-preserve-modtime', '--verify', self.file]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        (cmd_out, cmd_err) = process.communicate()

        self.log.debug("FLAC exited with code: %d", process.returncode)
        if process.returncode != 0:
            cmd_err = cmd_err.strip()
            self.log.critical("FLAC exited with error code: %d", process.returncode)
            self.log.critical("STDOUT:\n%s\nSTDERR: %s", cmd_out, cmd_err)
        else:
            cmd_err = cmd_err.strip()
            r = cmd_err.split("\n")
            r = r[len(r) - 1]
            m = re.match(r'.*Verify OK, .*', r)
            if m is None:
                self.log.critical(r)
                self.log.critical("FLAC 'Verify OK' not found")
            else:
                self.log.debug("FLAC verification succeed")
                result = True

        return result

    def remove_tag(self, tag : str):
        result = False

        cmd = [self.metaflac_path, '--remove-tag=' + tag, self.file]
        process = subprocess.run(cmd, capture_output=True, universal_newlines=True)

        self.log.debug("METAFLAC exited with code: %d", process.returncode)
        if process.returncode != 0:
            self.log.critical("METAFLAC exited with error code: %d", process.returncode)
        else:
            self.log.debug("METAFLAC removed tag successfully")
            result = True

        return result

    def replace_tag(self, tag : str, new_tag : str):
        result = False
        value = self.get_tag(tag)
        if value is not None:
            result = True
            if self.remove_tag(tag):
                self.add_tag(new_tag, value)
        return result

    def test(self):
        result = False

        cmd = [self.flac_path, '--test', self.file]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        (cmd_out, cmd_err) = process.communicate()
        if process.returncode != 0:
            cmd_err = cmd_err.strip()
            self.log.critical("FLAC exited with error code: %d", process.returncode)
            self.log.critical("STDOUT:\n%s\nSTDERR: %s", cmd_out, cmd_err)
        else:
            cmd_err = cmd_err.strip()
            r = cmd_err.split("\n")
            r = r[len(r) - 1]
            m = re.match(r'.*ok', r)
            if m is None:
                self.log.critical(r)
                self.log.critical("FLAC '*ok' not found")
            else:
                self.log.debug("FLAC verification succeed")
                result = True

        return result
