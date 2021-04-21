import csv
import io
import requests
from fractions import Fraction
from ape_safe import ApeSafe
from brownie import *
import math

def main(depositYfi = True):
    r = requests.get('https://003.coordinape.me/api/csv?epoch=1')
    buff = io.StringIO(r.text)
    contributors = list(csv.DictReader(buff))

    sent_max = 100
    num_contributors = len(contributors)
    max_votes = sent_max * num_contributors

    # the 0.03% group has 24.44 YFI allocated for this epoch
    yfi_allocated = Wei(24.44 * 10 ** 18)

    # Convert received votes to Fraction so we can cleanly avoid floating point
    # error when we adjust the unsent votes
    for contributor in contributors:
        contributor['received'] = Fraction(contributor['received'])

    # Each person should have sent 100 votes but some failed to do so
    # As a group, we voted on spreading the votes as if they voted for all
    # the others equally with their leftover votes.
    for contributor in contributors:
        sent = int(contributor['sent'])

        # If a contributor didn't send all of their votes, spread those evenly
        if sent != sent_max:
            leftover_to_send = sent_max - sent

            # Only spread out evenly to others, not oneself
            for contributor_to_receive_more in contributors:
                if contributor_to_receive_more['No.'] != contributor['No.']:
                    contributor_to_receive_more['received'] += Fraction(leftover_to_send) / Fraction(num_contributors - 1)

    # Let's make sure those fractions add up to max_votes
    sum_received = 0
    for contributor in contributors:
        sum_received += contributor['received']

    assert(sum_received.numerator == max_votes)
    assert(sum_received.denominator == 1)

    safe = ApeSafe('ychad.eth')
    yfi = safe.contract('0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e')
    yvyfi = safe.contract('0xE14d13d8B3b85aF791b2AADD661cDBd5E6097Db1')
    disperse = safe.contract("0xD152f549545093347A162Dce210e7293f1452150")

    if depositYfi:
        assert(yfi.balanceOf(safe.account) >= yfi_allocated)
        yvyfi_before = yvyfi.balanceOf(safe.account)
        yfi.approve(yvyfi, yfi_allocated)
        yvyfi.deposit(yfi_allocated)
        yvyfi_to_disperse = yvyfi.balanceOf(safe.account) - yvyfi_before
    else:
        # I don't think this is exactly how deposit calculates the yvYFI out, but it should be close enough
        yvyfi_to_disperse = Wei(yfi_allocated / yvyfi.pricePerShare() * 10 ** 18)

    # Converting here will leave some dust
    amounts = [Wei(yvyfi_to_disperse * (contributor['received'] / Fraction(max_votes))) for contributor in contributors]

    # Dust should be less than or equal to 1 Wei per contributor due to the previous floor
    dust = abs(Wei(sum(amounts)) - yvyfi_to_disperse)
    assert dust <= num_contributors

    # Some lucky folks can get some dust, woot
    for i in range(math.floor(dust)):
        amounts[i] += Wei(1)

    assert Wei(sum(amounts)) == yvyfi_to_disperse
    assert yfi_allocated == (yvyfi_to_disperse * yvyfi.pricePerShare()) / 10 ** 18

    yvyfi.approve(disperse, sum(amounts))

    recipients = [contributor['address'] for contributor in contributors]
    disperse.disperseToken(yvyfi, recipients, amounts)
    history[-1].info()

    safe_tx = safe.multisend_from_receipts()
    safe.preview(safe_tx)
    safe.post_transaction(safe_tx)

if __name__ == "__main__":
    main()
