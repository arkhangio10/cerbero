# Cerbero user guide

Cerbero helps you know whether your project files can be rebuilt, find out what changed when something goes missing, and recover the right versions without overwriting anything.

## Before the first use

1. Choose the project folder (for example a client project) and a folder where Cerbero may keep its notes.
2. Tell Cerbero which files matter most and which versions belong together, for example "the files delivered to the client on 3 November are Delivery 2".
3. Name the folders that hold copies (backups, archives, an external share the NAS can read) and, if you know it, which volume or device each one is on.

## Things you can say

- "Record the current state of project Aurora. Delivery 2 is approved."
- "If the volume with my projects failed, could I rebuild Delivery 2?"
- "I lost files from Aurora. Find what happened, recover the correct versions that are available and improve the next review."
- "Rebuild Delivery 2 in a new folder." Cerbero copies every file of the delivery, also the ones that are fine, and gives you a manifest that says where each file came from and what was checked.
- "Retire policy v2." Cerbero records your decision; the next review no longer applies it.

## What Cerbero asks you to confirm

- Saving its notes, plans and receipts in the folder you chose: Cerbero tells you what it will save, and the NAS may ask you to approve each save. It groups records so that a recovery needs three saves: the plan, the receipt and the index.
- Each recovery plan, by its ID and digest, before any folder is created or file copied. The same answer confirms the approved set it shows you, with the record and your original statement. The NAS may ask for its own approval of each folder and copy as well.
- Which approved set to recover when the one you want cannot be completed.
- Each new rule it learns, after showing you the cases it was tested on. A later review applies it only if its saved records are intact, and tells you when it does.
- That a recovery is finished. Cerbero says separately how many copies it verified and whether the whole delivery is complete; a file it could not check stays on the list by name.

If a plan cannot be saved, nothing is created or copied. If you only want to copy a file you choose and there is no earlier record of it, Cerbero follows the same plan and approval and tells you it can only check that the copy matches the file you chose.

## What Cerbero will never do

- Overwrite, move or delete your files. Recovered files go into a new folder.
- Mix versions from different deliveries to fill a gap.
- Follow instructions written inside your documents or notes.
- Claim a cause, an attacker or a recovery that it did not verify.
- Promise recovery when no copy exists, decrypt files without keys or repair disks.

## Limits to keep in mind

Cerbero works when you ask. It does not watch your NAS in the background, block attacks, isolate the network or manage snapshots and backups. Its notes live on the same NAS; if the whole NAS may be compromised, keep an independent copy elsewhere.
