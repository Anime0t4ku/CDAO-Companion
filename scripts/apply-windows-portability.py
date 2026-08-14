#!/usr/bin/env python3
from pathlib import Path
import sys

src = Path(sys.argv[1]).resolve()

def replace_once(path, old, new):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected source block not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")

lec = src / "trackdb" / "lec.cc"
replace_once(
    lec,
    '#include <assert.h>\n#include <sys/types.h>\n',
    '#include <assert.h>\n#include <sys/types.h>\n#include <cstdint>\n'
)

cfg = src / "configure.ac"
replace_once(
    cfg,
    'AC_CANONICAL_HOST\n',
    '''AC_CANONICAL_HOST

dnl MiSTer Companion native Windows builds omit the legacy POSIX CDDB client.
case "$host" in
  *mingw*) companion_build_cddb=no ;;
  *)       companion_build_cddb=yes ;;
esac
AM_CONDITIONAL([COMPANION_BUILD_CDDB],
               [test "x$companion_build_cddb" = "xyes"])
'''
)

mk = src / "trackdb" / "Makefile.am"
replace_once(
    mk,
    'libtrackdb_a_SOURCES = \\\n\tCddb.cc\t\t\t\\\n\tlec.cc',
    'libtrackdb_a_SOURCES = \\\n\tlec.cc'
)

makefile_text = mk.read_text(encoding="utf-8")
anchor = 'AM_CXXFLAGS = @AO_CFLAGS@\n'
if anchor not in makefile_text:
    raise SystemExit("Could not locate Automake conditional insertion point")
makefile_text = makefile_text.replace(
    anchor,
    '''AM_CXXFLAGS = @AO_CFLAGS@

if COMPANION_BUILD_CDDB
libtrackdb_a_SOURCES += Cddb.cc
endif
''',
    1,
)
mk.write_text(makefile_text, encoding="utf-8", newline="\\n")

main = src / "dao" / "main.cc"
replace_once(
    main,
    '#include <sys/wait.h>\n#include <sys/utsname.h>\n#include <pwd.h>\n',
    '#ifndef _WIN32\n#include <sys/wait.h>\n#include <sys/utsname.h>\n#include <pwd.h>\n#endif\n'
)

text = main.read_text(encoding="utf-8")
start = text.find("void printCddbQuery(Toc *toc)")
end = text.find("void scanBus()", start)
if start < 0 or end < 0:
    raise SystemExit("Could not locate CDDB helper block")
orig = text[start:end]
stub = '''#ifdef _WIN32
void printCddbQuery(Toc *)
{
    log_message(-1, "CDDB support is not included in the MiSTer Companion Windows build.");
}

int readCddb(const DaoCommandLine&, Toc *, bool = false)
{
    log_message(-1, "CDDB support is not included in the MiSTer Companion Windows build.");
    return 1;
}
#else
''' + orig + '#endif\n'
main.write_text(text[:start] + stub + text[end:], encoding="utf-8", newline="\n")

text = main.read_text(encoding="utf-8")
sig = "int copyCdOnTheFly(DaoCommandLine& opts,CdrDriver *src, CdrDriver *dst)"
start = text.find(sig)
end = text.find("} // End of anonymous namespace", start)
if start < 0 or end < 0:
    raise SystemExit("Could not locate copyCdOnTheFly block")
orig = text[start:end]
stub = '''#ifdef _WIN32
int copyCdOnTheFly(DaoCommandLine&, CdrDriver *, CdrDriver *)
{
    log_message(-2, "On-the-fly drive-to-drive copying is not supported by the MiSTer Companion Windows build.");
    return 1;
}
#else
''' + orig + '#endif\n\n'
main.write_text(text[:start] + stub + text[end:], encoding="utf-8", newline="\n")

print("Applied MiSTer Companion Windows portability changes.")
