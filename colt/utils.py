#!/usr/bin/env python


def dictmerge(dst, src):
	for key, value in src.items():
		if not key in dst:
			dst[key] = value
			continue
		if value.__class__ is list:
			dst[key].extend(src[key])
		else:
			dst[key] = dictmerge(dst[key], src[key])
	return dst

