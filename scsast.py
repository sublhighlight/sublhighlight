import regex as re


re_token_patt = re.compile(r"([a-zA-Z0-9_\-.]+|\,|\|| - |\(|\))")
OP_OR = "|"
OP_XCL = " - "
OP_INCL = ","
OPERATORS = (OP_OR, OP_XCL, OP_INCL)


def __opgroup(expr, op):
	r = None
	buf = []
	for item in expr:
		if item == op:
			if len(buf) == 1 and isinstance(buf[0], tuple):
				buf = buf[0]
			if not r:
				r = (op, [buf])
			else:
				r[1].append(buf)
			buf = []
		elif isinstance(item, list):
			buf.append(__opgroup(item, op))
		elif isinstance(item, tuple):
			buf.append((item[0], __opgroup(item[1], op)))
		else:
			buf.append(item)
	if buf:
		if not r:
			return buf
		if len(buf) == 1 and isinstance(buf[0], tuple):
			buf = buf[0]
		r[1].append(buf)
	return r


def __splittags(expr):
	if isinstance(expr, tuple):
		op, subxp = expr
		for i in range(len(subxp)):
			if isinstance(subxp[i], tuple):
				__splittags(subxp[i])
			else:
				for j in range(len(subxp[i])):
					subxp[i][j] = subxp[i][j].split(".")
	else:
		for i in range(len(expr)):
			if isinstance(expr[i], tuple):
				__splittags(expr[i])
			else:
				expr[i] = expr[i].split(".")


def parserulescope(string_expression):
	toks = re_token_patt.findall(string_expression)
	stck = [[]]
	tid = 0
	for t in toks:
		if t == "(":
			newxp = []
			stck[-1].append(newxp)
			stck.append(newxp)
		elif t == ")":
			if len(stck) <= 1:
				raise Exception(f"stray parens, token {repr(t)} ({tid}), in {toks}")
			stck.pop()
		else:
			stck[-1].append(t)
		tid += 1
	if len(stck) != 1:
		raise Exception(f"unblanced parens in {toks}")
	expr = stck[0]
	for op in OPERATORS:
		if isinstance(expr, tuple):
			expr = (expr[0], __opgroup(expr[1], op))
		else:
			expr = __opgroup(expr, op)
	__splittags(expr)
	return expr


def scorescope(scopedef, scopestack, ss_len):
	best_score = 0
	sd_len = len(scopedef)
	end_i = ss_len - sd_len + 1
	i = 0
	while i < end_i:
		score = 0
		j = 0
		while j < sd_len:
			sstags = scopestack[i+j]
			tags = scopedef[j]#.split(".")
			for a, b in zip(sstags, tags):
				if a != b:
					score = 0
					break
				score += 1
			if score <= 0:
				break
			j += 1
		if score > best_score:
			best_score = score
		i += 1
	return best_score


def scorexp(xp, scopestack, ss_len):
	if isinstance(xp, tuple):
		op, subxp = xp
		if op == OP_OR or op == OP_INCL: # is this correct? I don't think so
			best_score = 0
			for xp in subxp:
				score = scorexp(xp, scopestack, ss_len)
				best_score = max(best_score, score)
		elif op == OP_XCL:
			main, *xcl = subxp
			best_score = scorexp(main, scopestack, ss_len)
			for xp in xcl:
				score = scorexp(xp, scopestack, ss_len)
				if score > 0:
					best_score = 0
					break
		return best_score
	return scorescope(xp, scopestack, ss_len)


if __name__ == "__main__":
	import sys
	rulescope = parserulescope(sys.argv[1])
	print("rulescope", rulescope)
	ss = [['source', 'python'], ['keyword', 'control', 'import', 'python']]
	print("ss", ss)
	print("scorexp", scorexp(rulescope, ss, len(ss)))