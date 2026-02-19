# ASRP CID 6th Judicial District - Specialized Investigative Toolkit

This repository contains the custom software suite developed for the Criminal Investigations Division (CID) and Drug Task Force (DTF). It consists of two integrated components:

1.  **CID Record Management System (RMS)**: A Python-based Discord bot for case management, evidence tracking, and legal reference.
2.  **Ghost Wire Surveillance System**: A Lua-based FiveM script for covert audio monitoring and Confidential Informant (CI) operations.

---

## PART 1: CID Record Management System (Discord Bot)

A SQL-backed administrative tool designed to replace Google Docs/Sheets with a persistent, searchable database.

### Core Features
* **Case Management Lifecycle**: Full support for filing, editing, closing, and archiving investigations.
* **Arkansas Law Library**: A searchable database of over 60 Arkansas State Statutes (A.C.A.) seeded directly into the bot.
* **Field Guide Module**: An interactive menu containing Miranda Rights, SOPs, Chain of Command, and forensic checklists.
* **Evidence Locker**: Secure logging of bodycam footage and document links (Jackets) associated with specific case IDs.
* **Pagination System**: Optimized directory views to browse cases and laws without flooding the chat.

### Commands Reference
* `/file_case` - Initialize a new investigation (Generates unique Case ID).
* `/edit_case` - Modify case status, suspect information, or narrative.
* `/case_directory` - View a paginated list of all active investigations.
* `/case_lookup [ID]` - Retrieve the full dossier, including evidence links.
* `/law_directory` - Browse the Arkansas Penal Code database.
* `/search_law [Query]` - Find specific statutes by name or code (e.g., "Battery").
* `/field_guide` - Access the interactive officer training manual.
* `/add_evidence` - Append media/video evidence to a case file.
* `/add_jacket` - Link external documents (PDF/Google Docs).
* `/import_case` - [Admin] Manually ingest legacy records.
* `/delete_case` - [Overseer] Permanently purge a record.

### Technical Requirements
* Python 3.8 or higher
* Database: SQLite 

---


