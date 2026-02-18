# CID and DTF Record Management System

A dedicated Discord-based Record Management System (RMS) designed for Law Enforcement Roleplay (LERP) environments. This system provides a persistent, SQL-backed database for tracking investigations, evidence, and case jackets for both the Criminal Investigation Division (CID) and the Drug Task Force (DTF).

## Features

- **Departmental Logic**: Separate case ID generation for CID (YY-CID-XXX) and DTF (YY-DTF-XXX).
- **Relational Database**: Powered by SQLite for high performance and data persistence across bot restarts.
- **Evidence Locker**: Append bodycam footage and media links directly to case narratives with automated officer attribution.
- **Document Integration**: Support for "Case Jackets" to link Google Docs, PDFs, and external reports directly to a case file.
- **Complete Case Lifecycle**: Functions to file, edit, lookup, import legacy data, and delete records.
- **Security**: Hard-coded Admin ID protection for Case deletion and management commands and role-locked access for departmental commands.

