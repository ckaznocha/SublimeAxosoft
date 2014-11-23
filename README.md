# SublimeAxosoft
A Sublime Text 3 package for Axosoft (formerly OnTime).

## Features
* Set a default project
* Create a new item of any type in a project
* List all items assigned to you
* Search for items
* View/Edit an item directly from sublime text
* Delete an item
* Open an item in your browser
* Log time to any item

## Installation
### Package Control
This is the recommended installation method.

1. Install [Sublime Package Control](http://wbond.net/sublime_packages/package_control) if you have not already.
1. From the Command Palette select `Package Control: Install Package`.
1. Search for `SublimeAxosoft` and select it when it comes up.
1. Restart Sublime Text for good measure.
1. Continue to [Configuration](#configuration).

### Git
1. Open a terminal or cmd.
1. `cd` to your Sublime Text 3 `Packages` directory.
1. `git clone git://github.com/ckaznocha/SublimeAxosoft.git`.
1. Restart Sublime Text if you had it open for good measure.
1. Continue to [Configuration](#configuration).

## Configuration
Before you can use this package you'll need to configure it to use your Axosoft instance.

1. Figure out the URL you use to access Axosoft.
1. From Sublime Text navigate to the `Preferences` menu and find your way to `Package Settings->SublimeAxosoft->Settings - User`.
1. In the file that opens, add a property called `axosoft_domain` with the value set to the URL from step 1.
    * e.g. if your URL is `http://foo.axosoft.com` you would use `foo.axosoft.com` as the value.
    * Your file should look something like this:
    ```JSON
        {
            "axosoft_domain" : "foo.axosoft.com"
        }
    ```
1. Save the file.
2. You will now be able to authenticate and begin using the package.

## Usage

### Log In
Before you can do anything you will need to authenticate with your Axosoft instance.

1. From the Command Palette select `Axosoft: Log In`.
1. A new browser window will open prompting you to log in and grant access to `SublimeAxosoft`
1. Once you grant access you will be forwarded to a page displaying your authentication code.
1. Copy and paste the the authentication code into the `code` prompt at the bottom of your Sublime Text window and hit enter.

### Log Out
You may wish to revoke access from Sublime Text to access your Axosoft instance.

1. From the Command Palette select `Axosoft: Log Out`.

### Set the current project
1. From the Command Palette select `Axosoft: Set Project`.
1. You will be presented with a list of available projects, choose one.
1. You'll get a confirmation that the project has been set.

### Create a new item
1. From the Command Palette select `Axosoft: Create Feature`.
1. Follow the prompts.

### Interact with items
1. From the Command Palette select `Axosoft: List All Features` or `Axosoft: Search Features`.
1. Choose a feature to interact with.

#### Delete
1. Choose `Delete`.
1. Confirm deletion.

#### Log Time
1. Choose `Log Time`.
1. Follow the prompt.

#### Open in browser
1. Choose `Open in Browser`.

#### Edit in Sublime Text
1. Choose `View/Edit`.
1. Make some modifications in the new tab that opens.
1. Close the tab.
1. Confirm that you want to save your changes.


This project and its contributers are in no way affiliated with Axosoft. Axosoft is the trademark of Axosoft, LLC
