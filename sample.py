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

def get_data(samples, output, *interests):
    """
    Accessing each sample, organize and write the interested entires.

    Args:
        samples(str list) : list of unique identifiers of the samples
        output(str) : file name of the output
        *interests : multiple string of the tags of interested entries. If the
            tags are not in the 990 form, exception would be raised

    """
    
    with open(output, 'w') as out_csv:
        # The headers are the identifier and interested tags
        writer = csv.DictWriter(out_csv, fieldnames = ['id'] + list(interests), 
                                delimiter = '\t')
        writer.writeheader()

        url_p = 'https://s3.amazonaws.com/irs-form-990/'
        url_e = '_public.xml'

        for sample in samples:
            print(sample)
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

def _indicator(probability):
    """
    Indicator (Bernoulli) random variable with p = probability.

    Args:
        probability(float) : the probability of success, from 0 to 1.

    Returns:
        True : with probability p
        False : with probability (1 - p)

    Raises:
        ValueError : if probability not in the interval [0,1]
    """
    if probability < 0 or probability > 1:
        raise ValueError('probability should be from 0 to 1')

    return random.random() <= probability

