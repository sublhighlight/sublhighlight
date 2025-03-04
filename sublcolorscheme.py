import os
import re
import yaml
import tinycss2
import tinycss2.color3
from colorsys import hls_to_rgb, rgb_to_hls
from scsast import parserulescope


file_ext = "sublime-color-scheme"
color_scheme_dir_path = os.path.join(
	os.path.dirname(__file__) or ".",
	"color-scheme"
)
all_color_schemes_basenames = list(
	filter(
		lambda x:x.endswith(file_ext),
		os.listdir(color_scheme_dir_path)
	)
)
all_color_schemes_names = list(
	map(
		lambda x: os.path.splitext(x)[0],
		all_color_schemes_basenames
	)
)
all_color_schemes_paths = list(
	map(
		lambda x: os.path.abspath(
			os.path.join(
				color_scheme_dir_path,
				x
			)
		),
		all_color_schemes_basenames
	)
)


# yaml load error workaround, see: https://github.com/yaml/pyyaml/issues/89
def construct_value(load, node):
    if not isinstance(node, yaml.ScalarNode):
        raise yaml.constructor.ConstructorError(
            "while constructing a value",
            node.start_mark,
            "expected a scalar, but found %s" % node.id, node.start_mark
        )
    yield str(node.value)

yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:value', construct_value)
# end yaml load error workaround


def loadcolorscheme(path):
	with open(path, "rb") as f:
		content = f.read()
	# yes, json can be parsed as yaml with support for trailing commas!
	# unfortunately yaml will not take // as a line comment...
	try:
		return yaml.load(content, Loader=yaml.SafeLoader)
	except yaml.parser.ParserError:
		re_dbl_qt_str = re.compile(br"\"[^\"]*\"")
		cont_strmap = {b"${%d}" % i:v for i,v in enumerate(list(set(re_dbl_qt_str.findall(content))))}
		for k, v in cont_strmap.items():
			content = content.replace(v, k)
		content = content.replace(b"//", b"#")
		for k, v in cont_strmap.items():
			content = content.replace(k, v)
		return yaml.load(content, Loader=yaml.SafeLoader)


def parsecolorscheme(scheme):
	glob = scheme["globals"]
	_var = scheme["variables"]
	rules = scheme["rules"]
	try:
		for name in _var:
			_var[name] = evalexpr(_var, _var[name])
		for key in glob:
			glob[key] = evalexpr(_var, glob[key])
		for rule in rules:
			rule["scope"] = parserulescope(rule["scope"])
			if "foreground" in rule:
				rule["foreground"] = evalexpr(_var, rule["foreground"])
			if "background" in rule:
				rule["background"] = evalexpr(_var, rule["background"])
	except:
		print(f"parsecolorscheme: {scheme['name']}")
		raise
	return scheme


def evalexpr(_var, expr):
	def evalfunc(_var, compo):
		args = list(filter(lambda x:x.type != "whitespace", compo.arguments))
		if not args:
			raise ValueError(f"expecting args in function: {compo.name}")
		if compo.name == "var":
			return _var[args[0].value]
		elif compo.name == "color":
			if args[0].type == "function":
				color = evalfunc(_var, args[0])
			else:
				color = tinycss2.color3.parse_color(args[0].value)
			if color is None:
				raise ValueError(f"invalid color spec in function: {compo.name}")
			for i in range(1, len(args)):
				subcompo = args[i]
				if subcompo.type == "function":
					subargs = list(filter(lambda x:x.type != "whitespace", subcompo.arguments))
					if not subargs:
						raise ValueError(f"expecting args in function: {subcompo.name}")
					if subcompo.name in ("alpha", "a"):
						color = tinycss2.color3.RGBA(
							color.red,
							color.green,
							color.blue,
							float(subargs[0].value)
						)
					elif subcompo.name in ("saturation", "s"):
						_hls = rgb_to_hls(color.red, color.green, color.blue)
						_rgb = hls_to_rgb(_hls[0], _hls[1], float(subargs[0].value))
						color = tinycss2.color3.RGBA(*_rgb, color.alpha)
					elif subcompo.name in ("lightness", "l"):
						_hls = rgb_to_hls(color.red, color.green, color.blue)
						_rgb = hls_to_rgb(_hls[0], float(subargs[0].value), _hls[2])
						color = tinycss2.color3.RGBA(*_rgb, color.alpha)
					elif subcompo.name == "blend":
						blendcolor = tinycss2.color3.parse_color(subargs[0].value)
						if blendcolor is None:
							raise ValueError(f"invalid color spec in function: {subcompo.name}")
						t = subargs[1].value/100.0
						invt = 1.0 - t
						color = tinycss2.color3.RGBA(
							color.red * invt + blendcolor.red * t,
							color.green * invt + blendcolor.green * t,
							color.blue * invt + blendcolor.blue * t,
							color.alpha
						)
					elif subcompo.name == "blenda":
						blendcolor = tinycss2.color3.parse_color(subargs[0].value)
						if blendcolor is None:
							raise ValueError(f"invalid color spec in function: {subcompo.name}")
						t = subargs[1].value/100.0
						invt = 1.0 - t
						color = tinycss2.color3.RGBA(
							color.red * invt + blendcolor.red * t,
							color.green * invt + blendcolor.green * t,
							color.blue * invt + blendcolor.blue * t,
							color.alpha * invt + blendcolor.alpha * t
						)
					elif subcompo.name == "min-contrast":
						# ignored for now, sorry...
						pass
					else:
						raise ValueError(f"unknown function: {subcompo.name}")
			return color
		else:
			raise ValueError(f"unknown function: {compo.name}")
	def _doeval(expr):
		try:
			color = tinycss2.color3.parse_color(expr)
			if color is not None:
				return color
			components = tinycss2.parse_component_value_list(expr)
			for compo in components:
				if compo.type == "function":
					return evalfunc(_var, compo)
			return expr
		except:
			print(f"in expr: {expr}")
			raise
	if isinstance(expr, list):
		return list(map(_doeval, expr))
	return _doeval(expr)

