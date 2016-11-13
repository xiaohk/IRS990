import sample

curr_sample = sample.sampling(100000, 'index_2015.csv')
sample.get_data(curr_sample, 'sample_2015.csv', 
                'PYContributionsGrantsAmt', 
                'CYContributionsGrantsAmt', 
                'TotalContributionsAmt', 
                'ContributionsGiftsGrantsEtcAmt',
                'PYInvestmentIncomeAmt', 
                'CYInvestmentIncomeAmt')
