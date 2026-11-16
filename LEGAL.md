# Legal shape — global, no-login, legal minimum

## The one distinction everything turns on

**No login ≠ no ID.** An account, a password and a login are product
choices — this design drops all of them, on both sides. Identity
verification is a legal duty — no corridor on earth lets a money
service skip it entirely. Conflating the two is how illegal services
get built; keeping them separate is how this one stays legal globally.

## Send side — guest send

- No account creation, no password, no login. The sender opens the
  send page, enters the transfer, pays, and is done.
- The operator verifies the sender's identity on **every** send (a
  verification reference is stored — never raw ID images or numbers
  in this core) and screens sender and recipient against sanctions
  and watch lists before release.
- Why every send, at every amount: thresholds differ by corridor and
  change; verifying always is the strictest common denominator, and
  it keeps the per-transfer cap honest — the cap is a fraud/risk
  product limit, never a device to stay under an ID threshold.
  Splitting sends to dodge a cap or a check is structuring, a
  criminal offence in Canada, the US, the EU and most corridors; the
  core refuses over-cap sends and the pattern is screened.

## Receive side — link + code

- No account, no login, no app. The recipient opens the link (or
  gives the code at a pickup point), chooses cash or wallet.
- The one ID moment is at payout: ID shown at the pickup point and
  matched to the transfer, or the wallet provider's own verification.
  This is the operating norm of every major pickup network worldwide.

## Corridor notes (design inputs, not legal advice)

| Corridor | Sender-side duty (operator) | Receive-side norm |
|---|---|---|
| Canada (FINTRAC) | MSB registration; identity verification and records for remittances; sanctions screening; suspicious-transaction reporting | ID at pickup matched to the transfer |
| United States (FinCEN / BSA) | MSB registration + state licences; recordkeeping on transmittals; OFAC screening | ID at pickup; agent networks enforce it |
| EU / EEA (AMLD) | Licensed payment institution / agent model; CDD on customers; screening | ID at payout under agent rules |
| United Kingdom (FCA) | Authorised payment institution or agent; CDD + screening | ID at payout |
| Most pickup markets (LATAM, Africa, Asia) | Corridor partner carries local licence | Government ID at pickup is universal practice |

## Standing rules for this product

1. Operate only through a licensed route — partner network or own
   MSB/payment licences per corridor. The route decision is recorded
   as open in the README; nothing launches before it closes.
2. Records kept per the strictest applicable rule (FINTRAC: 5 years).
3. No marketing claim of "no KYC" or "anonymous" — the honest claim
   is: **no account, no login; ID once, at the legal minimum.**
4. This file is a design summary, not legal advice; a payments lawyer
   reviews each corridor before launch.
