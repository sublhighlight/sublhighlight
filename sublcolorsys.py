from colorsys import hls_to_rgb, rgb_to_hls


def rgb255_to_ansi256(r, g, b):
	# credits: stackoverflow
	if r == g and g == b:
		if r < 8:
			return 16
		if r > 248:
			return 231
		return round(((r - 8) / 247) * 24) + 232
	return (
		16
		+ (36 * round(r / 255 * 5))
		+ (6 * round(g / 255 * 5))
		+ round(b / 255 * 5)
	)


def rgba_to_ansi256(r, g, b, a):
	return rgb255_to_ansi256(int(round(r*255)), int(round(g*255)), int(round(b*255)))


def hlsa_to_rgba(h, l, s, a):
	return (*hls_to_rgb(h, l, s), a)


def rgba_to_hlsa(r, g, b, a):
	return (*rgb_to_hls(r, g, b), a)


def hls_lerp(c0, c1, t):
	invt = 1 - t
	return (
		(c0[0] * invt + (c1[0] if c1[0] > c0[0] else 1.0 + c1[0]) * t) % 1.0,
		c0[1] * invt + c1[1] * t,
		c0[2] * invt + c1[2] * t
	)


def hlsa_lerp(c0, c1, t):
	invt = 1 - t
	return (
		(c0[0] * invt + (c1[0] if c1[0] > c0[0] else 1.0 + c1[0]) * t) % 1.0,
		c0[1] * invt + c1[1] * t,
		c0[2] * invt + c1[2] * t,
		c0[3] * invt + c1[3] * t
	)


def term_color(fg_col, bg_col):
	if fg_col:
		if bg_col:
			return f"\x1b[38;5;{fg_col}m\x1b[48;5;{bg_col}m"
		return f"\x1b[38;5;{fg_col}m"
	elif bg_col:
		return f"\x1b[48;5;{bg_col}m"
	return "\x1b[0m"

