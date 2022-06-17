import logging
import re
import subprocess

# https://xiph.org/flac/documentation_tools_metaflac.html
# https://xiph.org/flac/documentation_tools_flac.html
# https://github.com/xiph/flac/blob/9b3826006a3fc27b34d9297a9a8194accacc2c44/src/flac/main.c

class FlacOperation:

    def __init__(self, flac_path, metadata_path, file):
        self.log = logging.getLogger('FlacOperation')

        self.flac_path = flac_path
        self.metaflac_path = metadata_path
        self.file = file

    def get_hash(self):

        hash = None
        cmd = [self.metaflac_path, '--show-md5sum', self.file]
        process = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)

        self.log.debug("METAFLAC exited with code: %d", process.returncode)
        if process.returncode != 0:
            self.log.critical("METAFLAC exited with error code: %d", process.returncode)
        else:
            m = re.match(r'(^\S*)\S+.*', process.stdout)
            if m is not None and len(m.groups()) == 1:
                hash = m.group(1)

        return hash

    def reencode(self):
        result = False

        cmd = [self.flac_path, '--force', '--no-error-on-compression-fail', '--verify', self.file]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        (cmd_out, cmd_err) = process.communicate()

        self.log.debug("FLAC exited with code: %d", process.returncode)
        if process.returncode != 0:
            cmd_err = cmd_err.strip()
            self.log.critical("FLAC exited with error code: %d", process.returncode)
            self.log.critical("STDOUT:\n%s\nSTDERR: %s", cmd_out, cmd_err)
        else:
            cmd_err = cmd_err.strip()
            if cmd_err is not None:
                r = cmd_err.split("\n")
                if r is None:
                    self.log.critical(r)
                    self.log.critical("FLAC output not found")
                else:
                    r = r[len(r) - 1]
                    m = re.match(r'.*Verify OK, .*', r)
                    if m is None:
                        self.log.critical(r)
                        self.log.critical("FLAC 'Verify OK' not found")
                    else:
                        self.log.debug("FLAC verification succeed")
                        result = True
            else:
                self.log.critical("FLAC output expected")

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
            if cmd_err is not None:
                r = cmd_err.split("\n")
                if r is None:
                    self.log.critical(r)
                    self.log.critical("FLAC output not found")
                else:
                    r = r[len(r) - 1]
                    m = re.match(r'.*ok', r)
                    if m is None:
                        self.log.critical(r)
                        self.log.critical("FLAC '*ok' not found")
                    else:
                        self.log.debug("FLAC verification succeed")
                        result = True                          

            else:
                self.log.critical("FLAC output expected")

        return result
