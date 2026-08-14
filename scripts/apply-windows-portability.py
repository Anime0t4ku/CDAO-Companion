#!/usr/bin/env python3
from pathlib import Path
import sys

src = Path(sys.argv[1]).resolve()

def replace_once(path, old, new):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected source block not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def replace_function(path, signature, replacement):
    text = path.read_text(encoding="utf-8")
    start = text.find(signature)
    if start < 0:
        raise SystemExit(f"Could not locate {signature} in {path}")
    brace = text.find("{", start)
    if brace < 0:
        raise SystemExit(f"Could not locate opening brace for {signature}")
    depth = 0
    end = None
    for pos in range(brace, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                end = pos + 1
                break
    if end is None:
        raise SystemExit(f"Could not locate closing brace for {signature}")
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8", newline="\n")

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

case "$host" in
  *mingw*)
    AC_DEFINE([USE_POSIX_THREADS], [1],
              [Use the pthread based reader/writer implementation])
    PTHREAD_CFLAGS="-pthread"
    PTHREAD_LIBS="-pthread"
    ;;
esac
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
mk.write_text(makefile_text, encoding="utf-8", newline="\n")

dao = src / "dao" / "dao.cc"
replace_once(
    dao,
    '#include <sys/types.h>\n#include <sys/wait.h>\n#include <assert.h>\n',
    '#include <sys/types.h>\n#ifndef _WIN32\n#include <sys/wait.h>\n#endif\n#include <assert.h>\n'
)

port = src / "dao" / "port.cc"

# Native Windows does not expose POSIX sigaction/sigset_t. cdrdao only needs
# these wrappers to avoid signals while entering sensitive drive operations.
# The standard C signal() call is sufficient for the handlers cdrdao installs;
# signal masking itself becomes a no-op on Windows.
replace_function(
    port,
    "void installSignalHandler(int sig, SignalHandler handler)",
    """void installSignalHandler(int sig, SignalHandler handler)
{
#ifdef _WIN32
    signal(sig, handler);
#else
    struct sigaction action;
    memset(&action, 0, sizeof(action));
    action.sa_handler = handler;
    sigemptyset(&(action.sa_mask));
    sigaction(sig, &action, NULL);
#endif
}"""
)

replace_function(
    port,
    "void blockSignal(int sig)",
    """void blockSignal(int sig)
{
#ifdef _WIN32
    (void)sig;
#else
    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, sig);
#ifdef HAVE_PTHREAD_SIGMASK
    pthread_sigmask(SIG_BLOCK, &set, NULL);
#else
    sigprocmask(SIG_BLOCK, &set, NULL);
#endif
#endif
}"""
)

replace_function(
    port,
    "void unblockSignal(int sig)",
    """void unblockSignal(int sig)
{
#ifdef _WIN32
    (void)sig;
#else
    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, sig);
#ifdef HAVE_PTHREAD_SIGMASK
    pthread_sigmask(SIG_UNBLOCK, &set, NULL);
#else
    sigprocmask(SIG_UNBLOCK, &set, NULL);
#endif
#endif
}"""
)

# Realtime POSIX scheduling and setuid/setgid privilege dropping have no
# equivalent role in the native Windows build. Return "not available" for
# scheduling and success for privilege dropping.
replace_function(
    port,
    "int setRealTimeScheduling(int priority)",
    """int setRealTimeScheduling(int priority)
{
#ifdef _WIN32
    (void)priority;
    return 2;
#else
    struct sched_param sched;
    int maxPriority;

    if (geteuid() != 0)
        return 1;

    maxPriority = sched_get_priority_max(SCHED_FIFO);
    if (maxPriority < 0)
        return 2;

    memset(&sched, 0, sizeof(sched));
    sched.sched_priority = maxPriority - priority;

    if (sched_setscheduler(0, SCHED_FIFO, &sched) != 0)
        return 2;

    return 0;
#endif
}"""
)

replace_function(
    port,
    "bool giveUpRootPrivileges()",
    """bool giveUpRootPrivileges()
{
#ifdef _WIN32
    return true;
#else
    bool ret = true;

    if (geteuid() != getuid()) {
        if (seteuid(getuid()) != 0)
            ret = false;
    }

    if (getegid() != getgid()) {
        if (setegid(getgid()) != 0)
            ret = false;
    }

    return ret;
#endif
}"""
)

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
