A showcase to demonstrate how a repository funtionality may be designed on top of MongoDB using Python.

For customer CONTACT Software, Bremen (CSB)

# Steps to perform

- [x] Solution Design for create operations
- [x] Solution Design for update operations
- [x] Solution Design for read operations
- [ ] Solution Design for (hard) delete operations
- [x] Creation of a cloud-instance which can be also accessed by CSB --> see below
- [x] Generation of test data
- [x] Implementation of create operation
- [x] Implementation of update operation
- [x] Implementation of read operation
- [ ] Implementation of delete operation

Optional

- [ ] REST API
- [ ] Web site for CRUD operations

# Implementation data

Python 3.13.x\
MongoDB Atlas

- URI: mongodb+srv://contactsoftware:IcVD1umisMGAESaH@cluster0.jx87lcm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0\
- Username: contactsoftware
- Password: IcVD1umisMGAESaH

# Major functionality

## Change stream

Start by: `python src/workitem_listener.py` (in a dedicated separate shell)\
Parameters: None\
Listens to changes in the document stores, located in MongoDB document storage:

- Work item
- Document (work item collection)
- Attachment
- Folder

- insert
- update
- delete

events will be recognized and stores the changes (AKA deltas) in document history store.

Revision 0 keeps always the initial version of the document

HINT: Please use delete_workitem.py for deletion. Only in this case a retrieval of deleted work item is possible. A deletion by mean of the work item store, the deletion state is lost forever.

## Initialization of the repository

Start by: `python src/init.py`\
Parameters: None

- Resets the entire database
- Creates all stores from scratch, including their indexes
- Resets the revision counter
- Resets the history stores\

## Create, update, delete, read test data

Start by: `python src/test_data.py`\
Parameters:
- --mode (-m) [crud]\
    - c: Create new work item\
    - r: Show work item
    - u: Update work item (arbitrary modification of description)
    - d: Delete work item
- `--(w)orkItemID <work Item ID>` (not required for mode 'c' (create a new work item))

- Creates almost 1'000 entries in work item store with arbitrary description and summary
An initialization of the repository is recommended, as initial step.

## Add attachment

Start by: `python src/add_attachment.py`\
Parameter: `--(w)workItemID <Work Item ID>`\
Adds an arbitrary number of attachments from testFiles folder, to given work item. This must create an entry in work item history store (including increment of revision).

## Remove attachment

Start by: `python src/remove_attachment.py`\
Parameter:
  `--(w)orkItemID <Work Item ID>`\
  `document name`
Adds an arbitrary number of attachments from testFiles folder, to given work item. This must create an entry in work item history store (including increment of revision).

## Download attachments

Start by: `python src/store_attachments.py`\
Parameter: `--(w)orkItemID <Work Item ID> [--(r)evision <Revision ID>]`\
Downloads all attachments of given work item to current folder. If revision ID is not given, attachments of HEAD revision will be taken.

## Create baseline

Start by: `python src/create_baseline.py`\
Parameters: `--(l)abel <Label> --(a)uthor <Author>`\
Creates a baseline in baseline store. In fact, it labels the HEAD revision.
(A "retrospective" labeling is not possible/recommended.)

### Compare Baselines

Start by: `python src/compare_baselines.py`\
Parameters: `--(w)orkItemID <Work Item ID> --(f)romRevision <From Revision> [--toRevision <To Revision>]`\
Compares textually "From Revision" with "To Revision" of specified work item. If "To Revision" is not given HEAD is assumed.

## Delete Work Item

Start by: `python src/delete.py`\
Parameter: `--(w)orkItemID <Work Item ID>`\
"Deletes" virtually the work item. It must stay in work item store due to traceability and for recovery purposes, eg. when a rollback has been initiated and the work item needs to be recovered.

## List changes

Start by: `python src/list_changes.py`\
Parameter: `--(w)orkItemID <Work Item ID> --(f)romRevision <From Revision>`\
Is more or less the "front end" of the supporting function "get_deltas", see below.

## Export log

Start by: `python src/log.py`\
Parameter: `[--(w)orkItemID <Work Item ID>]`\
Pretty print of all changes of work item. If no work item is specified all changes will be exported.

## Rollback

Start by: `python src/rollback.py`\
Parameters: `--(w)orkItemID <Work Item ID> --(t)oRevision <To Revision>`\
Resets work item's content back to historic state defined by "To Revision". If work item is labeled as "deleted", the work item will be recovered, ie. the label disappears. This action must create an entry in work item history store.

# Supporting modules

## Settings

File: `src\settings.py`
When imported it sets specific parameters (globals are inappropriate for author).

| Parameter | Purpose |
|-----------|---------|
| uri | The locator and authorization string for a MongoDB Atlas instance |
| dbName | Name of the database to be used in MongoDB instance |
| workItemCollection | Collection for work items |
| workItemHistoryCollection | Collection to keep all changes on work items identified by a revision ID |
| revisionsCollection | "Global" revision counter persisting in this collection |
| baselineCollection | Collection for labels assigned to specific revisions |
| UPLOAD_FOLDER | Folder name where samples files for attachment uploads may be found |
| textBlob | This is the base string from which work item's description is filled (with arbitrary number of words) and it is the source for generation of arbitrary strings which are injected into existing description strings |

## Get files

Call: `getFiles` (in get_files.py)\
Parameters: `[<Number of files>]`\
Returns a list of maximum 3 (if no number is specified) arbitray full path file names from sample file folder (-> settings.py).

## Get deltas

Start by: `python src/get_delta.py`\
Parameters: `<Work Item ID> <From Revision> [<To Revision>]`\
Generates pretty print of delta comparison among given work item's "From Revision" to "To Revision" (if omitted HEAD is assumed). The output is stored in HTML format as file in current folder labeled with "diff<YYYYmmdd-HHMMSS>.html".

## Prepare work item

Call: `prepareWorkItem` (in get_files.py)
Parameters: `<Work Item ID> <set of changes>`\
Injects a set of changes to given work item to rebuild work items historic state. This historic state is returned.\
The set of changes is provided by the underlying persistence layer when a work item is modified.
