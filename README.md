### ***Note: Not yet published!***

# elm-format plugin for Sublime Text

Run `elm-format` whenever you save an Elm file.

And add the keyboard shortcut `Ctrl+K` `Ctrl+F` (or `Cmd+K` `Cmd+F` on Mac) to run `elm-format` any time you want. No need to save.


***This is a fork of [evancz/elm-format-on-save](https://github.com/evancz/elm-format-on-save) to address issues [#3](https://github.com/evancz/elm-format-on-save/issues/4) and [#4](https://github.com/evancz/elm-format-on-save/issues/4).
If these are fixed upstream this plugin (ringvold/sublime-elm-format) will to be deprecated in favor of [evancz/elm-format-on-save](https://github.com/evancz/elm-format-on-save)***

## Install

0. Install [`elm-format`](https://github.com/avh4/elm-format) (can be installed to local project with NPM)
1. Install [Elm Syntax Highlighting](https://github.com/evancz/elm-syntax-highlighting) for Sublime Text
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) to open the Command Palette
3. Select **Package Control: Install Package**
4. Select **elm-format**

Try saving an Elm file to see if it works. You may see a panel open with troubleshooting advice if something has gone wrong!


## Including/Excluding Files

Do you only want `elm-format` to run on certain files? (e.g. only work code)

Go to **Sublime Text -> Preferences -> Package Settings -> elm-format -> Settings**

You will see two panels. The left is all the defaults and the right is your custom overrides. So in the right panel, you can override the default settings with something like:

```json
{
    "on_save": {
        "including": ["my/company/"],
        "excluding": ["src/generated/"]
    }
}
```

This would mean that you only run `elm-format` on code that is in the `my/company/` directory, but you skip any files in the `src/generated` directory.

See the left settings panel for more information about how to include and exclude files!


## Technical Details

This plugin works by modifying the code in the editor itself.

So when it runs "on save" it is specifically running _before_ the file is saved to disk.

This is really important if you have some elaborate file watching system set up! Other plugins may format _after_ the file is saved to disk, triggering a second save, and thereby degrading the performance of your file watching system.

# Alternatives

**[Elm Format On Save](https://github.com/evancz/elm-format-on-save):** The original elm-format plugin for Sublime Text. If you do not need issues [#3](https://github.com/evancz/elm-format-on-save/issues/4) and [#4](https://github.com/evancz/elm-format-on-save/issues/4) fix you should just use Elm Format On Save.
**[LSP-elm](https://github.com/sublimelsp/LSP-elm)**: A much more heavy weight plugin but can give more IDE like features through the Language Server Protol. Has support for elm-format so if you are using that plugin this one is not necessary.
