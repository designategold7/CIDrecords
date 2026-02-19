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

## PART 2: Ghost Wire Surveillance System (FiveM Script)

A specialized ESX resource utilizing `pma-voice` to facilitate undercover operations and wiretapping.

### Core Features
* **Covert Monitoring**: Allows detectives to listen to a target's audio in real-time without holding a radio or playing animations.
* **The Handover Mechanic**: Detectives can "plant" the wire on a Confidential Informant (CI). The CI becomes the transmitter, and the Detective becomes the receiver.
* **Visual Indicators**: An on-screen "REC" overlay confirms when the device is active for bodycam recording purposes.
* **Job Restriction**: Usage is strictly limited to Law Enforcement (Police/Sheriff/DTF).

### Usage Guide
1.  **Self-Wire**: Use the `cid_wire` item while alone to wear the wire yourself. You will broadcast to the monitoring frequency.
2.  **Planting**: Use the `cid_wire` item while standing next to another player (CI). The device will be transferred to them, and you will automatically connect to their audio feed.
3.  **Monitoring**: Other officers can listen in by setting their radio/call channel to the frequency displayed on the handler's screen.

### Technical Requirements
* Framework: ESX Legacy
* Voice System: pma-voice
* Inventory: ox_inventory (recommended) or esx_inventoryhud

### Installation
1.  Place the `esx_cidwire` folder into your server's `resources` directory.
2.  Add `ensure esx_cidwire` to your `server.cfg`.
3.  Insert the `cid_wire` item into your database items table.

---

**Authorized for Use by:**
Captain Casey Martin
CID Overseer / Training Division
6th Judicial District
