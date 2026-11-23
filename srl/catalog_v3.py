"""v3 held-out phrasings: four new test phrasings per required skill, written for the v3 study with Claude Code after
the v2 results were known (so v2's test2 queries can serve as v3's dev split). None of them repeats a v1 or v2
phrasing; tests/test_v3.py checks that and caps the character n-gram similarity to any earlier phrasing.
"{co}" is filled with a company name, as in v1 and v2.
"""

from __future__ import annotations

PHRASES_TEST3 = {
    "trailing-pe": [
        "At the current share price, what is {co}'s P/E against the sum of its last four quarters of reported EPS?",
        "Price {co} against twelve months of actual, already-reported earnings.",
        "What earnings multiple is {co} on if I use its reported results rather than estimates?",
        "Take {co}'s last four quarterly net profits and tell me the trailing earnings multiple at today's price.",
    ],
    "price-to-book": [
        "How many times its net asset value per share does {co}'s stock price sit at?",
        "Compare {co}'s market cap with the parent shareholders' equity on its latest balance sheet.",
        "Work out the price-to-book multiple for {co} from its most recent quarterly filing.",
        "Does {co} trade at a discount to its book equity per share?",
    ],
    "ev-ebitda": [
        "Add {co}'s net debt and non-controlling interests to its market value and divide by trailing EBITDA.",
        "On an enterprise value basis, how many years of EBITDA is {co} priced at?",
        "What's the EV-to-EBITDA ratio for {co} using the last four quarters?",
        "If lease obligations count as borrowings, what EV/EBITDA does {co} trade on?",
    ],
    "wacc-estimator": [
        "Combine {co}'s CAPM cost of equity with its after-tax borrowing rate into one discount rate.",
        "What hurdle rate does {co}'s capital structure imply, weighting equity and debt at market value?",
        "Put together a WACC for {co} using the 10-year government bond yield and its beta.",
        "Which discount rate fits {co} when equity and debt are weighted by market value?",
    ],
    "dividend-yield-payout": [
        "If I buy {co} at today's price, what cash yield do I get from its annual dividend?",
        "Divide {co}'s total dividends by its net income for last year.",
        "What fraction of earnings did {co} distribute, and what's the yield at the current price?",
        "Work out the yield on {co}'s declared dividend per share at today's close.",
    ],
    "rights-offering-summary": [
        "{co} is raising money by issuing new shares; at what discount, and how many new shares?",
        "Explain {co}'s rights issue: allocation method, offer price and use of funds.",
        "How much fresh capital is {co} raising through its share issue, and at what discount?",
        "Go through {co}'s paid-in capital increase filing and summarize the dilution for current holders.",
    ],
    "convertible-bond-summary": [
        "Pull the coupon, yield to maturity and conversion price from {co}'s CB issuance filing.",
        "What refixing clause and put dates come with {co}'s freshly issued convertible bonds?",
        "Lay out the terms of the convertible bonds {co} decided to issue this month.",
        "What share of {co}'s stock would its new CB issue represent after conversion?",
    ],
    "operating-margin-trend": [
        "For the past twelve quarters, what was {co}'s operating profit divided by revenue?",
        "Show how {co}'s operating margin has moved each quarter since 2022.",
        "Is {co}'s quarterly operating margin recovering or still sliding?",
        "Give me a quarterly series of {co}'s operating margin and flag the turning points.",
    ],
    "interest-coverage": [
        "Divide {co}'s operating income by its interest expense for each of the past three years.",
        "Is {co} earning enough operating profit to pay its interest comfortably?",
        "Show {co}'s interest coverage multiple and whether it dipped under one.",
        "How many times does {co}'s operating profit exceed its finance costs?",
    ],
    "free-cash-flow": [
        "Subtract {co}'s capital spending from its cash from operations for the last three years.",
        "Was {co}'s free cash flow positive in each of the past three fiscal years?",
        "Show {co}'s FCF trend from the reported cash flow statement.",
        "How much cash did {co} have left after investing in property and intangibles last year?",
    ],
    "moving-average-signals": [
        "Is {co}'s 20-day average now above or below its 60-day average?",
        "Has {co} formed a dead cross between its short and medium moving averages lately?",
        "Check {co}'s price against its 20-, 60- and 120-day averages and list any recent crosses.",
        "When was {co}'s last golden cross on the daily chart?",
    ],
    "stock-beta": [
        "Using two years of weekly data, how much does {co} move with the KOSPI?",
        "Give me {co}'s beta coefficient versus the KOSPI and the fit of the regression.",
        "Does {co} amplify or dampen market swings? Estimate its beta.",
        "Run {co}'s weekly returns against the index and report beta and R-squared.",
    ],
    "portfolio-rebalancing": [
        "Here are my current holdings, including {co}, and my target weights; what should I buy and sell?",
        "Bring my KRX portfolio back to its targets in whole shares, leaving about 1% in cash.",
        "My position in {co} has grown too large; produce trades to rebalance all holdings to target.",
        "Calculate the buy and sell quantities to return my account to equal weights.",
    ],
    "bond-ytm": [
        "Suppose a KTB with a 2.5% coupon trades at 97.9; what is its yield to maturity?",
        "What YTM does {co}'s bond maturing in 2028 offer at a clean price of 9,910 won?",
        "Back out the yield to maturity from this corporate bond's price and coupon dates.",
        "Find the yield that equates {co}'s bond price with its remaining cash flows.",
    ],
    "major-shareholder-changes": [
        "Has anyone newly reported a 5% stake in {co} in the last three months?",
        "Which large holders of {co} changed their stake or holding purpose according to 5% filings?",
        "Summarize the 5% rule reports filed on {co} this year.",
        "Did an activist fund disclose a 5%+ position in {co} with a management-participation purpose?",
    ],
    "foreign-investor-flows": [
        "Over the past 20 sessions, have foreign investors bought or sold more {co} stock?",
        "Show net buying by foreigners and institutions in {co} day by day.",
        "Is {co} seeing sustained foreign inflows this quarter?",
        "How many shares of {co} did foreigners net sell last week?",
    ],
    "peer-comparison-table": [
        "Set {co} against its listed rivals on valuation multiples and ROE, with the peer median.",
        "Is {co} cheap compared with the peers I name, on P/E and EV/EBITDA?",
        "Build a peer table for {co}: market cap, P/E, P/B, EV/EBITDA and ROE.",
        "How does {co} rank among its domestic competitors on valuation?",
    ],
    "fx-translation": [
        "Express {co}'s won-based income statement and balance sheet in dollars.",
        "Which exchange rates should I use to put {co}'s results into USD, and what do they come to?",
        "Show {co}'s last annual financials converted to US dollars.",
        "Convert {co}'s sales, operating profit and assets into dollars for a US peer comparison.",
    ],
    "dart-consolidated-statements": [
        "Fetch the group-level statements in {co}'s most recent annual report through DART.",
        "Save {co}'s consolidated income statement and balance sheet from the DART API as CSV files.",
        "Get the consolidated cash flow statement of {co} for the most recent quarter from DART.",
        "I want all three consolidated statements for {co} for 2024, straight from DART.",
    ],
    "earnings-surprise": [
        "How far above or below consensus was {co}'s operating profit last quarter?",
        "Did {co}'s quarterly revenue top analysts' expectations?",
        "Compare {co}'s actual operating profit with the street forecast and compute the surprise.",
        "Was {co}'s latest result a beat or a miss against consensus estimates?",
    ],
    "pe-band-chart": [
        "Draw {co}'s P/E band over five years to see where its price sits today.",
        "Chart {co}'s share price with bands at fixed multiples of trailing EPS.",
        "Over the last five years, has {co} ever traded above the 20x line on its P/E band?",
        "Make a monthly P/E band for {co} with lines from 5x to 25x.",
    ],
    "ex-dividend-calendar": [
        "What is the last day to buy {co} and still get its next dividend?",
        "Find {co}'s dividend record date and payment date after its board set them.",
        "When does {co} go ex-dividend this year?",
        "List the ex-date, record date and pay date for {co}'s upcoming dividend.",
    ],
    "bond-duration": [
        "What is the duration of {co}'s 5-year bond, and how much would its price drop if yields rose 1%?",
        "Compute modified duration and convexity for a KTB maturing in 2032.",
        "How much interest rate risk does this 4% coupon bond carry? Give me duration and convexity.",
        "Estimate how {co}'s bond price changes for a 50bp rate move using duration.",
    ],
    "fx-sensitivity": [
        "Based on its currency risk note, how much would a stronger dollar lift {co}'s pre-tax profit?",
        "Quantify {co}'s exposure to the won-dollar rate from its financial risk disclosure.",
        "How would a 10% move in KRW/USD change {co}'s profit before tax?",
        "What does the sensitivity table in {co}'s annual report say about exchange rate risk?",
    ],
    "dupont-roe": [
        "Explain {co}'s ROE with a DuPont split into margin, turnover and leverage.",
        "Over five years, has {co}'s return on equity come from margins or leverage?",
        "Decompose {co}'s ROE trend using the three-step DuPont formula.",
        "Which part of the DuPont identity drove {co}'s falling ROE?",
    ],
    "dart-segment-revenue": [
        "Using the segment note, split {co}'s revenue and operating profit by division.",
        "Which business unit of {co} generated the most revenue last year?",
        "Extract {co}'s segment figures from its DART report and tie them to consolidated revenue.",
        "Give me {co}'s sales and operating income by reportable segment.",
    ],
    "debt-maturity-profile": [
        "How much of {co}'s debt falls due next year versus its cash on hand?",
        "Show {co}'s loans and bonds grouped by the year they mature.",
        "Build {co}'s debt maturity schedule from the borrowings note.",
        "When are {co}'s biggest debt repayments due over the coming five years?",
    ],
    "historical-volatility": [
        "What has {co}'s annualized volatility been over the last 252 trading days?",
        "Compute {co}'s 20-day and 60-day historical volatility from log returns.",
        "Is {co}'s stock more volatile this month than its one-year average?",
        "Give me {co}'s realized volatility, annualized, for three lookback windows.",
    ],
    "dcf-valuation": [
        "What equity value per share does a five-year DCF give for {co}?",
        "Forecast {co}'s unlevered free cash flow for five years and discount it at its WACC.",
        "Do a discounted cash flow valuation of {co} with a terminal growth assumption.",
        "Estimate {co}'s fair value from projected free cash flows and a terminal value.",
    ],
    "preliminary-earnings-reader": [
        "From {co}'s preliminary earnings filing, compute revenue and operating profit growth year on year and quarter on quarter.",
        "{co} published preliminary results today; summarize the changes versus last year.",
        "Did {co} return to profit according to its preliminary earnings announcement?",
        "Pull the numbers from {co}'s preliminary results disclosure and show the YoY and QoQ changes.",
    ],
    "insider-trading-filings": [
        "Did any director or 10% owner of {co} disclose selling stock in the past year?",
        "List the stock trades by {co}'s executives from ownership change reports.",
        "Was there insider selling at {co} just before its last results?",
        "Net out insider buying and selling at {co} over the past three months.",
    ],
    "gross-margin-bridge": [
        "Decompose the change in {co}'s gross margin into price, volume and cost effects.",
        "Why did {co}'s gross margin shrink from last year? Split it into its drivers.",
        "Build a bridge of {co}'s gross margin from 2023 to 2024.",
        "How much of {co}'s gross margin gain came from higher selling prices?",
    ],
    "cash-conversion-cycle": [
        "In days, how quickly does {co}'s working capital cycle turn stock and customer credit back into cash?",
        "Track {co}'s DSO, DIO and DPO over the last eight quarters.",
        "Has {co}'s cash conversion cycle lengthened compared with a year ago?",
        "Compute {co}'s receivable, inventory and payable days and the resulting cash cycle.",
    ],
    "value-at-risk": [
        "What is the 99% one-day VaR in won for my portfolio including {co}?",
        "Use historical simulation to estimate my holdings' one-day value at risk.",
        "At 95% confidence, what's the most my stock portfolio could lose tomorrow?",
        "Compute the historical VaR of my five-stock portfolio with 500 days of data.",
    ],
    "credit-rating-history": [
        "How have Korean agencies' ratings on {co} changed over the past five years?",
        "List every rating and outlook change on {co} by KIS, NICE and Korea Ratings.",
        "Is there a split rating on {co} among the domestic agencies?",
        "When was {co}'s credit rating last raised or lowered?",
    ],
    "treasury-share-buyback": [
        "What buyback programs has {co} announced, and how big are they relative to market cap?",
        "Summarize {co}'s latest treasury stock purchase decision: amount, period and method.",
        "Did {co} actually complete its announced share repurchase?",
        "What own-share purchases has {co}'s board approved since 2024?",
    ],
    "cb-overhang-tracker": [
        "Tally the shares that {co}'s still-unconverted CBs could turn into.",
        "List {co}'s unconverted CB series with their current conversion prices.",
        "If every outstanding CB of {co} converted today, how many new shares would appear?",
        "What is the remaining convertible bond overhang on {co} as a share of its stock?",
    ],
    "risk-contribution": [
        "How much of my portfolio's total risk does each holding, including {co}, account for?",
        "Compute each stock's marginal contribution to my portfolio's volatility.",
        "Does {co} contribute more risk to my portfolio than its weight suggests?",
        "Split my portfolio volatility into percentage contributions by position.",
    ],
    "short-selling-balance": [
        "How big is the outstanding short position in {co}, in shares and as a percent of shares outstanding?",
        "Is short interest in {co} building up over the past month?",
        "Give me {co}'s daily short-selling balance for the last 20 trading days.",
        "Track the short balance on {co} in won.",
    ],
    "ipo-lockup-expiry": [
        "Which recent IPOs have lock-up expiries coming up, and how many shares unlock?",
        "When will {co}'s post-IPO lock-up end, and what portion of shares is released?",
        "List KOSDAQ listings from this year whose lock-ups end next month.",
        "Can {co}'s pre-IPO investors sell yet, or is the lock-up still in force?",
    ],
}
