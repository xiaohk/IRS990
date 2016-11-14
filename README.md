*Click `IRS990.ipynb` to see documentations in a better format.*


## Approaches
After getting the data, I did some research about the 990 Form. I decide to do a mini-project studying the relations between the contribution and investment of organizations. There are many different approaches.
1. Study the contribution changing rate with investment changing rate over 1, 2, or 3 years
2. Study the contribution and investment in a specific year
3. Study the contribution and investment in a specific area (i.e. Madison WI)
4. Study the contribution and investment over different kinds of orgs
5. $\dots \dots$

## Steps
For this project, I would choose 2 over 2015 population. Following are the steps I am planning to take.
1. Fairly create a sample of orgs
    - With re-usable parameters(size, etc)
2. Get the interested entries for the orgs created above
    - With re-usable parameters(interested keys)
    - Write the result into a file, so it is easier for analyzing
3. Filter dirty data
    - Remove unhelpful data from the sample file
3. Analyze the data
    - Basis measuring statistics
    - Virtualization 
    - Explore relations of two keys

## Sampling
To be fair, I would use random sampling. Since the population size varies from year to year, I would use reservoir sampling algorithm.


```python
import csv
import random
import xml.etree.ElementTree as ET
import requests

def sampling(size, f_name):
    """
    Random sampling `size` samples using the f_name csv file as population. 
    Reservoir sampling algorithm is used.

    Args:
        size(int) : sample size
        f_name(string) : name of the population file

    Returns:
        int list : samples, each element is the unique identifier of the filing
    """
    samples = []
    counter = 0
    with open(f_name, 'r') as fp:
        first_line = fp.readline()
        for line in fp:
            counter += 1
            # Fill in the samples 
            if len(samples) < size:
                samples.append(line.strip('\n')[-18:])
            # Dynamic probability of replacing samples with the new sample
            else:
                indicator = int(random.random() * counter)
                # With size/counter probability
                if indicator < size:
                    samples[indicator] = line.strip('\n')[-18:]
    return samples
```

## Fetching data
Once we have the organization samples, we can access the database to get the values we are interested. To make the function reusable, I would use a flexible approach, instead of hard code.

The flow is 
1. Use the unique identifier to locate the 990 form
2. Parse the xml file
3. Fetch the values with interested tags
4. Organize and create local csv file


```python

def get_data(samples, output, *interests):
    """
    Accessing each sample, organize and write the interested entires.

    Args:
        samples(str list) : list of unique identifiers of the samples
        output(str) : file name of the output
        *interests : multiple string of the tags of interested entries. If the
            tags are not in the 990 form, values will be replaced with empty string

    """
    
    with open(output, 'w') as out_csv:
        # The headers are the identifier and interested tags
        writer = csv.DictWriter(out_csv, fieldnames = ['id'] + list(interests), 
                                delimiter = '\t')
        writer.writeheader()

        url_p = 'https://s3.amazonaws.com/irs-form-990/'
        url_e = '_public.xml'
        
        # Use counter to track the task rate
        counter = 0
        total = float(len(samples))

        for sample in samples:
            counter += 1
            print("Finished " + str(counter / total * 100) + "%")
            # Parse the xml file
            xml_response = requests.get(url_p + sample + url_e)
            root = ET.fromstring(xml_response.content)

            # Get the data for interested tags
            data = {'id' : sample}

            for tag in interests:
                # For missing data, we use empty string as replacement
                try:
                    data[tag] = next(root.iter('{http://www.irs.gov/efile}' + 
                                               tag)).text
                except StopIteration:
                    data[tag] = ''

            writer.writerow(data)
```

Now we can write a script to do the real operations. 

I choose the sample size to be 30000, and interested keys are all keys related to contribution and investment. 

This script has run for hours, so I used `ssh` and `screen` to execute it on the computers in the CS lab.


```python
import sample

curr_sample = sample.sampling(30000, 'index_2015.csv')
sample.get_data(curr_sample, 'sample_2015.csv', 
                'PYContributionsGrantsAmt', 
                'CYContributionsGrantsAmt', 
                'TotalContributionsAmt', 
                'ContributionsGiftsGrantsEtcAmt',
                'PYInvestmentIncomeAmt', 
                'CYInvestmentIncomeAmt')
```

    Finished 100.0%


The result(first 15 lines) is shown below.


```python
with open('sample_2015.csv', 'r') as fp:
    length = 0
    for line in fp:
        # Illustrate one part of the csv file
        if length < 15:
            print(line)
        length += 1
```

    id	PYContributionsGrantsAmt	CYContributionsGrantsAmt	TotalContributionsAmt	ContributionsGiftsGrantsEtcAmt	PYInvestmentIncomeAmt	CYInvestmentIncomeAmt
    
    201542249349300954	344438	68709	68709		385	435
    
    201510659349200201				4910		
    
    201521699349200427				310		
    
    201530429349200853				4903		
    
    201531349349305353	38335	49927	49927		0	0
    
    201542399349300724	603535	348126	348126		0	9842
    
    201530629349100408						
    
    201502529349100310						
    
    201502239349301460	137017	210906	210906		0	0
    
    201511359349101536						
    
    201502309349200960						
    
    201542029349300824		989148	989148			131
    
    201502439349300735	372522	441452	441452		98	-3174
    
    201531209349101023			240000			
    



```python
print(length)
```

    28259


## Format the data
It ends the process of building a sample. Now I want to focus on the `PYContributionsGrantsAmt` and  `PYInvestmentIncomeAmt` two entries. I want to see whether there are some relations between of them.

Although we have 28259 neat and clean entries with the key which we may be interested in, many of them do not have `PYContributionsGrantsAmt` and `PYInvestmentIncomeAmt`. To make reading csv easier, we need to erase the unvalid data from the sample file.


```python
with open('sample_2015.csv', 'r') as fp:
    with open('interest.csv', 'w') as out_fp:
        # Header line
        out_fp.write(fp.readline())
        for line in fp:
            entries = line.split('\t')
            
            # We only want the data with  valid PYContributionsGrantsAmt 
            # and PYInvestmentIncomeAmt
            if entries[1] and entries[1] != "RESTRICTED" and \
            entries[5] and entries[5] != "RESTRICTED":
                out_fp.write(line)
```


```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Constants for the key
CONTRI = "PYContributionsGrantsAmt"
INVEST = "PYInvestmentIncomeAmt"

# Build data frame for analysis, from_csv() reader would maek some errors while parsing
df = pd.DataFrame.from_csv('interest.csv', sep = '\t')
```

                        PYContributionsGrantsAmt  CYContributionsGrantsAmt  \
    id                                                                       
    201542249349300954                    344438                     68709   
    201531349349305353                     38335                     49927   
    201542399349300724                    603535                    348126   
    201502239349301460                    137017                    210906   
    201502439349300735                    372522                    441452   
    201500729349300330                   3886855                   4286945   
    201522369349300207                    432619                    594609   
    201501349349305660                    418960                     44427   
    201522369349300307                    277082                    722789   
    201541359349309199                   6017511                   6118975   
    201521599349300852                    294874                    254497   
    201531359349306593                         0                         0   
    201532299349302418                    447104                    431291   
    201532299349302443                   1534385                   2240547   
    201521319349300912                     39290                     54034   
    201532299349302518                         0                     41404   
    201532299349301003                         0                         0   
    201532299349302558                    692968                    712936   
    201521499349300842                    390470                    152370   
    201501319349303315                         0                         0   
    201541769349300424                    407204                    488917   
    201531599349300028                     37778                     64427   
    201532469349300403                     98017                     78012   
    201501669349300845                     39105                     54946   
    201520489349300942                   4032666                   3452716   
    201500129349300230                   9530144                   3885286   
    201512229349301031                   4255925                   6269615   
    201531349349307178                     11982                     10664   
    201511359349306896                    132081                    240741   
    201531669349300018                    426090                     69830   
    ...                                      ...                       ...   
    201530209349300648                       437                      3813   
    201500669349300410                    533566                    728247   
    201542269349300449                     24935                     98423   
    201500709349300305                     17682                     19907   
    201521329349301422                         0                         0   
    201540129349300789                   5788068                   6147855   
    201540159349300404                    124625                         0   
    201500859349300825                    957053                    978098   
    201510709349300111                     37833                     35934   
    201510709349300126                    619693                    749195   
    201532109349301373                         0                         0   
    201541949349301279                      2000                      2000   
    201501479349300635                    389681                    151891   
    201520659349300527                   3050307                   3188885   
    201542749349300544                         0                         0   
    201511669349300816                     60000                     55000   
    201531359349307668                    175485                    132995   
    201501059349300210                     14914                     74577   
    201502269349302760                    219909                    234079   
    201512119349301206                    461573                    486900   
    201520659349300632                    117575                    104511   
    201510239349300606                   2310619                   2749217   
    201520479349301102                     74699                    110968   
    201521329349301002                    160200                    180300   
    201501359349308185                      5537                      3075   
    201530489349300823                   3428585                  11970151   
    201501329349303335                      6500                    302632   
    201542119349301279                    929323                   1114449   
    201520649349300002                    356433                    258137   
    201521349349305142                         0                         0   
    
                       TotalContributionsAmt  ContributionsGiftsGrantsEtcAmt  \
    id                                                                         
    201542249349300954                 68709                             NaN   
    201531349349305353                 49927                             NaN   
    201542399349300724                348126                             NaN   
    201502239349301460                210906                             NaN   
    201502439349300735                441452                             NaN   
    201500729349300330               4286945                             NaN   
    201522369349300207                594609                             NaN   
    201501349349305660                 44427                             NaN   
    201522369349300307                722789                             NaN   
    201541359349309199               6118975                             NaN   
    201521599349300852                254497                             NaN   
    201531359349306593                   NaN                             NaN   
    201532299349302418                431291                             NaN   
    201532299349302443               2240547                             NaN   
    201521319349300912                 54034                             NaN   
    201532299349302518                 41404                             NaN   
    201532299349301003                   NaN                             NaN   
    201532299349302558                712936                             NaN   
    201521499349300842                152370                             NaN   
    201501319349303315                   NaN                             NaN   
    201541769349300424                488917                             NaN   
    201531599349300028                 64427                             NaN   
    201532469349300403                 78012                             NaN   
    201501669349300845                 54946                             NaN   
    201520489349300942               3452716                             NaN   
    201500129349300230               3885286                             NaN   
    201512229349301031               6269615                             NaN   
    201531349349307178                 10664                             NaN   
    201511359349306896                240741                             NaN   
    201531669349300018                 69830                             NaN   
    ...                                  ...                             ...   
    201530209349300648                  3813                             NaN   
    201500669349300410                728247                             NaN   
    201542269349300449                 98423                             NaN   
    201500709349300305                 19907                             NaN   
    201521329349301422                   NaN                             NaN   
    201540129349300789               6147855                             NaN   
    201540159349300404                   NaN                             NaN   
    201500859349300825                978098                             NaN   
    201510709349300111                 35934                             NaN   
    201510709349300126                749195                             NaN   
    201532109349301373                     0                             NaN   
    201541949349301279                  2000                             NaN   
    201501479349300635                151891                             NaN   
    201520659349300527               3188885                             NaN   
    201542749349300544                   NaN                             NaN   
    201511669349300816                 55000                             NaN   
    201531359349307668                132995                             NaN   
    201501059349300210                 74577                             NaN   
    201502269349302760                234079                             NaN   
    201512119349301206                486900                             NaN   
    201520659349300632                104511                             NaN   
    201510239349300606               2749217                             NaN   
    201520479349301102                110968                             NaN   
    201521329349301002                180300                             NaN   
    201501359349308185                  3075                             NaN   
    201530489349300823              11970151                             NaN   
    201501329349303335                302632                             NaN   
    201542119349301279               1114449                             NaN   
    201520649349300002                258137                             NaN   
    201521349349305142                   NaN                             NaN   
    
                        PYInvestmentIncomeAmt  CYInvestmentIncomeAmt  
    id                                                                
    201542249349300954                    385                    435  
    201531349349305353                      0                      0  
    201542399349300724                      0                   9842  
    201502239349301460                      0                      0  
    201502439349300735                     98                  -3174  
    201500729349300330                 104638                 121881  
    201522369349300207                      0                      0  
    201501349349305660                 391823                 307090  
    201522369349300307                  43051                  59512  
    201541359349309199                   5981                   2582  
    201521599349300852                    181                    103  
    201531359349306593                    270                    318  
    201532299349302418                     10                     37  
    201532299349302443                     63                      0  
    201521319349300912                   8923                  47214  
    201532299349302518                  50005                  38501  
    201532299349301003                   1076                   4194  
    201532299349302558                  41411                  15722  
    201521499349300842                  69869                  65164  
    201501319349303315                    502                    516  
    201541769349300424                    886                    486  
    201531599349300028                    121                    159  
    201532469349300403                      0                      0  
    201501669349300845                     96                     96  
    201520489349300942                  50917                 112657  
    201500129349300230                 589039                 894849  
    201512229349301031                   7626                  -9368  
    201531349349307178                      0                      0  
    201511359349306896                   1109                    299  
    201531669349300018                   2556                   2672  
    ...                                   ...                    ...  
    201530209349300648                     80                     64  
    201500669349300410                   3039                  11793  
    201542269349300449                  12932                  35255  
    201500709349300305                    275                   4185  
    201521329349301422                  22128                      0  
    201540129349300789                 -21401                  96108  
    201540159349300404                  58686                  49320  
    201500859349300825                    544                    456  
    201510709349300111                      0                      0  
    201510709349300126                     36                     30  
    201532109349301373                   1321                   1496  
    201541949349301279                 137158                    345  
    201501479349300635                  86942                  50229  
    201520659349300527                   1160                   3072  
    201542749349300544                 375153                 587794  
    201511669349300816                   8598                   7059  
    201531359349307668                    471                      0  
    201501059349300210                      4                      8  
    201502269349302760                     55                   7006  
    201512119349301206                  24778                  10737  
    201520659349300632                  57114                   4411  
    201510239349300606               16649673               11022391  
    201520479349301102                  -7026                   5713  
    201521329349301002                    833                    135  
    201501359349308185                   5696                   6733  
    201530489349300823                  52848                  14436  
    201501329349303335                    758                    610  
    201542119349301279                    472                    350  
    201520649349300002                      0                      0  
    201521349349305142                 163189                 151724  
    
    [11747 rows x 6 columns]


## Analyzing the data
After getting the 11747 entries from the valid data, we can start our analysis. 
1. Basis measuring statistics
2. Virtualization 
3. Explore relations of two keys


```python
print(df[CONTRI].mean())
print(df[CONTRI].median())
print(df[CONTRI].std())
```

    2142237.82617
    18194432.1808
    173226.0



```python
print(df[INVEST].mean())
print(df[INVEST].median())
print(df[INVEST].std())
```

    359683.324849
    3618067.79855


The standard deviation is so large that the mean is not accurate. Two medians can give us a big picture of two data. Next we can draw the box plot to further illustrate the measures.


```python
%matplotlib inline
df.boxplot(CONTRI)
```




    <matplotlib.axes._subplots.AxesSubplot at 0x10643a240>




![png](output_17_1.png)



```python
df.boxplot(INVEST)
```




    <matplotlib.axes._subplots.AxesSubplot at 0x106acfa90>




![png](output_18_1.png)


The boxplots show that both data are highly skewed, and there are some outliers.


```python
sca = df.plot(x=INVEST, y=CONTRI, style='o')
sca.set_ylim(0,10000000)
```




    (0, 10000000)




![png](output_20_1.png)


Many organize have a small (converges to $0$) investment but a significant contribution. We need to further understand the data before doing other analysis and operations.

From the right part of the plot, we cannot see there exists a clear linear relation between investment and contribution. 

## Conclusion
It is very fun to do a real-world data analyzing. I have learned A LOT, including xml parsing, pandas data analyzing, from this mini project.

The result is not quite as what I expected. If I have more time, or I would redo this project, I would definitely:

1. Do more research on the 990 Form, and come up with more helpful key entries to use.
2. Try to clustering the population. Using random sampling is not very fair in this project. I would try to divide the organizations into different groups, and perform the analysis in and within those groups.
3. Check the result of pandas csv reading result, it seems there are some wrongly-formated entries.
4. Explore more about the relations between contribution and investment.
3. Except the contribution and investment, I am also interested in some other cool studies. For example, how LGBTQ organizations develop in the United States from 2010.

