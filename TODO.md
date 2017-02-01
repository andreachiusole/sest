TODO:
-----

Requirements to develop.

Do not change the order or insert new reqs in the middle of the list.

1. ~~set up the email sending module.~~

1. ~~save every field as a string, and save (inside the channel class) the `encoding' to use to recover the value from that string.~~

1. redefine the Record.save() method, by placing the actions to be triggered there

1. let the user define different triggering actions for each channel

5. set up a cron job that every X (5 mins? 10?) sends a request on a special View that scans the whole DB of Channels, and compares the last_update field with the update_interval (it still has to be created) and trigger a special trigger action the user chose for that channel to signal inactivity

1. make the user choose which kind of field encoding to use from a defined list for each field of the channel.

1. check whether the values are of the correct type at the saving time.

1. check (with a test) that requests with wrong field names (instead of field1, .., field43) are not accepted by the upload view.

1. check (with a test) that fields (keys) without values (field1=& ...) are not accepted by the upload view.

10. linked with R3: at the saving time, check that the values are consistent with their field encoding.