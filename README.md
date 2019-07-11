# eve-fit-deleter

This script will delete all saved personal fits from your character.

This script is not maintained. If it stops working and you need it to work you can ask to get it fixed (or fix it and make a pull request. OR even better: Fork it and make a better version).

There will be no confirmation questions. Once you start the process all your saved fits will be deleted.

How to use:
* Create an application at https://developers.eveonline.com/applications with scopes to `esi-fittings.read_fittings.v1` and `esi-fittings.write_fittings.v1`. Set callback url to `http://localhost/oauth-callback`.
* When the script asks for them give the client ID and secret key that you got when you created the application.
* Log in the characters for which you want to delete all fits.
* Paste the code from URL bar after you log in and are redirected
* Start the deletion process.


## Requirements
* Python 3
* Requests https://2.python-requests.org//en/master/
