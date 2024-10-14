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


def parsesyntax(syntax:dict, syntaxes_by_fname:dict):
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
	parents = syntax.get("extends", None)
	if parents:
		if isinstance(parents, str):
			parents = [parents]
		parents = list(
			map(
				lambda x:os.path.splitext(os.path.basename(x))[0],
				parents
			)
		)
		not_found = list(filter(lambda x:x not in syntaxes_by_fname, parents))
		if not_found:
			raise KeyError(f"parsesyntax: {syntax['name']}, cannot find parent syntaxes: {not_found}")
		parents = list(
			map(
				lambda x:syntaxes_by_fname[x],
				parents
			)
		)
		syntax["variables"] = _syntax_merge_vars(*parents, syntax)
		syntax["contexts"] = _syntax_merge_contexts(*parents, syntax)
	return syntax

	