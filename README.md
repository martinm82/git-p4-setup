# gitp4setup.py - git-p4 workspace creator

The official [git-p4](https://github.com/git/git/blob/master/git-p4.py) extension creates a new Git repository from an already existing Perforce workspace.

`gitp4setup.py` is to make it very straightforward to create a local git repository together with a new Perforce workspace using git-p4.

## Requirements
* [Install git with Python and P4 support](https://github.com/git/git)
* [Download the P4 command-line client](https://www.perforce.com/downloads/helix#clients)

## Setup

* Checkout this repository

    ```
    $ cd ~/workspace
    $ git clone https://github.com/martinm82/git-p4-setup.git
    ```
* Create a Git and P4 workspace:

    ```
    $ ./git-p4-setup/gitp4setup.py dev-mystream-myname-myhost //mydepot/mystream
    ```

