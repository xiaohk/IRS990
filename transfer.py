with open('sample_2015.csv', 'r') as fp:
    with open('interest.csv', 'w') as out_fp:
        out_fp.write(fp.readline())
        for line in fp:
            entries = line.split('\t')
            if entries[1] and entries[1] != "RESTRICTED" and \
            entries[5] and entries[5] != "RESTRICTED":
                out_fp.write(line)
        
