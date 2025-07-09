# Simplenote-to-NotallyX
A simple python script to help import your notes from Simplenote to NotallyX.

If you want to import your notes from [Simplenote](https://simplenote.com/) to [NotallyX](https://github.com/PhilKes/NotallyX) you will realize that Simplenote puts all the notes inside a single json file and only provides seperate files in plain text, which actually works with NotallyX but it will not import the tags and the dates will be changed to when you import them. So with the help of Chatgpt I somehow managed to create a simple python script that splits the single json into multiple json files and reformats the data just as google keep does, so that when you import them it looks like you never imported them but created in NotallyX itself. Do note that this is only once tested by me and I have zero coding knowledge so always take backups in case it does not work. The script will try to delete duplicates but otherwise the title and body text will be the same, with date and tags intact.

Guide:

1. Install python
2. Place the exported json file of simplenote in any folder.
3. Rename it to simplenote_export.json
4. Place the python file SimplenoteToNotallyX.py in the same folder
5.  Open terminal/powershell in that folder or use the cd command.
6. Run script with python SimplenoteToNotallyX.py 
7. If succeeded, it will create a zip and a folder in the same directory with the name google_keep_notes
8. Put the generated zip onto your phone and open NotallyX.
9. Go to its settings > import notes from other app > Google Keep > Import & select the zip.
10. Wait a bit and it should be imported in a few seconds.
11. Never use simplenote again.
