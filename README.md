# Sublime Highlight

## Description:
Line-buffered commandline output colorization compatible with [Sublime Text](https://www.sublimetext.com/)'s
syntax-highlighting.

## Examples:

* `python3 hl.py -ls` (list all available syntax names)
* `python3 hl.py -lc` (list all available color schemes)
* `cat hl.py | python3 hl.py -s Python -c Mariana | less -r`
* `cat helloworld.c | python3 hl.py -s C -c Celeste | less -r`
* `tail -f log.txt | python3 hl.py -s CustomLog -c Monokai`
* `python3 hl.py data.yaml` (recognise syntax from extension)
* `python3 hl.py blob` (recognise syntax from first line, if possible)

## Installation:

* `pip install -r requirements.txt`
* (optional) `chmod +x /path/to/hl.py && ln -s /path/to/hl.py /usr/bin/hl`

## How to:
- Export a syntax form Sublime Text:
	- `Tools` > `Developer` > `View Package File...`
	- Type the name of the syntax you want to export
	- Create `syntax/Name.sublime-syntax` (extension is required)
	- Use with `-s Name`
- Export a color-scheme from Sublime Text:
	- `Tools` > `Developer` > `View Package File...`
	- Type the name of the color-scheme you want to export
	- Create `color-scheme/Name.sublime-color-scheme` (extension is required)
	- Use with `-c Name`
- Create a custom syntax:
	- Refer to https://www.sublimetext.com/docs/syntax.html
- Create a custom color-scheme:
	- Refer to https://www.sublimetext.com/docs/color_schemes.html
