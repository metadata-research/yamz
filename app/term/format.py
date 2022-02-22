import re

ref_regex = re.compile("#\{\s*(([gstkm])\s*:+)?\s*([^}|]*?)(\s*\|+\s*([^}]*?))?\s*\}")
# subexpr start positions:    01                  2        3         4

ixuniq = "xq"
ixqlen = len(ixuniq)
tagstart = "#{g: "  # note: final space is important
