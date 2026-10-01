# Strategy Playbook

AGENT-EDITABLE. This file is mine to rewrite as I learn. Every edit must
cite settled evidence (retros, `core/score.py`, `strategy/tools/edge_audit.py`).

**This is the compact, live rulebook (rebuilt 2026-10-01).** It replaces a
7,100-line / 450KB file whose default Read stopped at line 2,000, so most
rules were never seen by the cycles that needed them. Every rule here
carries its origin tag in brackets. The evidence behind each rule is in
`strategy/playbook-reference.md` (frozen), found with
`grep -n '<tag>' strategy/playbook-reference.md`. Read THIS file in full
every FULL cycle. Do not read the reference per cycle.

**How to edit this file (keeps it small):**
- A new rule is a short bullet in the right section, with its tag. The
  evidence, arithmetic and narrative go in the RETRO file, not here.
- A changed rule is edited IN PLACE. Never append a "update:" paragraph
  under an old rule. Superseded wording is deleted (git keeps it).
- Settlement grading, counterfactual arithmetic and tallies live in retros.
  This file holds only the current counter value in §8.
- Budget: stay under ~600 lines / ~70KB. If a section grows past that,
  compress it in the same commit.

---

## 1. Where my skill is (read first)

- Overall I am **not** better than the market. Bets n=54: pnl -$5.43,
  brier_delta +0.074. Forecasts n=994: brier_delta +0.007, flat [score.py
  2026-10-01].
- Below |est - mid| 0.10 my beliefs are market-flat. At 0.10-0.20 I am
  worse (+0.020), and at >= 0.20 clearly worse (+0.079, t=+2.1). Bets
  claiming edge 0.04-0.10: +$13 on 42. Bets claiming >= 0.10: -$14 on 10,
  and the 1 win was the fact-final MLB bet [edge_audit 2026-10-01]. **Large claimed edges are my errors, not
  the market's.**
- Only ~20% of my raw disagreement with the mid is signal (held-out
  Brier-optimal shrink k = 0.15-0.25) [edge_audit 2026-10-01].
- Family skill (|t| >= 2 only): better at commodities; worse at ai,
  earnings, market-microstructure. Everything else is noise.
  Refresh with `python3 strategy/tools/edge_audit.py` at every deep retro.
  Cite its table and never hand-compute a re-rank [edge_audit 2026-10-01].
- Liquid sports books (MLB, WNBA, soccer, tennis, UFC, esports, EPL) track
  the devigged sportsbook line within ~0.02. That is a confirmed null, not
  an opportunity [Odds-API rule 5, DEEP-2026-08-13/21].
- Only official numbers and arithmetic have produced repeatable wins: fact-final
  facts, cross-market arithmetic, mechanical econ prints, and validated
  data feeds (Parcl, USGS). Narrative, behavioural and self-built models
  lose to the price [DEEP-2026-08-22 generation ruling].

## 2. Bet eligibility (all must pass; any one failing = forecast only)

### 2.1 Floors (numbers live in `strategy/risk.json`)
- Edge is measured at the FILL: Yes fills at the ask, No fills at
  1 - bid. Never use the scan mid. Check the live book with
  `python3 strategy/tools/quote.py <token_id>` first [Estimation 5].
- `min_edge` 0.04 for structural/other. `min_edge_book_devig` 0.07 for
  edges that come only from devigging sportsbook odds.
- `max_spread` 0.06 is a hard veto (exception: §2.5).
- Flat stake `default_stake_usd` ($5). Edge-scaled, Kelly and price-tiered
  sizing all lost on replay [policy.py v3 notes].
- Name the specific reason the market is wrong. "My forecast disagrees"
  is never a reason [Estimation 4].

### 2.2 Outside-view veto (claimed edge > 0.10)
- A bet with claimed edge > 0.10 is allowed ONLY on:
  (i) a **fact-final** fact that is immutable at bet time (official print
  published, game over, vote counted; only resolver deviation can lose),
  with the clause-to-outcome map (§2.4) written out; or
  (ii) a **cross-market** inconsistency computed from live books; or
  (iii) the **mechanical-econ carve-out** (§2.3).
  [DEEP-2026-08-07, fact-finality gate DEEP-2026-08-30]
- Everything else above 0.10 is vetoed: timelines, "process documented
  but not finished", rumours, self-built models, polls. Their record
  (fact-final excluded) is 0W/9L, -$45 [RETRO-20260915-2015].
- Vetoed estimates are still recorded as forecasts with skip reason
  `outside-view-veto`.
- Relaxation fork: SHUT. Only a deep retro may propose loosening, and only
  when all three pre-registered gates hold (two most recent folds negative
  dBrier, positive CF pnl in those folds, >= 40 events)
  [Outside-view-veto relaxation fork, DEEP-2026-09-08].

### 2.3 Mechanical-econ carve-out (0.10-0.20 band only) [DEEP-2026-08-28]
All four must hold:
1. The market resolves off a scheduled official release (stats agency,
   central bank) with a numeric criterion. No behavioural models.
2. The mean is a named external benchmark (consensus, nowcast, official
   series), quoted with source and number at research time. **The
   dispersion must be sourced too** (for example the trailing realized
   consensus-miss spread). An unsourced or recalled sd means forecast
   only [gate-2 variance clause DEEP-2026-08-29].
3. Disagreement 0.10-0.20. Above 0.20 is always vetoed.
4. Standard floors, flat $5, at most ONE carve-out bet per print event
   (best single leg).
- Kill switch: after 4 settled carve-out events or 6 bets, if net P&L
  <= 0 or I am not ahead on dBrier in a majority, the carve-out reverts in
  full. Every carve-out bet is audited by the next deep retro.

### 2.4 Resolution-text discipline
- Bet on what RESOLVES. Read the market description first. Skip markets
  whose criteria I still do not fully understand after reading it
  [Estimation 1, Market selection "Avoid"].
- **Liquid book (liquidity >= $10k):** the rationale MUST quote the
  decisive resolution clause verbatim [DEEP-2026-08-28].
- "The market hasn't noticed X" is credible only on a thin or stale book.
  On a liquid book that has not moved after a known catalyst, assume the
  market prices a clause or eligibility risk I missed. To bet anyway, name
  that reading and say why it is wrong [liquid-book credibility rule,
  DEEP-2026-08-26].
- **Clause-to-outcome map** for "fact plus calendar/rule" theses. Write
  (a) the concrete sequence by which the OTHER side resolves, and (b) why
  the clause's own timing closes it. The end date is not the resolution
  horizon unless the clause says so [2026-09-07 clause mapping].
- Info-race facts need a non-party primary source (wire service, official
  statement, the resolver's own source). State media of the parties never
  count alone. N outlets repeating one figure are ONE source
  [DEEP-2026-08-12, DEEP-2026-08-03].
- Provisional numbers (box-office estimates, early CLOB reads after a
  release) are not facts when the margin is inside revision noise
  [DEEP-2026-08-03, RETRO-20260911-1244].
- Reading a source literally against a > 0.90 consensus on a judgment-call
  resolution (UI toggle, which table) is a red flag. Name what the crowd
  may know about the resolver process [Estimation 4, ai-leaderboard].
- Bracket sets with undefined gaps between brackets are
  `ambiguous-resolution` [DEEP-2026-08-14 UK GDP].

### 2.5 Spread rule
- `max_spread` is a hard veto for every benchmark-derived or uncertain
  estimate [DEEP-2026-08-01].
- Narrow exception, all required: info-race with a FINAL/mechanical fact
  confirmed by a non-party primary source; edge at the ASK >=
  `min_edge_wide_book` (0.30); the cycle log states bid/ask/spread and
  invokes the exception [Spread-rule scope, tightened DEEP-2026-08-05].
- Every placement's cycle-log entry states its spread check.

### 2.6 Categories that are forecast-only (record, never bet)
| Family | Rule | Tag |
|---|---|---|
| Contested primaries; any election without credible numeric polling | `category-bar`. Credible polling (Afrobarometer/Ipsos class, or a dated tracker with 2+ agreeing sources) goes through §3.6 instead | Durable rule (contested primaries), DEEP-2026-08-13 |
| social-media-postcount (Musk/Trump post counts) | blanket bar, `category-bar` | DEEP-2026-08-15 |
| weather (city temperature brackets) | standing no-bet | DEEP-2026-08-26, 2026-09-03 |
| news: "will an institution do/complete X by date", process documented as active, my P(Yes) below the market | `process-shape-bar`. Exception: a dated official fact that maps to No through the clause. Lift when 10 skipped rows have settled with dBrier <= 0 | News-cell process-shape bar RETRO-20260918-1518 |
| Utterance markets, Yes side | Bet only with a quoted base rate from >= 2 comparable prior transcripts (same speaker, same venue class). Otherwise `unvalidated-method` | Utterance gate DEEP-2026-09-12 |
| Touch families (crypto, equity, commodity, Treasury "hit X") | `unvalidated-method`, forecast only indefinitely | Touch-family gate DEEP-2026-09-01/24 |
| Scheduled-close crypto strikes/brackets | forecast only; re-grade at n=8 | RETRO-20260927-1815 |
| Soccer Poisson-derivative totals, MLB cross-line Normal totals | forecast only until n >= 6 independent MATCHES/GAMES (legs of one game count once) | 2026-08-28, 2026-09-05, DEEP-2026-09-15 |
| UMich prelim-to-final revision | forecast only until a sourced revision history (ALFRED) or 4 independent prints beat the mid | RETRO-20260925-1612 |
| Resolver-series bands (e.g. Senate odds prints), box-office self-models | forecast only | RETRO-20260925-2015, 2026-08-18 |
| Same-day index/ETF direction or threshold close | `architecture-mismatch`; quote record-time bid/ask | Fit rubric, RETRO-20260917-2050 |
| Any first-contact method with no settled track record | `unvalidated-method` until its pre-registered bar is met | maiden-voyage discipline |

Ruled OUT for research (no reachable benchmark) unless a primary source
appears: AI/product release DATES from rumours, player trade
destinations, foreign seat-place brackets without 2 agreeing numeric polls
or a near-complete count, Musk net worth (Bloomberg 403), Iranian rial
(Bonbast not verifiable), UFC method-of-victory props without one book
quoting every leg [exploration entries 2026-08-11/18/19].

### 2.7 Families with an active bet rule
- **Parcl home-value brackets** (validated feed): bet only legs where the
  momentum-conditioned sample has ZERO crossings and the unconditional
  rate is <= ~3%. Momentum-dependent legs stay forecast only. A loss on
  any zero-crossing leg, or a resolver value that differs from the API
  history, sends the family to forecast only. Grade each monthly set as
  ONE decision [Parcl, RETRO-20260930-1615].
- **USGS M5.5+ weekly counts** (validated feed): normal floors, needs a
  dated count plus observed pace (§3.4).
- **Canada GDP (StatCan monthly)**: benchmark is the 14-month
  flash-to-first-print error table. Any tilt on top is capped at 0.05 of
  bracket mass [DEEP-2026-09-29].
- **Book-devig**: requires the 0.07 floor, a power devig, a single named
  book's coherent quote, and a fresh line (§3.7). Recreational or political
  book tables need a dated, refreshable source or a check for poll-driven
  PM moves the books missed [b063db346052, 2026-09-17].
- **Cross-market (siblings)**: the implied probabilities must be
  numerically INCOMPATIBLE. Work the arithmetic. A bracket containing the
  threshold proves nothing. Check book depth before reading a sum-check
  [DEEP-2026-08-03, siblings caveat]. A single central-bank futures read
  13 days out is a weak basis. If a second fade of that shape loses, require
  a futures read within 72h [DEEP-2026-09-30 RBA].

### 2.8 Exposure
- One position per market+outcome. The ledger rejects add-ons.
- **Event cap** `max_stake_per_event_usd` ($10). An event is one
  real-world trigger (one game, print, ruling or election night). Legs on
  the same trigger count only if positively correlated. A hedge leg must
  argue its correlation sign in the rationale AT ENTRY [DEEP-2026-09-09].
- Retros grade a correlated pair as ONE decision (net P&L).
- **First-contact family cap:** until a new benchmark family has its first
  settlement, total open stake across the family is <= $10
  [DEEP-2026-09-29].
- Edge classes to pass to `ledger.py --edge-class`: `info-race`,
  `cross-market`, `book-devig`, `other`. An already-immutable fact is
  recorded as `info-race` (the ledger has no fact-final choice); say
  "fact-final" in the rationale and retros grade it as fact-final. If fact-final reaches n >= 5 settled with a
  good record, propose adding it to `real.allowed_edge_classes`
  [DEEP-2026-08-26].

## 3. Estimation method

### 3.1 Order of work
1. Read the resolution criteria and source. Pin the exact threshold,
   basis and date.
2. Form my estimate BEFORE looking hard at the price. Write it down.
3. Find the sharpest external benchmark and reconcile against it.
4. Check the live book (quote.py), then compute the edge at the fill.

### 3.2 What goes into est_prob [DEEP-2026-09-26 general rule]
- When a named mechanical or benchmark read exists (touch.py, a
  bootstrap, a driftless resolver-series model, a devigged book, a
  nowcast, a ladder-implied sd), **est_prob IS that read**.
- A shade enters est_prob only when it comes from a measured print quoted
  in the note (source + number + timestamp). Everything else (recency,
  momentum, "the market thinks otherwise", inferred opens) is written as
  "shade view: X" in the note and NOT recorded. Unmeasured shades are
  0 for 5 so far.
- Exception (a): a liquid sibling (>= $1k) priced < 0.02 or > 0.98
  against my API/bootstrap read, where I cannot name the reason. Record
  est_prob within 0.10 of that mid and write "api view: X" in the note
  [RETRO-20260926-0015].
- Exception (b): official-figure centring for turnout and seat counts
  (§3.6).
- When every qualitative signal in my note points the same way as the
  book's lean, I do not record a number on the other side of the mid
  because of one scrape of unknown freshness. Centre on the mid and record
  `market-agrees` [RETRO-20260921-1405].
- A model that prints a RANGE across defensible inputs, with the price
  inside that range, means no edge. A bet needs the price outside the
  WHOLE range by >= min_edge, and the note quotes the range
  [RETRO-20260921-0633]. A market declined as `unvalidated-method` stays
  declined on that method until a settled row validates it. A smaller edge
  days later is not new evidence.

### 3.3 Sources and benchmarks
- Count sources by primary ORIGIN, not by search hits. Five pages
  restating one leaderboard are one source [DEEP-2026-09-02].
- Quote the exact bid/ask about to be passed to forecast.py/ledger.py in
  the note. A sharp move since the last check is a signal to re-research
  [RETRO-20260904-2215].
- Kalshi (`strategy/tools/kalshi.py`, direct API works) and CME FedWatch
  are benchmarks when contracts settle on the same terms. Check both
  sides' bid/ask. Two order books disagreeing about the same unknown is a
  spread, not an edge. It needs a mechanical anchor on one side
  [DEEP-2026-08-08]. Event ticker vs series ticker: `--event-ticker
  KXU3-26JUL`.
- Manifold is play money (reference only). Metaculus API is 403.
- Devig with `strategy/tools/devig.py`. Use the POWER number for any side
  below ~0.60 [DEEP-2026-07-31].
- Line freshness: if any book already matches PM, assume PM is current
  and I saw a stale line [DEEP-2026-07-31].
- Bracket sets after a release: once `umaResolutionStatus` is "proposed",
  sibling brackets pin the print (one leg near 1, the rest near 0). An
  immediate post-release CLOB read before that is NOT corroboration
  [RETRO-20260911-1244].
- Same-day deadline with a live rumour: "nothing announced yet" is weak
  evidence for No. Re-check near the actual cutoff [2026-09-01 Mythos].
- Fed chair presser opening statements carry a staff PCE estimate (named,
  dated, primary). Its hit rate is still unsourced [2026-09-17].
- Cleveland Fed nowcast is reachable from the operator runner. Its RMSE is
  not sourced yet, so CPI rows stay outside the carve-out [2026-09-07].

### 3.4 Counts, prices and models
- **Cumulative counts** (views, downloads, signatures): need a DATED count
  plus an OBSERVED pace (two dated reads of the same source >= ~3h apart).
  Without both, no forecast (`no-anchor`). Market re-pricing is not an
  anchor [DEEP-2026-09-04, RETRO-20260926-2015]. RYD API lags YouTube by
  ~19k views, so it counts as a dated read.
- **Post counts** (xtracker.polymarket.com API): compute pace yourself as
  cumulative / actual elapsed days. Never use a plain Gaussian. est_prob =
  the UNSHADED bootstrap (aligned windows when n >= 20)
  [2026-08-13/14, RETRO-20260925-1812].
- **Weather (forecast only):** same-day rows condition on the observed
  partial-day max with sd 0.6C after local noon. If that fetch fails, no
  forecast. Next-day rows use sd 1.2C [2026-09-03].
- **Commodity moving day:** when the day's move already exceeds ~2
  window-sds, scale the remaining-session sd from the larger of the
  window sd and the day's realized range. Prefer superseding close to the
  settle [RETRO-20260922-0015]. Conflict-linked commodities jump on
  headlines, so "range so far" is not a bound [DEEP-2026-08-06].
- **Commodity touch ladders:** read the Active Month roll clause before
  the spot price. Use a sourced vol (e.g. OVX via FRED) [2026-09-17].
- **Touch rows:** `touch.py` at a measured realized vol or a
  market-implied vol from an adjacent rung, with a named dated source.
  Guessed vol is retired. Single stocks: from the last close or a quoted
  premarket print, never an index-beta-inferred open
  [DEEP-2026-09-01, RETRO-20260925-2213].
- **Treasury touch** with <= 5 prints left: the RAW bootstrap (drift
  kept), updated for the overnight futures move [RETRO-20260928-2215].
- **Scheduled-close crypto:** use the ladder-implied sd unless a dated
  catalyst inside the window justifies wider. Realized vol goes in the
  note [RETRO-20260927-1815].
- **AI/product release dates:** without a primary source (official post,
  docs page, named exec) est_prob = the ladder mid. A leak lean goes in
  the note. Only a POSITIVE finding moves it [RETRO-20260928-2015].
- **Resolver-series bands:** driftless random walk with measured sd.
  Drift goes in the note [RETRO-20260925-2015].

### 3.5 Econ prints
- Earnings: check GAAP vs non-GAAP first. No GAAP consensus found means
  `benchmark-unreachable`. Consensus clearing a threshold priced >= ~0.80
  is not an edge [2026-08-04/06].
- PPI YoY: base-effect chain YoY_next ≈ YoY_now × (1+MoM_cons) /
  (1+MoM_same_month_last_year_actual) − 1. Needs the actual
  last-year MoM [2026-08-11, won].
- PMI: use only numbers explicitly labelled ISM (not S&P Global/Markit)
  and tied to the release the market cites [2026-08-23].
- JOLTS: record the LinkUp model centre. No tilt past consensus on soft
  signals [DEEP-2026-09-30].
- Econ ladders: record every bracket whose book I read, centre included.
  A nowcast-centred mean may shift toward the ladder's shape. A recalled
  sd never substitutes for the market's implied sd [RETRO-20260911-1615].

### 3.6 Elections (vote share, seats, turnout)
- Default sd **3.0 points (state/regional), 2.5 (national)**. A smaller sd
  must cite settled rows. Agreement between polls is never the sd. Refit at
  n >= 12 draws [RETRO-20260921-1625/1730].
- **Centre stress test** before any bracket bet: recompute with the mean
  at the latest poll and one point further along the trend. The edge must
  hold at both. An sd sweep is not a robustness check.
- **No bet against the trend:** no bet that needs a party to reverse its
  trailing poll trend unless a sourced event explains it.
- A centre correction for party X applies to every bracket on party X in
  the same event, in the same commit. Insurgent/established pairs on the
  same side tend to miss in offsetting directions [2026-09-18/21].
- Near-boundary bracket (mean within 0.5pt of the edge): no-edge unless the
  centre has a sourced shift.
- Managed elections: the state pollster understates the ruling party.
  Centre at forecast-top plus the prior cycle's miss. Without a sourced
  prior miss, the book is the centre (`market-agrees`). Turnout centres at
  the prior official figure plus the miss. Online-vote front-loading
  carries the first print forward [RETRO-20260921-1120, 0925-1421]. Check
  that a prior cycle's exception regions are on THIS cycle's roster
  [RETRO-20260925-1432].
- A third-party poll-aggregation seat model counts as mechanical (adopt
  it, no blend) [RETRO-20260907-1006].
- Use a poll aggregator (predictionedge.com, RealClearPolling) before
  calling polls contradictory [2026-08-09].
- Counting (not yet a rule): consolidation squeezes small parties on the
  leader's side. Run the stress test with their mean 2 points DOWN.

### 3.7 Sports
- Event-time check before research: pin the actual start time from the
  description or one search. `end_date` is not the match time (tennis
  draws). Never research or bet a started or unverifiable game
  [DEEP-2026-08-04].
- Esports and all single-game markets: pre-match only.
- MLB/WNBA `-1.5` spreads (home or away slug): check the moneyline devig
  first. If the named team is not the favourite, log
  `benchmark-unreachable` without spending a devig call
  [2026-09-02, 2026-09-30].
- Series games: confirm the date and probable starters match before using
  any line [2026-08-08].
- Never mix books ("best odds across bookmakers"). Devig only one named
  book's full quote [2026-08-05].
- WebSearch esports "odds" are often Polymarket's own price echoed. Use
  only a snippet that names a real book with a different number.

### 3.8 Utterance markets
- Count ONLY the named speaker's lines, per transcript, never pooled
  [2026-09-16].
- Sweep constituent words as well as the exact phrase (disfluent
  transcripts) [2026-09-15].
- N+ count markets: scale each analogue's count to the expected speech
  length. If the nearest analogue sits at N or within 1, cap at 0.50 unless
  a scheduled hook raises the rate [RETRO-20260924-1729].
- Words that became topical recently: count only post-topic analogues and
  state n [RETRO-20260925-0748].

### 3.9 Search-result traps (treat as no benchmark)
- The summarizer echoes an assumption in my query back as a fact. Phrase
  odds queries neutrally.
- Prior-year actuals surface for a recurring release. Check the publish
  date of every result.
- Contradictory sources: skip. Do not average.
- A stated resolution source that is unreadable (JS page, 403) with no
  verifiable proxy: `benchmark-unreachable`.
- Forebet/oddsportal/oddspedia 403 from datacenters. WebSearch works.
  Re-verify reachability each cycle rather than assuming yesterday's block.

## 4. Research selection

- **Coverage precondition:** spend ONE search establishing that a sharp
  benchmark exists before deeper research. If none, drop it
  [OPERATOR EDIT 2026-08-03].
- **Fit score** 0-5, one point each: mechanical resolution, benchmark
  reachable THIS cycle, edge persists hours-days, bounded resolution tail,
  research cost small vs payout. <= 2 is exploration territory. Log it in
  the funnel [Fit rubric DEEP-2026-08-05].
- **Priority:** (1) validated-feed families and mechanical econ prints with
  a reachable benchmark, (2) cross-market sibling arithmetic, (3) fact-final
  checks on scheduled events, (4) everything else [DEEP-2026-08-18
  decision implications, DEEP-2026-09-22, §1]. Families that
  `edge_audit.py` shows as worse than market (ai, earnings,
  market-microstructure, plus weather/news/social by sign) get research
  time only with a mechanical anchor [DEEP-2026-09-16 allocation rule].
- **Scheduled-release triage:** every FULL cycle names the scheduled
  prints in the pool and assigns each one: research now, defer to a named
  cycle, or skip with a reason [DEEP-2026-08-05].
- **Sibling census:** group the scan by `event_id` and log
  `sibling_groups: N` in the funnel. Run the census BEFORE the first web
  search on a bracketed candidate, and read `my_open_forecasts` on every
  sibling. A sibling researched < ~6h ago with no new fact: record from
  that research, do not re-research [DEEP-2026-08-22, 2026-09-19].
- **Validated-feed sweep:** each FULL cycle checks ONE family from the list
  (Parcl home value, USGS M5.5+ weekly, IMF PortWatch chokepoint 7-day MA)
  outside the escalation slots, rotating, and records every leg read. A
  family joins only after a resolution-match check. **Retire the sweep** if
  7 days (test date 2026-10-06) produce no leg with ask-edge >= min_edge
  outside Parcl [DEEP-2026-09-29, 2026-09-30].
- **Caps per FULL cycle:** at most ONE slot for fact-finality-gated
  timeline-rumour questions (sibling ladders share it)
  [DEEP-2026-09-02]. At most ONE social-media-postcount event family,
  unless grading a pre-registered check [DEEP-2026-09-26].
- **Odds API** (`core/odds.py`, ~10-12 credits/day): `sports` once per
  cycle. Spend `odds`/`scores` only on pre-qualified candidates. At most ONE
  devig confirmation sweep per WEEK per channel (not per league). Grep the
  cycle log for the week's sweep BEFORE any odds call [DEEP-2026-08-13/21/22].
- **Re-research cooldown:** a no-edge or no-benchmark conclusion holds
  ~2h unless something new happens. After two re-checks that find no new
  information, close the candidate until resolution [DEEP-2026-08-04,
  DEEP-2026-08-13].
- **Exploration budget:** ~1 candidate per FULL cycle testing a NAMED,
  not yet characterized property. Prefer categories where an external
  benchmark plausibly exists over ones that can only end "self-model,
  vetoed". A new league through known machinery does not qualify
  [DEEP-2026-08-05/10/17].
- Live book first for near-resolution news: stale scan mids hide asks
  already at 0.98 [2026-07-30].

## 5. Recording: forecasts, funnel, taxonomy

- **Record every researched candidate** with a concrete probability
  (`core/forecast.py record`), bets and declines alike. Never invent an
  estimate. No estimate formed means no forecast row.
- Before the call, state the target outcome string in the note. After
  it, check that the returned `delta_vs_mid` points the intended way. Use
  `--confirm-extreme` for |est - mid| > 0.40 only after re-checking the
  outcome label [2026-08-15 trap, guard 2026-08-24].
- `--supersede` when a re-check moves est by >= 0.05 or changes the skip
  reason. If research on one market shows an open forecast on ANOTHER
  market is stale, record that superseding row in the same cycle
  [2026-08-24, 2026-09-30].
- The category tag is immutable. Check it before recording. A superseding
  row copies the superseded row's tag. View-count brackets are
  `video-views`. Post counts are `social-media-postcount`
  [DEEP-2026-09-20/27/30].
- **Skip-reason taxonomy:**
  - `no-edge`: the edge itself failed the floor.
  - `market-agrees`: my estimate sits on the price.
  - `outside-view-veto`: claimed edge > 0.10, estimate distrusted.
  - `wide-spread-veto`: the edge cleared the floor and only max_spread
    blocked it. If both this and the veto apply, use
    `outside-view-veto`.
  - `category-bar`, `process-shape-bar`: a §2.6 bar is the reason
    (also below 0.10).
  - `unvalidated-method`: a first-contact method, or one gated in §2.6.
  - `architecture-mismatch`: a speed race or same-day index direction.
  - `ambiguous-resolution`.
  - Estimate-free (NO forecast row): `benchmark-unreachable`,
    `census-consistent`, `no-anchor`, `budget-exhausted`.
  [DEEP-2026-08-11/13/14/25, RETRO-20260908-1612]
- **Funnel line:** every tick that records a forecast, and every FULL
  cycle (`"researched": []` if none), appends one line to
  `strategy/funnel.jsonl` IN THE SAME COMMIT. Fields: cycle, strategy_rev,
  `pool_by_query`, `pool_total`, `screened`, `escalated`,
  `screener_batches`, `sibling_groups`, and researched[] (market_id,
  category, fit_score, skip_reason, forecast_id). Before committing, check
  that `tail -1 strategy/funnel.jsonl` carries this cycle's timestamp
  [Coverage weld DEEP-2026-08-20, DEEP-2026-09-30].
- **Run `python3 strategy/tools/reconcile.py`** before the commit of any
  tick that recorded a forecast. It must print OK. Quote its literal line
  (`OK: funnel<->forecast coverage reconciles over last 24h`) in the cycle
  log. On FAIL, repair it in the same commit [DEEP-2026-08-21/22].
- **Watch item** (schedule.json) in the same commit when a batch settles
  more than ~24h out, feeds a veto ledger, or carries a reading rule
  [DEEP-2026-08-18].
- Durable lessons go in this playbook, never only in schedule.json reason
  fields [DEEP-2026-08-05].

## 6. Every tick: settle, grade, monitor, pace

- **Grade on the tick that settles.** If resolve.py settles ANYTHING
  (bets or forecasts) on any tick (FULL, LIGHT or TRIGGERED), that tick
  writes the retro [schedule.json rule, DEEP-2026-09-02/30].
- Settled `outside-view-veto` / `wide-spread-veto` rows are graded in the
  RETRO file, with `python3 core/counterfactual.py ledger` as the
  authoritative arithmetic (side, realizable ask, spread). Quote veto
  dBrier with AND without refusal rows (no ask). The old hand table in
  playbook-reference.md is frozen. Do not append to it
  [DEEP-2026-09-30, DEEP-2026-09-27].
- `brier_delta` sign: NEGATIVE = I beat the market. Copy numbers from
  score.py, never recompute the sign [DEEP-2026-08-21].
- **Open-position monitor line** in every cycle log: for each open
  position past its end date, log id, entry, live bid/ask, and the signed
  move `(live mark of the held side − entry)`. Otherwise log
  "open-position monitor: none past end date". Call out any adverse move
  >= 0.10. A held token near 0 is ALWAYS adverse [DEEP-2026-08-02/03/31].
- Held-position re-checks: a re-check with no NEW qualifying fact should
  move toward the market. When a position with >= 3 re-checks settles,
  log `own-closer k of m` (§8) [DEEP-2026-09-16].
- **Pacing (schedule.json):** defer a FULL only when every candidate is
  either concluded within ~2h with nothing new, or gated on an unreachable
  source. Set `next_full_cycle_after` to the next event boundary, <= 3h
  out, never past a known event start. Every FULL advances the pointer.
  Run a FULL if fewer than `min_full_cycles_per_day` ran in 24h. Count
  them with the exact awk command in `schedule.json` `notes`, and copy the
  number it prints [DEEP-2026-08-04/06/10/26].
- **Screener budget:** 150 batches per UTC day, shared by both runners (15
  per screened FULL). Space screened FULLs >= 2h apart unless a dated
  catalyst needs one. Keep >= 45 batches unspent until 16:00Z
  [DEEP-2026-09-24].
- **Watch items:** update checkpoints IN PLACE, ~2,000-char cap per item.
  Settled and graded items move verbatim to `strategy/watch-archive.md`
  [DEEP-2026-09-14/28].
- **Git at step 0:** run `git branch -vv`. If HEAD is detached, reattach
  before any work (`git checkout -B main origin/main` only when the stale
  ref is an ancestor, checked with `git merge-base --is-ancestor`)
  [2026-08-20 trap].
- Fetch books into `work/` (gitignored), not `/tmp`.

## 7. Mech second opinions (operator-machine cycles only, CYCLE.md 5a)

- Send off-chain requests STRICTLY one at a time and wait for each
  delivery. After ONE 401 nonce rejection, go straight to
  `legacy_on_chain=true`. Retry a 503 once with a new request_id
  [2026-09-07].
- The first ~140 characters of the prompt carry the distinguishing noun
  AND the date. One `?` sentence, no price [2026-09-21].
- For interpretive clause questions, send the clause and question only.
  Facts I supply get echoed back as confidence [2026-09-09].
- Before crediting a far-off market-aware p_yes, read the serper top
  results. A Polymarket event page (price leak) or a same-month prior-year
  date marks the delivery as contaminated. An R1-vs-GPT gap is a model
  comparison only when the top-5 results match [2026-09-07, 2026-09-21].
- R1 protocol: every candidate with the R1 pair also gets the GPT-4.1
  market-aware baseline (same mech, sent last). Each UTC day, >= 3
  researchable markets settling within 5 days get the full triple. Report
  researchable and price markets as separate groups [operator note
  2026-09-21].

## 8. Open pre-registrations and counters (update the number in place)

| Item | Current | Fires when | Tag |
|---|---|---|---|
| Outside-view-veto relaxation fork | NOT MET (11th, 2026-09-26) | 3 gates, §2.2 | DEEP-2026-09-08 |
| Blend bar (market-prior blending) | NOT met: fails leave-one-out (edge_audit 2026-10-01) | w_opt <= 0.80, improvement >= 0.002 surviving LOO, 2 passes | proposals 2026-09-11 |
| Mechanical-econ carve-out kill switch | count settled carve-out events/bets in retros | 4 events or 6 bets | DEEP-2026-08-28 |
| fact-final → real allowed classes | 1W/0L (5fbf676cfd7f) | n >= 5 settled | DEEP-2026-08-26 |
| News process-shape bar | count skipped rows settled | 10 settled, dBrier <= 0 → lift | RETRO-20260918-1518 |
| Utterance Yes-gate review | fresh count from 2026-09-17 | 5 qualifying rows | DEEP-2026-09-17 |
| Utterance No-side vetoed rows | 3W/1L, +$8.20, ONE speaker-venue-day | 5 rows over >= 3 days incl. a non-ceremonial venue | DEEP-2026-09-25 |
| Unmeasured shades | 0 for 5 events | >= 8 events → re-grade §3.2 | DEEP-2026-09-26 |
| Held-position re-check bias | Iran 0ed1d77858d7: own-closer 0 of 6 | 3 positions in minority → convergence rule | DEEP-2026-09-16 |
| AI release-date anchoring | ~2 launch events | n=8 distinct markets | DEEP-2026-09-29 |
| Treasury touch drift | 3 markets, one trending month | Oct ladder, split by trend; revert to mid if raw loses in a flat month | DEEP-2026-09-29 |
| Soccer Poisson derivatives | 3 matches (2 favourable) | 6 independent matches | 2026-09-05 |
| MLB cross-line totals | 1 game (model-high) | 6 independent games | DEEP-2026-09-15 |
| Scheduled-close crypto ladder sd | 3 rows | n=8 | RETRO-20260927-1815 |
| Unexplained price move vs public-record read | 1-for-2 | 3rd instance → rule | DEEP-2026-09-30 |
| Validated-feed sweep retirement | test 2026-10-06 | no leg >= min_edge outside Parcl in 7 days | DEEP-2026-09-29 |
| Parcl October set | Sep set WON (1 decision) | any zero-crossing loss → forecast only | RETRO-20260930-1615 |
| PortWatch "<25" low-side skew | open | grade at settlement | 2026-09-30 |
| Countable-metric carve-out | one event only (GTA VI) | >= 3 independent events (operator ask) | DEEP-2026-09-05 |
