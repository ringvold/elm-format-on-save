import os
import os.path
import re
import sublime
import sublime_plugin
import subprocess



#### COMMAND ####


class ElmFormatCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        elm_format = find_elm_format(self.view)

        if elm_format == None:
            return

        region = sublime.Region(0, self.view.size())
        content = self.view.substr(region)
        previous_position = self.view.viewport_position()

        stdout, stderr = subprocess.Popen(
            [elm_format, '--stdin', '--yes', '--elm-version=0.19'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=os.name=="nt").communicate(input=bytes(content, 'UTF-8'))

        if stderr.strip():
            open_panel(self.view, re.sub('\x1b\[\d{1,2}m', '', stderr.strip().decode()))
        else:
            self.view.replace(edit, region, stdout.decode('UTF-8'))
            self.view.set_viewport_position((0, 0), False)
            self.view.set_viewport_position(previous_position, False)
            self.view.window().run_command("hide_panel", {"panel": "output.elm_format"})

    def is_visible(self):
        return self.should_show_plugin()

    def is_enabled(self):
        return self.should_show_plugin()

    def should_show_plugin(self):
        scope = self.view.scope_name(0)
        return scope.find('source.elm') != -1

#### ON SAVE ####


class ElmFormatOnSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        scope = view.scope_name(0)
        if scope.find('source.elm') != -1 and needs_format(view):
            view.run_command('elm_format')


def needs_format(view):
    settings = sublime.load_settings('elm-format-on-save.sublime-settings')
    on_save = settings.get('on_save', True)

    if isinstance(on_save, bool):
        return on_save

    if isinstance(on_save, dict):
        path = view.file_name()
        included = is_included(on_save, path)
        excluded = is_excluded(on_save, path)
        if isinstance(included, bool) and isinstance(excluded, bool):
            return included and not excluded

    open_panel(view, invalid_settings)
    return False


def is_included(on_save, path):
    if "including" in on_save:
        if not isinstance(on_save.get("including"), list):
            return None

        for string in on_save.get("including"):
            if string in path:
                return True

        return False

    return True


def is_excluded(on_save, path):
    if "excluding" in on_save:
        if not isinstance(on_save.get("excluding"), list):
            return None

        for string in on_save.get("excluding"):
            if string in path:
                return True

        return False

    return False



#### EXPLORE PATH ####


def find_elm_format(view):

    #
    # 1. use absolute_path if defined in plugin settings
    settings = sublime.load_settings('elm-format-on-save.sublime-settings')
    given_path = settings.get('absolute_path')
    if given_path != None and given_path != '':
        if isinstance(given_path, str) and os.path.isabs(given_path) and os.access(given_path, os.X_OK):
            return given_path

        open_panel(view, bad_absolute_path)
        return None

    #
    # 2. check for elm-format in node_modules relative to active view
    active_view_parents = generate_dirs(os.path.dirname(view.file_name()), limit=500)
    for parent in active_view_parents:
        closest_to_view_elm_format = os.path.join(parent, 'node_modules', '.bin', 'elm-format')
        if os.path.exists(closest_to_view_elm_format):
            return closest_to_view_elm_format

    #
    # 3. check locally installed '--no-bin-links'
    st_project_path = str(get_st_project_path())
    project_elm_format_path_nbl = os.path.join(st_project_path, 'node_modules', 'elm-format', 'bin', 'elm-format')
    if os.path.exists(project_elm_format_path_nbl):
        return project_elm_format_path_nbl

    #
    # 4. look for elm-format on PATH
    exts = os.environ['PATHEXT'].lower().split(os.pathsep) if os.name == 'nt' else ['']
    for directory in os.environ['PATH'].split(os.pathsep):
        for ext in exts:
            path = os.path.join(directory, 'elm-format' + ext)
            if os.access(path, os.X_OK):
                return path

    open_panel(view, cannot_find_elm_format())
    return None



#### ERROR MESSAGES ####


def open_panel(view, content):
    window = view.window()
    panel = window.create_output_panel("elm_format")
    panel.set_read_only(False)
    panel.run_command('erase_view')
    panel.run_command('append', {'characters': content})
    panel.set_read_only(True)
    window.run_command("show_panel", {"panel": "output.elm_format"})



#### ERROR MESSAGES ####


def cannot_find_elm_format():
    return """-- ELM-FORMAT NOT FOUND -----------------------------------------------

I tried run elm-format, but I could not find it on your computer.

Try the recommendations from:

  https://github.com/evancz/elm-format-on-save/blob/master/troubleshooting.md

If everything fails, just remove the "elm-format-on-save" plugin from
your editor via Package Control. Sometimes it is not worth the trouble.

-----------------------------------------------------------------------

NOTE: Your PATH variable led me to check in the following directories:

    """ + '\n    '.join(os.environ['PATH'].split(os.pathsep)) + """

But I could not find `elm-format` in any of them. Please let me know
at https://github.com/evancz/elm-format-on-save/issues if this does
not seem correct!
"""


invalid_settings = """-- INVALID SETTINGS ---------------------------------------------------

The "on_save" field in your settings is invalid.

For help, check out the section on including/excluding files within:

  https://github.com/evancz/elm-format-on-save/blob/master/README.md

-----------------------------------------------------------------------
"""


bad_absolute_path = """-- INVALID SETTINGS ---------------------------------------------------

The "absolute_path" field in your settings is invalid.

I need the following Python expressions to be True with the given path:

    os.path.isabs(absolute_path)
    os.access(absolute_path, os.X_OK)

Is the path correct? Do you need to run "chmod +x" on the file?

-----------------------------------------------------------------------
"""



#### HELPERS ####


def generate_dirs(start_dir, limit=None):
    """
    Generate directories, starting from start_dir.

    Hat tip goes to SublimeLinter 3 and JsPrettier.

    :param start_dir: The search start path.
    :param limit: If limit is None, the search will continue up to the root directory.
        Otherwise a maximum of limit directories will be checked.
    """
    right = True

    while right and (limit is None or limit > 0):
        yield start_dir
        start_dir, right = os.path.split(start_dir)

        if limit is not None:
            limit -= 1

def get_st_project_path():
    """Get the active Sublime Text project path.

    Original: https://gist.github.com/astronaughts/9678368

    :rtype: object
    :return: The active Sublime Text project path.
    """
    window = sublime.active_window()
    folders = window.folders()
    if len(folders) == 1:
        return folders[0]
    else:
        active_view = window.active_view()
        if active_view:
            active_file_name = active_view.file_name()
        else:
            active_file_name = None
        if not active_file_name:
            return folders[0] if len(folders) else os.path.expanduser('~')
        for folder in folders:
            if active_file_name.startswith(folder):
                return folder
        return os.path.dirname(active_file_name)
