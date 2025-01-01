# Positive EV Betting in the Premier League

![HighMatchDiagram](assets/banner.png)

I’m a football fan who likes to bet and also likes math. I thought it would be cool to see how some of the concepts I’ve learned can be applied to betting on football.

---

# Initial Approach

## Collecting the Data

In order to find the expected value of any bet, I need the probabilities of the thing I will be betting as well as the return on that bet. To start with, I grabbed matchday odds from a local betting app, and got predictions from Opta’s supercomputer to get probabilities for win, draw, and loss for each match.

The expected value tells me how much I should expect over a long run to win per euro bet. The formula for expected value is given by:
     
$$
EV = P(\text{parlay win}) \cdot (\text{combined odds} - 1) - (1 - P(\text{parlay win})).
$$

where the combined odds are the multiplication of all individual odds for each match in a parlay, given by:

$$
P(\text{combined odds}) = \prod_{i=1}^{j} o_i
$$

where j is the number of bets in the parlay.

The probability of winning is calculated from probability of all outcomes in the parlay hitting:

$$
P(\text{parlay win}) = \prod_{i=1}^{n} P_i
$$

where n is the number of matches in a matchweek.

Note: for some matches I used my own intuition. Specifically, for matchday 20 of the 24/25 PL season the supercomputer had liverpool winning against manchester unite at 71%. In this sense, I used my own judgement and put the win percentage to 100.

## Running Numbers

After collecting the data, I ran every single parlay combination, and sorted by the EV in order to find the highest paying bets. For each parlay, I returned 3 different parameters: the probability of it hitting, the EV, and the combined odds of the parlay. With this information I picked the parlay with the highest EV and visualised some of the returns.

### High-EV, High Match Parlays

The most profitable parlays were aways those with the highest number of matches strung together. Of course in this way we would get ridiculously high odds - some as big as 7745 (winning 7745 euro on a 1 euro bet). The problem with such parlays is that they had probabilities just as low to match the high payouts. A commoon probability for such parlays would be in the 0.0005% - 0.007% range. 

The reality was shown in the following equity curve. It was a slow and dreary wait to become profitable. Not to mention that the minimum wait time was at least 1000 weeks.

![HighMatchDiagram](assets/highmatches.png)


---

### High-EV, Lower Match Parlays

I modeled each parlay under the binomial distribution. Each match has three potential outcomes, each with a probability of $\frac{1}{3}$. For the sake of simplicity, I focused on betting on just one of those outcomes for each match. This setup allowed me to calculate the probabilities of hitting a parlay with different numbers of matches.

By plotting the binomial distribution, I could visualize how the probability of success changes as the number of matches ($n$) in a parlay increases. This gives insight into which $n$ has the highest probability of hitting and can help guide the strategy toward more frequent wins while managing risk.

![Binomial_Distribution](assets/binomial.png)

In this case the highest hitting number was three!

We can now adjust our initial calculation to limit the number of matches in a single parlay to 3. Of these calculations 2 different strategies can be considered. One is in prioritising probability over expected value, and the other to prioritise expected value. Taking matchday 20 as an example, we have 2 different entries:

Parlay 1: [('Tottenham vs Newcastle', 'Win'), ('Liverpool vs Man United', 'Win'), ('Wolves vs Nottingham Forest', 'Loss')], EV: 1.4940742400000002, Probability: 0.28350000000000003, Combined Odds: 8.79744

Parlay 7: [('Fulham vs Ipswich Town', 'Win'), ('Liverpool vs Man United', 'Win'), ('Wolves vs Nottingham Forest', 'Loss')], EV: 1.0571812352000003, Probability: 0.4347, Combined Odds: 4.73241

Plotting both equity curves for much smaller timeframes, we see that for parlay 1:

![Equity_Curve_028](assets/prob028.png)

We see that we see profitability at around week 18, with a much faster comeback and a much smaller drawdown. For parlay 7:

![Equity_Curve_028](assets/prob043.png)

Which is quite similar to parlay 1, with a smaller drawdown, and faster profitability.

## Picking the Trade-off

An important thing to note is that the fixtures change every week, along with the odds! Achieving a positive EV of 1.49 may not always be possible. In that sense, we must try to stick as closely as possible to 1 strategy, that may appear more reliably. In this case, achieving an EV of over 1.05, with at least a probability of 0.4 should be our goal. In other words, we aim for higher probability reliable 3 way parlays.

# Risk

The question is now how much I should bet per parlay. The kelly criterion explains a method in order to determine how much I should risk per bet, according to formula:

$$
f^* = \frac{bp-q}{b}
$$

where:
- $f^*$ is the bet size.
- $b$ is the net odds.
- $p$ is the probability of winning.
- $q = (1-p)$ is the probability of losing.

This means that for every matchweek, we size our bets differently, according to the specific odds, and probabilities we get. Note that the strategy will remain the same, we still aim for high probability bets, but we vary how much we bet according to the criterion. For example in matchday 20, as seen above for parlay 7, we have Probability: 0.4347, and Combined Odds: 4.73241. Thus we get bet size as:

$$
f^* = \frac{4.73241*0.4347-(1-0.4347)}{4.73241} = 0.3619
$$

This result indicates that I should bet 36.19% of my account balance on this bet. The problem with such a high number is that if 3 bets go wrong in a row, I bust. Following the original binomial distribution the probability of that occouring is 0.296. In other words almost 1/3 of the time, if I follow such a high risk, I will tend to lose my account. To account for this, I plotted the time to be profitable against a fraction of the kelly criterion in steps of 0.05 from 0 to 1:

![Time_to_profit](assets/time_to_profit.png)

Which shows that 0.05, 0.1, and 0.15 to be the lowest time to profit. In this case, this would make sense. By minimizing my risk, I can still keep playing the game. Below are the balance curves for each of the three kelly fractions. By intuition it would make most sense to take the 0.15, as we maximise our profit while minimizing our risk in the trade off. 

![Kelly_Curve_005](assets/kelly005.png)

![Kelly_Curve_010](assets/kelly010.png)

![Kelly_Curve_015](assets/kelly015.png)

Our new formula, for all matchweeks will be:

$$
f^* = \frac{0.15\cdot(bp-q)}{b}
$$

And for matchday 20:

$$
f^* = \frac{0.15\cdot(4.73241*0.4347-(1-0.4347))}{4.73241} = 0.054289
$$

Which is 5.43% of our account.

# Further Exploration

1. Different bookmakers have different odds. A change of 0.05 is huge for EV.
2. Different football prediction websites? Which ones are reliable, and stats and data driven?
3. Timing of bet. Odds get worse closer to match day. Betting for matchweek n right after matchweek n-1 may be the best time.
