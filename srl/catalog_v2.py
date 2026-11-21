"""v2 held-out phrasings: four new test phrasings per required skill, written for the v2 study with Claude Code after
the v1 results were known (so v1's dev and test queries can serve as v2's dev split). None of them repeats a v1
phrasing; tests/test_v2.py checks that. "{co}" is filled with a company name, as in v1.
"""

from __future__ import annotations

PHRASES_TEST2 = {
    "trailing-pe": [
        "Using {co}'s reported net profit for the past four quarters, what P/E does today's price imply?",
        "Give me {co}'s price-to-earnings ratio on a trailing twelve-month basis from its filings.",
        "How many times its last year of actual EPS is {co} priced at today?",
        "Recompute {co}'s TTM P/E after its latest quarterly report came out.",
    ],
    "price-to-book": [
        "What multiple of book value per share does {co} trade at today?",
        "Using the newest quarterly balance sheet, how does {co}'s share price compare with its equity per share?",
        "Calculate {co}'s P/B ratio as of yesterday's close.",
        "Is {co} valued above 1x book on its latest consolidated equity?",
    ],
    "ev-ebitda": [
        "Including net debt and minority interests, what is {co} worth relative to its last-twelve-month EBITDA?",
        "Give me {co}'s enterprise value divided by trailing EBITDA.",
        "How does {co}'s EV compare with its EBITDA over the past four quarters?",
        "Compute {co}'s EV/EBITDA multiple with lease liabilities in net debt.",
    ],
    "wacc-estimator": [
        "What blended cost of equity and debt should I discount {co}'s cash flows at?",
        "Work out {co}'s weighted average cost of capital using a KOSPI beta and the 10-year KTB yield.",
        "Estimate {co}'s WACC with market-value weights and an after-tax cost of debt.",
        "I need the discount rate for valuing {co}: combine its cost of equity and borrowing cost.",
    ],
    "dividend-yield-payout": [
        "What percentage of last year's profit did {co} hand back as cash dividends?",
        "Calculate {co}'s dividend yield on today's price from its declared DPS.",
        "Give me {co}'s payout ratio and current dividend yield.",
        "How generous is {co}'s dividend relative to its share price and earnings?",
    ],
    "rights-offering-summary": [
        "{co} filed a paid-in capital increase; summarize the issue price, discount and new share count.",
        "What will {co} spend the proceeds of its rights offering on, and how much does it raise?",
        "How much will the new share issue dilute existing shareholders of {co}?",
        "Break down {co}'s capital increase decision: allocation method, size and pricing.",
    ],
    "convertible-bond-summary": [
        "Summarize the terms of the CB {co} just issued: coupon, maturity and conversion price.",
        "What is the refixing floor on {co}'s new convertible bonds?",
        "How many shares could {co}'s latest convertible bond issue convert into?",
        "When can holders of {co}'s new CBs put them back, and at what yield?",
    ],
    "operating-margin-trend": [
        "Track {co}'s operating profit margin quarter by quarter for three years.",
        "Is {co}'s operating margin trending up or down since 2023?",
        "Show {co}'s operating profit as a percent of sales for each of the last 12 quarters.",
        "Find the quarters where {co}'s operating margin changed direction.",
    ],
    "interest-coverage": [
        "How comfortably does {co}'s EBIT cover its interest expense?",
        "Give me {co}'s operating profit to interest expense ratio for the last three years.",
        "Did {co}'s interest coverage fall below 1x in any recent year?",
        "Check {co}'s ability to service its debt interest from operating profit.",
    ],
    "free-cash-flow": [
        "What was {co}'s operating cash flow minus capital spending in each of the past three years?",
        "Compute {co}'s historical free cash flow from the cash flow statement.",
        "Has {co} generated positive free cash flow after capex recently?",
        "Show me {co}'s FCF, operating cash flow and capex side by side for three years.",
    ],
    "moving-average-signals": [
        "Has {co} had a golden cross between its 20-day and 60-day averages this year?",
        "Where is {co} trading relative to its 20, 60 and 120-day moving averages?",
        "Flag any dead cross in {co}'s chart over the last twelve months.",
        "Is {co} still above its 120-day moving average line?",
    ],
    "stock-beta": [
        "Regress {co}'s weekly returns on the KOSPI over two years and give me the beta.",
        "How much does {co} tend to move when the KOSPI moves 1%?",
        "What is {co}'s market beta and R-squared against the KOSPI?",
        "Is {co} more or less volatile than the market, measured by beta?",
    ],
    "portfolio-rebalancing": [
        "My account has drifted; generate whole-share trades to return to my target weights, including {co}.",
        "I want to cut my position in {co} to 20% of the portfolio; what orders bring all holdings back to target?",
        "Turn these target allocations into buy and sell orders for my KRX holdings.",
        "Rebalance my five-stock portfolio, which includes {co}, while keeping a small cash buffer.",
    ],
    "bond-ytm": [
        "At a clean price of 9,720 won, what yield to maturity does {co}'s corporate bond offer?",
        "Work out the YTM of a 10-year KTB with a 2.75% coupon priced at 96.4.",
        "What yield does this KRW bond trade at, given its coupon schedule and price?",
        "Turn the quoted price of {co}'s 2029 bond into a yield to maturity.",
    ],
    "major-shareholder-changes": [
        "Which investors reported crossing 5% in {co} this year?",
        "Show me the bulk-holding report history for {co} and the stated purposes.",
        "Did any 5% holder of {co} change its holding purpose recently?",
        "List changes in {co}'s large shareholdings from 5% reports over the past year.",
    ],
    "foreign-investor-flows": [
        "What have foreigners done in {co} over the past month: how much net buying or selling?",
        "Give me daily net buying of {co} by foreign investors and institutions.",
        "Are foreign investors still accumulating shares of {co}?",
        "Show cumulative foreign net purchases of {co} since the start of the quarter.",
    ],
    "peer-comparison-table": [
        "Compare {co} with three listed rivals on P/E, P/B, EV/EBITDA and ROE.",
        "Put together a comparable company table for {co} with peer medians.",
        "How expensive is {co} against the median of the peers I give you?",
        "Line up {co} and its domestic competitors on valuation and profitability multiples.",
    ],
    "fx-translation": [
        "Restate {co}'s income statement and balance sheet in US dollars.",
        "What do {co}'s revenue and total assets look like in USD at the proper exchange rates?",
        "Convert {co}'s latest financials from won into dollars for a comparison with US companies.",
        "Translate {co}'s KRW statements to USD using average and period-end rates.",
    ],
    "dart-consolidated-statements": [
        "Pull {co}'s full consolidated statements for the latest annual report from DART.",
        "I need every line of {co}'s consolidated cash flow statement for 2024 from the DART API.",
        "Download {co}'s consolidated balance sheet and income statement for the second quarter.",
        "Fetch {co}'s consolidated financial statements via the DART OpenAPI and save them as CSV.",
    ],
    "earnings-surprise": [
        "By how much did {co}'s operating profit beat or miss consensus last quarter?",
        "How did {co}'s reported revenue compare with the analyst consensus?",
        "Was {co}'s latest quarter a positive or negative earnings surprise?",
        "Measure the gap between {co}'s reported quarterly profit and street estimates.",
    ],
    "pe-band-chart": [
        "Plot {co}'s share price against P/E bands of 5x to 25x trailing earnings over five years.",
        "Is {co} near the top or bottom of its historical P/E band?",
        "Make a five-year P/E band chart for {co}.",
        "Show where {co}'s price sits relative to fixed multiples of its trailing EPS over time.",
    ],
    "ex-dividend-calendar": [
        "By when must I buy shares of {co} to receive the upcoming dividend?",
        "What are the record date, ex-date and pay date of {co}'s next dividend?",
        "{co} sets its dividend record date after the board decision; when is it this year?",
        "Find the ex-dividend date for {co}'s year-end payout.",
    ],
    "bond-duration": [
        "What is the modified duration of {co}'s 7-year bond at a 3.8% yield?",
        "How much would this KTB lose if yields rose 100bp, using duration and convexity?",
        "Compute Macaulay duration and convexity for a 4% coupon bond due in 2033.",
        "How sensitive is {co}'s bond price to interest rate changes?",
    ],
    "fx-sensitivity": [
        "According to its notes, how much would {co}'s pre-tax profit change if the won fell 10% against the dollar?",
        "What does {co}'s financial risk note say about FX sensitivity?",
        "Estimate the profit impact on {co} of a 5% stronger dollar from its currency risk table.",
        "How exposed is {co}'s pre-tax income to KRW/USD moves?",
    ],
    "dupont-roe": [
        "Split {co}'s return on equity into net margin, asset turnover and leverage for five years.",
        "Why did {co}'s ROE change: margins, asset turnover or financial leverage?",
        "Give me a three-factor DuPont breakdown of {co}'s ROE.",
        "Which DuPont factor explains {co}'s ROE improvement?",
    ],
    "dart-segment-revenue": [
        "How much revenue and operating profit did each of {co}'s business segments report?",
        "Pull {co}'s operating segment figures from the notes of its latest DART filing.",
        "Which segment of {co} contributes the most sales?",
        "Show {co}'s results by reportable segment and reconcile them to group revenue.",
    ],
    "debt-maturity-profile": [
        "How much of {co}'s borrowings come due in the next 12 months compared with its cash?",
        "Build a maturity ladder of {co}'s loans and bonds.",
        "When do {co}'s debts mature over the next five years?",
        "Bucket {co}'s borrowings by maturity year from the borrowings note.",
    ],
    "historical-volatility": [
        "What is {co}'s 20-day realized volatility, annualized?",
        "Compute {co}'s historical volatility over 60 and 252 trading days.",
        "Is {co}'s daily return volatility higher this month than over the past year?",
        "Give me {co}'s annualized volatility from daily log returns.",
    ],
    "dcf-valuation": [
        "What is {co} worth per share on a five-year discounted cash flow model?",
        "Discount {co}'s forecast unlevered free cash flows at 8.5% with 1.5% terminal growth.",
        "Build a DCF for {co} from my growth and margin assumptions and bridge to equity value.",
        "Estimate {co}'s intrinsic value with a DCF and give me value per share.",
    ],
    "preliminary-earnings-reader": [
        "{co} released preliminary quarterly results; what are the YoY and QoQ changes?",
        "From {co}'s preliminary earnings filing, how much did operating profit grow versus a year ago?",
        "Did {co}'s preliminary results show a turnaround to profit?",
        "Read {co}'s preliminary results announcement and tabulate the changes in revenue and net income.",
    ],
    "insider-trading-filings": [
        "Which of {co}'s executives sold shares in the last three months?",
        "Show the share trades reported by {co}'s officers and major shareholders this year.",
        "Is there net insider buying or selling at {co} lately?",
        "Did any insider at {co} trade shares shortly before an earnings release?",
    ],
    "gross-margin-bridge": [
        "Why did {co}'s gross margin improve this year: higher prices, more volume or cheaper inputs?",
        "Bridge {co}'s gross margin from last year to this year.",
        "How much of {co}'s gross margin change came from unit costs?",
        "Make a gross margin waterfall for {co} with price, volume and cost effects.",
    ],
    "cash-conversion-cycle": [
        "How long does {co} take to turn inventory and receivables into cash?",
        "Compute {co}'s cash conversion cycle for the last eight quarters.",
        "Are {co}'s days sales outstanding and inventory days rising?",
        "Give me {co}'s DSO, DIO, DPO and CCC trend.",
    ],
    "value-at-risk": [
        "What is the 95% one-day historical VaR of my stock portfolio, which includes {co}?",
        "How much could my holdings lose on a bad day at 99% confidence?",
        "Run historical simulation VaR on my portfolio with 500 days of returns.",
        "Give me my portfolio's daily value at risk in won.",
    ],
    "credit-rating-history": [
        "Show the rating actions on {co}'s bonds by Korean agencies over five years.",
        "Has any domestic agency changed {co}'s rating outlook recently?",
        "What credit ratings do KIS, NICE and Korea Ratings assign to {co}, and how have they moved?",
        "When was {co} last downgraded by a Korean rating agency?",
    ],
    "treasury-share-buyback": [
        "How large is {co}'s treasury share purchase plan relative to its free float?",
        "Did {co} buy back the shares it said it would, and through a trust or directly?",
        "Summarize {co}'s share repurchase decisions over the past two years.",
        "What period and amount did {co} set for its latest buyback?",
    ],
    "cb-overhang-tracker": [
        "How much potential dilution is left from {co}'s unconverted convertible bonds?",
        "Which of {co}'s CB series can be converted now, and into how many shares?",
        "Estimate the new shares {co} could issue if its remaining CBs convert at current prices.",
        "Track {co}'s outstanding convertible bond overhang.",
    ],
    "risk-contribution": [
        "How much of my portfolio's volatility comes from {co}?",
        "Break my portfolio risk down by holding using the covariance matrix.",
        "Which stock in my portfolio contributes the most to total risk?",
        "Compute percentage risk contributions for my holdings, including {co}.",
    ],
    "short-selling-balance": [
        "What share of {co}'s outstanding shares is currently sold short?",
        "How has the short-selling balance on {co} changed this month?",
        "Show {co}'s short balance in won and as a percent of shares.",
        "Is short interest in {co} near its one-year high?",
    ],
    "ipo-lockup-expiry": [
        "Which recent KOSDAQ listings have lock-ups ending next month?",
        "How many of {co}'s shares become free to sell when the IPO lock-up ends?",
        "List lock-up release dates and unlocked share counts for this year's IPOs.",
        "When can the venture capital investors in {co} sell after its listing?",
    ],
}
