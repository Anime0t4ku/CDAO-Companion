# Windows portability changes

cdrdao 1.2.6 already contains a native Windows SCSI implementation
(`ScsiIf-nt.cc`) and selects it for MinGW hosts, but a few legacy components
still assume POSIX.

The Companion Windows build therefore:

- adds the missing `<cstdint>` include for `int16_t`;
- omits the POSIX CDDB client;
- disables only the fork/pipe based on-the-fly drive-to-drive copy path.

The functions Companion needs remain enabled: `scanbus`, `read-cd`, `read-toc`,
`write`, normal MMC/SCSI access, `toc2cue`, and `cue2toc`.

The CDDB source exclusion is implemented with an Automake conditional (`COMPANION_BUILD_CDDB`), rather than a configure substitution inside `libtrackdb_a_SOURCES`, because Automake does not permit substitutions in `_SOURCES` variables.

The Windows build workflow installs MSYS2 Python explicitly and runs the patcher with `python3`; this avoids relying on whatever Python happens to be present on a GitHub-hosted Windows runner.

## Native Windows threading/portability

The native Windows build forces cdrdao's pthread reader/writer path using
MinGW-w64 winpthreads. This intentionally avoids the alternative Unix
`fork()`/`wait()`/SysV shared-memory implementation.

Windows also receives small compatibility wrappers for:

- `sigaction` / POSIX signal masks;
- POSIX realtime scheduling;
- Unix UID/GID privilege dropping.

These facilities are not required to access optical drives through cdrdao's
native Windows SCSI/MMC backend. The actual CD read/write code remains the
upstream implementation.
