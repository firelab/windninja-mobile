# WindNinja Server-Application Notification System

## Summary
The WindNinja Mobile application system does not yet implement a true push notification system. This is planned for a future release once we have full operational infrastructure in place. 

In lieu of the push notification system, the server implements a simple "notifications" API.  The mobile application requests "messages" from the server during startup. If any messages are returned, they will be displayed to the user in a simple popup window at that time. 


## Notification Format

The notification message is a simple structure with:

* id : unique string value... uuid preferred
* expires: an ISO formatted, timezone aware date time string.  This date is checked during an API request.  Only messages with an expires date after the current date time will be returned to the client.
* message: any string text, can be html encoded for fancy display.

In the 'FileStore' implemenation, this object is stored a plain text JSON. For example: 
	
.\Data\notifications\76ff1f4e-7ff9-4f21-8ef7-1ad186b99765.json

`
{
	"id":"76ff1f4e-7ff9-4f21-8ef7-1ad186b99765",
	"message": "<strong>This is test notification ONE</strong>",
	"expires": "2020-10-25T23:59:59+00:00"
}
`
## Creating Notifications

In the 'FileStore' implementation, this is as simple as creating a text file and typing in the formatted structure. 

There is also a simple pyhton script in the Notification directory that will create the text file in the correct format.  The file is created in the same directory as the script.  It can be run from the data store folder or another location and then the file copied to the datastore folder.

`
manage_notification.py create --message "this is a message" --expires 2018-01-01T23:59 --zone EST
`

The action value required and 'create' is the only thing currently implemented. The other parameters are optional.  If not supplied default values will be provided as placeholders.  The expires date will be in the past. 

--message can be any text but must be enclosed in quotes.  Unless it's a simple small message, it's probably best to edit manually after the fact.
--expires is a date+time string in format YYYY-MM-DDTHH:MM.  This can be manually edited as well but providing the value here will ensure the correct ISO format and time zone are created.
--zone is the timezone of the expires date. Implemented values are GMT, EST, CST, MST, PST.  The date time can be edited after the script is run.