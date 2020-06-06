import os
from collections import namedtuple
from subprocess import call

APP_ARMOR_PROFILE_STENCIL = """
#include <tunables/global>

{executable_path} {
    #include <abstractions/base>
    #include <abstractions/python>

    # FILE_SYSTEM_RESTRICTION_BLOCK
    {fs_restrictions}
}
"""

FileSystemRestriction = namedtuple('FsRestriction', ['path', 'permissions', 'should_restrict_sub_files'])


class AppArmorSecProfile:
    PROFILES_DIR = "/etc/apparmor.d/"

    def __init__(self, executable_path: str):
        self._executable_path = executable_path
        self._profile_path = self.get_app_armor_profile_path(executable_path)
        self._file_system_restrictions = []

    @staticmethod
    def get_app_armor_profile_path(executable_path: str):
        app_armor_config_name = executable_path.replace(os.path.sep, ".").lstrip(".")
        return os.path.join(AppArmorSecProfile.PROFILES_DIR, app_armor_config_name)

    def add_fs_restriction(self, restriction: FileSystemRestriction):
        self._file_system_restrictions.append(restriction)

    def _dump_fs_restrictions(self):
        dumped_restrictions = []
        for r in self._file_system_restrictions:
            path = r.path
            path += os.path.sep if not r.path.endswith(os.path.sep) else ""
            path += "**" if r.should_restrict_sub_files else ""
            dumped_restrictions.append(f"{path} {r.permissions},")

        return os.linesep.join(dumped_restrictions)

    def _write_profile(self):
        with open(self._profile_path, 'wt', encoding='utf-8') as profile_file:
            profile_file.write(APP_ARMOR_PROFILE_STENCIL.format(executable_path=self._executable_path,
                                                                fs_restrictions=self._dump_fs_restrictions()))

    def _call_apparmor_parser(self):
        call(["apparmor_parser", self._profile_path])

    def write_profile_and_update_app_armor(self):
        self._write_profile()
        self._call_apparmor_parser()