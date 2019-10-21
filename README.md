# tap-lookml

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls LookML files from [GitHub v3 API ](https://developer.github.com/v3/) to extract LookML components using [lkml parser](https://github.com/joshtemple/lkml).
- Extracts the following resources:
  - Model Files: [Git API Search](https://developer.github.com/v3/search/#search-code) with [filename and extension filters](https://help.github.com/en/articles/searching-code) for **model** and **lkml**
  - Models: Parse items (connection, includes, datagroups, explores, joins, etc.) using **lkml**
  - View Files: [Git API Search](https://developer.github.com/v3/search/#search-code) with [filename and extension filters](https://help.github.com/en/articles/searching-code) for **view** and **lkml**
  - Views: Parse items (derived table, dimensions, measures, filters, parameters, sets, etc.) using **lkml**
- Outputs the schema for each resource
- Incrementally pulls data based on the input state (file last-modified in GitHub)


## Streams

**model_files**
- Search Endpoint (ALL Model Files): https://api.github.com/search/code?q=filename:.model.+extension:lkml+repo:[GIT_OWNER]/[GIT_REPOSITORY]
- File Endpoint: https://api.github.com/repos/[GIT_OWNER]/[GIT_REPOSITORY]/contents/[GIT_FILE_PATH]
- Primary key fields: url
- Foreign key fields: repository_id
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove _links node, remove content node, add repository name, path, folder, and repository ID

**models**
- Primary key fields: url
- Replication strategy: FULL_TABLE (ALL for each model_file)
- Transformations: Decode, parse model_file **content** and convert to JSON

**view_files**
- Search Endpoint (ALL View Files): https://api.github.com/search/code?q=filename:.view.+extension:lkml+repo:[GIT_OWNER]/[GIT_REPOSITORY]
- File Endpoint: https://api.github.com/repos/[GIT_OWNER]/[GIT_REPOSITORY]/contents/[GIT_FILE_PATH]
- Primary key fields: url
- Foreign key fields: repository_id
- Replication strategy: INCREMENTAL (Search ALL, filter results)
  - Bookmark field: last_modified
- Transformations: Remove _links node, remove content node, add repository name, path, folder, and repository ID

**views**
- Primary key fields: url
- Replication strategy: FULL_TABLE (ALL for each model_file)
- Transformations: Decode, parse model_file **content** and convert to JSON


## Authentication


## Quick Start

1. Install

    Clone this repository, and then install using setup.py. We recommend using a virtualenv:

    ```bash
    > virtualenv -p python3 venv
    > source venv/bin/activate
    > python setup.py install
    OR
    > cd .../tap-lookml
    > pip install .
    ```
2. Dependent libraries
    The following dependent libraries were installed.
    ```bash
    > pip install singer-python
    > pip install singer-tools
    > pip install target-stitch
    > pip install target-json
    
    ```
    - [singer-tools](https://github.com/singer-io/singer-tools)
    - [target-stitch](https://github.com/singer-io/target-stitch)

3. Create your tap's `config.json` file. This tap connects to GitHub with a [GitHub OAuth2 Token](https://developer.github.com/v3/#authentication). This may be a [Personal Access Token](https://github.com/settings/tokens) or [Create an authorization for an App](https://developer.github.com/v3/oauth_authorizations/#create-a-new-authorization). Each tap connects to a single Looker/LookML Git Repository (where your Looker LookML code is hosted for your Looker Project); provide the name of the `git_repositories` delimited by a comma (spaces are ignored) and the `git_owner` of those repositories (whcih can be a User or Organization). 

    ```json
    {
        "api_token": "YOUR_GITHUB_API_TOKEN",
        "git_owner": "YOUR_GITHUB_ORGANIZATION_OR_USER",
        "git_repositories": "LOOKER_GIT_REPO_1, LOOKER_GIT_REPO_2, ...",
        "start_date": "2019-01-01T00:00:00Z",
        "user_agent": "tap-lookml <api_user_email@your_company.com>"
    }
    ```
    
    Optionally, also create a `state.json` file. `currently_syncing` is an optional attribute used for identifying the last object to be synced in case the job is interrupted mid-stream. The next run would begin where the last job left off.

    ```json
    {
        "currently_syncing": "users",
        "bookmarks": {
            "model_files": "2019-10-13T19:53:36.000000Z",
            "view_files": "2019-10-13T18:50:11.000000Z"
        }
    }
    ```

4. Run the Tap in Discovery Mode
    This creates a catalog.json for selecting objects/fields to integrate:
    ```bash
    tap-lookml --config config.json --discover > catalog.json
    ```
   See the Singer docs on discovery mode
   [here](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#discovery-mode).

5. Run the Tap in Sync Mode (with catalog) and [write out to state file](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#running-a-singer-tap-with-a-singer-target)

    For Sync mode:
    ```bash
    > tap-lookml --config tap_config.json --catalog catalog.json > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    To load to json files to verify outputs:
    ```bash
    > tap-lookml --config tap_config.json --catalog catalog.json | target-json > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    To pseudo-load to [Stitch Import API](https://github.com/singer-io/target-stitch) with dry run:
    ```bash
    > tap-lookml --config tap_config.json --catalog catalog.json | target-stitch --config target_config.json --dry-run > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```

6. Test the Tap
    
    While developing the lookml tap, the following utilities were run in accordance with Singer.io best practices:
    Pylint to improve [code quality](https://github.com/singer-io/getting-started/blob/master/docs/BEST_PRACTICES.md#code-quality):
    ```bash
    > pylint tap_lookml -d missing-docstring -d logging-format-interpolation -d too-many-locals -d too-many-arguments
    ```
    Pylint test resulted in the following score:
    ```bash
    Your code has been rated at 9.68/10
    ```

    To [check the tap](https://github.com/singer-io/singer-tools#singer-check-tap) and verify working:
    ```bash
    > tap-lookml --config tap_config.json --catalog catalog.json | singer-check-tap > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    Check tap resulted in the following:
    ```bash
    The output is valid.
    It contained 58 messages for 4 streams.

        4 schema messages
        48 record messages
        6 state messages

    Details by stream:
    +-------------+---------+---------+
    | stream      | records | schemas |
    +-------------+---------+---------+
    | model_files | 2       | 1       |
    | models      | 2       | 1       |
    | view_files  | 17      | 1       |
    | views       | 27      | 1       |
    +-------------+---------+---------+
    ```
---

Copyright &copy; 2019 Stitch
