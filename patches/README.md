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
