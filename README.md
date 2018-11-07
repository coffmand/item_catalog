# Project: item_catalog
#### By: Don Coffman
### Project 4 in Udacity's Full Stack Web Developer Nanodegree Program (2018)


## Description:
Project 4 is based on a linemode Python Flask Web Application which creates and maintains an Item Catalog containing User-defined
parent Categories, which in-turn contain User-defined related child Items.

3rd Party Login functionality is provided, using Google and Facebook.

The application considers User authorization (ie: Login) when allowing a given User the ability to make changes to the
Catalog database, thus protecting the integrity of the Catalog data.
Only logged-in Users can make changes to the database, Creating new Categories and related Items, as well as Editing or Deleting
any of the Categories and/or Items that they originally created.

- Notes on this point:
  - A User can only create Items under the Categories that he/she has originally created.
  - Deletion of a Category by default also deletes any Items under that Category. (ie: Cascade Delete)
  - A User can only Edit Items and Categories that he/she originally created.
    - When editing an Item, changes to the Category field (ie: the parent Category under which the Item exists) are
      constrained to only allow the Item to be re-attached to a Category _that the user originally created._
      - This rule is in place to prevent the case where an Item is re-attached to a parent Category with a different owner,
        thus allowing the Category owner to delete that Category and along with it an Item owned by a different User.

Non-logged-in Users can display any of the existing Categories and/or Items and request information through the API.

The application stores the Item Catalog data in a local SQLAlchemy SQLite database. Information displayed by the application
is read from the database.

API access to the Category and Item data stored in the database is provided. (_See Usage --> API Access, below_)


- The program's SQLAlchemy SQLite relational DB, resides on a locally-installed VirtualMachine (VM) VirtualBox/Vagrant
  LINUX environment. (_See Requirements / Prerequisistes, below_)
  - The 'itemcatalog' database (file: itemcatalog.db)  consists of (3) tables:
    - 'user'
    - 'category'
    - 'item'

  - SQLAlchemy provides an interface between the SQLite relational data and the Python object data.

  - The Web Interface is driven by the Flask framework Endpoint/Route definitions. HTML generation is enhanced through
    Flask's use of the Jinja Template Engine system. (_See Project Contents / Template Files, below_)

 - The program session interacts with localhost port 8000 through a standard browser. (http://localhost:8000)


## Project Contents:

- **application.py**: Main Python program code file and application entry point.

- **db_models.py**: Python/Flask/SQLAlchemy class definitions specifying Object Relationship Mapping info.

- **client_secrets.json**: Supporting use of Google Login functionality, the Client Application Registration data in this JSON file
                           is downloaded from Google. (File in GitHub repo is empty.)

- **fb_client_secrets.json**: Supporting use of Facebook Login functionality, the Client Application Registration data in this JSON file
                              is generated through app registation with Facebook. (File in GitHub repo is a template.)

  - **Template Files**:

    - **common.html**: Flask/Jinja template containing Meta data and standard CSS and Font links.

    - **header.html**: Flask/Jinja template containing standard Header Elements: Title, Logo, Login/out and Home link.

    - **footer.html**: Flask/Jinja template containing standard Footer Elements

    - **login.html**: HTML file containing Google and Facebook login Elements and script functionality

    - **showcategories.html**: Flask/Jinja template supporting Display of All Categories

    - **newcategory.html**: Flask/Jinja template supporting Creation of a New Category

    - **editcategory.html**: Flask/Jinja template supporting Editing of a Selected Category

    - **deletecategory.html**: Flask/Jinja template supporting Deletion of a Selected Category

    - **showitems.html**: Flask/Jinja template supporting Display of All Items for a Selected Category

    - **showitem.html**: Flask/Jinja template supporting Display of Detail Info for a Selected Item

    - **newitem.html**: Flask/Jinja template supporting Creation of a New Item

    - **edititem.html**: Flask/Jinja template supporting Editing of a Selected Item

    - **deleteitem.html**: Flask/Jinja template supporting Deletion of a Selected Item


  - **Static Files**:

    - **main.css**: Main CCS File.

    - **responsive.css**: CCS File containing rules for Responsive Style behavior.

    - **no_image_warning_240x160.jpg**: JPEG Graphic Image File - Default display in showItem() window when User has not specified
                                        an Image File for an Item .

- **Vagrantfile**: Vagrant Configuration file Drives installation and Configuration of sofware supporting the Vagrant (VM) environment

- **.gitignore**: Defines files to be ignored by Git Version Control system

- **README.md**: (This) Project README file (GitHub Markdown)




## Requirements / Prerequisites:
- **Git Bash Shell**: Since use of the above program is intended to be performed in a LINUX-style terminal shell env, it is suggested
     that a shell such as this is installed locally.

- **Python 2.7xx** (Min) must be installed on the target system and the path to the interpreter should be included in environment variables.

- **VirtualBox** must be installed on the target system. (This is the software that runs the VirtualMachine session.)
  - Download installation through virtualbox.org:
    - https://www.virtualbox.org/wiki/Download_Old_Builds_5_1
      _Note: As of October 2017, the supported version of VirtualBox to install is version 5.1. Newer versions do not work with the
       current release of Vagrant._

- **Vagrant** must be installed on the target system. (This is the software that configures the VM environment and allows
      file sharing between your normal env and the new VM environment.)
  - Download installation through vagrantup.com:
    - https://www.vagrantup.com/downloads.html

- **VM Configuration** In order to correctly configure the VM env for this project, a 'Vagrantfile' is included in the
    root directory of the GitHub repository for the 'item_catalog' project. (ie: Clone/Installation Directory)
    This dir also contains the Python code files,
    the 'templates' and 'static' sub-directories and their files, and the .git repo sub-dir, so that when the Vagrant VM Env is started,
    all of the required files and directories will be accessible through the **/vagrant** shared directory linkage.
    (_Note: Not all local files and dirs are accessible when the Vagrant Env is running ..._)
    - The 'Vagrantfile' also contains a definition of which localhost ports will be accessible by the application.
      - The 'item_catalog' application uses localhost port 8000.

    To startup the Vagrant LINUX session:
    - 'cd' to the above installation directory.
    - Execute the following command in the Shell to setup the VM env:
      - 'vagrant up'
    - After the above command has successfully completed, execute the following command in the Shell to startup the VM LINUX session:
      - 'vagrant ssh'
        _Note: - The SQLAlchemy / SQLite database engine and its functionality is only present in this env._
    - By executing 'cd' to the '/vagrant' shared directory, you are taken back to the original installation dir, where the
      main Python program file **application.py** resides.

    - Hitting 'Ctrl-D' in the shell terminates the current Vagrant ssh LINUX session, returning to the standard git-bash shell.

    - Useful resources related to Vagrant/VirtualBox:
      - Execute 'vagrant help' to access vagrant help documentation
      - Execute ' vagrant global-status' to view the run status of all local Vagrant environments
      - To help troubleshoot localhost port connections left open, the Oracle VirtualBox Manager application can help to identify and
        close any 'dangling' port connections. (Since my local system is on Windows 7, this software was accessed through Windows.)


- **3rd-Party Login Functionality Client/Application Registration**
    In order to use the Google and Facebook login capability for the local 'Item Catalog' sessions, register the application
    at the following sites and make the following local file changes:
    - Google:  https://console.developers.google.com/apis
      - After registration, download the Client Application Registration JSON data file and paste its contents into the empty
        **client_secrets.json** file in the installation dir, and save the file.
        Update the **templates/login.html** file, replacing the string _PASTE_YOUR_GOOGLE_CLIENT_ID_HERE_ with the Google-supplied
        Client ID string from the JSON data, saving the file.
        - Notes:
          - Make sure the Client ID Application Name registered with Google matches contents of the APPLICATION_NAME variable
            defined in the **application.py** code:
              --> ``` APPLICATION_NAME = "Item Catalog Application" ```
            A mismatch causes the Google Login to not operate correctly.
          - Make sure the registered 'javascript_origins' include the foundational localhost port 8000 address.
          - Make sure the registered 'redirect_uris' include the localhost port 8000 redirects to '/login', '/gconnect', and '/fbconnect'.

    - Facebook:   https://developers.facebook.com/
      - After registration, use the Facebook-supplied information to update the **fb_client_secrets.json** file in the installation dir.
        Replace the string _PASTE_YOUR_FACEBOOK_APP_ID_HERE_ with the Facebook App ID string,
        replace the string _PASTE_YOUR_FACEBOOK_CLIENT_SECRET_HERE_ with the Facebook Client Secret string, and save the file.
        Update the **templates/login.html** file, replacing the string _PASTE_YOUR_FACEBOOK_APP_ID_HERE_ with the Facebook-supplied
        App ID string, saving the file.



## Installation:
- Clone this GitHub repository on local system
  -- OR --
- Download Zip File to local system and unzip



## Usage:
- Using local system command-line interface Shell:

  - Change directory to the above repo installation location.
  - Start up a Vagrant LINUX session:

    - Execute the following command in the Shell to setup the VM env:
      - 'vagrant up'

    - After the above command has successfully completed, execute the following command in the Shell to startup the VM LINUX session:
      - 'vagrant ssh'

  - 'cd' to the '/vagrant' shared directory, which points back to the original installation dir, where the
    main Python program file **application.py** resides.

  - Execute the following:
    - **python application.py**

    - The Web server application is currently set up to display debug info, so immediately status info will appear in
        the Terminal Display window.

    - Hitting 'Ctrl-C' in the shell terminates the current web server app session.

    - Hitting 'Ctrl-D' in the shell terminates the current Vagrant ssh LINUX session, returning to the standard git-bash shell.

    - Access and test the Item Catalog application by visiting: http://localhost:8000 or http://localhost:8000/categories
      in your local browser.


  - API Access:
    The following URL Enpoints are available for API Access, returning the requested data in JSON format.
    The URLs are constructed by combining the base **http://localhost:8000** URL path with the following path suffixes:

    - Suffix **/api/v1/categories/JSON** :
      - Returns JSON representation of All Category records

    - Suffix **/api/v1/categories/<category_id>/JSON** :
      - Returns JSON representation of the Category record with 'id' Field = <category_id>

    - Suffix **/api/v1/categories/<category_id>/items/JSON** :
      - Returns JSON representation of all Item records with a 'category_id' Field = <category_id>

    - Suffix **/api/v1/categories/<category_id>/items/<item_id>/JSON** :
      - Returns JSON representation of the Item record with an 'id' Field = <item_id> and a 'category_id' Field = <category_id>



## Contributions:
- The general layout of this README file is based on a template suggested by PhillipCoach in a Udacity Forum post
  and previously used/mentioned by Steven Wooding
- Some of the VM Installation/startup instructions are based on the Udacity Lesson/Project instructions.
- Much of the 3rd Party Google and Facebook login functionality comes directly from the Udacity lesson, with some
  minor cleanup and fixes applied.


## Extra Credit Changes Description:
- The Item record was designed and implemented to provide Image File handling.
- The styling of the application's Web Page elements incorporates Responsive behavior, controlled by the 'static/responsive.css'
  file.
- Incorporated Cascading Delete functionality through SQLAlchemy, and enforced underlying ownership integrity in Item edit
  functionality. (_See Description section, above_)
- Incorporate some level of CSRF protection on CRUD functionality.
