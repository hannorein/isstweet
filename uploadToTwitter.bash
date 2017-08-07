#!/bin/bash
MESSAGE=`cat $1`
FILENAME="$2"

MEDIAJSON=`/usr/local/bin/twurl -H upload.twitter.com -X POST '/1.1/media/upload.json' --file "$FILENAME" --file-field 'media'`
MEDIAID=`echo "$MEDIAJSON" | sed -rn 's/\{\"media_id\":(.*)\,\"media_id_string.*/\1/p'`
/usr/local/bin/twurl "/1.1/statuses/update.json" --raw-data "media_ids=$MEDIAID&status=$MESSAGE"
