# coordinape003epoch

Yearn allocated 24.44 YFI to be distributed across 25 folks who contributed to Yearn in the early days. This distribution was done through 003.coordinape.com as part of a special one-time epoch. This repo contains the ApeSafe script to generate the TX for the disbursement of this 24.44 YFI according to the vote results of the 003 coordinape epoch.

The folks in this special coordinape group held a normal vote, however, since some people didn't fully vote, we decided as a group to split the unsent votes equally. This way the people who didn't vote don't benefit massively from a lack of participation.

This script handles the redistribution of the remaining votes and the conversion of the 24.44 YFI into yvYFI for dispersement. Either equivalent yvYFI can directly be sent from ychad.eth or 24.44 YFI can be deposited into the vault and the resulting yvYFI shares will be sent instead. Both should be equivalent and the multi-sig can choose whichever is best. 
