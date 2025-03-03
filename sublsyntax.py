import os
import yaml
from itertools import chain


file_ext = "sublime-syntax"


def ctx_findprop(ctx, key, default):
	return (list(filter(lambda x:key in x, ctx)) or [{key:default}])[0].get(key, default)


def loadsyntax(path):
	with open(path, "rb") as f:
		content = f.read()
	return yaml.load(content, Loader=yaml.SafeLoader)


def loadsyntaxesmp(paths):
	from multiprocessing.pool import ThreadPool as MPPool
	def threadloadsyntax(path):
		return os.path.splitext(os.path.basename(path))[0], loadsyntax(path)
	with MPPool() as p:
		return {k: v for k, v in p.map(threadloadsyntax, paths)}


def parsesyntax(syntax:dict, syntaxes_by_fname:dict, syntax_dir_path:str, postlazyloadsyntax = lambda x:x):
	def _syntax_merge_vars(*s):
		return {k: v for k, v in chain(*map(dict.items, map(lambda x:x.get("variables", None) or {}, s)))}
	def _syntax_merge_contexts(*s):
		result = {}
		for synt in s:
			ctx = synt["contexts"]
			for ctxname in ctx:
				if ctxname not in result:
					result[ctxname] = ctx[ctxname]
				elif ctx_findprop(ctx[ctxname], "meta_prepend", False):
					result[ctxname] = ctx[ctxname] + result[ctxname]
				elif ctx_findprop(ctx[ctxname], "meta_append", False):
					result[ctxname] = result[ctxname] + ctx[ctxname]
				else:
					result[ctxname] = ctx[ctxname] + result[ctxname]
		return result
	parent_syntaxes_paths = syntax.get("extends", None)
	if parent_syntaxes_paths:
		if isinstance(parent_syntaxes_paths, str):
			parent_syntaxes_paths = [parent_syntaxes_paths]
		parent_syntaxes_paths = list(
			map(
				lambda x:(x, os.path.abspath(os.path.join(syntax_dir_path, f"{x}.{file_ext}"))),
				map(
					lambda x:os.path.splitext(os.path.basename(x))[0],
					parent_syntaxes_paths
				)
			)
		)
		parent_syntaxes = []
		for name, path in parent_syntaxes_paths:
			if name not in syntaxes_by_fname:
				syntaxes_by_fname[name] = parsesyntax(
					loadsyntax(path),
					syntaxes_by_fname,
					syntax_dir_path,
					postlazyloadsyntax=postlazyloadsyntax
				)
				postlazyloadsyntax(syntaxes_by_fname[name])
			parent_syntaxes.append(syntaxes_by_fname[name])
		syntax["variables"] = _syntax_merge_vars(*parent_syntaxes, syntax)
		syntax["contexts"] = _syntax_merge_contexts(*parent_syntaxes, syntax)
	return syntax

	